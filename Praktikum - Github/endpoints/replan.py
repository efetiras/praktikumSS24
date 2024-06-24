from bottle import request, response
import json
import requests
from utils import enqueue, er_queue, intake_queue, nursing_queue_A, nursing_queue_B, surgery_queue


def replan():
    # Get 'patient_id' and 'patient_status' from the query parameters
    patient_id = request.query.patient_id
    patient_status = request.query.patient_status

    # Validate the status
    valid_statuses = {'A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'EM'}
    if patient_status not in valid_statuses and not patient_status.startswith('EM - '):
        response.status = 400
        return json.dumps({'error': 'Invalid patient status'})

    # Ensure patient_id is provided
    if not patient_id:
        response.status = 400
        return json.dumps({'error': 'patient_id is required'})

    url = "https://cpee.org/flow/start/url/"
    payload = {
        "behavior": "fork_running",
        "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Efe_Tiras.dir/Test.xml",
        "init": json.dumps({
            "patientStatus": patient_status,
            "patientID": patient_id,
            "time": "0",
            "arrivalTime":"08:00",
            "valid_em_sub_statuses":"['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4']"
        })
    }
    try:
        post_response = requests.post(url, data=payload)
        post_response.raise_for_status()
        instance_number = post_response.json().get('CPEE-INSTANCE', 'N/A')
        print(f'A CPEE instance with number {instance_number} has been created.')
    except requests.exceptions.HTTPError as http_err:
        response.status = post_response.status_code
        return json.dumps({'error': f'HTTP error occurred: {http_err}', 'details': post_response.text})
    except requests.exceptions.RequestException as e:
        response.status = 500
        return json.dumps({'error': f'Request error occurred: {e}'})

    # Prepare the response dictionary
    response_data = {
        'patient_id': patient_id,
        'patient_status': patient_status,
        'CPEE-INSTANCE': instance_number
    }
    # Set the response content type to application/json
    response.content_type = 'application/json'
    return json.dumps(response_data)