import bottle
from bottle import Bottle, run, request, response
import json
import requests
import threading
import time
from endpoints.er import er_treatment
from endpoints.nursing import nursing
from endpoints.surgery import surgery
from endpoints.replan import replan
from endpoints.patient import patient, assign_diagnosis
from endpoints.resources import resources_status
from endpoints.releaseResources import release_resources
from endpoints.intake import intake
from endpoints.releasing import releasing
from utils import are_resources_available, patients
from redis import Redis
from rq import Queue, Connection, Worker
from concurrent.futures import ThreadPoolExecutor
import json
import threading
import numpy as np

# Create ThreadPoolExecutors to manage worker threads with different max workers
er_executor = ThreadPoolExecutor(max_workers=3)# Example: 3 workers for ER room
intake_executor = ThreadPoolExecutor(max_workers=4) 
surgery_executor = ThreadPoolExecutor(max_workers=5)
nursingA_executor = ThreadPoolExecutor(max_workers=30)
nursingB_executor = ThreadPoolExecutor(max_workers=40)

@bottle.route('/add-job',method='GET')
def add_job():
    try:
        patient_id = request.query.patient_id
        patient_status = request.query.patient_status
        resource_type = request.query.resource_type
        callback_url = bottle.request.headers['CPEE-CALLBACK']
        print(f"CallBack-ID: {callback_url}")
        if not patient_status:
          response.status = 400
          return json.dumps({'error': str(e)})

        print(patient_id, patient_status, resource_type)
        if resource_type == 'er':
            print(er_treatment)
            er_executor.submit(er_treatment,patient_id,patient_status, callback_url)
        elif resource_type == 'intake':
            print(intake)
            intake_executor.submit(intake, patient_id, patient_status, callback_url)
        elif resource_type == 'surgery':
            surgery_executor.submit(surgery, patient_id, patient_status, callback_url)
        elif resource_type == 'nursing':
            if patient_status.startswith('A') or (patient_status.startswith('EM - ') and patient_status.split(' - ')[1].startswith('A')):
                nursingA_executor.submit(nursing, patient_id, patient_status, callback_url)
            elif patient_status.startswith('B') or (patient_status.startswith('EM - ') and patient_status.split(' - ')[1].startswith('B')):
                nursingB_executor.submit(nursing, patient_id, patient_status, callback_url)
        else:
          response.status = 400
          return json.dumps({'error': 'Invalid resource type'})
          
         # Immediate response indicating the request is accepted for async processing
        return bottle.HTTPResponse(
            json.dumps({'Ack.:': 'Response later'}),
            status=202,
            headers={'content-type': 'application/json', 'CPEE-CALLBACK': 'true'}
        )
    except Exception as e:
        response.status = 500
        return json.dumps({'error': str(e)})

#app.route('/er', method='GET', callback=er_treatment)
#app.route('/nursing', method='GET', callback=nursing)
#app.route('/surgery', method='GET', callback=surgery)
bottle.route('/replan', method='GET', callback=replan)
bottle.route('/patient', method='GET', callback=patient)
bottle.route('/resources', method='GET', callback=resources_status)
bottle.route('/releaseResources', method='GET', callback=release_resources)
#app.route('/intake', method='GET', callback=intake)
bottle.route('/releasing', method='GET', callback=releasing)
#app.route('/start', method='GET', callback=start)
if __name__ == '__main__':
    ipv6_address = '::'  # This listens on all IPv6 addresses
    port = 8080  # Port number

    # Run the Bottle server with IPv6 support
    bottle.run(host=ipv6_address, port=port)