# Deployment

This section covers how to deploy the ClassCharts Calendar Sync application to AWS.

## Deployment Options

- [Standard Deployment](standard.md) - The recommended approach for most users
- [Advanced Options](advanced.md) - Custom configurations, profiles, and parameters
- [Troubleshooting](troubleshooting.md) - Resolving common deployment issues

## Deployment Overview

The ClassCharts Calendar Sync application is deployed as an AWS Serverless application consisting of:

1. **AWS Lambda Function** - Runs the calendar synchronization code
2. **Amazon S3 Bucket** - Stores the generated calendar files
3. **CloudWatch Events Rule** - Triggers the Lambda function every 6 hours
4. **IAM Role and Policies** - Provides the necessary permissions

## Deployment Process

The deployment process uses the AWS Serverless Application Model (SAM) to deploy the application:

1. **Build** - Packages the code and dependencies into a deployment package
2. **Deploy** - Creates or updates the AWS CloudFormation stack

```bash
# Build the application
sam build

# Deploy with guided setup
sam deploy --guided
```

## Deployment Requirements

Before deploying, ensure you have:

1. AWS CLI and SAM CLI installed and configured
2. AWS credentials with appropriate permissions
3. ClassCharts credentials stored in AWS Secrets Manager

See the [Getting Started](../getting-started.md) guide for detailed instructions on setting up these requirements.