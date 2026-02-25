#!/bin/bash
# PostgreSQL Setup Script for Enterprise DaaS Governance Portal
# Run this script with: sudo bash setup_postgresql.sh

set -e

echo "=== PostgreSQL Setup for DaaS Governance Portal ==="

# Install PostgreSQL
echo "📦 Installing PostgreSQL..."
apt update
apt install -y postgresql postgresql-contrib

# Start PostgreSQL service
echo "🚀 Starting PostgreSQL service..."
systemctl start postgresql
systemctl enable postgresql

# Create database and user
echo "🗄️  Creating database and user..."
sudo -u postgres psql <<EOF
CREATE DATABASE governance_portal;
CREATE USER daas_admin WITH PASSWORD 'daas_secure_password_2026';
GRANT ALL PRIVILEGES ON DATABASE governance_portal TO daas_admin;
ALTER DATABASE governance_portal OWNER TO daas_admin;
\q
EOF

echo "✅ PostgreSQL setup complete!"
echo ""
echo "📝 Database Details:"
echo "   Database: governance_portal"
echo "   User: daas_admin"
echo "   Password: daas_secure_password_2026"
echo ""
echo "🔗 Connection String:"
echo "   postgresql://daas_admin:daas_secure_password_2026@localhost:5432/governance_portal"
echo ""
echo "⚠️  IMPORTANT: Change the password in production!"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with the connection string above"
echo "2. cd backend && source venv/bin/activate"
echo "3. alembic upgrade head"
echo "4. python seed_data.py"
