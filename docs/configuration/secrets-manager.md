# AWS Secrets Manager Configuration

The ClassCharts Calendar Sync application uses AWS Secrets Manager to securely store ClassCharts credentials. This keeps sensitive information like passwords out of your code and configuration files.

## Secret Format

The application expects secrets to be stored in JSON format with specific fields.

### For Multiple Students (Recommended)

```json
{
  "email": "your-classcharts-email@example.com",
  "password": "your-classcharts-password",
  "student_ids": [1234562, 7654321]
}
```

### For a Single Student (Legacy Format)

```json
{
  "email": "your-classcharts-email@example.com",
  "password": "your-classcharts-password",
  "student_id": 1234562
}
```

!!! note
    The legacy format with `student_id` is supported for backward compatibility. New deployments should use the `student_ids` array format.

## Creating the Secret

You can create the secret using the AWS CLI:

```bash
aws secretsmanager create-secret \
    --name classcharts/credentials \
    --secret-string '{
      "email":"your-email@example.com",
      "password":"your-password",
      "student_ids":[1234562, 7654321]
    }' \
    --region eu-west-2
```

To use a specific profile:

```bash
aws secretsmanager create-secret \
    --profile your-aws-profile \
    --name classcharts/credentials \
    --secret-string '{
      "email":"your-email@example.com",
      "password":"your-password",
      "student_ids":[1234562]
    }' \
    --region eu-west-2
```

## Secret Location

The Lambda function accesses the secret using the name specified in the `SECRET_NAME` environment variable. By default, this is `classcharts/credentials`.

You can change the secret name by:

1. Updating the `SECRET_NAME` environment variable in the template
2. Using the `--parameter-overrides` flag during deployment

```bash
sam deploy --parameter-overrides SecretName=my/custom/secret/path
```

## IAM Permissions

The Lambda function requires permissions to read the secret from AWS Secrets Manager. The SAM template includes the necessary IAM policy:

```yaml
Policies:
  - Version: '2012-10-17'
    Statement:
      - Effect: Allow
        Action:
          - secretsmanager:GetSecretValue
        Resource: !Sub 'arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:${SecretName}*'
```

## Security Considerations

- Never commit your credentials to version control
- Use IAM policies to restrict access to the secret
- Consider enabling rotation for the secret (though this would require manual updates to ClassCharts credentials)
- When testing locally, use environment variables instead of creating development secrets