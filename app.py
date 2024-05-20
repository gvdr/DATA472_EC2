from flask import Flask, jsonify, request
from datetime import datetime
import requests
from datetime import datetime, timedelta
from flask import Flask
application = Flask(__name__)

url = 'https://apis.ecan.govt.nz/waterdata/observations/graphql'
API_Key = 'ec9a031b4a674316b1bb21d9479f4595'
headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': API_Key
}

location_data = {
    'query': '''
        query {
            getObservations {
                locationId
                name
                nztmx
		        nztmy
            }
        }
    '''
}
defaultdate = datetime.now() - timedelta(days=2)

# Define the query to get observations for a specific time period
def get_data_date(date_str = defaultdate.strftime('%Y-%m-%d')):
    
    # Define the query to get observations for a specific location and time period
    observations_data = {
        'query': f'''
            query {{
                getObservations {{
                    locationId
                    observations(filter: {{ start: "{date_str} 00:00:00", end: "{date_str} 23:59:59" }}) {{
                        qualityCode
                        timestamp
                        value
                    }}
                }}
            }}
        '''
    }  
     
    response_observation = requests.post(url, headers=headers, json=observations_data)
    response_observation_data = response_observation.json()
    observations = response_observation_data.get('data', {}).get('getObservations', [])
    # Initialize a list to store the observation records with location_id, quality_code, timestamp, and value
    observation_records = []
    for observation in observations:
        # Check if there are observations for the location, and only process if there are observations
        if observation['observations']:
            location_id = observation['locationId']
            observation_data = observation['observations']
            for data in observation_data:
                record = {}  # Change record from tuple to dictionary
                if data['value'] or data['qualityCode']:
                    record['locationId'] = location_id
                    record['qualityCode'] = data['qualityCode']
                    record['timestamp'] = data['timestamp']
                    record['value'] = data['value']
                    observation_records.append(record)
    return observation_records



# New route to handle requests with dataset name and date
@application.route('/')
def get_data():
    dataset = get_data_date()
    
    return jsonify(dataset)

# New route to handle requests with location
@application.route('/location')
def get_location():
    # Retrieve data for all locations
    response_location = requests.post(url, headers=headers, json=location_data)
    response_location_data = response_location.json()
    locations = response_location_data.get('data', {}).get('getObservations', [])
    return jsonify(locations)

# New route to handle requests with dataset name and date
@application.route('/data/<date_str>')
def get_data_by_date(date_str):
    # Validate date format
    try:
        date = datetime.strptime(date_str, '%Y%m%d')
    except ValueError:
        return "Invalid date format. Please use YYYYMMDD.", 400

    # Retrieve data for the given date
    dataset = get_data_date(date.strftime('%Y-%m-%d'))
    
    if dataset:
        return jsonify(dataset)        
    else:
        return "Dataset not found.", 404

if __name__ == "__main__":
    
    application.run(host="0.0.0.0", port=8000)
