```markdown
# Troubleshooting Commands
## MecanjeoOps Infrastructure — Quick Reference
**Mecandjeo Technology — Platform Engineering — 2026**

---

## 1. AWS Credentials and Connectivity

```bash
# WHY: First check before any session — confirms your IAM credentials
#      are valid and not expired. Everything else fails if this fails.
# EXPECTED: JSON with UserId, Account 776735193826, and Arn
# IF WRONG: Run `aws configure` and re-enter your access keys
aws sts get-caller-identity
#============================================

# WHY: Quick test that your machine can reach AWS services.
#      Useful when terraform init fails with network errors.
# EXPECTED: List of S3 buckets including mecandjeo-infra-dev-tfstate
# IF WRONG: Check internet connection or VPN — disconnect VPN if active
aws s3 ls | head -5

#=============================================
# WHY: Confirms the S3 backend bucket exists before running terraform init.
#      If the bucket is missing terraform init will fail immediately.
# EXPECTED: No output and exit 0 = bucket exists
# IF WRONG: "Backend ready ✅" or "Bucket missing ❌"
aws s3api head-bucket \
  --bucket mecandjeo-infra-dev-tfstate \
  && echo "Backend ready ✅" \
  || echo "Bucket missing ❌ — see README prerequisites"


#==============================================
# WHY: Shows all Terraform state files currently in the S3 bucket.
#      Use this to confirm state keys exist and are at correct paths.
# EXPECTED: Four lines showing shared, dashboard, portfolio, school state keys
# IF WRONG: Missing key means that app has not been deployed yet
aws s3 ls s3://mecandjeo-infra-dev-tfstate/ --recursive

#======================================================
# WHY: Gets your current public IP address.
#      Your IP changes between sessions — update terraform.tfvars
#      allowed_ssh_cidr if it changes or SSH will be blocked.
# EXPECTED: Your current public IP e.g. 98.85.216.142
curl ifconfig.me

#=======================================================
# WHY: Confirms all three ALBs exist and are in active state.
#      Use after terraform apply to verify ALBs were created.
# EXPECTED: Three rows — dashboard, portfolio, school — all State: active
# IF WRONG: Missing ALB means terraform apply failed or was not run
aws elbv2 describe-load-balancers \
  --query "LoadBalancers[*].{Name:LoadBalancerName,DNS:DNSName,State:State.Code}" \
  --output table
```

---

## 2. ECS — Service Health

```bash
# WHY: Most important diagnostic command — tells you immediately
#      if ECS tasks are running, starting, or failing.
#      Running should equal Desired. Pending means tasks are starting.
#      Running=0 with Pending=0 means tasks are crashing on startup.
# EXPECTED: Desired=2, Pending=0, Running=2 for healthy dashboard
# IF WRONG: Run section 3 (Task Failure Diagnosis) to find root cause

# Dashboard
aws ecs describe-services \
  --cluster mecandjeo-infra-dev-cluster \
  --services mecandjeo-infra-dev-service \
  --query "services[0].{Running:runningCount,Pending:pendingCount,Desired:desiredCount}" \
  --output table

# Portfolio
aws ecs describe-services \
  --cluster mecandjeo-portfolio-dev-cluster \
  --services mecandjeo-portfolio-dev-service \
  --query "services[0].{Running:runningCount,Pending:pendingCount,Desired:desiredCount}" \
  --output table

# School
aws ecs describe-services \
  --cluster mecandjeo-school-dev-cluster \
  --services mecandjeo-school-dev-service \
  --query "services[0].{Running:runningCount,Pending:pendingCount,Desired:desiredCount}" \
  --output table
#==========================================================================================

# WHY: Check all three apps at once — useful at session start
#      to confirm everything is healthy before testing in browser.
# EXPECTED: All three show Running = Desired
# IF WRONG: Investigate the failing app using sections 3, 4, and 5
echo "=== Dashboard ===" && \
aws ecs describe-services \
  --cluster mecandjeo-infra-dev-cluster \
  --services mecandjeo-infra-dev-service \
  --query "services[0].{Running:runningCount,Desired:desiredCount}" \
  --output table && \
