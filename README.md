## DATA472 - Individual Project: ECAN River Flow Data ETL Project
**Student**: Tao Yan - 85698590

### 1. Introduction
This project aims to extract, transform, and load quality and flow data from major rivers in the Canterbury region of New Zealand. The goal is to obtain clean, timely, and accurate data in sufficient quantity to support further data analysis and research. All observational environmental river flow data is extracted via the GraphQL API endpoint at [ECAN Water Data Observations](https://apis.ecan.govt.nz/waterdata/observations/graphql).

### 2. Data Description
The ECAN river flow dataset includes water level records from 152 river and lake sites across Canterbury, ranging from the Clarence River/Waiau Toa in the north to the Waitaki River in the south. River flow is recorded at 132 of these sites, and this data is combined with water level measurements to produce continuous flow records. The dataset also incorporates data from 19 additional sites monitored by partner agencies, such as the National Institute of Water and Atmospheric Research and the Christchurch City Council. As of May 10, 2024, there are 288 observation locations, with quality and flow data being recorded every 15 minutes at approximately half of these sites, resulting in 12,000 to 13,000 observation records daily. Location-related information is deemed relatively static and stable, thus classified as master data, while observation records are considered transactional data.

### 3. Project Structure
The project is structured into the following main components:
* **Data Extraction**: 
Utilizing the ECAN GraphQL API endpoint to extract: 
1) All location and metric-related data, such as type and flow unit.
2) Observation data, such as quality and flow, within a specified date range due to API restrictions on the maximum number of records per extraction.
* **Data Transformation and Cleansing**: 
Detecting and transferring any variations in master data, like location information, to the database. Approximately half of the observation data records are blank and are thus deleted. Additionally, transformations are applied to associate each observation record with its corresponding location for insertion into a relational database.
* **Database Setup and Data Loading**: 
Initially, a local PostgreSQL database is established for testing purposes, followed by the setup of an RDS PostgreSQL database on AWS. The database is connected in the script using the command: `psql --host=data472-tya51-database.cyi9p9kw8doa.ap-southeast-2.rds.amazonaws.com --port=5432 --username=postgres --dbname=postgres`. Required tables are created, and clean data is loaded into the database.
* **Data Structure and Visualization**: 

API data scheme:
1) Locations
   
![Alt text for the image](https://github.com/DataAdvisory/EC2/blob/main/Schema1.jpg)

2) Observations

![Alt text for the image](https://github.com/DataAdvisory/EC2/blob/main/Schema2.jpg)

Database table scheme:

1) Locations 

![Alt text for the image](https://github.com/DataAdvisory/EC2/blob/main/Schema3.jpg)

2) Observations

![Alt text for the image](https://github.com/DataAdvisory/EC2/blob/main/Schema2.jpg)

Data Visualization
1)	Colours represent various river water qualities.
2)	Sizes represent different river flow.

* **Logging**: The project uses Logging for logging.
* **Scheduled Task**: A run_etl.sh file and cron job is set up to run ETL.py to download the data daily.
### 4. Installation and Usage
* **Pre-requisites**
1. Python: This project is built with Python 3.12
2. PostgreSQL: This project depends on PostgresSQL database to store data.
* **Clone and install**
1. Clone the repository: git clone git@github.com: DataAdvisory/EC2.git,   cd EC2
2. Install dependencies: pip install -r requirements.txt
* **Usage**
1. Start the PostgreSQL database in RDS server.
2. Configure cron job to run ETL.py.
3. Start flaskapp.service and nginx reverse proxy to enable web API.
4. Access master data: http://13.236.194.130/tya51/api/river/metadata
5. Access location data: http://13.236.194.130/tya51/api/river/location 
6. Access observation data: http://13.236.194.130/tya51/api/river/observation/YYYY-MM-DD
### 5. Code Overview
* **Dependencies**
Flask: For web API
psycopg2: For GEOMETRY conversion
Requests: For HTTP requests
Pg: For connecting PostgreSQL
Cron: For scheduling tasks
Logging: For logging.
* **Key Functions**
ETL: Download data through GraphQL API, transforming and cleansing data, and insert data into the PostgreSQL database.
App: Set up web API endpoint service and output data.
Run_etl.sh: Establish scheduling task to run ETL daily.
### 6. Logging
The project uses Logging for logging. Logs are written to the log file of ETL.log in the log directory.
### 7. Scheduled Task
A run_etl.sh and a cron job are set up to run ETL.py after midnight (Australia time) every day to download and update the data.
run_etl.sh
current_date=$(date +%Y%m%d)
start_date=$(date -d "$current_date -5 day" +%Y-%m-%d)
end_date=$(date -d "$current_date -4 day" +%Y-%m-%d)
/usr/bin/python3 /home/ubuntu/EC2/ETL.py --startdate $start_date --enddate $end_date
const job = new CronJob(
    " 0 1 * * * /home/ubuntu/EC2/run_etl.sh"
);
job.sta
