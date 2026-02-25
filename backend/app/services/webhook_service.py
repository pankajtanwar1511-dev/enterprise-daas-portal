"""
Webhook Trigger Service
Handles triggering webhooks when events occur in the system
"""
import httpx
import hmac
import hashlib
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from ..models_integrations import Webhook, WebhookDelivery, WebhookEventType


class WebhookService:
    """Service for triggering webhooks"""

    @staticmethod
    async def trigger_event(
        db: Session,
        event_type: str,
        payload: Dict[str, Any],
        related_id: int = None
    ) -> List[WebhookDelivery]:
        """
        Trigger all webhooks subscribed to a specific event type.

        Args:
            db: Database session
            event_type: Event type (e.g., 'asset.created')
            payload: Event data to send
            related_id: Optional ID of related entity (asset_id, user_id, etc.)

        Returns:
            List of WebhookDelivery objects
        """
        # Find all active webhooks subscribed to this event
        webhooks = db.query(Webhook).filter(
            Webhook.active == True,
            Webhook.events.contains([event_type])
        ).all()

        if not webhooks:
            return []

        # Enrich payload with metadata
        full_payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload
        }

        # Trigger all webhooks concurrently
        deliveries = []
        tasks = [
            WebhookService._deliver_webhook(db, webhook, event_type, full_payload)
            for webhook in webhooks
        ]

        delivery_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in delivery_results:
            if isinstance(result, WebhookDelivery):
                deliveries.append(result)

        return deliveries

    @staticmethod
    async def _deliver_webhook(
        db: Session,
        webhook: Webhook,
        event_type: str,
        payload: Dict[str, Any],
        attempt: int = 1
    ) -> WebhookDelivery:
        """
        Deliver payload to a single webhook with retry logic.

        Args:
            db: Database session
            webhook: Webhook configuration
            event_type: Event type
            payload: Payload to deliver
            attempt: Current attempt number (for retries)

        Returns:
            WebhookDelivery record
        """
        # Calculate signature
        payload_str = str(payload)
        signature = hmac.new(
            webhook.secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        start_time = datetime.utcnow()
        delivery = None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook.url,
                    json=payload,
                    headers={
                        "X-Webhook-Signature": signature,
                        "X-Webhook-Event": event_type,
                        "X-Webhook-ID": str(webhook.webhook_id),
                        "X-Webhook-Attempt": str(attempt),
                        "Content-Type": "application/json"
                    },
                    timeout=webhook.timeout_seconds
                )

                duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                success = 200 <= response.status_code < 300

                # Create delivery record
                delivery = WebhookDelivery(
                    webhook_id=webhook.webhook_id,
                    event=event_type,
                    payload=payload,
                    status_code=response.status_code,
                    response_body=response.text[:1000],  # Limit to 1000 chars
                    success=success,
                    duration_ms=duration_ms,
                    attempt_number=attempt
                )

                db.add(delivery)

                # Update last triggered
                webhook.last_triggered = datetime.utcnow()

                db.commit()
                db.refresh(delivery)

                # Retry if failed and retries remaining
                if not success and attempt < webhook.retry_count:
                    await asyncio.sleep(min(2 ** attempt, 60))  # Exponential backoff
                    return await WebhookService._deliver_webhook(
                        db, webhook, event_type, payload, attempt + 1
                    )

                return delivery

        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Create failed delivery record
            delivery = WebhookDelivery(
                webhook_id=webhook.webhook_id,
                event=event_type,
                payload=payload,
                error_message=str(e)[:1000],
                success=False,
                duration_ms=duration_ms,
                attempt_number=attempt
            )

            db.add(delivery)
            db.commit()
            db.refresh(delivery)

            # Retry if retries remaining
            if attempt < webhook.retry_count:
                await asyncio.sleep(min(2 ** attempt, 60))  # Exponential backoff
                return await WebhookService._deliver_webhook(
                    db, webhook, event_type, payload, attempt + 1
                )

            return delivery

    @staticmethod
    def trigger_asset_created(db: Session, asset_data: Dict[str, Any]):
        """Convenience method for triggering asset.created event"""
        asyncio.create_task(
            WebhookService.trigger_event(
                db,
                WebhookEventType.ASSET_CREATED.value,
                asset_data,
                asset_data.get('asset_id')
            )
        )

    @staticmethod
    def trigger_asset_updated(db: Session, asset_data: Dict[str, Any]):
        """Convenience method for triggering asset.updated event"""
        asyncio.create_task(
            WebhookService.trigger_event(
                db,
                WebhookEventType.ASSET_UPDATED.value,
                asset_data,
                asset_data.get('asset_id')
            )
        )

    @staticmethod
    def trigger_asset_deleted(db: Session, asset_id: int):
        """Convenience method for triggering asset.deleted event"""
        asyncio.create_task(
            WebhookService.trigger_event(
                db,
                WebhookEventType.ASSET_DELETED.value,
                {"asset_id": asset_id},
                asset_id
            )
        )

    @staticmethod
    def trigger_compliance_violation(db: Session, violation_data: Dict[str, Any]):
        """Convenience method for triggering compliance.violation event"""
        asyncio.create_task(
            WebhookService.trigger_event(
                db,
                WebhookEventType.COMPLIANCE_VIOLATION.value,
                violation_data
            )
        )

    @staticmethod
    def trigger_sla_breached(db: Session, sla_data: Dict[str, Any]):
        """Convenience method for triggering sla.breached event"""
        asyncio.create_task(
            WebhookService.trigger_event(
                db,
                WebhookEventType.SLA_BREACHED.value,
                sla_data
            )
        )