echo "=== Portfolio ===" && \
aws ecs describe-services \
  --cluster mecandjeo-portfolio-dev-cluster \
  --services mecandjeo-portfolio-dev-service \
  --query "services[0].{Running:runningCount,Desired:desiredCount}" \
  --output table && \
echo "=== School ===" && \
aws ecs describe-services \
  --cluster mecandjeo-school-dev-cluster \
  --services mecandjeo-school-dev-service \
  --query "services[0].{Running:runningCount,Desired:desiredCount}" \
  --output table
```

---

## 3. ECS — Task Failure Diagnosis

```bash
# WHY: When Running=0, tasks are stopping before they can register
#      with the ALB. This command lists the stopped task IDs so you
#      can describe them in the next command to find the failure reason.
# EXPECTED: One or more task ARNs listed
# IF WRONG: Empty output means no recently stopped tasks — check running tasks instead

# Dashboard stopped tasks
aws ecs list-tasks \
  --cluster mecandjeo-infra-dev-cluster \
  --desired-status STOPPED \
  --output text

# Portfolio stopped tasks
aws ecs list-tasks \
  --cluster mecandjeo-portfolio-dev-cluster \
  --desired-status STOPPED \
  --output text

# School stopped tasks
aws ecs list-tasks \
  --cluster mecandjeo-school-dev-cluster \
  --desired-status STOPPED \
  --output text

#====================================================================

# WHY: Shows exactly why a task stopped — the most useful diagnostic
#      command when tasks keep crashing. Copy the task ID (32 chars)
#      from the list above and paste it below.
#      Common reasons:
#        CannotPullContainerError → ECR image missing or wrong tag
#        Essential container exited → app crashed on startup
#        ResourceInitializationError → network/IAM issue
# EXPECTED: Table showing STOPPED status and the specific failure reason
# IF WRONG: Read the Reason column — it tells you exactly what to fix

# Dashboard — paste task ID from list above
aws ecs describe-tasks \
  --cluster mecandjeo-infra-dev-cluster \
  --tasks PASTE_TASK_ID_HERE \
  --query "tasks[0].{Status:lastStatus,Reason:stoppedReason,Container:containers[0].reason}" \
  --output table

# Portfolio — paste task ID from list above
aws ecs describe-tasks \
  --cluster mecandjeo-portfolio-dev-cluster \
  --tasks PASTE_TASK_ID_HERE \
  --query "tasks[0].{Status:lastStatus,Reason:stoppedReason,Container:containers[0].reason}" \
  --output table

# School — paste task ID from list above
aws ecs describe-tasks \
  --cluster mecandjeo-school-dev-cluster \
  --tasks PASTE_TASK_ID_HERE \
  --query "tasks[0].{Status:lastStatus,Reason:stoppedReason,Container:containers[0].reason}" \
  --output table
```

---

## 4. ALB — Target Health

```bash
# WHY: When the browser shows 503, the ALB has no healthy targets.
#      This command shows whether ECS tasks have registered with the
#      ALB and whether they are passing health checks on their port.
#      Common states:
#        healthy   → app is running and /health returns 200
#        unhealthy → app is running but health check fails
#        initial   → task just started, health check not run yet
#        unused    → no tasks registered at all
#        Target.Timeout → security group blocking the port
# EXPECTED: State: healthy for all registered targets
# IF WRONG: Target.Timeout → add port to app_ports in security module

# Dashboard — port 8000
TG_ARN=$(aws elbv2 describe-target-groups \
  --names mecandjeo-infra-dev-tg \
  --query "TargetGroups[0].TargetGroupArn" \
  --output text) && \
aws elbv2 describe-target-health \
  --target-group-arn $TG_ARN \
  --output json

# Portfolio — port 8001
TG_ARN=$(aws elbv2 describe-target-groups \
  --names mecandjeo-portfolio-dev-tg \
  --query "TargetGroups[0].TargetGroupArn" \
  --output text) && \
