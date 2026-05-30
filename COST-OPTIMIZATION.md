# Cost Optimization & Management

**MecanjeoOps — AWS Platform Engineering**  
**Mecandjeo Technology — Platform Engineering — 2026**

---

## Overview

This project is designed to minimize AWS costs by separating free-tier infrastructure (shared resources) from billable application workloads (ECS Fargate). This document covers cost management strategies, resource tagging, cleanup procedures, and estimated costs.

---

## Cost Breakdown

### Free-Tier Resources (Always Running — $0/month)

These resources live in `resources/shared/dev/` and cost nothing. Safe to leave deployed permanently.

| Resource | Type | Cost | Notes |
|----------|------|------|-------|
| VPC | Networking | Free | 1 VPC, unlimited within limits |
| Subnets | Networking | Free | Public + Private subnets |
| Internet Gateway | Networking | Free | Inbound traffic to IGW is free |
| Route Tables | Networking | Free | Unlimited route tables |
| Network ACLs | Networking | Free | Stateless firewall rules |
| Security Groups | Networking | Free | Stateful firewall rules |
| IAM Roles | Identity | Free | Task execution + task roles |
| IAM Policies | Identity | Free | Least-privilege policies |
| EC2 Key Pair | Compute | Free | SSH key storage |
| EC2 Instance (t3.micro) | Compute | ~$0/month* | Free tier eligible (12 months new accounts) |

*If outside free tier: ~$7.37/month for t3.micro in us-east-1

---

### Billable Application Resources (Per App — ~$15-25/month each)

These are deployed separately for each application and incur charges.

| Resource | Type | Quantity | Est. Cost/Month | Notes |
|----------|------|----------|-----------------|-------|
| Application Load Balancer | Load Balancing | 1/app | $16.20 | $0.0225/hour + LCU charges |
| ECS Fargate Task | Compute | 1-2/app | $5.50-11.00 | 0.25 vCPU + 512 MB memory, on-demand |
| Elastic Container Registry | Container Registry | 1/app | <$0.50 | Storage for container images |
| CloudWatch Logs | Monitoring | ~100 MB/app | <$1.00 | Log ingestion (first 5GB free) |
| Data Transfer | Networking | ~1-5 GB/month | $0.09-0.45 | Outbound data transfer (first 1 GB free) |
| **Total per App** | | | **~$20-30/month** | |

**With 3 apps (Dashboard, Portfolio, School):** ~$60-90/month + shared infrastructure

---

## Resource Tagging Strategy

All Terraform resources should be tagged for cost allocation and resource management.

### Required Tags

Add these tags to all resources via Terraform:

```hcl
locals {
  common_tags = {
    Project     = "mecandjeo-infra"
    Environment = "dev"              # dev, prod
    Application = "dashboard"        # shared, dashboard, portfolio, school
    Owner       = "michael-emmanuel"
    CostCenter  = "platform-eng"
    ManagedBy   = "terraform"
    CreatedDate = "2026-05-30"
    Retention   = "permanent"        # permanent, temporary, ephemeral
  }
}
```

### Applying Tags in Modules

```hcl
resource "aws_alb" "app" {
  name = var.app_name
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.app_name}-alb"
      Resource = "load-balancer"
    }
  )
}
```

### Using Tags for Cost Allocation

1. **AWS Console → Billing → Cost Explorer:**
   - Filter by `Application` tag to see per-app costs
   - Filter by `Environment` tag to compare dev vs. prod
   - Filter by `CostCenter` tag for department billing

2. **CLI command to estimate by application:**
   ```bash
   aws ce get-cost-and-usage \
     --time-period Start=2026-05-01,End=2026-05-31 \
     --granularity MONTHLY \
     --metrics BlendedCost \
     --group-by Type=TAG,Key=Application
   ```

---

## Cleanup Procedures

### Safe Destruction Order

**IMPORTANT:** Always destroy in this order to avoid breaking dependent resources.

```bash
# Step 1: Destroy all applications (each independent)
cd resources/portfolio/dev
terraform destroy -auto-approve

cd resources/dashboard/dev
terraform destroy -auto-approve

cd resources/school/dev
terraform destroy -auto-approve

# Step 2: Destroy shared infrastructure (LAST)
cd resources/shared/dev
terraform destroy -auto-approve
```

**Why this order?**
- Applications depend on shared infrastructure (VPC, security groups)
- Destroying shared resources first breaks application state files
- Destroying apps first allows clean, independent removal

### Estimated Time to Destroy

- Per app: 3-5 minutes
- Shared infrastructure: 5-10 minutes
- **Total:** ~20-30 minutes for complete teardown

---

## Cost Monitoring & Alerts

### 1. Enable AWS Billing Alerts

```bash
# Enable billing alerts (requires root account)
aws ce create-budget \
  --budget Name=mecandjeo-monthly-limit,Type=MONTHLY,Limit=100 \
  --notifications-with-subscribers

# Or via AWS Console:
# Billing → Billing Preferences → Enable billing alerts → Alarms
```

### 2. CloudWatch Budget Alarm

```hcl
resource "aws_budgets_budget" "monthly" {
  name              = "mecandjeo-monthly-limit"
  budget_type       = "MONTHLY"
  limit_unit        = "USD"
  limit_value       = "100"
  time_period_start = "2026-05-01"
  time_period_end   = "2099-12-31"

  cost_filters = {
    Application = ["dashboard", "portfolio", "school"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    notification_type          = "FORECASTED"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_channel_type  = "EMAIL"
    notification_channel_value = "your-email@example.com"
  }
}
```

### 3. Cost Explorer Dashboard

