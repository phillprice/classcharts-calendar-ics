from datetime import datetime
import json
import os
import boto3
import requests
from ics import Calendar, Event

# Import config settings
import config

def get_secrets():
    """Retrieve secrets from AWS Secrets Manager or use local fallback for testing"""
    # For local testing, use environment variable to enable local mode
    if os.environ.get('LOCAL_TESTING', '').lower() == 'true':
        print("Using local test secrets instead of AWS Secrets Manager")
        # Return mock secrets for local testing
        return {
            'email': os.environ.get('TEST_EMAIL', 'test@example.com'),
            'password': os.environ.get('TEST_PASSWORD', 'test_password'),
            'student_ids': [os.environ.get('TEST_STUDENT_ID', '12345')]
        }
    
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
        print("If running locally, set LOCAL_TESTING=true environment variable")
        raise e

def generate_calendar_for_student(student_id, auth_headers):
    """Generate calendar for a single student
    
    Args:
        student_id: The ClassCharts student ID
        auth_headers: Headers containing the authentication token
        
    Returns:
        tuple: (Calendar object, Student name)
    """
    try:
        # Get student details - use the students API response data since pupil endpoint is failing
        student_response = requests.get(
            f"{config.CLASSCHARTS_BASE_URL}pupils",
            headers=auth_headers
        )
        print(f"Student details status: {student_response.status_code}")
        student_details = student_response.json()
        # Find the student with matching ID in the pupils list
        student_name = f"student-{student_id}"
        for student in student_details.get('data', []):
            if student.get('id') == student_id:
                student_name = student.get('name')
                break
        print(f"Got student name: {student_name}")
        
        # Get timetable
        print(f"Fetching timetable for student {student_id}")
        tt = requests.get(f"{config.CLASSCHARTS_BASE_URL}timetable/{student_id}", headers=auth_headers)
        print(f"Timetable response status: {tt.status_code}")
        print(f"Timetable response content: {tt.text[:100]}...")
        
        # Try to parse the timetable response
        try:
            dates = tt.json()
            print(f"Parsed timetable JSON successfully")
        except json.JSONDecodeError as e:
            print(f"Error parsing timetable JSON: {e}")
            print(f"First 100 characters: {repr(tt.text[:100])}")
            # Create empty calendar if we can't parse the timetable
            return Calendar(), student_name
        
        c = Calendar()
        
        # Check if timetable dates exist in the response
        if not dates.get('meta', {}).get('timetable_dates'):
            print(f"No timetable_dates found in response. Response structure: {json.dumps(dates)[:200]}...")
            return c, student_name
        
        # Process each timetable date
        for date in dates['meta']['timetable_dates']:
            print(f"Processing date: {date} for student {student_name}")
            day_response = requests.get(
                f"{config.CLASSCHARTS_BASE_URL}timetable/{student_id}?date={date}", 
                headers=auth_headers
            )
            print(f"Day response status for {date}: {day_response.status_code}")
            
            # Try to parse the day response
            try:
                day_data = day_response.json()
            except json.JSONDecodeError as e:
                print(f"Error parsing day JSON for {date}: {e}")
                print(f"First 100 characters: {repr(day_response.text[:100])}")
                continue  # Skip this day
            
            # Make sure data exists and is a list
            if not day_data.get('data') or not isinstance(day_data['data'], list):
                print(f"No lesson data found for {date}")
                continue
                
            for lesson in day_data['data']:
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
    except Exception as e:
        print(f"Error in generate_calendar_for_student: {e}")
        # Return empty calendar on error
        return Calendar(), f"student-{student_id}"

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
        print(f"Students API status code: {students_response.status_code}")
        print(f"Students API response headers: {students_response.headers}")
        print(f"Found students raw response: {students_response.text}")
        
        # Check if response is valid JSON
        try:
            students_data = students_response.json()
            print(f"Successfully parsed students JSON: {json.dumps(students_data)[:200]}...")
        except json.JSONDecodeError as e:
            print(f"Error parsing students JSON: {e}")
            print(f"First 100 characters of response: {repr(students_response.text[:100])}")
            # Continue with student_ids from secrets instead of API response
        
        # Process students API response or use student_ids from secrets
        students = []
        try:
            students_data = students_response.json()
            if 'data' in students_data and isinstance(students_data['data'], list):
                students = students_data['data']
                print(f"Successfully parsed {len(students)} students from API")
        except json.JSONDecodeError as e:
            print(f"Using student_ids from secrets instead of API response due to JSON error: {e}")
            
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
            
            # Upload to S3 (with error handling for local testing)
            try:
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
            except Exception as e:
                print(f"Failed to upload {tmp_file} to {config.BUCKET_NAME}/{filename}: {e}")
                # For local testing, we can still return the local file path
                if os.environ.get('LOCAL_TESTING', '').lower() == 'true':
                    print(f"Local calendar file created at {tmp_file}")
                    s3_urls.append({
                        'student_id': student_id,
                        'student_name': student_name,
                        'calendar_local_path': tmp_file
                    })
                else:
                    # Re-raise the exception if not in local testing mode
                    raise e
        
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