# -*- coding: utf-8 -*-
"""solution.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Cbv9Cz68tnixVq2GE_TCEGmP9Jau5npH
"""



pip install jason

import json

pip install pandas dask json psutil

import pandas as pd
import dask.dataframe as dd
import psutil
import json
import time
from google.colab import files

# Function to get system configuration and resource usage
def get_system_stats():
    mem_info = psutil.virtual_memory()
    cpu_info = psutil.cpu_times_percent(interval=0, percpu=False)
    return {
        "system_configuration": {
            "cpu_count": psutil.cpu_count(logical=False),
            "total_memory": mem_info.total / (1024 ** 3)  # in GB
        },
        "resource_usage": {
            "average_cpu_percent": cpu_info.user,
            "average_memory_used_percent": mem_info.percent
        }
    }

# Function to calculate costs from DataFrame
def calculate_costs(df):
    try:
        total_cost = df['line_item_blended_cost'].sum().compute()
        tax_cost = df[df['line_item_line_item_type'] == 'Tax']['line_item_blended_cost'].sum().compute()
        usage_cost = total_cost - tax_cost
        return {
            "total_cost": round(total_cost, 2),
            "tax_cost": round(tax_cost, 2),
            "usage_cost": round(usage_cost, 2)
        }
    except KeyError as e:
        print(f"Column not found: {e}")
        return None

# Function to extract cost details from Parquet file
def extract_cost_details(file_path):
    start_time = time.time()

    # Read Parquet file with Dask
    df = dd.read_parquet(file_path, columns=['line_item_blended_cost', 'line_item_line_item_type'])

    cost_details = calculate_costs(df)

    print(f"Time taken to process: {time.time() - start_time} seconds")
    return cost_details

# Function to process DataFrame and generate nested JSON
def generate_nested_json(df):
    # Convert datetime columns to strings if needed
    datetime_columns = ['bill_billing_period_start_date', 'bill_billing_period_end_date']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = df[col].astype(str)

    # Define cost columns
    cost_columns = {
        "total_cost": ['line_item_blended_cost', 'line_item_unblended_cost', 'line_item_total_amount'],
        "tax_cost": ['line_item_tax_amount'],
        "usage_cost": ['line_item_usage_amount']
    }

    # Check if the columns exist in the DataFrame and handle them appropriately
    for cost_type, cols in cost_columns.items():
        valid_cols = [col for col in cols if col in df.columns]
        if valid_cols:
            df[cost_type] = df[valid_cols].astype(float).sum(axis=1)
        else:
            df[cost_type] = 0.0

    # Group by the appropriate columns
    numeric_columns = [col for col in df.columns if df[col].dtype in ['float64', 'int64']]
    grouped = df.groupby(['line_item_resource_id', 'product_region', 'line_item_product_code', 'product_usagetype'])[numeric_columns].sum().reset_index().compute()

    # Construct the nested dictionary
    nested_dict = {}
    for _, row in grouped.iterrows():
        region = row['product_region']
        usage_type = row['product_usagetype']
        product_code = row['line_item_product_code']
        resource_id = row['line_item_resource_id']
        identity_line_item_id = row.get('identity_line_item_id', 'N/A')

        if region not in nested_dict:
            nested_dict[region] = []

        existing_detail = next((item for item in nested_dict[region] if usage_type in item['details']), None)
        if existing_detail:
            details = existing_detail['details']
        else:
            existing_detail = {
                "total_cost": str(row['total_cost']),
                "usage_cost": str(row['usage_cost']),
                "details": {}
            }
            nested_dict[region].append(existing_detail)
            details = existing_detail['details']

        if usage_type not in details:
            details[usage_type] = []

        details[usage_type].append({
            f"{region}-{usage_type}_total_cost": str(row['total_cost']),
            f"{region}-{usage_type}_details": {
                resource_id: {
                    "total_cost": str(row['total_cost']),
                    "identityLineItemId": identity_line_item_id,
                    "line_item_resource_id": resource_id,
                    "region": region,
                    "line_item_product_code": product_code,
                    "product_usagetype": usage_type
                }
            }
        })

    return nested_dict

# Define file path
file_path = '/content/CUR10MB.parquet'

# Get initial system stats
initial_stats = get_system_stats()

# Extract cost details and read DataFrame for JSON generation
cost_details = extract_cost_details(file_path)
df = dd.read_parquet(file_path)

# Generate nested JSON
nested_json = generate_nested_json(df)

if cost_details:
    # Get final system stats
    final_stats = get_system_stats()

    # Create the final output dictionary
    output_data = {
        "region_details": nested_json,
        "cost_details": cost_details,
        "system_configuration": {
            "initial_stats": initial_stats,
            "final_stats": final_stats
        }
    }

    # Save JSON to a file
    json_file_path = 'output_data.json'
    with open(json_file_path, 'w') as json_file:
        json.dump(output_data, json_file, indent=2)

    # Create a download link
    display(FileLink(json_file_path))

    # Print the results (optional)
    print(json.dumps(output_data, indent=2))

    # Calculate average CPU and memory usage during the process
    initial_cpu_usage = initial_stats['resource_usage']['average_cpu_percent']
    final_cpu_usage = final_stats['resource_usage']['average_cpu_percent']
    average_cpu_usage = (initial_cpu_usage + final_cpu_usage) / 2

    initial_memory_usage = initial_stats['resource_usage']['average_memory_used_percent']
    final_memory_usage = final_stats['resource_usage']['average_memory_used_percent']
    average_memory_usage = (initial_memory_usage + final_memory_usage) / 2

    print(f"Average CPU Usage: {average_cpu_usage}%")
    print(f"Average Memory Usage: {average_memory_usage}%")