**AWS Console → Cost Management → Cost Explorer:**
- Group by: Application, Environment, Service
- Time range: Last 30 days
- Refresh daily to monitor trends

---

## Estimated Monthly Costs

### Scenario 1: Development Only (All apps)

```
Shared Infrastructure:    $0-10/month
  - VPC, Security Groups, IAM: Free
  - EC2 t3.micro: Free (first 12 months) or $7

Dashboard Dev:            $20-30/month
  - ALB: $16.20
  - ECS Fargate (1 task): $5.50
  - Misc: $1-2

Portfolio Dev:            $20-30/month
  - (Same as Dashboard)

School Dev:               $20-30/month
  - (Same as Dashboard)

Total Dev:                $60-100/month
```

### Scenario 2: Dev + Production (Dashboard only)

```
Shared Infrastructure:    $0-10/month
Dashboard Dev:            $20-30/month
Dashboard Prod:           $20-30/month
  (Higher compute, more replicas)

Total with Prod:          $40-70/month
```

### Scenario 3: All Apps, Dev + Prod

```
Shared Infrastructure:    $0-10/month
Dashboard Dev + Prod:     $40-60/month
Portfolio Dev + Prod:     $40-60/month
School Dev + Prod:        $40-60/month

Total All:                $120-190/month
```

---

## Cost Optimization Tips

### 1. Right-Size Compute

Current: **0.25 vCPU + 512 MB memory** per task

- For light apps (portfolio, school): Keep as-is
- For heavy apps (dashboard): Consider scaling to 0.5 vCPU + 1 GB
- Measure CloudWatch metrics before upgrading

**Command to check CPU/memory utilization:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=mecandjeo-dashboard-dev-service \
  --start-time 2026-05-24T00:00:00Z \
  --end-time 2026-05-31T00:00:00Z \
  --period 86400 \
  --statistics Average
```

### 2. Use Spot Instances for Dev

For development workloads, ECS Spot instances can save **70-90%** on compute costs.

```hcl
capacity_provider_strategy {
  capacity_provider = "FARGATE_SPOT"
  weight           = 1
  base             = 0
}
```

**Trade-off:** Spot instances may be interrupted (acceptable for dev, not for prod).

### 3. Consolidate Environments

Instead of dev + prod, consider:
- **Single dev environment** for cost-conscious teams
- **Shared prod environment** with high availability
- **Feature branches** trigger temporary Terraform deployments (then destroy)

### 4. Delete Unused ECR Images

```bash
# List unused images older than 30 days
aws ecr describe-images \
  --repository-name mecandjeo-dashboard \
  --query 'imageDetails[?imagePushedAt<=`2026-04-30`]'

# Delete old images
aws ecr batch-delete-image \
  --repository-name mecandjeo-dashboard \
  --image-ids imageTag=old-tag
```

### 5. Implement Auto-Shutdown for Dev

Schedule dev environments to shut down after hours:

```hcl
# Terraform: Set minimum task count to 0 after 6 PM, restore at 8 AM
resource "aws_appautoscaling_scheduled_action" "dev_shutdown" {
  service_namespace       = "ecs"
  schedule                = "cron(0 18 * * MON-FRI *)"  # 6 PM weekdays
  timezone                = "America/New_York"
  scalable_dimension      = "ecs:service:DesiredCount"
  scalable_target_id      = aws_appautoscaling_target.ecs.id
  scalable_target_action {
    min_capacity = 0
  }
}

resource "aws_appautoscaling_scheduled_action" "dev_startup" {
  service_namespace       = "ecs"
  schedule                = "cron(0 8 * * MON *)"      # 8 AM Monday
  timezone                = "America/New_York"
  scalable_dimension      = "ecs:service:DesiredCount"
  scalable_target_id      = aws_appautoscaling_target.ecs.id
  scalable_target_action {
    min_capacity = 1
  }
}
```

---

## Cost Estimation Commands

### Estimate Apply (Before Deploying)

```bash
cd resources/dashboard/dev
terraform plan -var-file=terraform.tfvars.pipeline \
  | grep -E "resource|will be|plan:"

# Manual review: ALB = $16.20/mo, ECS Fargate = $5.50/mo per task
```

### Estimate Current AWS Bill

```bash
# Get current month-to-date costs
aws ce get-cost-and-usage \
  --time-period Start=2026-05-01,End=2026-05-31 \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --filter file://cost-filter.json

# Output: JSON with daily costs by service
```

### Estimate Next Month

```bash
aws ce get-cost-forecast \
  --time-period Start=2026-06-01,End=2026-06-30 \
  --metric BLENDED_COST \
  --granularity MONTHLY \
  --filter file://cost-filter.json
```

---

## Monthly Cost Audit Checklist

- [ ] Review AWS Cost Explorer for the previous month
- [ ] Check for unused resources (orphaned ALBs, old ECR images, unused ENIs)
- [ ] Verify all resources have proper tags
- [ ] Confirm no production apps are running in dev environment
- [ ] Review CloudWatch alarms — any over-provisioning?
- [ ] Update estimated costs in this document if rates change

---

## References

- [AWS EC2 Pricing](https://aws.amazon.com/ec2/pricing/on-demand/)
- [AWS ECS Fargate Pricing](https://aws.amazon.com/ecs/pricing/)
- [AWS ALB Pricing](https://aws.amazon.com/elasticloadbalancing/pricing/)
- [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/)
- [AWS Budgets](https://aws.amazon.com/aws-cost-management/aws-budgets/)
- [Tag Best Practices](https://docs.aws.amazon.com/general/latest/gr/tagging.html)
