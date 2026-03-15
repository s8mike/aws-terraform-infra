### 2. AWS Console equivalent steps per stage

This is an excellent learning parallel — understanding what Terraform is doing under the hood in the console makes you a much stronger engineer. Here's the console equivalent for every stage:

**Stage 2 — VPC (Console steps):**
1. Go to **VPC → Your VPCs → Create VPC**
2. Set CIDR to `10.0.0.0/16`, name it `webforx-infra-dev-vpc`
3. Go to **Subnets → Create Subnet**, select your VPC, create 4 subnets one by one with correct CIDRs and AZs
4. For public subnets, enable **"Auto-assign public IPv4"** in subnet settings
5. Go to **Internet Gateways → Create**, then **Actions → Attach to VPC**
6. Go to **Route Tables → Create**, associate with VPC, add route `0.0.0.0/0 → IGW` for public RT
7. Select each public subnet → **Route Table tab → Edit route table association**
8. Create a second route table for private subnets with no internet route, associate private subnets

**Stage 3 — EC2 (Console steps):**
1. Go to **EC2 → Launch Instance**
2. Choose Amazon Linux 2, t2.micro (free tier)
3. Select your VPC and a public subnet
4. Create or select a key pair, download `.pem` file
5. Configure security group to allow SSH port 22 from your IP
6. Launch and wait for running state
7. Connect via `ssh -i keypair.pem ec2-user@PUBLIC_IP`

**Stage 4 — Security Groups + IAM (Console steps):**
1. Go to **EC2 → Security Groups → Create Security Group**
2. Add inbound rules explicitly — port 80 from ALB, port 443, etc.
3. Go to **IAM → Roles → Create Role**
4. Select trusted entity: **AWS Service → ECS Task**
5. Attach policies: `AmazonECSTaskExecutionRolePolicy`
6. Name it `webforx-ecs-task-execution-role`

**Stage 5 — ECS Fargate (Console steps):**
1. Go to **ECS → Clusters → Create Cluster**, select Fargate
2. Go to **Task Definitions → Create**, select Fargate launch type
3. Add container: name `nginx`, image `nginx:latest`, port `80`
4. Set task CPU to `256`, memory to `512`
5. Go to **Clusters → your cluster → Services → Create**
6. Select your task definition, set desired count to `2`
7. Select your VPC and private subnets

**Stage 6 — ALB (Console steps):**
1. Go to **EC2 → Load Balancers → Create → Application Load Balancer**
2. Set scheme to **internet-facing**, select your VPC and public subnets
3. Create a **Target Group** with target type `IP`, protocol HTTP, port 80
4. Configure health check path as `/`
5. Add listener on port 80 forwarding to the target group
6. Update ECS service to attach to the target group

**Stage 7 — Auto Scaling + Remote State (Console steps):**
1. Go to **ECS → your service → Update → Auto Scaling tab**
2. Set min 1, max 4 tasks, add CPU scaling policy at 70% threshold
3. Go to **S3 → Create Bucket** named `webforx-tfstate-dev`, enable versioning
4. Go to **DynamoDB → Create Table** named `webforx-tfstate-lock`, partition key `LockID`
5. Update `backend.tf` to point to the S3 bucket and reinitialize Terraform

---