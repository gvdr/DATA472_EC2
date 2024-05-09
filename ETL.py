import requests
import json
import psycopg2
from datetime import datetime, timedelta
import os

url = 'https://apis.ecan.govt.nz/waterdata/observations/graphql'
API_Key = 'ec9a031b4a674316b1bb21d9479f4595'
headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': API_Key
}
GEO_TYPE = 2193
location_data = {
    'query': '''
        query {
            getObservations {
                locationId
                name
                nztmx
		        nztmy
                type
                unit
            }
        }
    '''
}
# Get yesterday's date
yesterday = datetime.now() - timedelta(days=1)
yesterday_str = yesterday.strftime("%Y-%m-%d")
# Define the start date and end date
start_date = datetime(datetime.now().year, 1, 1)
#end_date = datetime(start_date.year, start_date.month, 1) + timedelta(days=32)
#end_date = end_date.replace(day=1) - timedelta(days=1)
end_date = start_date + timedelta(days=1)
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

# Define the query to get observations for a specific location and time period
observations_data = {
    'query': f'''
        query {{
            getObservations {{
                locationId
                observations(filter: {{ start: "{start_date_str} 00:00:00", end: "{end_date_str} 23:59:59" }}) {{
                    qualityCode
                    timestamp
                    value
                }}
            }}
        }}
    '''
}

# Execute the query and handle the response
response_location = requests.post(url, headers=headers, json=location_data)
response_observation = requests.post(url, headers=headers, json=observations_data)
response_location_data = response_location.json()
response_observation_data = response_observation.json()
locations = response_location_data.get('data', {}).get('getObservations', [])
observations = response_observation_data.get('data', {}).get('getObservations', [])
old_location_metadata = {'locationId': 'str', 'name': 'str', 'nztmx': 'float', 'nztmy': 'float', 'type': 'str', 'unit': 'str'}
old_observation_metadata = {
    'observations': [
        {
            'qualityCode': 'str',
            'timestamp': 'str',
            'value': 'float'
        }
    ],
}

def get_metadata(json_data):
    # Initialize an empty dictionary for the metadata
    metadata = {}

    # Iterate over the keys in the first dictionary in the JSON data
    for key in json_data[0]:
        # Get the type of the value corresponding to the key
        value_type = type(json_data[0][key]).__name__

        # Add the key and its type to the metadata dictionary
        metadata[key] = value_type

    return metadata
def get_metadata(json_data):
    # Initialize an empty dictionary for the metadata
    metadata = {}

    # Initialize a dictionary to keep track of whether a decimal point has been seen
    has_decimal = {key: False for key in json_data[0]}

    # Iterate over all dictionaries in the JSON data
    for entry in json_data:
        for key, value in entry.items():
            # Check if the value is a number with a decimal point
            if isinstance(value, float):
                has_decimal[key] = True

    # Determine the type for each key based on the presence of decimal points
    for key, value in json_data[0].items():
        if has_decimal[key]:
            value_type = 'float'
        else:
            value_type = type(value).__name__

        # Add the key and its type to the metadata dictionary
        metadata[key] = value_type

    return metadata

def get_observation_metadata(json_data):
    # Initialize an empty dictionary for the metadata
    metadata = {}

    # Iterate over the keys in the first dictionary in the JSON data
    for key, value in json_data[0].items():
        # Check if the value is a list
        if isinstance(value, list):
            # If the list is not empty, get the metadata of the first dictionary in the list
            if value:
                metadata[key] = [get_metadata(value)]
        else:
            # Get the type of the value
            value_type = type(value).__name__

            # Add the key and its type to the metadata dictionary
            metadata[key] = value_type

    return metadata

current_location_metadata = get_metadata(locations)
current_observation_metadata = get_observation_metadata(observations)

# Compare the old and current metadata
changes = {k: current_location_metadata[k] for k in current_location_metadata if k in old_location_metadata and current_location_metadata[k] != old_location_metadata[k]}
changes.update({k: current_observation_metadata[k] for k in current_observation_metadata if k in old_observation_metadata and current_observation_metadata[k] != old_observation_metadata[k]})
# Print out any changes in the metadata
if changes != {}:
    # Send alert to users about the changes in metadata
    alert_message = "Changes in metadata detected:\n"
    for key, value in changes.items():
        alert_message += f"{key}: {value}\n"
    print(alert_message)
