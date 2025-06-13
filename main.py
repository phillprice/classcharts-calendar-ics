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

def generate_calendar_for_student(student_id, auth_headers):
    """Generate calendar for a single student
    
    Args:
        student_id: The ClassCharts student ID
        auth_headers: Headers containing the authentication token
        
    Returns:
        tuple: (Calendar object, Student name)
    """
    # Get student details
    student_details = requests.get(
        f"{config.CLASSCHARTS_BASE_URL}pupil/{student_id}",
        headers=auth_headers
    ).json()
    student_name = student_details.get('data', {}).get('name', f"student-{student_id}")
    
    # Get timetable
    tt = requests.get(f"{config.CLASSCHARTS_BASE_URL}timetable/{student_id}", headers=auth_headers)
    dates = tt.json()
    c = Calendar()
    
    # Process each timetable date
    for date in dates['meta']['timetable_dates']:
        print(f"Processing date: {date} for student {student_name}")
        day = requests.get(f"{config.CLASSCHARTS_BASE_URL}timetable/{student_id}?date={date}", headers=auth_headers)
        for lesson in day.json()['data']:
            # Apply subject name mappings
            if lesson["subject_name"] in config.SPECIAL_SUBJECT_MAPPINGS:
                lesson["subject_name"] = config.SPECIAL_SUBJECT_MAPPINGS[lesson["subject_name"]]
            
            print(f"Adding lesson for {student_name}: {lesson['subject_name']} - {lesson['teacher_name']}")
            e = Event()
            e.name = f"{lesson['subject_name']} - {lesson['teacher_name']}"
            e.location = lesson["room_name"]
            e.begin = datetime.fromisoformat(lesson["start_time"])
            e.end = datetime.fromisoformat(lesson["end_time"])
            c.events.add(e)
    
    return c, student_name

def lambda_handler(event, context):
    """Main Lambda function handler"""
    try:
        # Get secrets for ClassCharts login
        secrets = get_secrets()
        email = secrets.get('email')
        password = secrets.get('password')
        student_ids = secrets.get('student_ids', [])
        
        # If student_ids is not provided or empty, check for legacy student_id key
        if not student_ids and 'student_id' in secrets:
            student_ids = [secrets.get('student_id')]
        
        if not student_ids:
            raise ValueError("No student IDs found in secrets")
            
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
        
        auth_headers = {"Authorization": f"Basic {session}"}
        
        # Get student info
        students_response = requests.get(
            f"{config.CLASSCHARTS_BASE_URL}pupils",
            headers=auth_headers
        )
        print(f"Found students: {students_response.text}")
        
        # Create a calendar for each student
        s3_urls = []
        s3 = boto3.client('s3')
        
        for student_id in student_ids:
            calendar, student_name = generate_calendar_for_student(student_id, auth_headers)
            
            # Create filename for this student
            filename = config.CALENDAR_FILENAME_TEMPLATE.format(student_id=student_id, student_name=student_name.replace(' ', '_').lower())
            
            # Write calendar to tmp file
            tmp_file = f"{config.LAMBDA_TMP_DIR}/{filename}"
            with open(tmp_file, "w") as f:
                f.write(calendar.serialize())
            
            # Upload to S3
            s3.upload_file(
                tmp_file, 
                config.BUCKET_NAME,
                filename,
                ExtraArgs={'ACL': 'public-read', 'ContentType': config.CALENDAR_CONTENT_TYPE}
            )
            
            # Get S3 URL for the calendar
            calendar_url = f'https://{config.BUCKET_NAME}.s3.amazonaws.com/{filename}'
            s3_urls.append({
                'student_id': student_id,
                'student_name': student_name,
                'calendar_url': calendar_url
            })
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Calendars successfully updated',
                'calendars': s3_urls,
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