aws elbv2 describe-target-health \
  --target-group-arn $TG_ARN \
  --output json

# School — port 8002
TG_ARN=$(aws elbv2 describe-target-groups \
  --names mecandjeo-school-dev-tg \
  --query "TargetGroups[0].TargetGroupArn" \
  --output text) && \
aws elbv2 describe-target-health \
  --target-group-arn $TG_ARN \
  --output json
```

---

## 5. CloudWatch Logs

```bash
# WHY: When a task stops with "Essential container exited" you need
#      to read the application logs to see what error caused the crash.
#      This lists the most recent log streams — each stream corresponds
#      to one container run. Pick the most recent one.
# EXPECTED: Table showing stream names — copy the most recent one
# IF WRONG: Empty table means the container never started logging
#           — check ECR image and task definition

# Dashboard
MSYS_NO_PATHCONV=1 aws logs describe-log-streams \
  --log-group-name /ecs/mecandjeo-infra-dev \
  --order-by LastEventTime \
  --descending \
  --max-items 3 \
  --query "logStreams[*].logStreamName" \
  --output table

# Portfolio
MSYS_NO_PATHCONV=1 aws logs describe-log-streams \
  --log-group-name /ecs/mecandjeo-portfolio-dev \
  --order-by LastEventTime \
  --descending \
  --max-items 3 \
  --query "logStreams[*].logStreamName" \
  --output table

# School
MSYS_NO_PATHCONV=1 aws logs describe-log-streams \
  --log-group-name /ecs/mecandjeo-school-dev \
  --order-by LastEventTime \
  --descending \
  --max-items 3 \
  --query "logStreams[*].logStreamName" \
  --output table
#=======================================================================

# WHY: Reads the actual application log output from a specific container
#      run. This is where you see Python tracebacks, missing env vars,
#      database connection errors, and import failures.
#      Copy the stream name from the describe-log-streams output above.
# EXPECTED: Application startup logs ending with "Uvicorn running on..."
# IF WRONG: Read the error — common issues:
#           "Expected string, got None" → missing env variable
#           "ModuleNotFoundError"       → missing dependency in requirements.txt
#           "Connection refused"        → database not reachable

# Dashboard — paste stream name from describe-log-streams above
MSYS_NO_PATHCONV=1 aws logs get-log-events \
  --log-group-name /ecs/mecandjeo-infra-dev \
  --log-stream-name PASTE_STREAM_NAME_HERE \
  --limit 30 \
  --query "events[*].message" \
  --output text

# Portfolio — paste stream name from describe-log-streams above
MSYS_NO_PATHCONV=1 aws logs get-log-events \
  --log-group-name /ecs/mecandjeo-portfolio-dev \
  --log-stream-name PASTE_STREAM_NAME_HERE \
  --limit 30 \
  --query "events[*].message" \
  --output text

# School — paste stream name from describe-log-streams above
MSYS_NO_PATHCONV=1 aws logs get-log-events \
  --log-group-name /ecs/mecandjeo-school-dev \
  --log-stream-name PASTE_STREAM_NAME_HERE \
  --limit 30 \
  --query "events[*].message" \
  --output text
```

---

## 6. ECR — Image Verification

```bash
# WHY: ECS tasks fail with CannotPullContainerError when the ECR image
#      does not exist or the tag in the task definition does not match
#      any pushed image. Always verify the image exists before deploying.
# EXPECTED: Table showing v1.0.0, latest, and SHA tags with push timestamps
# IF WRONG: Push the image first — see POST-DEPLOYMENT-ACTIVITIES.md

# Dashboard
aws ecr describe-images \
  --repository-name mecandjeo-infra-dev \
  --query "imageDetails[*].{Tags:imageTags,Pushed:imagePushedAt}" \
  --output table

# Portfolio
aws ecr describe-images \
  --repository-name mecandjeo-infra-portfolio \
  --query "imageDetails[*].{Tags:imageTags,Pushed:imagePushedAt}" \
  --output table

# School
aws ecr describe-images \
  --repository-name mecandjeo-school-platform-dev \
  --query "imageDetails[*].{Tags:imageTags,Pushed:imagePushedAt}" \
  --output table

