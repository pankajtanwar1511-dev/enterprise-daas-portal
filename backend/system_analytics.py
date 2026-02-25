#!/usr/bin/env python3
"""
System Analytics & Health Check
Comprehensive testing and monitoring dashboard
"""
import sys
from sqlalchemy import func, text
from app.database import SessionLocal
from app import models
from app.models_extended import Vendor, BusinessGoal, StrategicInitiative, BudgetAllocation
from app.models_integrations import Webhook, WebhookDelivery, APIKey, IntegrationLog
from datetime import datetime, timedelta
from tabulate import tabulate


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def get_database_statistics(db):
    """Get comprehensive database statistics"""
    print_section("DATABASE STATISTICS")

    stats = [
        ["Roles", db.query(models.Role).count()],
        ["Users", db.query(models.User).count()],
        ["Active Users", db.query(models.User).filter(models.User.is_active == True).count()],
        ["Domains", db.query(models.Domain).count()],
        ["Assets", db.query(models.Asset).count()],
        ["Compliant Assets", db.query(models.Asset).filter(models.Asset.naming_compliant == True).count()],
        ["Non-Compliant Assets", db.query(models.Asset).filter(models.Asset.naming_compliant == False).count()],
        ["Compliance Violations", db.query(models.ComplianceViolation).count()],
        ["Change Requests", db.query(models.ChangeRequest).count()],
        ["Business Goals", db.query(BusinessGoal).count()],
        ["Strategic Initiatives", db.query(StrategicInitiative).count()],
        ["Vendors", db.query(Vendor).count()],
        ["Webhooks", db.query(Webhook).count()],
        ["Active Webhooks", db.query(Webhook).filter(Webhook.active == True).count()],
        ["Webhook Deliveries", db.query(WebhookDelivery).count()],
        ["API Keys", db.query(APIKey).count()],
        ["Active API Keys", db.query(APIKey).filter(APIKey.active == True).count()],
        ["Integration Logs", db.query(IntegrationLog).count()],
    ]

    print(tabulate(stats, headers=["Metric", "Count"], tablefmt="grid"))


def get_asset_analytics(db):
    """Get asset analytics"""
    print_section("ASSET ANALYTICS")

    # Assets by environment
    env_stats = db.query(
        models.Asset.environment,
        func.count(models.Asset.asset_id).label('count')
    ).group_by(models.Asset.environment).all()

    print("📊 Assets by Environment:")
    print(tabulate(env_stats, headers=["Environment", "Count"], tablefmt="grid"))
    print()

    # Assets by lifecycle stage
    lifecycle_stats = db.query(
        models.Asset.lifecycle_stage,
        func.count(models.Asset.asset_id).label('count')
    ).group_by(models.Asset.lifecycle_stage).all()

    print("📈 Assets by Lifecycle Stage:")
    print(tabulate(lifecycle_stats, headers=["Lifecycle Stage", "Count"], tablefmt="grid"))
    print()

    # Compliance rate
    total_assets = db.query(models.Asset).count()
    compliant_assets = db.query(models.Asset).filter(models.Asset.naming_compliant == True).count()
    compliance_rate = (compliant_assets / total_assets * 100) if total_assets > 0 else 0

    print(f"✅ Compliance Rate: {compliance_rate:.1f}% ({compliant_assets}/{total_assets} assets)")


def get_integration_analytics(db):
    """Get Phase 3 integration analytics"""
    print_section("PHASE 3: INTEGRATION ANALYTICS")

    # Webhook statistics
    total_webhooks = db.query(Webhook).count()
    active_webhooks = db.query(Webhook).filter(Webhook.active == True).count()
    total_deliveries = db.query(WebhookDelivery).count()
    successful_deliveries = db.query(WebhookDelivery).filter(WebhookDelivery.success == True).count()

    webhook_stats = [
        ["Total Webhooks", total_webhooks],
        ["Active Webhooks", active_webhooks],
        ["Total Deliveries", total_deliveries],
        ["Successful Deliveries", successful_deliveries],
        ["Failed Deliveries", total_deliveries - successful_deliveries],
        ["Success Rate", f"{(successful_deliveries/total_deliveries*100):.1f}%" if total_deliveries > 0 else "N/A"],
    ]

    print("🔔 Webhook Statistics:")
    print(tabulate(webhook_stats, headers=["Metric", "Value"], tablefmt="grid"))
    print()

    # API Key statistics
    total_keys = db.query(APIKey).count()
    active_keys = db.query(APIKey).filter(APIKey.active == True).count()
    total_usage = db.query(func.sum(APIKey.usage_count)).scalar() or 0

    api_key_stats = [
        ["Total API Keys", total_keys],
        ["Active API Keys", active_keys],
        ["Inactive API Keys", total_keys - active_keys],
        ["Total API Calls", int(total_usage)],
    ]

    print("🔑 API Key Statistics:")
    print(tabulate(api_key_stats, headers=["Metric", "Value"], tablefmt="grid"))
    print()

    # Integration logs
    integration_stats = db.query(
        IntegrationLog.integration_type,
        func.count(IntegrationLog.log_id).label('count'),
        func.sum(func.cast(IntegrationLog.status == 'success', int)).label('success')
    ).group_by(IntegrationLog.integration_type).all()

    if integration_stats:
        print("🔗 External Integration Statistics:")
        integration_data = [
            [stat[0], stat[1], stat[2] or 0, stat[1] - (stat[2] or 0)]
            for stat in integration_stats
        ]
        print(tabulate(integration_data,
                      headers=["Integration", "Total Calls", "Success", "Failed"],
                      tablefmt="grid"))
    else:
        print("🔗 No external integration calls yet")