else:
    print("Could not extract cost details due to missing columns.")

pip install dask[dataframe]

import pandas as pd
import psutil
import json
import time
from google.colab import files  # Use this for downloading the file in Colab

# Function to get system configuration and resource usage
def get_system_stats():
    mem_info = psutil.virtual_memory()
    cpu_info = psutil.cpu_times_percent(interval=0, percpu=False)
    return {
        "system_configuration": {
            "cpu_count": psutil.cpu_count(logical=False),
            "total_memory": mem_info.total / (1024 ** 3)  # in GB
        },
        "resource_usage": {
            "average_cpu_percent": cpu_info.user,
            "average_memory_used_percent": mem_info.percent
        }
    }

# Function to calculate costs from DataFrame
def calculate_costs(df):
    try:
        total_cost = df['line_item_blended_cost'].sum()
        tax_cost = df[df['line_item_line_item_type'] == 'Tax']['line_item_blended_cost'].sum()
        usage_cost = total_cost - tax_cost
        return {
            "total_cost": round(total_cost, 2),
            "tax_cost": round(tax_cost, 2),
            "usage_cost": round(usage_cost, 2)
        }
    except KeyError as e:
        print(f"Column not found: {e}")
        return None

# Function to extract cost details from Parquet file
def extract_cost_details(file_path):
    start_time = time.time()

    # Read Parquet file with pandas
    df = pd.read_parquet(file_path, columns=['line_item_blended_cost', 'line_item_line_item_type'])

    cost_details = calculate_costs(df)

    print(f"Time taken to process: {time.time() - start_time} seconds")
    return cost_details

# Function to process DataFrame and generate nested JSON
def generate_nested_json(df):
    # Convert datetime columns to strings if needed
    datetime_columns = ['bill_billing_period_start_date', 'bill_billing_period_end_date']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = df[col].astype(str)

    # Define cost columns
    cost_columns = {
        "total_cost": ['line_item_blended_cost', 'line_item_unblended_cost', 'line_item_total_amount'],
        "tax_cost": ['line_item_tax_amount'],
        "usage_cost": ['line_item_usage_amount']
    }

    # Check if the columns exist in the DataFrame and handle them appropriately
    for cost_type, cols in cost_columns.items():
        valid_cols = [col for col in cols if col in df.columns]
        if valid_cols:
            df[cost_type] = df[valid_cols].astype(float).sum(axis=1)
        else:
            df[cost_type] = 0.0

    # Group by the appropriate columns
    numeric_columns = [col for col in df.columns if df[col].dtype in ['float64', 'int64']]
    grouped = df.groupby(['line_item_resource_id', 'product_region', 'line_item_product_code', 'product_usagetype'])[numeric_columns].sum().reset_index()

    # Construct the nested dictionary
    nested_dict = {}
    for _, row in grouped.iterrows():
        region = row['product_region']
        usage_type = row['product_usagetype']
        product_code = row['line_item_product_code']
        resource_id = row['line_item_resource_id']
        identity_line_item_id = row.get('identity_line_item_id', 'N/A')

        if region not in nested_dict:
            nested_dict[region] = []

        existing_detail = next((item for item in nested_dict[region] if usage_type in item['details']), None)
        if existing_detail:
            details = existing_detail['details']
        else:
            existing_detail = {
                "total_cost": str(row['total_cost']),
                "usage_cost": str(row['usage_cost']),
                "details": {}
            }
            nested_dict[region].append(existing_detail)
            details = existing_detail['details']

        if usage_type not in details:
            details[usage_type] = []

        details[usage_type].append({
            f"{region}-{usage_type}_total_cost": str(row['total_cost']),
            f"{region}-{usage_type}_details": {
                resource_id: {
                    "total_cost": str(row['total_cost']),
                    "identityLineItemId": identity_line_item_id,
                    "line_item_resource_id": resource_id,
                    "region": region,
                    "line_item_product_code": product_code,
                    "product_usagetype": usage_type
                }
            }
        })

    return nested_dict

# Define file path
file_path = '/content/CUR10MB.parquet'

# Get initial system stats
initial_stats = get_system_stats()

# Extract cost details and read DataFrame for JSON generation
cost_details = extract_cost_details(file_path)
df = pd.read_parquet(file_path)

# Generate nested JSON
nested_json = generate_nested_json(df)

if cost_details:
    # Get final system stats
    final_stats = get_system_stats()

    # Create the final output dictionary
    output_data = {
        "region_details": nested_json,
        "cost_details": cost_details,
        "system_configuration": {
            "initial_stats": initial_stats,
            "final_stats": final_stats
        }
    }

    # Save JSON to a file
    with open('output_data.json', 'w') as json_file:
        json.dump(output_data, json_file, indent=2)

    # Download the file in Colab
    files.download('output_data.json')

    # Print the results (optional)
    print(json.dumps(output_data, indent=2))

    # Calculate average CPU and memory usage during the process
    initial_cpu_usage = initial_stats['resource_usage']['average_cpu_percent']
    final_cpu_usage = final_stats['resource_usage']['average_cpu_percent']
    average_cpu_usage = (initial_cpu_usage + final_cpu_usage) / 2

    initial_memory_usage = initial_stats['resource_usage']['average_memory_used_percent']
    final_memory_usage = final_stats['resource_usage']['average_memory_used_percent']
    average_memory_usage = (initial_memory_usage + final_memory_usage) / 2

    print(f"Average CPU Usage: {average_cpu_usage}%")
    print(f"Average Memory Usage: {average_memory_usage}%")
else:
    print("Could not extract cost details due to missing columns.")