#==========================================================================


# WHY: Quick overview of all ECR repositories in the account.
#      Use to confirm all three app repositories exist before deploying.
# EXPECTED: Three repositories — mecandjeo-infra-dev,
#           mecandjeo-infra-portfolio, mecandjeo-school-platform-dev
# IF WRONG: Create missing repository — see README prerequisites
aws ecr describe-repositories \
  --query "repositories[*].{Name:repositoryName,URI:repositoryUri}" \
  --output table
```

---

## 7. Terraform State

```bash
# WHY: Confirms how many resources Terraform is tracking in each state.
#      Zero means state is empty — either never deployed or destroyed.
#      Use at session start to know what is already running.
# EXPECTED:
#   shared/dev    → 21 (if deployed and running)
#   dashboard/dev → 12 (if deployed and running)
#   portfolio/dev → 12 (if deployed and running)
#   school/dev    → 12 (if deployed and running)
#   Any zero      → that app is not currently deployed

# Shared
cd resources/shared/dev && \
  echo "Shared resources:" && \
  terraform state list | wc -l

# Dashboard
cd resources/dashboard/dev && \
  echo "Dashboard resources:" && \
  terraform state list | wc -l

# Portfolio
cd resources/portfolio/dev && \
  echo "Portfolio resources:" && \
  terraform state list | wc -l

# School
cd resources/school/dev && \
  echo "School resources:" && \
  terraform state list | wc -l

#===========================================================

# WHY: Shows the current Terraform outputs for each app.
#      Use after apply to get ALB DNS names and verify
#      shared infrastructure outputs are available for
#      terraform_remote_state to read.
# EXPECTED: Key-value pairs including alb_dns_name, vpc_id etc
# IF WRONG: "No outputs found" means apply was not run or outputs
#           were not declared — run terraform apply to write them

cd resources/shared/dev    && terraform output      # the && in the command means "Run the second command if the first succeed".
cd resources/dashboard/dev && terraform output
cd resources/portfolio/dev && terraform output
cd resources/school/dev    && terraform output

#================================================================

# WHY: When two terraform applies run at the same time or a previous
#      apply was interrupted, the state file can remain locked.
#      This prevents any new apply from running.
#      Get the lock ID from the error message and paste it below.
# EXPECTED: "Successfully unlocked the state"
# IF WRONG: Wait 2 minutes and retry — lock may still be releasing

cd resources/dashboard/dev
# WHY: Replace LOCK_ID_HERE with the ID from the lock error message
terraform force-unlock LOCK_ID_HERE
```

---

## 8. Security Group Verification

```bash
# WHY: When a new application port is added but traffic is still
#      timing out, the security group may not have been updated.
#      This confirms which ports are open from the ALB to ECS tasks.
# EXPECTED: Ingress rules for ports 8000, 8001, 8002
#           all with source being the ALB security group ID
# IF WRONG: Add missing port to app_ports list in
#           modules/security/main.tf and apply shared infrastructure
aws ec2 describe-security-groups \
  --filters "Name=tag:Name,Values=mecandjeo-infra-dev-ecs-sg" \
  --query "SecurityGroups[0].IpPermissions" \
  --output json

#========================================================================

# WHY: Confirms the ALB security group allows HTTP traffic from the
#      internet on port 80. Without this no browser requests reach the ALB.
# EXPECTED: Ingress on port 80 from 0.0.0.0/0
# IF WRONG: ALB security group was not created correctly —
#           run terraform apply on shared infrastructure
aws ec2 describe-security-groups \
  --filters "Name=tag:Name,Values=mecandjeo-infra-dev-alb-sg" \
  --query "SecurityGroups[0].IpPermissions" \
  --output json
```

---

## 9. Force ECS Redeployment

```bash
# WHY: After terraform apply creates a new task definition revision,
#      ECS does not automatically replace running tasks with the new
#      image. This command forces all running tasks to be replaced
#      with fresh containers using the latest task definition.
#      Use when code changes are deployed but browser still shows
#      old content — even after terraform apply succeeds.
# EXPECTED: Service update accepted — tasks begin replacing within 30s
# IF WRONG: Check IAM permissions — the Terraform IAM user needs
#           ecs:UpdateService permission