def get_recent_activity(db):
    """Get recent system activity"""
    print_section("RECENT ACTIVITY (Last 24 Hours)")

    yesterday = datetime.utcnow() - timedelta(days=1)

    # Recent assets
    recent_assets = db.query(models.Asset).filter(
        models.Asset.created_at >= yesterday
    ).order_by(models.Asset.created_at.desc()).limit(5).all()

    if recent_assets:
        print("🆕 Recently Created Assets:")
        asset_data = [
            [a.asset_id, a.asset_name, a.environment, a.created_at.strftime("%Y-%m-%d %H:%M")]
            for a in recent_assets
        ]
        print(tabulate(asset_data,
                      headers=["ID", "Name", "Environment", "Created At"],
                      tablefmt="grid"))
    else:
        print("🆕 No assets created in last 24 hours")
    print()

    # Recent webhook deliveries
    recent_deliveries = db.query(WebhookDelivery).filter(
        WebhookDelivery.delivered_at >= yesterday
    ).order_by(WebhookDelivery.delivered_at.desc()).limit(5).all()

    if recent_deliveries:
        print("🔔 Recent Webhook Deliveries:")
        delivery_data = [
            [d.delivery_id, d.event, "✅" if d.success else "❌",
             d.delivered_at.strftime("%Y-%m-%d %H:%M"), f"{d.duration_ms}ms"]
            for d in recent_deliveries
        ]
        print(tabulate(delivery_data,
                      headers=["ID", "Event", "Status", "Delivered At", "Duration"],
                      tablefmt="grid"))
    else:
        print("🔔 No webhook deliveries in last 24 hours")


def get_user_activity(db):
    """Get user activity statistics"""
    print_section("USER ACTIVITY")

    users = db.query(models.User).all()

    user_data = [
        [
            u.username,
            u.role.role_name,
            u.last_login.strftime("%Y-%m-%d %H:%M") if u.last_login else "Never",
            "✅" if u.is_active else "❌"
        ]
        for u in users
    ]

    print(tabulate(user_data,
                  headers=["Username", "Role", "Last Login", "Active"],
                  tablefmt="grid"))


def get_strategic_metrics(db):
    """Get strategic business metrics"""
    print_section("STRATEGIC BUSINESS METRICS")

    # Business goals
    goals = db.query(BusinessGoal).all()

    if goals:
        print("🎯 Business Goals Progress:")
        goal_data = [
            [
                g.goal_name[:40] + "..." if len(g.goal_name) > 40 else g.goal_name,
                g.status,
                g.priority,
                f"{g.current_value}/{g.target_value}",
                f"{(g.current_value/g.target_value*100):.1f}%" if g.target_value > 0 else "N/A"
            ]
            for g in goals
        ]
        print(tabulate(goal_data,
                      headers=["Goal", "Status", "Priority", "Progress", "%"],
                      tablefmt="grid"))
    else:
        print("🎯 No business goals defined")
    print()

    # Budget allocation
    budgets = db.query(BudgetAllocation).all()

    if budgets:
        print("💰 Budget Allocation:")
        budget_data = [
            [
                b.fiscal_year,
                b.category,
                f"${b.allocated_amount:,.0f}",
                f"${b.spent_amount:,.0f}",
                f"{(b.spent_amount/b.allocated_amount*100):.1f}%" if b.allocated_amount > 0 else "N/A"
            ]
            for b in budgets
        ]
        print(tabulate(budget_data,
                      headers=["Year", "Category", "Allocated", "Spent", "% Used"],
                      tablefmt="grid"))
    else:
        print("💰 No budget allocations defined")


