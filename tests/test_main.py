import json
import os
import pytest
import boto3
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime
from freezegun import freeze_time
import responses
# Use the decorator-based approach for moto
from moto.core.decorator import mock_aws

# Import the module we want to test
import main

# We're now using the conftest.py fixture for credentials

@pytest.fixture
def secret_data():
    return {
        "email": "test@example.com",
        "password": "test-password",
        "student_id": 1234562
    }

@pytest.fixture
def setup_secretsmanager(secret_data):
    # Use the decorator-based approach
    with mock_aws():
        # Create a secret in the mock SecretManager service
        import config
        secretsmanager = boto3.client('secretsmanager', region_name=config.AWS_REGION)
        secretsmanager.create_secret(
            Name=config.SECRET_NAME,
            SecretString=json.dumps(secret_data)
        )
        yield

@pytest.fixture
def classcharts_login_response():
    return {
        "meta": {
            "session_id": "test-session-id"
        }
    }

@pytest.fixture
def classcharts_pupils_response():
    return {
        "data": [
            {
                "id": 1234562,
                "name": "Ava Test"
            }
        ]
    }

@pytest.fixture
def classcharts_timetable_response():
    return {
        "meta": {
            "timetable_dates": ["2024-06-12"]
        }
    }

@pytest.fixture
def classcharts_lessons_response():
    return {
        "data": [
            {
                "teacher_name": "Mr Test Teacher",
                "lesson_id": 123456,
                "lesson_name": "8XTest1",
                "subject_name": "Test Subject",
                "is_alternative_lesson": False,
                "period_name": "1:1",
                "period_number": "1",
                "room_name": "T1",
                "date": "2024-06-12",
                "start_time": "2024-06-12T09:00:00+01:00",
                "end_time": "2024-06-12T09:55:00+01:00",
                "key": 123456789,
                "note_abstract": "",
                "note": "",
                "pupil_note_abstract": "",
                "pupil_note": "",
                "pupil_note_raw": ""
            },
            {
                "teacher_name": "Ms Citizenship",
                "lesson_id": 234567,
                "lesson_name": "8XCitizenship",
                "subject_name": "Citizenshi",
                "is_alternative_lesson": False,
                "period_name": "2:1",
                "period_number": "2",
                "room_name": "C1",
                "date": "2024-06-12",
                "start_time": "2024-06-12T10:00:00+01:00",
                "end_time": "2024-06-12T10:55:00+01:00",
                "key": 234567890,
                "note_abstract": "",
                "note": "",
                "pupil_note_abstract": "",
                "pupil_note": "",
                "pupil_note_raw": ""
            }
        ]
    }

@pytest.fixture
def setup_s3():
    # Use the decorator-based approach
    with mock_aws():
        # Create bucket
        import config
        s3 = boto3.client('s3', region_name=config.AWS_REGION)
        s3.create_bucket(
            Bucket=config.BUCKET_NAME,
            CreateBucketConfiguration={'LocationConstraint': config.AWS_REGION}
        )
        yield


@freeze_time("2024-06-12")
@responses.activate
def test_lambda_handler_success(setup_secretsmanager, setup_s3, 
                               classcharts_login_response,
                               classcharts_pupils_response,
                               classcharts_timetable_response,
                               classcharts_lessons_response):
    # Mock ClassCharts API responses
    import config
    base_url = config.CLASSCHARTS_BASE_URL
    
    # Mock login API
    responses.add(
        responses.POST,
        f"{base_url}login",
        json=classcharts_login_response,
        status=200
    )
    
    # Mock pupils API
    responses.add(
        responses.GET,
        "https://www.classcharts.com/apiv2parent/pupils",
        json=classcharts_pupils_response,
        status=200
    )
    
    # Mock timetable API
    responses.add(
        responses.GET,
        f"{base_url}timetable/1234562",
        json=classcharts_timetable_response,
        status=200
    )
    
    # Mock timetable date API
    responses.add(
        responses.GET,
        f"{base_url}timetable/1234562?date=2024-06-12",
        json=classcharts_lessons_response,
        status=200
    )
    
    # Call the Lambda handler
    response = main.lambda_handler({}, None)
    
    # Verify response
    assert response['statusCode'] == 200
    assert 'message' in json.loads(response['body'])
    assert json.loads(response['body'])['message'] == 'Calendar successfully updated'
    
    # Verify S3 upload
    import config
    s3 = boto3.client('s3', region_name=config.AWS_REGION)
    objects = s3.list_objects_v2(Bucket=config.BUCKET_NAME)
    assert objects['KeyCount'] == 1
    assert objects['Contents'][0]['Key'] == config.CALENDAR_FILENAME


@freeze_time("2024-06-12")
def test_get_secrets(setup_secretsmanager, secret_data):
    # Call the get_secrets function
    result = main.get_secrets()
    
    # Verify the result
    assert result == secret_data
    
    # Verify the secret name is correct
    import config
    assert config.SECRET_NAME.startswith('classcharts/')


@freeze_time("2024-06-12")
@responses.activate
def test_citizenshi_renamed_to_a2b(setup_secretsmanager, setup_s3,
                                 classcharts_login_response,
                                 classcharts_pupils_response,
                                 classcharts_timetable_response,
                                 classcharts_lessons_response):
    # Mock ClassCharts API responses
    import config
    base_url = config.CLASSCHARTS_BASE_URL
    
    # Mock login API
    responses.add(
        responses.POST,
        f"{base_url}login",
        json=classcharts_login_response,
        status=200
    )
    
    # Mock pupils API
    responses.add(
        responses.GET,
        "https://www.classcharts.com/apiv2parent/pupils",
        json=classcharts_pupils_response,
        status=200
    )
    
    # Mock timetable API
    responses.add(
        responses.GET,
        f"{base_url}timetable/1234562",
        json=classcharts_timetable_response,
        status=200
    )
    
    # Mock timetable date API
    responses.add(
        responses.GET,
        f"{base_url}timetable/1234562?date=2024-06-12",
        json=classcharts_lessons_response,
        status=200
    )
    
    # Track calls to print to verify subject renaming
    with patch('builtins.print') as mock_print:
        # Call the Lambda handler
        main.lambda_handler({}, None)
        
        # Check if the print function was called with the renamed subject
        mock_print.assert_any_call("Adding lesson: A2B - Ms Citizenship")


@freeze_time("2024-06-12")
@responses.activate
def test_lambda_handler_error_handling():
    # Call lambda_handler without any mocks to simulate errors
    response = main.lambda_handler({}, None)
    
    # Verify response shows error
    assert response['statusCode'] == 500
    assert 'message' in json.loads(response['body'])
    assert 'Error updating calendar' in json.loads(response['body'])['message']