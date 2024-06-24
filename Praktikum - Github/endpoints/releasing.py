from bottle import request, response
import json
import requests
from datetime import datetime, timedelta
from utils import patients, handle_queue, er_queue, intake_queue, nursing_queue_A, nursing_queue_B, surgery_queue

def releasing():
    patient_id = request.query.patient_id
    patient_status = request.query.patient_status
    arrival_time = request.query.arrival_time
    time = request.query.time
    # Validate patient_id and patient_status
    if not patient_id:
        response.status = 400
        return json.dumps({'error': 'patient_id is required'})

    if not patient_status:
        response.status = 400
        return json.dumps({'error': 'patient_status is required'})

    valid_statuses = {'A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'EM'}
    if patient_status not in valid_statuses and not patient_status.startswith('EM - '):
        response.status = 400
        return json.dumps({'error': 'Invalid patient status'})

    # Parse arrival_time and time_spent
    try:
        arrival_time_obj = datetime.strptime(arrival_time, '%H:%M')
    except ValueError as e:
        response.status = 400
        return json.dumps({'error': f'Invalid arrival_time format: {e}'})

    try:
        time_spent_minutes = float(time)
        release_time_obj = arrival_time_obj + timedelta(minutes=time_spent_minutes)
        release_time = release_time_obj.strftime('%H:%M')
    except ValueError as e:
        response.status = 400
        return json.dumps({'error': f'Invalid time format: {e}'})

    # Handle the queue for the specific resource
    if patient_status in {'A1', 'A2', 'A3', 'A4'} or patient_status.startswith('EM - A'):
        next_patient_id, next_patient_status = handle_queue(nursing_queue_A)
    elif patient_status in {'B1', 'B2', 'B3', 'B4'} or patient_status.startswith('EM - B'):
        next_patient_id, next_patient_status = handle_queue(nursing_queue_B)
    elif patient_status == 'ER' or patient_status.startswith('EM'):
        next_patient_id, next_patient_status = handle_queue(er_queue)
    else:
        next_patient_id, next_patient_status = None, None

    if patient_id in patients:
        del patients[patient_id]

    # If there's a next patient in the queue, start a new instance for them
    if next_patient_id and next_patient_status:
        url = "https://cpee.org/flow/start/url/"
        payload = {
        "behavior": "fork_running",
        "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Efe_Tiras.dir/Test.xml",
        "init": json.dumps({
            "patientStatus": next_patient_status,
            "patientID": next_patient_id,
            "time": "0",
            "arrivalTime":"08:00",
            "valid_em_sub_statuses":"['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4']"
        })
    }

        try:
            post_response = requests.post(url, data=payload)
            post_response.raise_for_status()
            instance_number = post_response.json().get('CPEE-INSTANCE', 'N/A')
        except requests.exceptions.HTTPError as http_err:
            response.status = post_response.status_code
            return json.dumps({'error': f'HTTP error occurred: {http_err}', 'details': post_response.text})
        except requests.exceptions.RequestException as e:
            response.status = 500
            return json.dumps({'error': f'Request error occurred: {e}'})
    else:
        instance_number = None

    response_data = {
        'message': f'Patient {patient_id} with status {patient_status} is released',
        'next_patient_id': next_patient_id,
        'next_patient_status': next_patient_status,
        'CPEE-INSTANCE': instance_number,
        'releaseTime': release_time
    }

    # Set the response content type to application/json
    response.content_type = 'application/json'
    return json.dumps(response_data)