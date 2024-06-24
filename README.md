# praktikumSS24
TUM Praktikum 

#running the simulation

Praktikum - Github file should be downloaded. When the file "appTest2.py" is run through with the command 'python3 appTest2.py', the server will start. 

In the process hub my updated xml file is in Test.xml (newest version). 

If you want to create new instances to test the simulation this is how I do it with my inital parameters which should be there in the beginning. 
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
Data Flow: 

Patient Admission:

Checks if the patient has an ID; if not, generates a unique one.
Verifies resource availability.

Resource Availability:

If resources are unavailable, the patient is rescheduled to 8 AM the next day.
If resources are available, checks if the patient is an Emergency.

Emergency Handling:

If the patient is Emergency, they proceed to the emergency task.
Emergency time is calculated based on diagnosis.
Phantom and Treatment values are returned.

Non-Emergency Handling:

Non-emergency patients go to intake.
Phantom and Treatment values are returned.

Async Resource Tasks:

Tasks such as nursing, surgery, emergency, intake are handled asynchronously.
If no resource is available, the patient is added to the respective queue.

Release Time Calculation:

For each patient how many minutes passed in the simulation is calculated. Adding this to the arrival time gives us the release time.

Releasing Task:

If there are patients in the queue, new instances are created with their ID and status.
Time and diagnosis probabilities are taken from the sheet.