# Dashboard
aws ecs update-service \
  --cluster mecandjeo-infra-dev-cluster \
  --service mecandjeo-infra-dev-service \
  --force-new-deployment \
  --region us-east-1 \
  && echo "Dashboard redeployment forced ✅"

# Portfolio
aws ecs update-service \
  --cluster mecandjeo-portfolio-dev-cluster \
  --service mecandjeo-portfolio-dev-service \
  --force-new-deployment \
  --region us-east-1 \
  && echo "Portfolio redeployment forced ✅"

# School
aws ecs update-service \
  --cluster mecandjeo-school-dev-cluster \
  --service mecandjeo-school-dev-service \
  --force-new-deployment \
  --region us-east-1 \
  && echo "School redeployment forced ✅"
```

---

## 10. Docker Hub Verification

```bash
# WHY: Confirms Docker Hub images were pushed successfully by the
#      pipeline. Use when a pipeline says it pushed but you want
#      to verify the tags exist publicly.
# EXPECTED: latest and one or more SHA tags e.g. a3f8c12d
# IF WRONG: Pipeline docker job failed — check GitHub Actions logs

# Dashboard tags
# WHY: Confirms dashboard image is publicly accessible on Docker Hub
curl -s \
  "https://hub.docker.com/v2/repositories/s8mike/mecandjeo-dashboard/tags/" \
  | jq -r '.results[].name'

# Portfolio tags
# WHY: Confirms portfolio image is publicly accessible on Docker Hub
curl -s \
  "https://hub.docker.com/v2/repositories/s8mike/mecandjeo-portfolio/tags/" \
  | jq -r '.results[].name'

# School tags
# WHY: Confirms school image is publicly accessible on Docker Hub
curl -s \
  "https://hub.docker.com/v2/repositories/s8mike/mecandjeo-school/tags/" \
  | jq -r '.results[].name'
```

---

## 11. Pre-Deploy Checklist

```bash
# WHY: Run this bundle before every terraform apply to catch
#      missing prerequisites before they cause cryptic errors.
#      Catches the most common session startup failures in one shot.
# EXPECTED: All lines show ✅
# IF WRONG: Fix each ❌ before running terraform apply

echo "=== Pre-Deploy Check ===" && \

# WHY: Expired credentials cause every subsequent command to fail
echo -n "AWS credentials : " && \
aws sts get-caller-identity \
  --query "Account" --output text && \

# WHY: S3 bucket must exist before terraform init can connect to backend
echo -n "S3 bucket       : " && \
aws s3api head-bucket \
  --bucket mecandjeo-infra-dev-tfstate 2>/dev/null \
  && echo "EXISTS ✅" || echo "MISSING ❌ — create bucket first" && \

# WHY: Dashboard ECR must exist — ECS cannot pull image without it
echo -n "Dashboard ECR   : " && \
aws ecr describe-repositories \
  --repository-names mecandjeo-infra-dev \
  --query "repositories[0].repositoryName" \
  --output text 2>/dev/null || echo "MISSING ❌" && \

# WHY: Portfolio ECR must exist — ECS cannot pull image without it
echo -n "Portfolio ECR   : " && \
aws ecr describe-repositories \
  --repository-names mecandjeo-infra-portfolio \
  --query "repositories[0].repositoryName" \
  --output text 2>/dev/null || echo "MISSING ❌" && \

# WHY: School ECR must exist — ECS cannot pull image without it
echo -n "School ECR      : " && \
aws ecr describe-repositories \
  --repository-names mecandjeo-school-platform-dev \
  --query "repositories[0].repositoryName" \
  --output text 2>/dev/null || echo "MISSING ❌" && \

