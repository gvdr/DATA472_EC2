# Get the current date
current_date=$(date +%Y%m%d)

# Calculate the start and end dates
start_date=$(date -d "$current_date -5 day" +%Y-%m-%d)
end_date=$(date -d "$current_date -4 day" +%Y-%m-%d)


# Run the Python script with the calculated dates
/usr/bin/python3 /home/ubuntu/EC2/ETL.py --startdate $start_date --enddate $end_date
