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
