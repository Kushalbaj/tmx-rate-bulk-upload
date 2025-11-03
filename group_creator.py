import csv
import requests
import json
import os

tmx_token = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI1ZmIzZTBmYzJhNTE4NjJjMDM0NDkzMjIiLCJpYXQiOjE3MjE5NjU1NzJ9.VvRVC5QLYEmMd8ZHdJ1WR9juXhkuS44J7XzQNI1ZesE'
test_token = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI1YWU4OTcyYjVlYjNiMDI4MzljYWQwZTEiLCJpYXQiOjE3MjA0MDYzMDB9.bGwxV_eqGQViYyYbx-H45rRbDSsA-CfT0swh9YFr3l0'

# Define the API URL and headers
api_url = 'https://api.axle.network/user/create-group-profile-settings'
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'authorization': test_token,
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://app.portpro.io',
    'referer': 'https://app.portpro.io/',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

# Function to read CSV and group ZIP codes by linehaul
def group_zipcodes_by_linehaul(csv_file_path):
    groups = {}
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            linehaul = row['LINEHAUL']
            zipcode = row['ZIPCODE']
            if linehaul not in groups:
                groups[linehaul] = []
            groups[linehaul].append(zipcode)
    return groups

# Function to create CSV files for each group
def create_csv_files(groups, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    total_groups = len(groups)
    for index, (linehaul, zipcodes) in enumerate(groups.items(), start=1):
        file_path = os.path.join(output_dir, f"linehaul_{linehaul}.csv")
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['zipcode'])
            for zipcode in zipcodes:
                writer.writerow([zipcode])
        print(f"CSV file created for linehaul {linehaul} ({index}/{total_groups}): {file_path}")

# Function to make API calls for each group
def create_group_profiles(groups):
    total_groups = len(groups)
    for index, (linehaul, zipcodes) in enumerate(groups.items(), start=1):
        group_name = f"Zipcode Group {index}"
        payload = {
            "group": {
                "name": group_name,
                "zipcodes": zipcodes
            },
            "type": "ZIP_CODE"
        }
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print(f"Group {group_name} created successfully ({index}/{total_groups}).")
        else:
            print(f"Failed to create group {group_name} ({index}/{total_groups}). Status code: {response.status_code}, Response: {response.text}")

# Main function
csv_file_path = 'base_rates_va.csv'  # Replace with your CSV file path
output_directory = 'output_csv_files'  # Replace with your desired output directory
groups = group_zipcodes_by_linehaul(csv_file_path)
# create_csv_files(groups, output_directory)
create_group_profiles(groups)
