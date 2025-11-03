from api_client import PortProAPI, ChargeTemplate, CustomerRateRecord, Profile, ChargeProfileData
from typing import List
import csv
from collections import defaultdict
import concurrent.futures
import threading

# Initialize the API client
api = PortProAPI(
    # base_url="https://sandbox-api.app.portpro.io",
    base_url="http://localhost:8081",
    # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI1ZmIzZTBmYzJhNTE4NjJjMDM0NDkzMjIiLCJpYXQiOjE3MzM0NjE4NjB9.OUBsDTNO-pwRpwVzuHFCFi4b72QWhQQR5R6lFusTeZc",
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI1ZmIzZTBmYzJhNTE4NjJjMDM0NDkzMjIiLCJpYXQiOjE3NDYwODU1NzN9.Ub35EHXPwxRE2zclITbvbS6aMpj8uZtLfLE-Q8Xvqwc",
    vendor_type="driver" # driver or None
)
def create_rate_for_zipcodes(api, zipcodes, terminal_id, terminal_name, amount):
    """
    Creates a charge template and customer rate record for multiple zipcodes.
    
    Args:
        api (PortProAPI): The API client instance
        zipcodes (List[str]): List of zipcodes for delivery locations
        terminal_id (str): The terminal ID
        terminal_name (str): The terminal name
        amount (int): The rate amount
    
    Returns:
        dict: The API response from creating the customer rate record
    
    Raises:
        Exception: If any API call fails
    """
    try:
        terminal = Profile(
            _id=terminal_id,
            name=terminal_name,
            profile_type="terminal",
            profile={"_id": terminal_id, "name": terminal_name}
        )
        
        delivery_locations = [
            Profile(
                name=zipcode,
                profile_type="zipCode",
                profile={"name": zipcode, "zipCode": zipcode}
            ) for zipcode in zipcodes
        ]

        name = f"{terminal_name}-{amount}"

        template = ChargeTemplate(
            name=name,
            charge_name="Line Haul",
            charge_code="Base Price",
            description="Line Haul",
            amount=amount
        )
        
        # Create charge template
        template_data = api.create_charge_template(template)

        # Create the customer rate record using the charge template data
        rate_record = CustomerRateRecord(
            name=name,
            load_types=["IMPORT", "EXPORT", "ROAD"],
            customers=[
                Profile(
                    _id="6509789287550d5c4aba54aa",
                    name="All Customers",
                    profile=None,
                    profile_type="customer/group"
                )
            ],
            pickup_location=[
                Profile(
                    _id="6509789287550d5c4aba54aa",
                    name="All Customers",
                    profile=None,
                    profile_type="customer/group"
                )
            ],
            delivery_location=delivery_locations,
            terminals=[terminal],
            effective_start_date="2025-06-24T05:00:00.000Z",
            effective_end_date="2032-03-02T04:59:59.999Z",
            charge_profile_data=template_data,
            vendor_type=api.vendor_type,
        )
        
        rate_response = api.create_customer_rate_record(rate_record)
        print(f"Customer rate record created successfully for {name}")
        return rate_response

    except Exception as e:
        print(f"Error creating rate for zipcodes {zipcodes}: {e}")
        raise

def process_csv_and_create_rates(csv_file_path, terminal_id, terminal_name, num_threads=10):
    """
    Reads a CSV file with zipcode and linehaul data, groups by linehaul amount,
    and creates rates for each group using multiple threads.
    
    Args:
        csv_file_path (str): Path to the CSV file
        terminal_id (str): The terminal ID
        terminal_name (str): The terminal name
        num_threads (int): Number of threads to use for API calls
    """
    try:
        # Group zipcodes by linehaul amount
        linehaul_groups = defaultdict(list)
        total_zipcodes = 0
        
        # Read the CSV file
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                zipcode = row['ZIPCODE']
                linehaul = float(row['LINEHAUL'])  # Convert to float for numeric handling
                linehaul_groups[linehaul].append(zipcode)
                total_zipcodes += 1
        
        # Display summary and wait for user confirmation
        print(f"\nSummary of rates to be created:")
        print(f"Total unique linehaul rates: {len(linehaul_groups)}")
        print(f"Total zipcodes to process: {total_zipcodes}")
        print("\nBreakdown by linehaul amount:")
        
        for linehaul, zipcodes in sorted(linehaul_groups.items()):
            print(f"  ${linehaul}: {len(zipcodes)} zipcodes")
        
        user_input = input(f"\nDo you want to proceed with creating these rates using {num_threads} threads? (y/n): ")
        if user_input.lower() != 'y':
            print("Operation cancelled by user.")
            return []
        
        # Function to process a single linehaul group
        def process_linehaul_group(linehaul, zipcodes):
            try:
                print(f"Creating rate for {len(zipcodes)} zipcodes with linehaul amount {linehaul}")
                response = create_rate_for_zipcodes(
                    api=api,
                    zipcodes=zipcodes,
                    terminal_id=terminal_id,
                    terminal_name=terminal_name,
                    amount=linehaul
                )
                return {
                    'linehaul': linehaul,
                    'zipcode_count': len(zipcodes),
                    'response': response,
                    'status': 'success'
                }
            except Exception as e:
                print(f"Error creating rate for linehaul {linehaul}: {e}")
                return {
                    'linehaul': linehaul,
                    'zipcode_count': len(zipcodes),
                    'error': str(e),
                    'status': 'error'
                }
        
        # Create a print lock to prevent garbled console output
        print_lock = threading.Lock()
        
        # Process linehaul groups in parallel using ThreadPoolExecutor
        results = []
        print(f"\nStarting API calls with {num_threads} threads...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submit all tasks
            future_to_linehaul = {
                executor.submit(process_linehaul_group, linehaul, zipcodes): linehaul
                for linehaul, zipcodes in linehaul_groups.items()
            }
            
            # Process results as they complete
            completed = 0
            total = len(future_to_linehaul)
            
            for future in concurrent.futures.as_completed(future_to_linehaul):
                linehaul = future_to_linehaul[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Update progress
                    completed += 1
                    with print_lock:
                        print(f"Progress: {completed}/{total} ({(completed/total)*100:.1f}%) - Completed linehaul ${linehaul}")
                        
                except Exception as e:
                    with print_lock:
                        print(f"Error processing linehaul {linehaul}: {e}")
        
        # Summarize results
        successful = sum(1 for r in results if r.get('status') == 'success')
        failed = sum(1 for r in results if r.get('status') == 'error')
        
        print(f"\nProcessing complete:")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total: {len(results)}")
        
        return results
    
    except Exception as e:
        print(f"Error processing CSV and creating rates: {e}")
        raise

# Example usage
if __name__ == "__main__":
    try:
        # Replace with your actual CSV file path
        csv_file_path = "inputs/Driver/"

        # Process the CSV and create rates with 10 threads
        results = process_csv_and_create_rates(
            csv_file_path=csv_file_path,
            terminal_id="5fb54bf4825b9a4174fcd878",
            terminal_name="Norfolk",
            num_threads=10
        )
        
        if results:
            successful_count = sum(1 for r in results if r.get('status') == 'success')
            print(f"Successfully created {successful_count} rate groups")
        
    except Exception as e:
        print("Error in main execution:", e)
