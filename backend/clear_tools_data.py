"""
Clear all tools data from database before re-seeding
"""
from app.database import SessionLocal
from app import models, models_extended, models_advanced, models_integrations, models_collaboration

def clear_all_tools_data():
    """Delete all tool data from database"""

    db = SessionLocal()

    try:
        print("\n" + "="*70)
        print("  🗑️  CLEARING ALL TOOLS DATA")
        print("="*70 + "\n")

        # Delete in reverse order to respect foreign keys
        print("Deleting SLA Violations...")
        db.query(models_advanced.SLAViolation).delete()
        db.commit()

        print("Deleting Import Jobs...")
        db.query(models_integrations.ImportJob).delete()
        db.commit()

        print("Deleting Impact Analysis Runs...")
        db.query(models_advanced.ImpactAnalysisRun).delete()
        db.commit()

        print("Deleting Policy Validations...")
        db.query(models_advanced.PolicyValidation).delete()
        db.commit()

        print("Deleting Governance Policies...")
        db.query(models_advanced.GovernancePolicy).delete()
        db.commit()

        print("Deleting Activity Logs...")
        db.query(models_collaboration.ActivityLog).delete()
        db.commit()

        print("Deleting Comments...")
        db.query(models_collaboration.Comment).delete()
        db.commit()

        print("Deleting Notifications...")
        db.query(models_collaboration.Notification).delete()
        db.commit()

        print("Deleting Tasks...")
        db.query(models_collaboration.Task).delete()
        db.commit()

        print("Deleting Integration Logs...")
        db.query(models_integrations.IntegrationLog).delete()
        db.commit()

        print("Deleting API Keys...")
        db.query(models_integrations.APIKey).delete()
        db.commit()

        print("Deleting Webhook Deliveries...")
        db.query(models_integrations.WebhookDelivery).delete()
        db.commit()

        print("Deleting Webhooks...")
        db.query(models_integrations.Webhook).delete()
        db.commit()

        print("Deleting SLA Monitoring...")
        db.query(models_advanced.SLAMonitoring).delete()
        db.commit()

        print("Deleting Schema Registry...")
        db.query(models_advanced.SchemaRegistry).delete()
        db.commit()

        print("Deleting Data Lineage Edges...")
        db.query(models_advanced.DataLineageEdge).delete()
        db.commit()

        print("Deleting Data Lineage Nodes...")
        db.query(models_advanced.DataLineageNode).delete()
        db.commit()

        print("Deleting Quality Check Runs...")
        db.query(models_advanced.QualityCheckRun).delete()
        db.commit()

        print("Deleting Data Quality Rules...")
        db.query(models_advanced.DataQualityRule).delete()
        db.commit()

        print("\n" + "="*70)
        print("  ✅ ALL TOOLS DATA CLEARED SUCCESSFULLY!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error clearing tools data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    clear_all_tools_data()