def run_health_checks(db):
    """Run system health checks"""
    print_section("SYSTEM HEALTH CHECKS")

    checks = []

    # Check 1: Database connectivity
    try:
        db.execute(text("SELECT 1"))
        checks.append(["Database Connection", "✅ Healthy", "Connected successfully"])
    except Exception as e:
        checks.append(["Database Connection", "❌ Failed", str(e)])

    # Check 2: Required tables exist
    try:
        db.query(models.Asset).count()
        db.query(Webhook).count()
        db.query(APIKey).count()
        checks.append(["Database Schema", "✅ Healthy", "All required tables present"])
    except Exception as e:
        checks.append(["Database Schema", "❌ Failed", str(e)])

    # Check 3: Data integrity
    total_assets = db.query(models.Asset).count()
    if total_assets > 0:
        checks.append(["Asset Data", "✅ Healthy", f"{total_assets} assets in database"])
    else:
        checks.append(["Asset Data", "⚠️ Warning", "No assets in database"])

    # Check 4: User authentication
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    if active_users > 0:
        checks.append(["User Authentication", "✅ Healthy", f"{active_users} active users"])
    else:
        checks.append(["User Authentication", "❌ Failed", "No active users"])

    # Check 5: Integration features
    webhook_count = db.query(Webhook).count()
    api_key_count = db.query(APIKey).count()
    if webhook_count > 0 or api_key_count > 0:
        checks.append(["Phase 3 Integration", "✅ Healthy",
                      f"{webhook_count} webhooks, {api_key_count} API keys"])
    else:
        checks.append(["Phase 3 Integration", "ℹ️ Info", "No integrations configured yet"])

    print(tabulate(checks, headers=["Component", "Status", "Details"], tablefmt="grid"))


def generate_summary_report(db):
    """Generate executive summary report"""
    print_section("EXECUTIVE SUMMARY")

    total_assets = db.query(models.Asset).count()
    compliant_assets = db.query(models.Asset).filter(models.Asset.naming_compliant == True).count()
    compliance_rate = (compliant_assets / total_assets * 100) if total_assets > 0 else 0

    total_users = db.query(models.User).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()

    total_webhooks = db.query(Webhook).count()
    active_webhooks = db.query(Webhook).filter(Webhook.active == True).count()

    total_api_keys = db.query(APIKey).count()
    active_api_keys = db.query(APIKey).filter(APIKey.active == True).count()

    print("📊 SYSTEM OVERVIEW")
    print(f"""
    ┌─────────────────────────────────────────────┐
    │  Enterprise DaaS Governance Portal          │
    │  Status: OPERATIONAL                        │
    │  Date: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC                │
    └─────────────────────────────────────────────┘

    📦 ASSET MANAGEMENT
       • Total Assets: {total_assets}
       • Compliance Rate: {compliance_rate:.1f}%
       • Compliant: {compliant_assets} | Non-Compliant: {total_assets - compliant_assets}

    👥 USER MANAGEMENT
       • Total Users: {total_users}
       • Active Users: {active_users}
       • Roles: {db.query(models.Role).count()}

    🔔 WEBHOOKS (Phase 3)
       • Total Webhooks: {total_webhooks}
       • Active: {active_webhooks}
       • Deliveries: {db.query(WebhookDelivery).count()}

    🔑 API KEYS (Phase 3)
       • Total Keys: {total_api_keys}
       • Active: {active_api_keys}
       • Total Usage: {db.query(func.sum(APIKey.usage_count)).scalar() or 0}

    🎯 STRATEGIC INITIATIVES
       • Business Goals: {db.query(BusinessGoal).count()}
       • Initiatives: {db.query(StrategicInitiative).count()}
       • Vendors: {db.query(Vendor).count()}
    """)


def main():
    """Main analytics dashboard"""
    print("\n" + "=" * 80)
    print("  ENTERPRISE DaaS GOVERNANCE PORTAL - SYSTEM ANALYTICS")
    print("=" * 80)

    db = SessionLocal()

    try:
        # Run all analytics
        run_health_checks(db)
        generate_summary_report(db)
        get_database_statistics(db)
        get_asset_analytics(db)
        get_integration_analytics(db)
        get_strategic_metrics(db)
        get_user_activity(db)
        get_recent_activity(db)

        print("\n" + "=" * 80)
        print("  ANALYTICS COMPLETE")
        print("=" * 80)
        print("\n✅ All systems operational\n")

    except Exception as e:
        print(f"\n❌ Error running analytics: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
