# GitHub Actions CI/CD Workflows

Automated testing, validation, and deployment pipelines for the Enterprise DaaS Governance Portal.

## Workflows Overview

### 1. **ci.yml** - Continuous Integration
**Triggers:** Push to `main`/`develop`, Pull requests
**Purpose:** Comprehensive testing and quality checks

**Jobs:**
- ✅ **Backend Tests & Coverage** (Unit + Integration tests with PostgreSQL)
- ✅ **Backend Linting** (Black, isort, flake8)
- ✅ **Frontend Build & Tests** (npm build, jest tests)
- ✅ **Frontend Linting** (ESLint)
- ✅ **Docker Build Verification** (Test backend/frontend image builds)
- ✅ **Security Scan** (Safety check for Python, npm audit for Node)
- ✅ **Overall Status Check** (Aggregate all job results)

**Running Time:** ~10-15 minutes

**Coverage Upload:** Automatically uploads to Codecov (if configured)

---

### 2. **pr-checks.yml** - Pull Request Validation
**Triggers:** Pull request open, synchronize, reopen
**Purpose:** Validate PR quality and provide feedback

**Jobs:**
- ✅ **PR Validation** (Conventional commits format, description check)
- ✅ **Changed Files Analysis** (Detect backend/frontend/docs changes)
- ✅ **Conditional Backend Checks** (Only runs if backend changed)
- ✅ **Conditional Frontend Checks** (Only runs if frontend changed)
- ✅ **Coverage Report** (Comment coverage % on PR)
- ✅ **PR Size Check** (Warn if PR is too large)

**Features:**
- Automatic PR comments with test results
- Coverage reporting directly in PR
- Smart execution (only runs relevant jobs)

---

### 3. **deploy.yml** - Deployment Pipeline
**Triggers:**
- Push to `main` → Production deployment
- Push to `develop` → Staging deployment
- Manual workflow dispatch → Choose environment

**Purpose:** Build Docker images and deploy to environments

**Jobs:**
- 🏗️ **Build & Push** (Docker images to GHCR)
- 🚀 **Deploy to Staging** (develop branch)
- 🚀 **Deploy to Production** (main branch, requires approval)
- 🧪 **Smoke Tests** (Post-deployment validation)
- ⏮️ **Rollback** (On failure)
- 📊 **Deployment Summary** (Aggregate status)

**Deployment Targets (examples provided):**
- AWS ECS/Fargate
- Kubernetes (kubectl)
- Docker Compose on VM (SSH)

---

## Setup Instructions

### 1. Repository Secrets

Configure these secrets in GitHub repository settings:

#### For CI (Optional)
```
CODECOV_TOKEN          # For coverage uploads (optional)
```

#### For Deployment (Required for deploy.yml)
```
# AWS Deployment
AWS_ACCESS_KEY_ID      # AWS credentials
AWS_SECRET_ACCESS_KEY  # AWS credentials

# SSH Deployment
STAGING_HOST           # Staging server hostname
STAGING_USER           # SSH username
STAGING_SSH_KEY        # SSH private key
PRODUCTION_HOST        # Production server hostname
PRODUCTION_USER        # SSH username
PRODUCTION_SSH_KEY     # SSH private key

# Docker Registry (uses GITHUB_TOKEN by default)
```

### 2. Environment Configuration

Create environments in repository settings:

1. **staging**
   - No protection rules (auto-deploy)
   - Deployment URL: https://staging.daas-portal.example.com

2. **production**
   - ✅ Required reviewers (1-2 approvers)
   - ✅ Wait timer (optional, e.g., 5 minutes)
   - Deployment URL: https://daas-portal.example.com

### 3. Branch Protection Rules

Configure branch protection for `main`:
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging
  - backend-tests
  - frontend-build
  - docker-build
- ✅ Require branches to be up to date before merging
- ✅ Require linear history (optional)

---

## Workflow Badges

Add these badges to your README.md:

```markdown
![CI Status](https://github.com/USERNAME/enterprise-daas-portal/actions/workflows/ci.yml/badge.svg)
![Deploy Status](https://github.com/USERNAME/enterprise-daas-portal/actions/workflows/deploy.yml/badge.svg)
```

---

## How Workflows Work Together

### Development Flow

