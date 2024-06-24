import requests
from bottle import request, response
import json
from utils import get_nursing_time, get_complication, resources

def nursing(patient_id,patient_status,callback_url):

    # Extract the base status if the status is of the form 'EM - X'
    if patient_status.startswith('EM - '):
        base_status = patient_status.split(' - ')[1]
    else:
        base_status = patient_status

    print(f"Received base_status: {base_status}")

    # Validate the status
    valid_statuses = {'A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4'}
    if base_status not in valid_statuses:
        response.status = 400
        return json.dumps({'error': 'Invalid patient status'})

    # Check if nursing resource is available
    if 'nursing_ward_A' in resources and 'nursing_ward_B' in resources:
        if base_status.startswith('A'):
            if resources['nursing_ward_A'] > 0:
                resources['nursing_ward_A'] -= 1
            else:
                response.status = 400
                return json.dumps({'error': 'No nursing resources available for type A'})
        elif base_status.startswith('B'):
            if resources['nursing_ward_B'] > 0:
                resources['nursing_ward_B'] -= 1
            else:
                response.status = 400
                return json.dumps({'error': 'No nursing resources available for type B'})
    else:
        response.status = 400
        return json.dumps({'error': 'Nursing resources not initialized'})

    # Calculate the nursing time
    nursing_time = get_nursing_time(base_status)

    # Determine if there are any complications
    complication = get_complication(base_status)

    # Prepare the response dictionary
    response_data = {
        'patient_id': patient_id,
        'patient_status': patient_status,
        'nursing_time': nursing_time,
        'complication': complication
    }

    # Set the response content type to application/json
    headers = {
        'content-type': 'application/json',
        'CPEE-CALLBACK': 'true'
    }
    print('here 4')
    # Send the callback response as a JSON payload
    print(callback_url, headers, response_data)
    requests.put(callback_url, headers=headers, json=response_data)

    print(f"PUT request sent to callback_url: {callback_url}")