import requests
from bottle import request, response
import json
from utils import get_operation_time, resources

def surgery(patient_id,patient_status,callback_url):
    print("entered surgery")
    # Extract the base status if the status is of the form 'EM - X'
    if patient_status.startswith('EM - '):
        base_status = patient_status.split(' - ')[1]
    else:
        base_status = patient_status

    # Validate the status
    valid_statuses = {'A2', 'A3', 'A4', 'B3', 'B4'}
    if base_status not in valid_statuses:
        response.status = 400
        return json.dumps({'error': 'Invalid patient status for surgery'})

    # Check if surgery resource is available
    if resources['operating_rooms_working_hours'] > 0:
        resources['operating_rooms_working_hours'] -= 1
    else:
        response.status = 400
        return json.dumps({'error': 'No surgery resources available'})

    # Calculate the surgery time
    surgery_time = get_operation_time(base_status)
    print(surgery_time)
    print(f"Surgery time for patient {patient_id} with status {patient_status}: {surgery_time} minutes")
    # Prepare the response dictionary
    response_data = {
        'patient_id': patient_id,
        'patient_status': patient_status,
        'surgery_time': surgery_time
    }

    headers = {
        'content-type': 'application/json',
        'CPEE-CALLBACK': 'true'
    }
    print('here 5')
    # Send the callback response as a JSON payload
    print(callback_url, headers, response_data)
    requests.put(callback_url, headers=headers, json=response_data)

    print(f"PUT request sent to callback_url: {callback_url}")