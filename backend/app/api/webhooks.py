"""
Webhook Management API
Allows users to create and manage webhooks for event notifications
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import secrets
import hmac
import hashlib
import httpx

from ..database import get_db
from ..dependencies import get_current_user
from .. import models
from ..models_integrations import Webhook, WebhookDelivery
from ..schemas_integrations import (
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookDeliveryResponse,
    WebhookTestRequest
)

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])


@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new webhook for receiving event notifications.

    **Events available:**
    - asset.created, asset.updated, asset.deleted
    - compliance.violation
    - change.approved, change.rejected
    - sla.breached, budget.threshold
    - user.created
    """
    # Generate a secure secret for webhook signature verification
    secret = secrets.token_urlsafe(32)

    # Create webhook
    webhook = Webhook(
        name=webhook_data.name,
        url=str(webhook_data.url),
        secret=secret,
        events=[event.value for event in webhook_data.events],
        retry_count=webhook_data.retry_count,
        timeout_seconds=webhook_data.timeout_seconds,
        created_by=current_user.user_id,
        active=True
    )

    db.add(webhook)
    db.commit()
    db.refresh(webhook)

    return webhook


@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all webhooks"""
    query = db.query(Webhook)

    if active_only:
        query = query.filter(Webhook.active == True)

    webhooks = query.offset(skip).limit(limit).all()
    return webhooks


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get webhook by ID"""
    webhook = db.query(Webhook).filter(Webhook.webhook_id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook


@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: int,
    webhook_update: WebhookUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update webhook"""
    webhook = db.query(Webhook).filter(Webhook.webhook_id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    # Update fields
    update_data = webhook_update.model_dump(exclude_unset=True)

    # Convert events enum to string values
    if "events" in update_data and update_data["events"]:
        update_data["events"] = [event.value for event in update_data["events"]]

    # Convert URL to string
    if "url" in update_data and update_data["url"]:
        update_data["url"] = str(update_data["url"])

    for field, value in update_data.items():
        setattr(webhook, field, value)

    db.commit()
    db.refresh(webhook)
    return webhook


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete webhook"""
    webhook = db.query(Webhook).filter(Webhook.webhook_id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    db.delete(webhook)
    db.commit()
    return None


@router.post("/{webhook_id}/test", response_model=dict)
async def test_webhook(
    webhook_id: int,
    test_request: WebhookTestRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Test a webhook by sending a test payload.
    Returns the response from the webhook endpoint.
    """
    webhook = db.query(Webhook).filter(Webhook.webhook_id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    # Create test payload
    payload = test_request.test_payload or {
        "event": test_request.event.value,
        "data": {
            "id": 999,
            "name": "Test Event",
            "message": "This is a test webhook delivery"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    # Calculate signature
    payload_bytes = str(payload).encode('utf-8')
    signature = hmac.new(
        webhook.secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    # Send webhook
    start_time = datetime.utcnow()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook.url,
                json=payload,
                headers={
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Event": test_request.event.value,
                    "Content-Type": "application/json"
                },
                timeout=webhook.timeout_seconds
            )

            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Log delivery
            delivery = WebhookDelivery(
                webhook_id=webhook.webhook_id,
                event=test_request.event.value,
                payload=payload,
                status_code=response.status_code,
                response_body=response.text[:1000],  # Limit to 1000 chars
                success=(200 <= response.status_code < 300),
                duration_ms=duration_ms,
                attempt_number=1
            )
            db.add(delivery)

            # Update last triggered
            webhook.last_triggered = datetime.utcnow()
            db.commit()

            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.text[:500],
                "duration_ms": duration_ms,
                "message": "Webhook test successful"
            }

    except httpx.RequestError as e:
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Log failed delivery
        delivery = WebhookDelivery(
            webhook_id=webhook.webhook_id,
            event=test_request.event.value,
            payload=payload,
            error_message=str(e),
            success=False,
            duration_ms=duration_ms,
            attempt_number=1
        )
        db.add(delivery)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Webhook test failed: {str(e)}"
        )


@router.get("/{webhook_id}/deliveries", response_model=List[WebhookDeliveryResponse])
async def get_webhook_deliveries(
    webhook_id: int,
    skip: int = 0,
    limit: int = 50,
    success_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get delivery logs for a webhook"""
    webhook = db.query(Webhook).filter(Webhook.webhook_id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    query = db.query(WebhookDelivery).filter(WebhookDelivery.webhook_id == webhook_id)

    if success_only:
        query = query.filter(WebhookDelivery.success == True)

    deliveries = query.order_by(WebhookDelivery.delivered_at.desc()).offset(skip).limit(limit).all()
    return deliveries


@router.get("/{webhook_id}/secret", response_model=dict)
async def get_webhook_secret(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get webhook secret for signature verification.
    Only webhook owner or admin can access.
    """
    webhook = db.query(Webhook).filter(Webhook.webhook_id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    # Check permissions
    if webhook.created_by != current_user.user_id and current_user.role.role_name != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized to access webhook secret")

    return {
        "webhook_id": webhook.webhook_id,
        "secret": webhook.secret,
        "message": "Use this secret to verify webhook signatures in your endpoint"
    }
