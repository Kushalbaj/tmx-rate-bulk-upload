# TMX Rate Upload Tool

A Python tool specifically designed for **TMX customers** to bulk upload customer and driver rates to the TMX/PortPro API. This tool processes CSV files containing zipcode and linehaul data, groups them by rate amount, and creates charge templates and rate records via the PortPro API.


## Features

- 📊 **CSV Processing**: Reads and processes CSV files with zipcode and linehaul rate data
- 🔄 **Grouping**: Automatically groups zipcodes by linehaul amount for efficient rate creation
- ⚡ **Multi-threaded**: Uses concurrent processing to upload rates in parallel
- 🎯 **Dual Support**: Supports both customer rates and driver rates for TMX customers
- 🔌 **API Client**: Comprehensive API client for interacting with PortPro/TMX endpoints
- 📝 **Charge Templates**: Creates charge templates automatically based on rate data
- 📍 **Terminal-based**: Supports rate creation for specific terminals

## Requirements

- Python 3.7+
- `requests` library

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
```

2. Install dependencies:
```bash
pip install requests
```

## Configuration

### API Configuration

Edit the API configuration in `create_zip_rates_v2.py`:

```python
api = PortProAPI(
    base_url="http://localhost:8081",  # or "https://sandbox-api.app.portpro.io"
    token="YOUR_TOKEN_HERE",
    vendor_type="driver"  # "driver" for driver rates, None for customer rates
)
```

### CSV File Format

Your CSV files should have the following columns:

- `ZIPCODE`: The zipcode for delivery location
- `LINEHAUL`: The linehaul rate amount

Example:
```csv
ZIPCODE,LINEHAUL
12345,150.00
67890,200.00
```

## Usage

### Uploading TMX Customer Rates

1. Place your CSV file in the `inputs/Customer/` directory
2. Edit `create_zip_rates_v2.py`:
   - Update the `csv_file_path` variable
   - Set `terminal_id` and `terminal_name`
   - Set `vendor_type=None` for TMX customer rates
3. Run the script:
```bash
python create_zip_rates_v2.py
```

### Uploading TMX Driver Rates

1. Place your CSV file in the `inputs/Driver/` directory
2. Edit `create_zip_rates_v2.py`:
   - Update the `csv_file_path` variable
   - Set `terminal_id` and `terminal_name`
   - Set `vendor_type="driver"` for TMX driver rates
3. Run the script:
```bash
python create_zip_rates_v2.py
```

## Multi-threading

The tool uses Python's `ThreadPoolExecutor` to process multiple rate groups in parallel. Default is 10 threads, but you can adjust:

```python
process_csv_and_create_rates(
    csv_file_path="path/to/file.csv",
    terminal_id="terminal_id",
    terminal_name="Terminal Name",
    num_threads=20  # Increase for faster processing
)
```

## How It Works

The tool automatically groups zipcodes by their linehaul amount:
- All zipcodes with the same linehaul amount are grouped together
- Each group creates a single rate record with multiple delivery locations
- Rate records are uploaded in parallel for faster processing

Sample TMX Data:
https://docs.google.com/spreadsheets/d/1lnKxG7R_lXJ5fu3cveVmhMBAl6scQ2ZTycinKGUCnYw/edit?gid=0#gid=0
