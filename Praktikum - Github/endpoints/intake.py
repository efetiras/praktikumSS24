import requests
from bottle import request, response
import json
import numpy as np
from utils import resources, patients

def intake(patient_id,patient_status,callback_url):

    if resources['intake'] > 0:
        resources['intake'] -= 1
        phantom = False
        intake_time = np.random.normal(1 * 60, 0.125 * 60)  # Intake time in minutes
    else:
        phantom = False
        intake_time = 0
    # Determine if treatment should be false for specific statuses
    treatment_status = patients[patient_id]['status'] if patient_id in patients else 'unknown'
    if treatment_status in {'A1', 'B1', 'B2'} or treatment_status.startswith('EM - ') and treatment_status.split(' - ')[1] in {'A1', 'B1', 'B2'}:
        treatment = False
    else:
        treatment = True

    response_data = {
        'phantom': phantom,
        'intakeNumber': resources['intake'],
        'intake_time': intake_time,
        'treatment': treatment
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