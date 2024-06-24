from bottle import request, response
import json
from utils import are_resources_available

def resources_status():
    # Check if resources are available
    resources_available = are_resources_available()

    # Prepare the response dictionary
    response_data = {
        'resources_available': resources_available
    }

    # Set the response content type to application/json
    response.content_type = 'application/json'
    
    # Return the response as JSON
    return json.dumps(response_data)