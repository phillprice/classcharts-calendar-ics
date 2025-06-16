# Environment Variables

The ClassCharts Calendar Sync application uses environment variables for configuration. These variables can be set in different ways depending on whether you're running in production or local development environments.

## Production Environment Variables

These variables are set during deployment and used in the Lambda environment:

| Variable | Default | Description | Required |
|----------|---------|-------------|:--------:|
| `AWS_REGION` | `eu-west-2` | AWS region for operations | Auto-set by Lambda |
| `BUCKET_NAME` | `classcharts-calendar-{account-id}` | S3 bucket name for calendars | Yes |
| `CALENDAR_FILENAME_TEMPLATE` | `{student_id}.ics` | Template for calendar filenames | No |
| `SECRET_NAME` | `classcharts/credentials` | Name for credentials in Secrets Manager | Yes |

## Local Testing Environment Variables

These variables are for local development and testing without AWS resources:

| Variable | Default | Description | Required for Local Testing |
|----------|---------|-------------|:-------------------------:|
| `LOCAL_TESTING` | `false` | Set to `true` to enable local testing mode | Yes |
| `TEST_EMAIL` | None | ClassCharts parent account email | Yes |
| `TEST_PASSWORD` | None | ClassCharts parent account password | Yes |
| `TEST_STUDENT_ID` | None | ClassCharts student ID | Yes |

## Setting Environment Variables

### In AWS Lambda (Production)

Environment variables in production are set via the SAM template:

```yaml
# From template.yaml
Environment:
  Variables:
    BUCKET_NAME: !Ref ClasschartsCalendarBucket
    CALENDAR_FILENAME_TEMPLATE: !Ref CalendarFilenameTemplate
    SECRET_NAME: !Ref SecretName
    AWS_ACCOUNT_ID: !Ref AWS::AccountId
```

### For Local Testing

#### Linux/macOS:

```bash
export LOCAL_TESTING=true
export TEST_EMAIL="your-classcharts-email@example.com"
export TEST_PASSWORD="your-classcharts-password"
export TEST_STUDENT_ID="your-student-id"
```

#### Windows (CMD):

```cmd
set LOCAL_TESTING=true
set TEST_EMAIL=your-classcharts-email@example.com
set TEST_PASSWORD=your-classcharts-password
set TEST_STUDENT_ID=your-student-id
```

#### Windows (PowerShell):

```powershell
$env:LOCAL_TESTING="true"
$env:TEST_EMAIL="your-classcharts-email@example.com"
$env:TEST_PASSWORD="your-classcharts-password"
$env:TEST_STUDENT_ID="your-student-id"
```

## Environment Variable Templates

### Filename Template

The `CALENDAR_FILENAME_TEMPLATE` variable supports placeholders:

- `{student_id}` - The numeric student ID from ClassCharts
- `{student_name}` - The student's name, with spaces replaced by underscores

Example templates:
```
{student_id}.ics                  # 7419922.ics
{student_name}_{student_id}.ics   # john_smith_7419922.ics
calendar_{student_name}.ics       # calendar_john_smith.ics
```

## Notes

- `AWS_REGION` is automatically set by AWS Lambda in production. The environment variable is only used for local development.
- In local testing mode, calendar files are created in the local `/tmp` directory instead of being uploaded to S3.
- When `LOCAL_TESTING=true`, AWS Secrets Manager is not used, and credentials are read from environment variables instead.