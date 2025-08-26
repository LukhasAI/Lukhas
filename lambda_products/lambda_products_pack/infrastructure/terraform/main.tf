terraform {
  required_version = ">= 1.3.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }

  backend "s3" {
    bucket         = "lambda-products-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

# AWS EKS Cluster for Lambda Products
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "lambda-products-cluster"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Elite auto-scaling configuration
  eks_managed_node_groups = {
    # Spot instances for cost optimization
    spot_agents = {
      min_size     = 3
      max_size     = 100
      desired_size = 10

      instance_types = ["t3.large", "t3a.large"]
      capacity_type  = "SPOT"

      labels = {
        Environment = "production"
        Type        = "agent"
      }

      taints = [{
        key    = "spot"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]

      update_config = {
        max_unavailable_percentage = 33
      }
    }

    # On-demand for critical services
    on_demand_core = {
      min_size     = 2
      max_size     = 20
      desired_size = 5

      instance_types = ["m5.xlarge"]
      capacity_type  = "ON_DEMAND"

      labels = {
        Environment = "production"
        Type        = "core"
      }
    }

    # GPU nodes for AI workloads
    gpu_ai = {
      min_size     = 0
      max_size     = 10
      desired_size = 2

      instance_types = ["g4dn.xlarge"]
      capacity_type  = "ON_DEMAND"

      labels = {
        Environment = "production"
        Type        = "ai-gpu"
      }

      taints = [{
        key    = "nvidia.com/gpu"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
  }

  # IRSA for pod-level AWS access
  enable_irsa = true

  # Cluster addons
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }
}

# VPC with elite networking
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "lambda-products-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-west-2a", "us-west-2b", "us-west-2c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = false  # HA NAT gateways
  enable_dns_hostnames = true
  enable_dns_support   = true

  # VPC Flow Logs for security
  enable_flow_log                      = true
  create_flow_log_cloudwatch_iam_role  = true
  create_flow_log_cloudwatch_log_group = true

  tags = {
    Environment = "production"
    Project     = "lambda-products"
  }
}

# RDS Aurora Serverless v2 for scalable database
module "aurora" {
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 8.0"

  name           = "lambda-products-db"
  engine         = "aurora-postgresql"
  engine_version = "15.3"

  vpc_id               = module.vpc.vpc_id
  db_subnet_group_name = module.vpc.database_subnet_group_name
  security_group_rules = {
    eks_ingress = {
      source_security_group_id = module.eks.node_security_group_id
    }
  }

  # Serverless v2 for auto-scaling
  serverlessv2_scaling_configuration = {
    max_capacity = 16
    min_capacity = 0.5
  }

  instance_class = "db.serverless"
  instances = {
    one = {}
    two = {}  # Read replica
  }

  # Automated backups
  backup_retention_period = 30
  preferred_backup_window = "03:00-04:00"

  # Performance insights
  enabled_cloudwatch_logs_exports = ["postgresql"]
  performance_insights_enabled     = true

  # Security
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn
}

# ElastiCache Redis for high-performance caching
module "elasticache" {
  source = "terraform-aws-modules/elasticache/aws"

  name = "lambda-products-cache"

  engine               = "redis"
  engine_version       = "7.0"
  family              = "redis7"
  port                = 6379
  node_type           = "cache.r7g.large"
  num_cache_nodes     = 3

  # Cluster mode for horizontal scaling
  parameter = [
    {
      name  = "cluster-enabled"
      value = "yes"
    }
  ]

  # Security
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Automatic failover
  automatic_failover_enabled = true
  multi_az_enabled          = true

  # Backups
  snapshot_retention_limit = 5
  snapshot_window          = "03:00-05:00"
}

# S3 buckets for data lake
resource "aws_s3_bucket" "data_lake" {
  bucket = "lambda-products-data-lake"

  tags = {
    Environment = "production"
    Purpose     = "data-lake"
  }
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
  }
}

# CloudFront CDN for global distribution
resource "aws_cloudfront_distribution" "main" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  origin {
    domain_name = aws_s3_bucket.static_assets.bucket_regional_domain_name
    origin_id   = "S3-static-assets"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.main.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-static-assets"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# WAF for DDoS protection
resource "aws_wafv2_web_acl" "main" {
  name  = "lambda-products-waf"
  scope = "CLOUDFRONT"

  default_action {
    allow {}
  }

  # Rate limiting rule
  rule {
    name     = "RateLimitRule"
    priority = 1

    statement {
      rate_based_statement {
        limit              = 10000
        aggregate_key_type = "IP"
      }
    }

    action {
      block {}
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }
}

# Monitoring with CloudWatch
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "lambda-products-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/EKS", "cluster_node_count", { stat = "Average" }],
            ["AWS/RDS", "DatabaseConnections", { stat = "Sum" }],
            ["AWS/ElastiCache", "CacheHits", { stat = "Sum" }],
            ["AWS/Lambda", "Invocations", { stat = "Sum" }]
          ]
          period = 300
          stat   = "Average"
          region = "us-west-2"
          title  = "System Metrics"
        }
      }
    ]
  })
}

# Auto-scaling policies
resource "aws_autoscaling_policy" "agents" {
  name                   = "lambda-products-agent-scaling"
  scaling_adjustment     = 10
  adjustment_type        = "PercentChangeInCapacity"
  cooldown              = 300
  autoscaling_group_name = module.eks.eks_managed_node_groups.spot_agents.asg_name

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

# KMS keys for encryption
resource "aws_kms_key" "main" {
  description             = "Lambda Products master key"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "aws_kms_key" "rds" {
  description             = "RDS encryption key"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "aws_kms_key" "s3" {
  description             = "S3 encryption key"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

# Outputs for other services
output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "database_endpoint" {
  value = module.aurora.cluster_endpoint
}

output "redis_endpoint" {
  value = module.elasticache.primary_endpoint
}

output "cdn_domain" {
  value = aws_cloudfront_distribution.main.domain_name
}
