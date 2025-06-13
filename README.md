# ClassCharts Calendar Sync

A simple AWS Lambda function that fetches timetable data from ClassCharts and creates an iCal calendar file hosted on S3.

## Prerequisites

- Python 3.9+
- pip installed (comes with Python)
- An AWS account with permissions to create Lambda, S3, IAM, and Secrets Manager resources
- AWS CLI installed and configured
- AWS SAM CLI installed

### Installing AWS CLI

1. Install the AWS CLI by following the [official AWS CLI installation instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html):

   **macOS**:

   ```bash
   curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
   sudo installer -pkg AWSCLIV2.pkg -target /
   ```

   **Windows**: Download and run the [AWS CLI MSI installer](https://awscli.amazonaws.com/AWSCLIV2.msi)

   **Linux**:

   ```bash
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

2. Configure the AWS CLI with your AWS credentials:

   ```bash
   aws configure
   ```

   You'll be prompted to enter:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region name (e.g., eu-west-2)
   - Default output format (json recommended)

3. You can create additional profiles with:

   ```bash
   aws configure --profile YOUR_PROFILE_NAME
   ```

### Installing AWS SAM CLI

1. Install the AWS SAM CLI by following the [official SAM CLI installation instructions](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html):

   **macOS**:

   ```bash
   # Using Homebrew
   brew tap aws/tap
   brew install aws-sam-cli
   ```

   **Windows**: Download and run the [AWS SAM CLI MSI installer](https://github.com/aws/aws-sam-cli/releases/latest/download/AWS_SAM_CLI_64_PY3.msi)

   **Linux**:

   ```bash
   # Install dependencies
   sudo apt-get update
   sudo apt-get install -y unzip

   # Download and install
   curl -sL "https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip" -o "aws-sam-cli-linux.zip"
   unzip aws-sam-cli-linux.zip -d sam-installation
   sudo ./sam-installation/install
   ```

2. Verify the installation:

   ```bash
   sam --version
   ```

## Configuration

All configuration settings have been centralized for easy management:

1. Environment variables for deployment settings
2. AWS Secrets Manager for sensitive credentials

> **Note**: AWS Lambda prevents setting `AWS_REGION` as an environment variable, as it's a reserved variable. The region is automatically set by AWS Lambda based on where the function is deployed.

### Configuration Files

| File | Purpose |
|------|---------|
| `config.py` | Centralized configuration with environment variable fallbacks |
| `template.yaml` | SAM template with environment variable definitions |

### Environment Variables

The following environment variables can be configured:

| Variable | Default | Description |
|----------|---------|-------------|
| `AWS_REGION` | `eu-west-2` | AWS region to use |
| `BUCKET_NAME` | `classcharts-calendar-{account-id}` | S3 bucket name for the calendar (automatically appends your AWS account ID for uniqueness) |
| `CALENDAR_FILENAME_TEMPLATE` | `{student_id}.ics` | Template for calendar filenames (supports `{student_id}` and `{student_name}` placeholders) |
| `SECRET_NAME` | `classcharts/credentials` | Name of the secret in AWS Secrets Manager |

### AWS Secrets Manager Configuration


Create a secret in AWS Secrets Manager with the following values:

```json
{
  "email": "your-classcharts-email@example.com",
  "password": "your-classcharts-password",
  "student_ids": [1234562, 7654321]
}
```

For a single student, you can either use the array format above or use the legacy format with a single `student_id` key:

```json
{
  "email": "your-classcharts-email@example.com",
  "password": "your-classcharts-password",
  "student_id": 1234562
}
```

Use the following AWS CLI command (replace with your values):

```bash
# For multiple students
aws secretsmanager create-secret \
    --name classcharts/credentials \
    --secret-string '{"email":"your-email@example.com","password":"your-password","student_ids":[1234562, 7654321]}' \
    --region eu-west-2

# For a single student (legacy format)
aws secretsmanager create-secret \
    --name classcharts/credentials \
    --secret-string '{"email":"your-email@example.com","password":"your-password","student_id":1234562}' \
    --region eu-west-2
```

### SAM Deployment Parameters

During deployment with SAM, you can override the default values:

```bash
sam deploy --guided \
  --parameter-overrides \
  BucketName=my-custom-bucket \
  CalendarFilenameTemplate="{student_name}_{student_id}.ics" \
  SecretName=my/custom/secret/path
```

## Setup

### 1. Install Dependencies and Build the SAM Application

```bash
pip install -r requirements.txt
sam build
```

The SAM build process will use pip to package dependencies based on the `requirements.txt` file.

> **Dependency Management**:
>
> This project uses AWS Lambda Powertools Python as a Lambda layer to handle common dependencies, which simplifies deployment. If you need additional packages, follow these approaches:
>
> 1. **Use Lambda Layers**: The project uses the AWS Lambda Powertools layer which includes frequently used libraries.
>
>    ```yaml
>    # In template.yaml
>    Layers:
>      - !Sub arn:aws:lambda:${AWS::Region}:017000801446:layer:AWSLambdaPowertoolsPython:56
>    ```
>
> 2. **Minimize requirements.txt**: Keep only the essential dependencies in requirements.txt that aren't already in the Lambda layer.
>
>    ```bash
>    # Current dependencies
>    requests>=2.32.0
>    ics>=0.7.2
>    aws-lambda-powertools-python>=2.30.0
>    ```
>
> 3. **Deploy with SAM**: SAM will handle packaging dependencies properly with the simplified requirements.
>
>    ```bash
>    sam build
>    sam deploy --profile YOUR_PROFILE_NAME --no-confirm-changeset
>    ```
>
> 4. **Alternative: Manual dependency packaging**: If you still encounter dependency issues, you can manually create a deployment package:
>
>    ```bash
>    # Create a package directory
>    mkdir -p package
>    
>    # Install dependencies to the package directory
>    pip install -r requirements.txt -t ./package/
>    
>    # Copy your Python files to the package directory
>    cp main.py config.py package/
>    
>    # Create a deployment zip file
>    cd package && zip -r ../deployment-package.zip .
>    
>    # Update your Lambda function with the zip
>    aws lambda update-function-code \
>        --function-name YOUR_LAMBDA_FUNCTION_NAME \
>        --zip-file fileb://deployment-package.zip \
>        --profile YOUR_PROFILE_NAME
>    ```

### 2. Deploy the Application

```bash
sam deploy --guided
```

If you want to use a specific AWS profile, use the `--profile` flag:

```bash
sam deploy --guided --profile YOUR_PROFILE_NAME
```

You can also combine the profile with parameter overrides:

```bash
sam deploy --guided --profile YOUR_PROFILE_NAME --parameter-overrides BucketName=custom-bucket-name CalendarFilename=calendar.ics
```

Follow the prompts in the interactive deployment process:

- Enter a stack name (e.g., classcharts-calendar)
- Choose a region (e.g., eu-west-2)
- Accept the default parameter values
- Confirm IAM role creation
- Confirm that the function may not have authorization defined

> **Troubleshooting Deployments**:
>
> If you encounter deployment errors, try the following solutions:
>
> 1. **Use a unique stack name**: If you've previously deployed a failed stack, try using a new stack name:
>
>    ```bash
>    sam deploy --guided --profile YOUR_PROFILE_NAME --stack-name classcharts-calendar-dev
>    ```
>
> 2. **Deploy without confirmation**: To bypass the changeset confirmation:
>
>    ```bash
>    sam deploy --no-confirm-changeset --profile YOUR_PROFILE_NAME
>    ```
>
> 3. **Check CloudFormation console**: For detailed error messages, check your AWS CloudFormation console.


### 3. Testing

The Lambda function will automatically run on a schedule (every 6 hours), but you can also test it manually through the AWS Console or using the AWS CLI:

```bash
aws lambda invoke --function-name classcharts-calendar-ClasschartsCalendarFunction-XXXXXXXXXXXX --payload '{}' output.txt
```

Replace `classcharts-calendar-ClasschartsCalendarFunction-XXXXXXXXXXXX` with the actual function name from the deployment output.

## Calendar Access

After deployment, each student's calendar will be accessible at a URL that includes your AWS account ID and the student ID, for example:

```text
https://classcharts-cal-dev-123456789012.s3.amazonaws.com/1234562.ics
https://classcharts-cal-dev-123456789012.s3.amazonaws.com/7654321.ics
```

The exact bucket name will be shown in the deployment outputs as `ClasschartsCalendarBucketName`. You can also find all calendar URLs in the Lambda function's response, which will include a list of all generated calendars.

**Note:** The calendar files are intentionally public to allow calendar applications to subscribe to them without authentication. This is achieved through:

- S3 bucket policy that allows public read access
- `public-read` ACL set on the files during upload

You can add these URLs to your calendar application as subscriptions. Each student's timetable will be in a separate calendar file, allowing you to color-code or enable/disable them individually in your calendar application.

## Project Structure

- `main.py` - Lambda function code
- `template.yaml` - SAM template defining AWS resources
- `requirements.txt` - Python dependencies

## Local Development

### Setting Up a Python Virtual Environment

It's recommended to use a virtual environment to isolate your dependencies:

#### Using venv (Python's built-in virtual environment)

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Using pyenv (for managing Python versions)

```bash
# Install pyenv (on macOS with Homebrew)
brew install pyenv

# Install Python version
pyenv install 3.12.0

# Set local Python version
pyenv local 3.12.0

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running Locally

Once your virtual environment is set up and activated:

```bash
# Run the script locally
python main.py
```

Note: Local testing requires appropriate AWS credentials with Secrets Manager access.

## Testing

The project uses pytest for testing. Tests are located in the `tests` directory.

### Installing Test Dependencies

Inside your virtual environment, install the test dependencies:

```bash
pip install pytest pytest-mock pytest-cov moto freezegun responses
```

### Running Tests

To run all tests:

```bash
pytest
```

To run tests with verbose output:

```bash
pytest -v
```

To run a specific test:

```bash
pytest tests/test_main.py::test_lambda_handler_success
```

### Test Coverage

To generate a test coverage report:

```bash
pytest --cov=main tests/
```

### Test Structure

Tests use the following libraries:

- `pytest`: Testing framework
- `pytest-mock`: For mocking dependencies
- `moto`: For mocking AWS services (S3 and Secrets Manager)
- `responses`: For mocking HTTP requests to ClassCharts API
- `freezegun`: For time freezing in tests

## Continuous Integration with GitHub Actions

This project is configured with GitHub Actions to automatically run tests on each push and pull request.

### Setting Up GitHub Actions

1. The tests will run automatically when you push to GitHub, using the workflow defined in `.github/workflows/test.yml`.

2. To enable GitHub Actions in your repository:
   - Go to your GitHub repository
   - Navigate to "Settings" > "Actions" > "General"
   - Ensure "Allow all actions and reusable workflows" is selected

3. To view test results:
   - Go to the "Actions" tab in your GitHub repository
   - Click on the latest workflow run to see test results

### Automated Deployment (Optional)

A deployment workflow is also included in `.github/workflows/sam-deploy.yml` that can automatically deploy your application to AWS.

To set up automated deployment:

1. Add these secrets to your GitHub repository (in Settings > Secrets and variables > Actions):
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

2. Make sure your AWS credentials have permission to:
   - Create/update CloudFormation stacks
   - Create/update Lambda functions
   - Create/update S3 buckets
   - Create/read Secrets Manager secrets

3. The deployment will trigger automatically on pushes to your main branch that change code files.

4. You can also manually trigger a deployment:
   - Go to the "Actions" tab
   - Select "Deploy with SAM" workflow
   - Click "Run workflow"

5. The GitHub Actions workflow is configured to deploy with the stack name `classcharts-calendar-prod` by default.
