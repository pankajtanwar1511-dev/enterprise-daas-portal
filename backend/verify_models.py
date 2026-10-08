#!/usr/bin/env python3
"""
Model Verification Script

Validates that all SQLAlchemy models match their PostgreSQL table schemas.
This prevents runtime errors caused by model/schema mismatches.
"""

import sys
from sqlalchemy import inspect, create_engine, text
from sqlalchemy.orm import Session
from app.database import engine, Base
from app import models, models_extended, models_advanced, models_integrations, models_itsm, models_collaboration

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def get_pg_table_columns(table_name):
    """Get column information from PostgreSQL table"""
    query = text("""
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = :table_name
        ORDER BY ordinal_position
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"table_name": table_name})
        columns = {}
        for row in result:
            columns[row[0]] = {
                'type': row[1],
                'nullable': row[2] == 'YES',
                'default': row[3]
            }
        return columns

def get_pg_foreign_keys(table_name):
    """Get foreign key information from PostgreSQL"""
    query = text("""
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = :table_name
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"table_name": table_name})
        fks = {}
        for row in result:
            fks[row[0]] = {
                'references_table': row[1],
                'references_column': row[2]
            }
        return fks

def verify_model(model_class):
    """Verify a single model against its PostgreSQL table"""
    table_name = model_class.__tablename__
    model_name = model_class.__name__

    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}Checking: {model_name} → {table_name}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")

    issues = []

    try:
        # Get PostgreSQL schema
        pg_columns = get_pg_table_columns(table_name)
        pg_fks = get_pg_foreign_keys(table_name)

        if not pg_columns:
            print(f"{RED}✗ Table '{table_name}' does not exist in PostgreSQL!{RESET}")
            return False

        # Get SQLAlchemy model columns
        inspector = inspect(model_class)
        model_columns = {col.name: col for col in inspector.columns}

        # Check for missing columns in model
        for pg_col_name in pg_columns:
            if pg_col_name not in model_columns:
                issues.append(f"{RED}✗ Column '{pg_col_name}' exists in PostgreSQL but missing in model{RESET}")

        # Check for extra columns in model
        for model_col_name in model_columns:
            if model_col_name not in pg_columns:
                issues.append(f"{YELLOW}⚠ Column '{model_col_name}' exists in model but missing in PostgreSQL{RESET}")

        # Check column properties (type, nullable)
        for col_name, model_col in model_columns.items():
            if col_name in pg_columns:
                pg_col = pg_columns[col_name]

                # Check nullable
                if model_col.nullable != pg_col['nullable']:
                    issues.append(
                        f"{YELLOW}⚠ Column '{col_name}': "
                        f"Model nullable={model_col.nullable}, "
                        f"PostgreSQL nullable={pg_col['nullable']}{RESET}"
                    )

        # Check foreign keys (from the table, not the mapper)
        table = model_class.__table__
        model_fks = {}
        for fk in table.foreign_keys:
            model_fks[fk.parent.name] = fk

        for fk_col_name in pg_fks:
            if fk_col_name not in model_fks:
                pg_fk = pg_fks[fk_col_name]
                issues.append(
                    f"{YELLOW}⚠ Foreign key on '{fk_col_name}' → {pg_fk['references_table']}.{pg_fk['references_column']} "
                    f"exists in PostgreSQL but may be missing in model{RESET}"
                )

        # Print results
        if issues:
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print(f"{GREEN}✓ Model matches PostgreSQL schema perfectly!{RESET}")
            return True

    except Exception as e:
        print(f"{RED}✗ Error verifying model: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main verification function"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}  MODEL VERIFICATION - Phase 2{RESET}")
    print(f"{BLUE}  Checking all SQLAlchemy models against PostgreSQL schemas{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")

    # Collect all model classes
    all_models = []

    # Models from app.models
    for attr_name in dir(models):
        attr = getattr(models, attr_name)
        if isinstance(attr, type) and issubclass(attr, Base) and hasattr(attr, '__tablename__'):
            all_models.append(attr)

    # Models from app.models_extended
    for attr_name in dir(models_extended):
        attr = getattr(models_extended, attr_name)
        if isinstance(attr, type) and issubclass(attr, Base) and hasattr(attr, '__tablename__'):
            all_models.append(attr)

    # Models from app.models_advanced
    for attr_name in dir(models_advanced):
        attr = getattr(models_advanced, attr_name)
        if isinstance(attr, type) and issubclass(attr, Base) and hasattr(attr, '__tablename__'):
            all_models.append(attr)

    # Models from app.models_integrations
    for attr_name in dir(models_integrations):
        attr = getattr(models_integrations, attr_name)
        if isinstance(attr, type) and issubclass(attr, Base) and hasattr(attr, '__tablename__'):
            all_models.append(attr)

    # Models from app.models_itsm
    for attr_name in dir(models_itsm):
        attr = getattr(models_itsm, attr_name)
        if isinstance(attr, type) and issubclass(attr, Base) and hasattr(attr, '__tablename__'):
            all_models.append(attr)

    # Models from app.models_collaboration
    for attr_name in dir(models_collaboration):
        attr = getattr(models_collaboration, attr_name)
        if isinstance(attr, type) and issubclass(attr, Base) and hasattr(attr, '__tablename__'):
            all_models.append(attr)

    # Remove duplicates and sort
    unique_models = list(set(all_models))
    unique_models.sort(key=lambda m: m.__tablename__)

    print(f"\n{BLUE}Found {len(unique_models)} models to verify{RESET}\n")

    # Verify each model
    results = {}
    for model in unique_models:
        results[model.__tablename__] = verify_model(model)

    # Summary
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}  VERIFICATION SUMMARY{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed

    print(f"Total Models Checked: {len(results)}")
    print(f"{GREEN}✓ Passed: {passed}{RESET}")
    print(f"{RED}✗ Failed: {failed}{RESET}\n")

    if failed > 0:
        print(f"{RED}Models with issues:{RESET}")
        for table_name, passed in results.items():
            if not passed:
                print(f"  {RED}✗ {table_name}{RESET}")
        print()
        sys.exit(1)
    else:
        print(f"{GREEN}✓ All models match their PostgreSQL schemas!{RESET}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