# WHY: Shared state must have real resources before apps can read
#      terraform_remote_state outputs — empty state = deploy fails
echo -n "Shared state    : " && \
aws s3 ls \
  s3://mecandjeo-infra-dev-tfstate/mecandjeo-shared/dev/ \
  2>/dev/null | wc -l | \
  xargs -I{} sh -c \
  '[ {} -gt 0 ] \
  && echo "EXISTS ✅" \
  || echo "DEPLOY SHARED FIRST ❌"' && \

echo "=== Check Complete ==="
```

---

## 12. Destroy Verification

```bash
# WHY: After terraform destroy, confirm no ALBs are still running
#      which would continue incurring charges.
# EXPECTED: Empty table or no rows — all ALBs destroyed
# IF WRONG: Manually delete lingering ALBs in AWS console
aws elbv2 describe-load-balancers \
  --query "LoadBalancers[*].{Name:LoadBalancerName,State:State.Code}" \
  --output table

# WHY: Confirms all ECS clusters are gone after destroy.
#      Running clusters with zero tasks still appear in billing.
# EXPECTED: Empty list — no clusters
# IF WRONG: Run terraform destroy again from the relevant directory
aws ecs list-clusters --output table

# WHY: Confirms VPC is destroyed when shared infrastructure is destroyed.
#      An orphaned VPC with attached resources can block future applies.
# EXPECTED: Empty — no VPCs with the mecandjeo-infra tag
# IF WRONG: Check for dependent resources preventing VPC deletion
aws ec2 describe-vpcs \
  --filters "Name=tag:Project,Values=mecandjeo-infra" \
  --query "Vpcs[*].{ID:VpcId,State:State}" \
  --output table

# WHY: Final cost safety check — confirms S3 and ECR survived destroy
#      and no unexpected resources are still running.
# EXPECTED: S3 bucket and ECR repos still exist — everything else gone
echo "=== Post-Destroy Verification ===" && \
echo "--- S3 State Keys ---" && \
aws s3 ls s3://mecandjeo-infra-dev-tfstate/ --recursive && \
echo "--- ECR Repositories ---" && \
aws ecr describe-repositories \
  --query "repositories[*].repositoryName" \
  --output table
```

---

## 13. Common Errors — Cause and Fix


| Error                                    | Cause                           | Fix                                           |
|------------------------------------------|---------------------------------|-----------------------------------------------|
| `503 Service Unavailable`                | ECS targets unhealthy           | Wait until Running = Desired                  |
| `Target.Timeout`                         | SG blocks container port        | Add port in `modules/security/main.tf`        |
| `CannotPullContainerError`               | Missing ECR image/tag           | Push image to ECR first                       |
| `remote_state outputs has no attributes` | Shared infra not applied        | Run `terraform apply` + `terraform output`    |
| `ERR_NAME_NOT_RESOLVED`                  | Old ALB DNS used                | Run `terraform output alb_dns_name`           |
| `terraform init timeout`                 | Cannot reach Terraform registry | Copy `.terraform/` and retry                  |
| `EntityAlreadyExists`                    | Wrong pipeline working dir      | Fix `working-directory` path                  |
| `undeclared variable`                    | Removed variable still passed   | Remove obsolete `-var` flag                   |
| `Expected string, got None`              | Missing env variable            | Add env var to ECS task definition            |
| `terraform fmt exit code 3`              | Formatting mismatch             | Run `terraform fmt -recursive`                |
| `state file locked`                      | Interrupted/concurrent apply    | Run `terraform force-unlock LOCK_ID`          |
| `changes not appearing`                  | Old ECS image still running     | Force new ECS deployment                      |
| `image/avatar not updating`              | Browser cache issue             | Hard refresh browser                          |
| `.pdf.pdf` extension                     | File renamed twice              | Rename file correctly                         |
```md
---

*MecanjeoOps Infrastructure — Troubleshooting Reference*
*Mecandjeo Technology — Platform Engineering — 2026*
```

Commit it:

```bash
git add TROUBLESHOOTING-COMMANDS.md
git commit -m "docs: add TROUBLESHOOTING-COMMANDS with inline WHY/EXPECTED/IF WRONG comments on every command"
git push
```

🚀