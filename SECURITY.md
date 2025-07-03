# Security Guide - ImmoAssist Multi-Agent System

This document outlines security best practices and configurations for deploying ImmoAssist in production environments.

## Table of Contents

1. [Authentication](#authentication)
2. [VPC Service Controls](#vpc-service-controls)
3. [Network Security](#network-security)
4. [IAM Configuration](#iam-configuration)
5. [Data Protection](#data-protection)
6. [Monitoring and Auditing](#monitoring-and-auditing)

---

## Authentication

### Application Default Credentials (ADC)

**✅ Recommended Approach:**

```bash
# Set up ADC for production
gcloud auth application-default login

# Verify authentication
gcloud auth application-default print-access-token
```

**✅ Best Practices:**

- Use ADC instead of service account keys
- Let Vertex AI auto-detect project configuration
- Avoid setting `GOOGLE_CLOUD_PROJECT` environment variable unless necessary

**❌ Avoid:**

```bash
# Don't export these unless absolutely necessary
export GOOGLE_CLOUD_PROJECT=your-project
export GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json
```

### Service Account Configuration

For production deployments:

```bash
# Create dedicated service account
gcloud iam service-accounts create immoassist-agent \
  --display-name="ImmoAssist Agent Service Account"

# Assign minimal required roles
gcloud projects add-iam-policy-binding YOUR_PROJECT \
  --member="serviceAccount:immoassist-agent@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding YOUR_PROJECT \
  --member="serviceAccount:immoassist-agent@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

---

## VPC Service Controls

### Overview

VPC Service Controls provide an additional layer of security by creating a security perimeter around Google Cloud resources.

### Configuration

1. **Create Security Perimeter:**

```bash
# Create access policy
gcloud access-context-manager policies create \
  --title="ImmoAssist Security Policy" \
  --scopes=projects/YOUR_PROJECT

# Create service perimeter
gcloud access-context-manager perimeters create \
  immoassist-perimeter \
  --title="ImmoAssist Perimeter" \
  --resources=projects/YOUR_PROJECT \
  --restricted-services=aiplatform.googleapis.com,storage.googleapis.com
```

2. **Configure Allowed Networks:**

```yaml
# vpc-sc-config.yaml
resources:
  - projects/YOUR_PROJECT
restrictedServices:
  - aiplatform.googleapis.com
  - storage.googleapis.com
  - firestore.googleapis.com
accessLevels:
  - name: "corporate_network"
    conditions:
      - ipSubnetworks:
          - "10.0.0.0/8" # Your corporate network
```

### Implementation in Code

The system automatically works with VPC-SC when properly configured:

```python
# No code changes required - ADC automatically respects VPC-SC
try:
    _, project_id = google.auth.default()
    logging.info(f"Google Cloud project detected via ADC: {project_id}")
except Exception as e:
    logging.error(f"Authentication failed - check VPC-SC configuration: {e}")
```

---

## Network Security

### Private Google Access

For enhanced security, configure private connectivity:

```bash
# Enable Private Google Access
gcloud compute networks subnets update SUBNET_NAME \
  --region=REGION \
  --enable-private-ip-google-access
```

### Firewall Rules

```bash
# Restrict outbound traffic to Google APIs only
gcloud compute firewall-rules create allow-google-apis \
  --direction=EGRESS \
  --priority=1000 \
  --network=VPC_NAME \
  --action=ALLOW \
  --rules=tcp:443 \
  --destination-ranges=199.36.153.8/30
```

### Private Service Connect

For maximum security, use Private Service Connect:

```bash
# Create private service connect endpoint
gcloud compute addresses create immoassist-psc-endpoint \
  --global \
  --purpose=PRIVATE_SERVICE_CONNECT

gcloud compute forwarding-rules create immoassist-psc \
  --global \
  --network=VPC_NAME \
  --address=immoassist-psc-endpoint \
  --target-service-attachment=projects/google-cloud-services/global/serviceAttachments/aiplatform
```

---

## IAM Configuration

### Principle of Least Privilege

**Required Roles for ImmoAssist:**

```bash
# Minimum required permissions
roles/aiplatform.user           # Vertex AI access
roles/storage.objectViewer      # Knowledge base access
roles/logging.logWriter         # Application logging

# Optional for enhanced features
roles/aiplatform.admin          # RAG corpus management
roles/storage.admin             # Vector store management
```

### Custom Role Definition

```yaml
# custom-immoassist-role.yaml
title: "ImmoAssist Agent Role"
description: "Custom role for ImmoAssist multi-agent system"
stage: "GA"
includedPermissions:
  - aiplatform.endpoints.predict
  - aiplatform.models.predict
  - storage.objects.get
  - storage.objects.list
  - logging.logEntries.create
```

Apply custom role:

```bash
gcloud iam roles create immoAssistRole \
  --project=YOUR_PROJECT \
  --file=custom-immoassist-role.yaml
```

---

## Data Protection

### Encryption

**Data at Rest:**

- All Google Cloud services use encryption by default
- Consider Customer-Managed Encryption Keys (CMEK) for sensitive data

**Data in Transit:**

- TLS 1.3 for all API communications
- Private Google Access for internal traffic

### Data Classification

**Sensitive Data Handling:**

```python
# Example: Sanitize user input in session data
def sanitize_user_data(user_input: str) -> str:
    """Remove or mask sensitive information from user input."""
    # Remove potential PII, financial data, etc.
    sanitized = re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b', '[CARD_MASKED]', user_input)
    return sanitized
```

### Session Security

```python
# Session data encryption (if storing sensitive info)
import cryptography.fernet

def encrypt_session_data(data: dict, key: bytes) -> str:
    """Encrypt sensitive session data."""
    f = Fernet(key)
    return f.encrypt(json.dumps(data).encode()).decode()
```

---

## Monitoring and Auditing

### Cloud Audit Logs

Enable comprehensive audit logging:

```bash
# Enable audit logs for all services
gcloud logging sinks create immoassist-audit-sink \
  bigquery.googleapis.com/projects/YOUR_PROJECT/datasets/audit_logs \
  --log-filter='protoPayload.serviceName="aiplatform.googleapis.com" OR protoPayload.serviceName="storage.googleapis.com"'
```

### Security Monitoring

**Key Metrics to Monitor:**

- Authentication failures
- Unusual API call patterns
- Data access patterns
- Network traffic anomalies

**Alerting Configuration:**

```yaml
# monitoring-alerts.yaml
alertPolicy:
  displayName: "ImmoAssist Security Alerts"
  conditions:
    - displayName: "High Error Rate"
      conditionThreshold:
        filter: 'resource.type="cloud_run_revision" AND severity>=ERROR'
        comparison: COMPARISON_GREATER_THAN
        thresholdValue: 10
  notificationChannels:
    - "projects/YOUR_PROJECT/notificationChannels/CHANNEL_ID"
```

### Access Review

Regular security reviews:

```bash
# Review service account permissions
gcloud projects get-iam-policy YOUR_PROJECT \
  --flatten="bindings[].members" \
  --filter="bindings.members:immoassist-agent@"

# Review recent authentication events
gcloud logging read 'protoPayload.authenticationInfo.principalEmail="immoassist-agent@YOUR_PROJECT.iam.gserviceaccount.com"' \
  --limit=50 \
  --format="table(timestamp,protoPayload.methodName,protoPayload.authenticationInfo.principalEmail)"
```

---

## Production Deployment Checklist

### Pre-Deployment Security Review

- [ ] VPC Service Controls configured
- [ ] Service account with minimal permissions
- [ ] Private Google Access enabled
- [ ] Audit logging configured
- [ ] Security monitoring alerts set up
- [ ] Network firewall rules reviewed
- [ ] Data encryption verified
- [ ] Access controls tested

### Runtime Security

- [ ] Regular security scans (Bandit, Safety)
- [ ] Dependency vulnerability monitoring
- [ ] Access pattern monitoring
- [ ] Incident response procedures
- [ ] Regular permission audits
- [ ] Security training for team

---

## Incident Response

### Security Event Response

1. **Immediate Actions:**

   - Isolate affected resources
   - Review audit logs
   - Assess impact scope
   - Document incident

2. **Investigation:**

   - Analyze authentication logs
   - Check for data access
   - Verify system integrity
   - Identify root cause

3. **Recovery:**
   - Remediate vulnerabilities
   - Update security configurations
   - Restore normal operations
   - Conduct post-incident review

### Emergency Contacts

- **Security Team**: security@immoassist.de
- **Operations**: ops@immoassist.de
- **Management**: emergency@immoassist.de

---

## Compliance

### Data Privacy (GDPR)

- User consent for data processing
- Data minimization principles
- Right to erasure implementation
- Data retention policies

### Industry Standards

- ISO 27001 alignment
- SOC 2 Type II compliance
- Cloud Security Alliance (CSA) guidelines
- German BSI Cloud Computing guidelines

---

For questions or security concerns, contact: security@immoassist.de
