from bottle import request, response
import json
import requests
import numpy as np
import random
from utils import assign_em_status, resources, patients

def er_treatment(patient_id,patient_status,callback_url):
    print("works ER")
    if resources['emergency_personnel'] > 0:
        resources['emergency_personnel'] -= 1
        treatment_time = np.random.normal(2 * 60, 0.5 * 60)  # ER treatment time in minutes
        queueER = False
    else:
        
        treatment_time = 0
        queueER = True

    # Determine if treatment should be false for specific statuses
    treatment_status = patient_status
    print(f"Determined treatment_status: {treatment_status}")
    if treatment_status in {'A1', 'B1', 'B2','EM', 'EM - A1', 'EM - B1','EM - B2'}:
        treatment = False
    else:
        treatment = True

    # 50/50 probability to set phantom to True or assign EM substatus
    print('here 1')
    if random.choice([True, False]):
        phantom = True

    else:
        phantom = False


    print('here 2')
    response_data = {
        'phantom': phantom,
        'resource_emergency': resources['emergency_personnel'],
        'treatment_time': treatment_time,
        'patient_status': patients[patient_id]['status'] if patient_id in patients else 'unknown',
        'treatment': treatment,
        'queueER': queueER
    }
    
    print('here 3')
    # response.content_type = 'application/json'
    # Immediate response indicating the request is accepted for async processing
    # Prepare the headers
    headers = {
        'content-type': 'application/json',
        'CPEE-CALLBACK': 'true'
    }
    print('here 4')
    # Send the callback response as a JSON payload
    print(callback_url, headers, response_data)
    requests.put(callback_url, headers=headers, json=response_data)
    
    print(f"PUT request sent to callback_url: {callback_url}")