# SAM Parameters

AWS SAM (Serverless Application Model) allows you to customize the deployment of the ClassCharts Calendar Sync application through parameters.

## Available Parameters

The following parameters can be customized during deployment:

| Parameter | Default | Description | Example Override |
|-----------|---------|-------------|------------------|
| `Environment` | `dev` | Environment name (dev, prod, etc.) | `prod` |
| `BucketName` | `classcharts-calendar` | S3 bucket base name | `my-school-calendar` |
| `CalendarFilenameTemplate` | `{student_id}.ics` | Format for calendar filenames | `{student_name}_{student_id}.ics` |
| `SecretName` | `classcharts/credentials` | Name of the secret in Secrets Manager | `my/classcharts/creds` |

## Parameter Details

### Environment

The `Environment` parameter specifies the deployment environment, such as "dev" or "prod". This is used in resource naming to prevent conflicts between different deployments.

Example:
```bash
sam deploy --parameter-overrides Environment=prod
```

### BucketName

The `BucketName` parameter sets the base name for the S3 bucket where calendar files are stored. The actual bucket name will be:

```
{BucketName}-{Environment}-{AWS::AccountId}
```

Example:
```bash
sam deploy --parameter-overrides BucketName=school-calendars
```

This would create a bucket named `school-calendars-dev-123456789012` for a dev environment.

### CalendarFilenameTemplate

The `CalendarFilenameTemplate` parameter specifies the naming pattern for calendar files. It supports the following placeholders:

- `{student_id}` - The ClassCharts student ID
- `{student_name}` - The student's name with spaces replaced by underscores

Example:
```bash
sam deploy --parameter-overrides CalendarFilenameTemplate="{student_name}_{student_id}.ics"
```

This would create filenames like `john_smith_1234567.ics`.

### SecretName

The `SecretName` parameter specifies the name of the secret in AWS Secrets Manager where ClassCharts credentials are stored.

Example:
```bash
sam deploy --parameter-overrides SecretName="school/classcharts/credentials"
```

## Using Parameter Overrides

### Single Parameter Override

```bash
sam deploy --parameter-overrides Environment=prod
```

### Multiple Parameter Overrides

```bash
sam deploy --parameter-overrides \
  Environment=prod \
  BucketName=school-calendars \
  CalendarFilenameTemplate="{student_name}.ics"
```

### With Specific Profile

```bash
sam deploy --profile school-admin --parameter-overrides Environment=prod
```

### Using a Configuration File

You can also create a `samconfig.toml` file in your project directory to specify default parameter values:

```toml
version = 0.1
[default]
[default.deploy]
[default.deploy.parameters]
stack_name = "classcharts-calendar"
s3_bucket = "aws-sam-cli-managed-default-samclisourcebucket-1234567890ab"
s3_prefix = "classcharts-calendar"
region = "eu-west-2"
capabilities = "CAPABILITY_IAM"
parameter_overrides = "Environment=dev BucketName=school-calendar"
confirm_changeset = true
```