conn = None
cursor = None
try:
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="data472-tya51-database.cyi9p9kw8doa.ap-southeast-2.rds.amazonaws.com",
        database="postgres",
        user="postgres",
        password="kPDqtBRfzbs680TsGKQj"
    )

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Create a table to store the data
    create_table_query = '''
        CREATE TABLE IF NOT EXISTS locations (
            location_id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            geom GEOMETRY(Point,  2193), -- SRID 2193 is for NZGD2000
            type VARCHAR(255),
            unit VARCHAR(255)
        )
    '''
    cursor.execute(create_table_query)
    # Check if the observation is already in the table
    select_query = "SELECT location_id, name, ST_X(geom) AS nztmx, ST_Y(geom) AS nztmy, type, unit FROM locations WHERE location_id = %s"

    # Insert the data into the table or update if not exists
    for location in locations:
        location_id = location['locationId']
        name = location['name']
        nztmx = location['nztmx']
        nztmy = location['nztmy']
        observation_type = location['type']
        unit = location['unit']
        # Execute the select query with the location_id
        cursor.execute(select_query, (location_id,))
        record = cursor.fetchone()

        if record:
            # Check if the name, nztmx, or nztmy is different
            if record[1] != name or record[2] != nztmx or record[3] != nztmy or record[4] != observation_type or record[5] != unit:
                # Send alert to users about the difference
                alert_message = f"Difference detected for locationId {location_id}:\n"
                if record[1] != name:
                    alert_message += f"Name: {record[1]} -> {name}\n"
                if record[2] != nztmx:
                    alert_message += f"nztmx: {record[2]} -> {nztmx}\n"
                if record[3] != nztmy:
                    alert_message += f"nztmy: {record[3]} -> {nztmy}\n"
                if record[4] != observation_type:
                    alert_message += f"Type: {record[4]} -> {observation_type}\n"
                if record[5] != unit:
                    alert_message += f"Unit: {record[5]} -> {unit}\n"
                print(alert_message)
                # Update the record in the table
                update_query = "UPDATE locations SET name = %s, geom = ST_SetSRID(ST_MakePoint(%s, %s), %s), type = %s, unit = %s WHERE location_id = %s"
                cursor.execute(update_query, (name, nztmx, nztmy, GEO_TYPE, observation_type, unit, location_id))
                conn.commit()
                print("Record updated in the database.")

        else:
            # Insert the new observation into the table
            insert_query = """
            INSERT INTO locations (location_id, name, geom, type, unit)
            VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), %s), %s, %s)
            """
            # Execute the query with the data
            print("Location added to the database:")
            print(f"Location ID: {location_id}")
            print(f"Name: {name}")
            print(f"nztmx: {nztmx}")
            print(f"nztmy: {nztmy}")
            print(f"Type: {observation_type}")
            print(f"Unit: {unit}")
            cursor.execute(insert_query, (location_id, name, nztmx, nztmy, GEO_TYPE, observation_type, unit))
            conn.commit()
    # Create a table to store the observations
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS observations (
        location_id INTEGER,
        quality_code VARCHAR(255),
        timestamp TIMESTAMP,
        value FLOAT,
        PRIMARY KEY (location_id, timestamp),
        FOREIGN KEY (location_id) REFERENCES locations (location_id)
        )
    '''
    cursor.execute(create_table_query)

    # Check if the observation is already in the table
    select_query = "SELECT observation_id, quality_code, timestamp, value FROM observations WHERE location_id = %s AND timestamp = %s"

    # Initialize a list to store the observation records with location_id, quality_code, timestamp, and value
    observation_records = []
    for observation in observations:
        # Check if there are observations for the location, and only process if there are observations
        if observation['observations']:
            location_id = observation['locationId']
            observation_data = observation['observations']
            for data in observation_data:
                record = {}  # Change record from tuple to dictionary
                record['locationId'] = location_id
                record['qualityCode'] = data['qualityCode']
                record['timestamp'] = data['timestamp']
                record['value'] = data['value']
                observation_records.append(record)

    observation_number = 0
    # Insert the data into the table or update if not exists

    for observation in observation_records:
        location_id = observation['locationId']

        observation_number += 1
        quality_code = observation['qualityCode']
        timestamp = observation['timestamp']
        value = observation['value']

        # Execute the select query with the location_id and timestamp
        #cursor.execute(select_query, (location_id, timestamp))
        #record = cursor.fetchone()


        # Check if the observation is already in the table, and process if it is not. If it is, update the record if there are differences.
        #if record:
            # Check if the quality_code, value, type, or unit is different
        #    if record[1] != quality_code or record[3] != value:
        #        # Send alert to users about the difference
        #        alert_message = f"Difference detected for observation at locationId {location_id} and timestamp {timestamp}:\n"
        #        if record[1] != quality_code:
        #            alert_message += f"Quality Code: {record[1]} -> {quality_code}\n"
        #        if record[3] != value:
        #            alert_message += f"Value: {record[3]} -> {value}\n"
        #        print(alert_message)
        #        # Update the record in the table
        #        update_query = "UPDATE observations SET quality_code = %s, value = %s WHERE location_id = %s AND timestamp = %s"
        #        cursor.execute(update_query, (quality_code, value, location_id, timestamp))
        #        conn.commit()
        #        print("Record updated in the database.")

        #else:
            # Insert the new observation into the table with INSERT ... ON CONFLICT
        insert_query = """
        INSERT INTO observations (location_id, quality_code, timestamp, value)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (location_id, timestamp) DO UPDATE SET quality_code = EXCLUDED.quality_code, value = EXCLUDED.value
        """
        # Execute the query with the data
        # print("Observation added to the database:")
        # print(f"Location ID: {location_id}")
        # print(f"Quality Code: {quality_code}")
        # print(f"Timestamp: {timestamp}")
        # print(f"Value: {value}")
        cursor.execute(insert_query, (location_id, quality_code, timestamp, value))
        conn.commit()

   # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create the file path for the extraction date file
    file_path = os.path.join(script_dir, "extraction_date.txt")

    # Append the dates with the current date to the extraction date file
    with open(file_path, 'a') as file:
        file.write(f"Start Date: {start_date_str} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"End Date: {end_date_str} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"observation record number: {observation_number}\n") 
    print("Dates appended to extraction_date.txt")
    print(f"observation record number: {observation_number}")       
except Exception as e:
    print(f"An error occurred: {e}")
finally:    
    # Close the cursor and connection
    if cursor is not None:
        cursor.close()
    if conn is not None:
        conn.close()

# # Extract all records from the table
# select_query = "SELECT location_id, name, ST_X(geom) AS nztmx, ST_Y(geom) AS nztmy FROM locations"

# # Execute the query
# cursor.execute(select_query)

# # Fetch all the records
# records = cursor.fetchall()

# # Transfer geom back to nztmx and nztmy
# for record in records:
#     location_id = record[0]
#     name = record[1]
#     nztmx = record[2]
#     nztmy = record[3]

# # Check if locations fetched by API are different from those in the database table locations
# api_locations = set([(str(location['locationId']), location['name'], "{:.0f}".format(location['nztmx']), "{:.0f}".format(location['nztmy'])) for location in locations])
# db_locations = set([(str(record[0]), record[1], "{:.0f}".format(record[2]), "{:.0f}".format(record[3]))  for record in records])

# # Find the locations that are in the API response but not in the database
# new_locations = [location for location in api_locations if location not in db_locations]

# if new_locations:
#     print("New locations found:")
#     for location in new_locations:
#         print(location)
#         # Insert the new locations into the database
#         location_id = location[0]
#         name = location[1]
#         nztmx = location[2]
#         nztmy = location[3]
#         # Use ST_MakePoint to create a point geometry from nztmx and nztmy
#         # Use ST_SetSRID to set the SRID to 2193 (NZGD2000)
#         insert_query = """
#         INSERT INTO locations (location_id, name, geom)
#         VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 2193))
#         """
#         # Execute the query with the data
#         cursor.execute(insert_query, (location_id, name, nztmx, nztmy))
#         conn.commit()
# else:
#     print("No new locations found.")



####################################################################################


# Insert the data into the table
# observations = data.get('data', {}).get('getObservations', [])
# for observation in observations:
#     location_id = observation['locationId']
#     name = observation['name']
#     nztmx = observation['nztmx']
#     nztmy = observation['nztmy']
#     # Use ST_MakePoint to create a point geometry from nztmx and nztmy
#     # Use ST_SetSRID to set the SRID to 4326 (WGS 84)
#     insert_query = """
#     INSERT INTO locations (location_id, name, geom)
#     VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
#     """
#     # Execute the query with the data
#     cursor.execute(insert_query, (location_id, name, nztmx, nztmy))
#     conn.commit()

# # Close the cursor and connection
# cursor.close()
# conn.close()

# response = requests.post(url, headers=headers, json=data)
# data = response.json()
# names = list(set([observation['name'].split(' at ')[0] for observation in data['data']['getObservations']]))
# transcript = ',\n'.join(names)
# print(transcript)