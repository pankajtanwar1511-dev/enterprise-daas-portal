"""
Slack Notification Service

Enhanced Slack integration for sending rich notifications to Slack channels.
Supports webhooks, formatted messages, and various notification types.
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

from ..logging_config import get_logger

logger = get_logger(__name__)


class SlackNotificationPriority(str, Enum):
    """Notification priority levels for Slack messages"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SlackNotificationType(str, Enum):
    """Types of Slack notifications"""
    TASK_ASSIGNED = "task_assigned"
    APPROVAL_NEEDED = "approval_needed"
    COMPLIANCE_VIOLATION = "compliance_violation"
    SLA_BREACH = "sla_breach"
    ASSET_UPDATED = "asset_updated"
    CHANGE_REQUEST = "change_request"
    GENERAL = "general"


class SlackNotifier:
    """
    Slack notification service for sending formatted messages to Slack channels.

    Supports:
    - Webhook-based notifications
    - Rich message formatting with blocks
    - Different notification types and priorities
    - Error handling and retries
    - Multiple channels
    """

    def __init__(self):
        """Initialize Slack notifier with configuration from environment"""
        self.enabled = os.getenv("SLACK_ENABLED", "false").lower() == "true"
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.default_channel = os.getenv("SLACK_DEFAULT_CHANNEL", "#governance-alerts")
        self.username = os.getenv("SLACK_BOT_USERNAME", "DaaS Governance Portal")
        self.icon_emoji = os.getenv("SLACK_BOT_ICON", ":shield:")

        # Validation
        if self.enabled and not self.webhook_url:
            logger.warning(
                "slack_config_incomplete",
                message="Slack integration is enabled but SLACK_WEBHOOK_URL is not set"
            )
            self.enabled = False

        # Priority color mapping
        self.priority_colors = {
            SlackNotificationPriority.LOW: "#36a64f",       # Green
            SlackNotificationPriority.MEDIUM: "#FFA500",    # Orange
            SlackNotificationPriority.HIGH: "#ff9900",      # Dark Orange
            SlackNotificationPriority.CRITICAL: "#ff0000",  # Red
        }

        # Notification type icons
        self.type_icons = {
            SlackNotificationType.TASK_ASSIGNED: ":clipboard:",
            SlackNotificationType.APPROVAL_NEEDED: ":raised_hand:",
            SlackNotificationType.COMPLIANCE_VIOLATION: ":warning:",
            SlackNotificationType.SLA_BREACH: ":rotating_light:",
            SlackNotificationType.ASSET_UPDATED: ":package:",
            SlackNotificationType.CHANGE_REQUEST: ":arrows_counterclockwise:",
            SlackNotificationType.GENERAL: ":information_source:",
        }

    def _get_color(self, priority: SlackNotificationPriority) -> str:
        """Get color code for priority level"""
        return self.priority_colors.get(priority, "#808080")  # Default to gray

    def _get_icon(self, notification_type: SlackNotificationType) -> str:
        """Get emoji icon for notification type"""
        return self.type_icons.get(notification_type, ":bell:")

    def send_notification(
        self,
        title: str,
        message: str,
        notification_type: SlackNotificationType = SlackNotificationType.GENERAL,
        priority: SlackNotificationPriority = SlackNotificationPriority.MEDIUM,
        channel: Optional[str] = None,
        fields: Optional[List[Dict[str, str]]] = None,
        link: Optional[str] = None,
        link_text: Optional[str] = "View Details"
    ) -> bool:
        """
        Send a notification to Slack

        Args:
            title: Notification title
            message: Main notification message
            notification_type: Type of notification
            priority: Priority level
            channel: Slack channel (override default)
            fields: Additional fields to display (list of {title, value, short})
            link: URL to relevant resource
            link_text: Text for the link button

        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("slack_disabled", message="Slack integration is disabled")
            return False

        try:
            # Build Slack message payload
            payload = self._build_payload(
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                channel=channel,
                fields=fields,
                link=link,
                link_text=link_text
            )

            # Send to Slack
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                logger.info(
                    "slack_notification_sent",
                    title=title,
                    type=notification_type.value,
                    priority=priority.value,
                    channel=channel or self.default_channel
                )
                return True
            else:
                logger.error(
                    "slack_notification_failed",
                    status_code=response.status_code,
                    response_text=response.text,
                    title=title
                )
                return False

        except Exception as e:
            logger.error(
                "slack_notification_error",
                error=str(e),
                title=title,
                type=notification_type.value
            )
            return False

    def _build_payload(
        self,
        title: str,
        message: str,
        notification_type: SlackNotificationType,
        priority: SlackNotificationPriority,
        channel: Optional[str],
        fields: Optional[List[Dict[str, str]]],
        link: Optional[str],
        link_text: str
    ) -> Dict[str, Any]:
        """Build Slack message payload with blocks and attachments"""

        icon = self._get_icon(notification_type)
        color = self._get_color(priority)

        # Main attachment
        attachment = {
            "color": color,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{icon} {title}",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                }
            ],
            "footer": f"DaaS Governance Portal | {priority.value.upper()} Priority",
            "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
            "ts": int(datetime.utcnow().timestamp())
        }

        # Add custom fields if provided
        if fields:
            field_blocks = []
            for field in fields:
                field_blocks.append({
                    "type": "mrkdwn",
                    "text": f"*{field.get('title', 'Field')}:*\n{field.get('value', 'N/A')}"
                })

            # Add fields in groups of 2 per section
            for i in range(0, len(field_blocks), 2):
                section_fields = field_blocks[i:i+2]
                attachment["blocks"].append({
                    "type": "section",
                    "fields": section_fields
                })

        # Add action button if link provided
        if link:
            attachment["blocks"].append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": link_text,
                            "emoji": True
                        },
                        "url": link,
                        "style": "primary" if priority in [SlackNotificationPriority.HIGH, SlackNotificationPriority.CRITICAL] else "default"
                    }
                ]
            })

        # Build final payload
        payload = {
            "channel": channel or self.default_channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "attachments": [attachment]
        }

        return payload

    # Convenience methods for common notification types

    def notify_task_assigned(
        self,
        task_title: str,
        assignee_name: str,
        assigned_by: str,
        due_date: Optional[str] = None,
        task_url: Optional[str] = None
    ) -> bool:
        """Send notification for task assignment"""
        fields = [
            {"title": "Assigned To", "value": assignee_name, "short": True},
            {"title": "Assigned By", "value": assigned_by, "short": True},
        ]

        if due_date:
            fields.append({"title": "Due Date", "value": due_date, "short": True})

        return self.send_notification(
            title="New Task Assigned",
            message=f"*{task_title}* has been assigned to {assignee_name}",
            notification_type=SlackNotificationType.TASK_ASSIGNED,
            priority=SlackNotificationPriority.MEDIUM,
            fields=fields,
            link=task_url,
            link_text="View Task"
        )

    def notify_approval_needed(
        self,
        request_title: str,
        requester: str,
        request_type: str,
        request_url: Optional[str] = None
    ) -> bool:
        """Send notification for approval requests"""
        fields = [
            {"title": "Requested By", "value": requester, "short": True},
            {"title": "Type", "value": request_type, "short": True},
        ]

        return self.send_notification(
            title="Approval Required",
            message=f"*{request_title}* is pending your approval",
            notification_type=SlackNotificationType.APPROVAL_NEEDED,
            priority=SlackNotificationPriority.HIGH,
            fields=fields,
            link=request_url,
            link_text="Review Request"
        )

    def notify_compliance_violation(
        self,
        violation_description: str,
        asset_name: str,
        severity: str,
        detected_at: str,
        violation_url: Optional[str] = None
    ) -> bool:
        """Send notification for compliance violations"""
        # Map severity to priority
        priority_map = {
            "Critical": SlackNotificationPriority.CRITICAL,
            "High": SlackNotificationPriority.HIGH,
            "Medium": SlackNotificationPriority.MEDIUM,
            "Low": SlackNotificationPriority.LOW,
        }
        priority = priority_map.get(severity, SlackNotificationPriority.MEDIUM)

        fields = [
            {"title": "Asset", "value": asset_name, "short": True},
            {"title": "Severity", "value": severity, "short": True},
            {"title": "Detected", "value": detected_at, "short": True},
        ]

        return self.send_notification(
            title="Compliance Violation Detected",
            message=f"*{violation_description}*",
            notification_type=SlackNotificationType.COMPLIANCE_VIOLATION,
            priority=priority,
            fields=fields,
            link=violation_url,
            link_text="View Violation"
        )

    def notify_sla_breach(
        self,
        sla_name: str,
        vendor_name: str,
        metric: str,
        threshold: str,
        actual: str,
        sla_url: Optional[str] = None
    ) -> bool:
        """Send notification for SLA breaches"""
        fields = [
            {"title": "Vendor", "value": vendor_name, "short": True},
            {"title": "Metric", "value": metric, "short": True},
            {"title": "Threshold", "value": threshold, "short": True},
            {"title": "Actual", "value": actual, "short": True},
        ]

        return self.send_notification(
            title="SLA Breach Detected",
            message=f"*{sla_name}* has been breached",
            notification_type=SlackNotificationType.SLA_BREACH,
            priority=SlackNotificationPriority.CRITICAL,
            fields=fields,
            link=sla_url,
            link_text="View SLA Details"
        )

    def notify_change_request(
        self,
        change_title: str,
        requested_by: str,
        environment: str,
        implementation_date: str,
        change_url: Optional[str] = None
    ) -> bool:
        """Send notification for change requests"""
        fields = [
            {"title": "Requested By", "value": requested_by, "short": True},
            {"title": "Environment", "value": environment, "short": True},
            {"title": "Implementation", "value": implementation_date, "short": True},
        ]

        return self.send_notification(
            title="New Change Request",
            message=f"*{change_title}*",
            notification_type=SlackNotificationType.CHANGE_REQUEST,
            priority=SlackNotificationPriority.HIGH,
            fields=fields,
            link=change_url,
            link_text="Review Change"
        )


# Singleton instance
_slack_notifier = None


def get_slack_notifier() -> SlackNotifier:
    """Get singleton instance of Slack notifier"""
    global _slack_notifier
    if _slack_notifier is None:
        _slack_notifier = SlackNotifier()
    return _slack_notifier
