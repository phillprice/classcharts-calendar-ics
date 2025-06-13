"""
ClassCharts Calendar Configuration Settings

This file contains all configuration settings for the ClassCharts Calendar application.
Environment variables take precedence over the default values defined here.
"""

import os

# AWS Region
AWS_REGION = os.environ.get('AWS_REGION', 'eu-west-2')

# S3 Configuration
# The BUCKET_NAME is set by the SAM template and already includes the account ID
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'classcharts-calendar-local')

CALENDAR_FILENAME = os.environ.get('CALENDAR_FILENAME', 'ical.ics')
CALENDAR_CONTENT_TYPE = 'text/calendar'

# AWS Secrets Manager Configuration
SECRET_NAME = os.environ.get('SECRET_NAME', 'classcharts/credentials')

# ClassCharts API Configuration
CLASSCHARTS_BASE_URL = os.environ.get('CLASSCHARTS_BASE_URL', 'https://www.classcharts.com/apiv2parent/')
CLASSCHARTS_USER_AGENT = os.environ.get(
    'CLASSCHARTS_USER_AGENT', 
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
)

# Calendar Processing
SPECIAL_SUBJECT_MAPPINGS = {
    'Citizenshi': 'A2B'
}

# Lambda Configuration
LAMBDA_TMP_DIR = '/tmp'