from bottle import request, response
import json
from utils import resources, patients

def release_resources():
    resource_selection = request.query.resource_selection
    patient_status = request.query.patient_status

    # Validate the resource selection
    valid_resource_selections = {'er', 'intake', 'surgery', 'nursing'}
    if resource_selection not in valid_resource_selections:
        response.status = 400
        return json.dumps({'error': 'Invalid resource selection'})

    # Release the specified resource
    if resource_selection == 'er':
        resources['emergency_personnel'] += 1
        current_value = resources['emergency_personnel']

    elif resource_selection == 'intake':
        resources['intake'] += 1
        current_value = resources['intake']
    elif resource_selection == 'surgery':
        resources['operating_rooms_working_hours'] += 1
        current_value = resources['operating_rooms_working_hours']
    elif resource_selection == 'nursing':
        if patient_status.startswith('EM - '):
            base_status = patient_status.split(' - ')[1]
        else:
            base_status = patient_status

        if base_status.startswith('A'):
            resources['nursing_ward_A'] += 1
            current_value = resources['nursing_ward_A']
        elif base_status.startswith('B'):
            resources['nursing_ward_B'] += 1
            current_value = resources['nursing_ward_B']
        else:
            response.status = 400
            return json.dumps({'error': 'Invalid patient status for nursing resource'})
    else:
        response.status = 400
        return json.dumps({'error': 'Unknown resource selection'})

    # Prepare the response dictionary
    response_data = {
        'resource_selection': resource_selection,
        'patient_status': patient_status,
        'message': f'{resource_selection} resource released successfully for patient status {patient_status}',
        'current_value': current_value
    }

    # Set the response content type to application/json
    response.content_type = 'application/json'
    return json.dumps(response_data)