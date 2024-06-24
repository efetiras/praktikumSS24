from bottle import request, response
import json
import uuid
import numpy as np
from utils import get_operation_time, get_nursing_time, resources, patients, em_probabilities_A, em_probabilities_B

def assign_diagnosis(status):
    if status == 'A':
        diagnoses = list(em_probabilities_A.keys())
        probabilities = list(em_probabilities_A.values())
    elif status == 'B':
        diagnoses = list(em_probabilities_B.keys())
        probabilities = list(em_probabilities_B.values())
    else:
        return status
    return np.random.choice(diagnoses, p=probabilities)


def patient():
    # Get 'id' and 'status' from query parameters
    id = request.query.patient_id
    status = request.query.patient_status

    # Validate the status
    valid_statuses = {
        'A', 'A1', 'A2', 'A3', 'A4',
        'B', 'B1', 'B2', 'B3', 'B4',
        'EM', 'EM - A1', 'EM - A2', 'EM - A3', 'EM - A4',
        'EM - B1', 'EM - B2', 'EM - B3', 'EM - B4'
    }
    if status not in valid_statuses:
        status = 'unknown'

    # Handle EM status

    if status == 'EM':
        base_status = np.random.choice(['A', 'B'], p=[0.5, 0.5])
        diagnosis = assign_diagnosis(base_status)
        status = f'EM - {diagnosis}'
    elif status == 'A' or status == 'B':
        status = assign_diagnosis(status)
    elif status.startswith('EM - '):
        # If it is already EM - A1, EM - A2, etc., keep the status unchanged
        pass
    else:
        # Assign diagnosis based on status
        status = assign_diagnosis(status)

    # Check if the given id exists in the patients dictionary
    if id in patients:
        existing_patient = True
        existing_status = patients[id]['status']

        # Update the patient's status if provided and valid
        if status != 'unknown':
            patients[id]['status'] = status
            patients[id]['operation_time'] = get_operation_time(status)
            patients[id]['nursing_time'] = get_nursing_time(status)
            patients[id]['total_time'] = patients[id]['operation_time'] + patients[id]['nursing_time']
    else:
        existing_patient = False
        existing_status = None

        # If id is not provided or does not exist, generate a new one
        if not id:
            id = str(uuid.uuid4())
        
        # Add new patient to the dictionary if status is valid
        if status != 'unknown':
            operation_time = get_operation_time(status)
            nursing_time = get_nursing_time(status)
            total_time = operation_time + nursing_time
            patients[id] = {
                'status': status,
                'operation_time': operation_time,
                'nursing_time': nursing_time,
                'total_time': total_time
            }

    # Print the current resource numbers
    print(f"Resources: {json.dumps(resources, indent=2)}")

    # Prepare the response dictionary
    response_data = {
        'id': id,
        'status': status,
        'existing_patient': existing_patient,
        'existing_status': existing_status,
        'operation_time': patients[id]['operation_time'] if id in patients else 0,
        'nursing_time': patients[id]['nursing_time'] if id in patients else 0,
        'total_time': patients[id]['total_time'] if id in patients else 0
    }

    # Set the response content type to application/json
    response.content_type = 'application/json'

    # Return the response as JSON
    return json.dumps(response_data)