```
Developer pushes to feature branch
         ↓
    PR opened to main
         ↓
┌────────────────────────┐
│   pr-checks.yml runs   │
│  - Validates PR format │
│  - Runs quick tests    │
│  - Comments results    │
└────────────────────────┘
         ↓
    PR approved & merged to main
         ↓
┌────────────────────────┐
│     ci.yml runs        │
│  - Full test suite    │
│  - Linting            │
│  - Security scans     │
└────────────────────────┘
         ↓
    All checks pass ✅
         ↓
┌────────────────────────┐
│   deploy.yml runs      │
│  - Builds Docker imgs  │
│  - Deploys to prod    │
│  - Runs smoke tests   │
└────────────────────────┘
```

### Staging vs Production

**Staging (develop branch):**
- Automatic deployment after CI passes
- No manual approval required
- Latest features testing

**Production (main branch):**
- Requires manual approval (environment protection)
- Database migrations run automatically
- Blue-green deployment ready
- Comprehensive health checks

---

## Monitoring and Debugging

### View Workflow Runs

1. Go to **Actions** tab in GitHub repository
2. Select workflow (CI/PR Checks/Deploy)
3. Click on specific run to see job details

### Download Artifacts

Workflows generate these artifacts:
- **backend-coverage-report** (HTML coverage report)
- **frontend-build** (Built frontend dist/)

Download from workflow run page → Artifacts section

### Re-run Failed Jobs

If a job fails temporarily (network issue, etc.):
1. Go to failed workflow run
2. Click "Re-run jobs" → "Re-run failed jobs"

### Manual Deployment

Trigger deployment manually:
1. Go to **Actions** tab
2. Select "Deploy to Environments" workflow
3. Click "Run workflow"
4. Choose branch and environment
5. Click "Run workflow"

---

## Customization Guide

### Adding New Test Job

```yaml
# In ci.yml
new-test-job:
  name: My New Test
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Run my test
      run: |
        echo "Running custom test"
        # Your test commands
```

### Adding Deployment Target

Edit `deploy.yml` and uncomment/modify relevant section:

**For AWS ECS:**
```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v2
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1

- name: Deploy to ECS
  run: |
    aws ecs update-service \
      --cluster production-cluster \
      --service daas-portal-backend \
      --force-new-deployment
```

**For Kubernetes:**
```yaml
- name: Deploy to Kubernetes
  run: |
    kubectl set image deployment/backend \
      backend=${{ needs.build-and-push.outputs.backend_tag }} \
      -n production
```

### Notification Integration

Add to deployment summary job:

**Slack:**
```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Deployment to production completed! ✅"
      }
```

**Email:**
```yaml
- name: Send email
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: Production Deployment Complete
    body: Deployment finished at ${{ github.sha }}
```

---

## Performance Optimization

### Caching

All workflows use caching:
- **Python dependencies**: `pip` cache
- **Node dependencies**: `npm` cache
- **Docker layers**: GitHub Actions cache

### Conditional Execution

PR checks only run relevant jobs:
```yaml
if: needs.changed-files.outputs.backend_changed == 'true'
```

### Parallel Execution

Jobs run in parallel where possible:
- Backend tests, frontend tests, linting all run concurrently
- Reduces total CI time

---

## Troubleshooting

### Common Issues

**1. Tests fail in CI but pass locally**
- Check environment variables (DATABASE_URL, SECRET_KEY)
- Ensure test database is properly set up
- Check Python/Node version matches

**2. Docker build fails**
- Verify Dockerfile syntax
- Check if all files are in build context
- Review .dockerignore to ensure needed files aren't excluded

**3. Deployment fails**
- Check secrets are configured correctly
- Verify SSH keys/AWS credentials
- Check deployment target is accessible

**4. Coverage upload fails**
- Verify CODECOV_TOKEN is set (if using Codecov)
- Check coverage report is generated correctly
- Review Codecov configuration

### Debug Mode

Enable debug logging:
1. Go to repository settings → Secrets
2. Add secret: `ACTIONS_STEP_DEBUG` = `true`
3. Re-run workflow

---

## Best Practices

1. **Always review PR checks** before merging
2. **Monitor deployment status** in real-time
3. **Keep secrets up to date** (rotate credentials regularly)
4. **Review failed jobs quickly** (don't let them pile up)
5. **Use manual approval for production** (safety net)
6. **Document custom changes** in this README

---

## Metrics and Goals

### Target Metrics
- ✅ CI completion time: <15 minutes
- ✅ Test coverage: >80%
- ✅ Deployment time: <10 minutes
- ✅ Deployment success rate: >95%

### Current Status
Run workflows to see current metrics in action!

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Secrets Management](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

**Last Updated:** February 25, 2026
**Version:** v1.0
**Status:** Production Ready
