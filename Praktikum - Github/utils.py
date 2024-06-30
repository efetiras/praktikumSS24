import numpy as np
import heapq
from collections import deque

# Priority queues for each resource
er_queue = []
intake_queue = []
nursing_queue_A = []
nursing_queue_B = []
surgery_queue = []

# Function to determine priority
def get_priority(patient_status):
    if patient_status == 'EM' or patient_status.startswith('EM - '):
        return 0
    return 1


# Example resource data
resources = {
    'intake': 4,
    'operating_rooms_working_hours': 5,
    'operating_rooms_after_hours': 1,
    'nursing_ward_A': 30,
    'nursing_ward_B': 40,
    'emergency_personnel': 9
}
resource_mapping = {
    'er': 'emergency_personnel',
    'intake': 'intake',
    'surgery': 'operating_rooms_working_hours',  # Assuming we're checking for working hours
    'nursingA': 'nursing_ward_A',
    'nursingB': 'nursing_ward_B'
}
# In-memory dictionary to store patient data
patients = {}

em_probabilities_A = {
    'A1': 1/2,
    'A2': 1/4,
    'A3': 1/8,
    'A4': 1/8
}

em_probabilities_B = {
    'B1': 1/2,
    'B2': 1/4,
    'B3': 1/8,
    'B4': 1/8
}
def enqueue(queue, patient_id, patient_status):
    priority = get_priority(patient_status)
    heapq.heappush(queue, (priority, patient_id, patient_status))

def dequeue(queue):
    if queue:
        return heapq.heappop(queue)
    return None

def handle_queue(queue):
    # Check if there's a patient in the queue
    next_patient = dequeue(queue)
    if next_patient:
        _, patient_id, patient_status = next_patient
        return patient_id, patient_status
    return None, None


def assign_em_status():
    type_choice = np.random.choice(['A', 'B'], p=[0.5, 0.5])  # Assuming equal probability to be A or B
    
    if type_choice == 'A':
        statuses = list(em_probabilities_A.keys())
        probabilities = list(em_probabilities_A.values())
    else:
        statuses = list(em_probabilities_B.keys())
        probabilities = list(em_probabilities_B.values())
    
    return np.random.choice(statuses, p=probabilities)

def get_operation_time(patient_status):
    operation_times = {
        'A2': lambda: np.random.normal(1 * 60, 0.25 * 60),
        'A3': lambda: np.random.normal(2 * 60, 0.5 * 60),
        'A4': lambda: np.random.normal(4 * 60, 0.5 * 60),
        'B3': lambda: np.random.normal(4 * 60, 0.5 * 60),
        'B4': lambda: np.random.normal(4 * 60, 60)
    }
    return operation_times.get(patient_status, lambda: 0)()

def get_nursing_time(patient_status):
    nursing_times = {
        'A1': lambda: np.random.normal(4 * 60, 0.5 * 60),
        'A2': lambda: np.random.normal(8 * 60, 2 * 60),
        'A3': lambda: np.random.normal(16 * 60, 2 * 60),
        'A4': lambda: np.random.normal(16 * 60, 2 * 60),
        'B1': lambda: np.random.normal(8 * 60, 2 * 60),
        'B2': lambda: np.random.normal(16 * 60, 2 * 60),
        'B3': lambda: np.random.normal(16 * 60, 4 * 60),
        'B4': lambda: np.random.normal(16 * 60, 4 * 60)
    }
    return nursing_times.get(patient_status, lambda: 0)()

def get_complication(patient_status):
    complications = {
        'A1': 0.01,
        'A2': 0.01,
        'A3': 0.02,
        'A4': 0.02,
        'B1': 0.001,
        'B2': 0.01,
        'B3': 0.02,
        'B4': 0.02
    }
    probability = complications.get(patient_status, 0)
    return np.random.rand() < probability

def are_resources_available():
    return all(value > 0 for value in resources.values())

def resource_available(resource_type):
    # Get the corresponding key from the resource_mapping dictionary
    resource_key = resource_mapping.get(resource_type)
    # Check if the resource_key is valid and exists in the resources dictionary
    if resource_key and resource_key in resources:
        # Check if the resource is available
        return resources[resource_key] > 0
    # Return False if the resource_key is not valid or does not exist in the resources dictionary
    return False
