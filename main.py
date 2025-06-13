from datetime import datetime
import json
import os
import boto3
import requests
from ics import Calendar, Event

# Import config settings
import config

def get_secrets():
    """Retrieve secrets from AWS Secrets Manager"""
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=config.AWS_REGION
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=config.SECRET_NAME
        )
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise e

def lambda_handler(event, context):
    """Main Lambda function handler"""
    try:
        # Get secrets for ClassCharts login
        secrets = get_secrets()
        email = secrets.get('email')
        password = secrets.get('password')
        student_id = secrets.get('student_id')
        
        # Login to ClassCharts
        login = requests.post(
            f"{config.CLASSCHARTS_BASE_URL}login",
            data={
                'email': email,
                'password': password,
                '_method': 'POST',
                "recaptcha-token": "no-token-available"
            },
            headers={
                'User-Agent': config.CLASSCHARTS_USER_AGENT
            }
        )
        tokens = login.json()
        session = tokens['meta']['session_id']
        print(f"Logged in successfully with session: {session}")
        
        auth = {"Authorization": f"Basic {session}"}
        
        # Get student info
        students = requests.get(
            f"{config.CLASSCHARTS_BASE_URL}pupils",
            headers={"Authorization": f"Basic {session}"}
        )
        print(f"Students info: {students.text}")
        
        # Get timetable
        tt = requests.get(f"{config.CLASSCHARTS_BASE_URL}timetable/{student_id}", headers=auth)
        dates = tt.json()
        c = Calendar()
        
        # Process each timetable date
        for date in dates['meta']['timetable_dates']:
            print(f"Processing date: {date}")
            day = requests.get(f"{config.CLASSCHARTS_BASE_URL}timetable/{student_id}?date={date}", headers=auth)
            for lesson in day.json()['data']:
                # Apply subject name mappings
                if lesson["subject_name"] in config.SPECIAL_SUBJECT_MAPPINGS:
                    lesson["subject_name"] = config.SPECIAL_SUBJECT_MAPPINGS[lesson["subject_name"]]
                
                print(f"Adding lesson: {lesson['subject_name']} - {lesson['teacher_name']}")
                e = Event()
                e.name = f"{lesson['subject_name']} - {lesson['teacher_name']}"
                e.location = lesson["room_name"]
                e.begin = datetime.fromisoformat(lesson["start_time"])
                e.end = datetime.fromisoformat(lesson["end_time"])
                c.events.add(e)
        
        # Write calendar to tmp file
        tmp_file = f"{config.LAMBDA_TMP_DIR}/{config.CALENDAR_FILENAME}"
        with open(tmp_file, "w") as f:
            f.write(c.serialize())
        
        # Upload to S3
        s3 = boto3.client('s3')
        s3.upload_file(
            tmp_file, 
            config.BUCKET_NAME,
            config.CALENDAR_FILENAME,
            ExtraArgs={'ACL': 'public-read', 'ContentType': config.CALENDAR_CONTENT_TYPE}
        )
        
        # Get S3 URL for the calendar
        calendar_url = f'https://{config.BUCKET_NAME}.s3.amazonaws.com/{config.CALENDAR_FILENAME}'
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Calendar successfully updated',
                'url': calendar_url,
                'bucket': config.BUCKET_NAME
            })
        }
    
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error updating calendar: {str(e)}'
            })
        }

# Allow local testing
if __name__ == "__main__":
    lambda_handler({}, None)