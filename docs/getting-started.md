# Getting Started

This guide will help you quickly set up the ClassCharts Calendar Sync application on your AWS account.

## Prerequisites

Before you begin, ensure you have the following:

### Required

- Python 3.9+ (3.12 recommended)
- pip package manager (included with Python)
- An AWS account with appropriate permissions:
  - Lambda: Create and manage functions
  - S3: Create buckets and manage objects
  - IAM: Create roles and policies
  - Secrets Manager: Create and access secrets
- ClassCharts parent account credentials

### Development Tools

- AWS CLI: For interacting with AWS services
- AWS SAM CLI: For local testing and deployment
- Git: For version control (optional)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/phillprice/classcharts-calendar-ics.git
cd classcharts-calendar-ics
```

### 2. Install Dependencies

```bash
# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure AWS Credentials

If you haven't configured AWS CLI yet:

```bash
aws configure
```

You'll be prompted to enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., eu-west-2)
- Default output format (json recommended)

### 4. Create AWS Secrets Manager Secret

Store your ClassCharts credentials in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
    --name classcharts/credentials \
    --secret-string '{"email":"your-email@example.com","password":"your-password","student_ids":[1234567, 7654321]}' \
    --region eu-west-2
```

!!! info "Multiple Students"
    The `student_ids` field accepts an array of student IDs for supporting multiple students.

### 5. Build and Deploy

```bash
# Build the SAM application
sam build

# Deploy with guided setup
sam deploy --guided
```

During the guided setup, you'll be asked to:
- Enter a stack name (e.g., `classcharts-calendar`)
- Choose an AWS region
- Configure deployment parameters
- Confirm IAM role creation

## Next Steps

After deployment, you should have:

1. A Lambda function that runs every 6 hours
2. An S3 bucket containing your calendar files
3. Public URLs for each student's calendar

Now you can:

- [Add the calendars to your applications](usage/calendar-applications.md)
- [Configure environment variables](configuration/environment-variables.md)
- [Learn about local development](development/environment-setup.md)