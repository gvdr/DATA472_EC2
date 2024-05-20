## DATA472 - Individual Project: ECAN River Flow Data ETL Project
Student: Tao Yan - 85698590
### 1. Introduction
This project is to extract, transform and load quality and flow data of major rivers in the region of Canterbury in New Zealand. The aim is to get clean, timely, accurate data with enough amount to support further data analyzing and investigation. All observational environmental river flow data is extracted through GraphQL API endpoint https://apis.ecan.govt.nz/waterdata/observations/graphql.
### 2. Data Description
ECAN river flow data records water levels at 152 river and lake sites in Canterbury, from the Clarence River/Waiau Toa in the north to the Waitaki River in the south. River flow at 132 of these sites are recorded and this information is combined with water level data to produce continuous flow records. All the data alongside data from 19 other sites recorded by partner agencies such as the National Institute of Water and Atmospheric Research and Christchurch City Council are included in the dataset. To be specific, there are 288 observation locations as of May 10 2024, and records of quality and flow will be observed and recorded every 15 minutes on about half locations, which will generate 12000 to 13000 observation records every day.
Hence, location related information is considered relatively static and stable, which is classified as master data, and observation records are treated as normal data.
### 3. Project Structure
The project consists of the following main components:
* Data Extraction: 
GraphQL API endpoint of ECAN was used to extract: 1) all location data and metric related data, such as type and flow unit. 2) observation data, such as quality and flow, based on specified date range, because API put a restriction on maximum records extraction per time.
* Data Transformation and Cleansing: 
Variation in master data, such as location information, will be detected and transferred to database. Observation data have about half blank records without any recorded value, thus this part of records are deleted accordingly. In the meantime, due to the fact that each location is attached with all its observation records in the obtained Json file, certain transformation is performed to make every records attach to corresponding location to insert to relational database.
* Database Setup and Data Loading: 
Firstly set up local PostgreSQL database for testing, then set up RDS PostgreSQL database in AWS. Connect database in the scipt using code "psql --host=data472-tya51-database.cyi9p9kw8doa.ap-southeast-2.rds.amazonaws.com --port=5432 --username=postgres --dbname=postgres", create required tables and load clean data into the database.
