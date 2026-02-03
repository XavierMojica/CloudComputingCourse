# *****************************************************************************************************
# Version: 1.0
# Author: Great Learning
#
# Description:
# This script processes S3 event notifications via SQS, extracts metadata from uploaded objects,
# stores the metadata in an RDS database, and allows users to interactively query stored metadata.
#
# Disclaimer:
# This script is provided "as is" without any warranties or guarantees. Great Learning 
# is not responsible for any issues, data loss, or unintended consequences arising from the use of 
# this script. Users are advised to review and modify the script as per their specific requirements.
#
# Copyright:
# Â© Great Learning. All rights reserved.
# Unauthorized copying or distribution of this script, via any medium, is strictly 
# prohibited without prior written permission from Great Learning.
# *****************************************************************************************************

import json
import boto3
import pymysql
import sys
import time
import urllib.parse  # Import URL decoding module

# AWS Clients
sqs = boto3.client('sqs', region_name="us-east-1")
s3 = boto3.client('s3', region_name="us-east-1")

# SQS Queue URL
queue_url = "YOUR_SQS_QUEUE_URL"  # Replace with your actual SQS queue URL

# RDS Connection Details
RDS_HOST = "YOUR_RDS_ENDPOINT"  # Replace with your actual RDS Endpoint


RDS_USER = "root"
RDS_PASSWORD = "password"
RDS_DB = "s3metadata"


def connect_to_rds():
    """Establish a connection to the RDS database."""
    print("Attempting to connect to RDS...")
    try:
        connection = pymysql.connect(
            host=RDS_HOST,
            user=RDS_USER,
            password=RDS_PASSWORD,
            database=RDS_DB,
            cursorclass=pymysql.cursors.Cursor
        )
        print("Connected to RDS successfully.")
        return connection
    except pymysql.MySQLError as e:
        print(f"Database connection error: {e}")
        sys.exit(1)


def ensure_table_exists(connection):
    """Ensure the metadata table exists in RDS."""
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS s3_metadata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_name VARCHAR(255),
                bucket_name VARCHAR(255),
                file_size BIGINT,
                content_type VARCHAR(255),
                last_modified DATETIME
            )
        """)
        connection.commit()
    print("Ensured table 's3_metadata' exists in the database.")


def insert_metadata_into_rds(connection, file_name, bucket_name, file_size, content_type, last_modified):
    """Insert metadata into RDS."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO s3_metadata (file_name, bucket_name, file_size, content_type, last_modified)
                VALUES (%s, %s, %s, %s, %s)
            """, (file_name, bucket_name, file_size, content_type, last_modified))
        connection.commit()
    except pymysql.MySQLError as e:
        print(f"Database insertion error: {e}")
        sys.exit(1)


def fetch_all_metadata_from_rds(connection):
    """Retrieve and display metadata of all objects stored in RDS."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT file_name, bucket_name, file_size, content_type, last_modified FROM s3_metadata")
            results = cursor.fetchall()

            if not results:
                print("\nNo metadata records found in the database.")
                return

            # Print table headers
            print("\nAll Stored Object Metadata in RDS:")
            print(f"{'File Name':<50} {'Bucket Name':<40} {'Size (bytes)':<15} {'Content Type':<25} {'Last Modified':<30}")
            print("-" * 250)

            for row in results:
                file_name, bucket_name, file_size, content_type, last_modified = row
                formatted_last_modified = str(last_modified)
                print(f"{file_name:<50} {bucket_name:<40} {file_size:<15} {content_type:<25} {formatted_last_modified:<30}")

    except pymysql.MySQLError as e:
        print(f"Database query error: {e}")
        sys.exit(1)


def process_s3_event(connection):
    """Process S3 events received via SQS."""
    print("Waiting for new S3 object events...")
    while True:
        response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=20)
        if 'Messages' not in response:
            print("No new messages in SQS. Waiting...")
            continue

        for message in response['Messages']:
            print("\nReceived SQS Message: ", message['Body'])
            try:
                event = json.loads(message['Body'])
                if 'Records' not in event:
                    print("Warning: No 'Records' key found in SQS message. Skipping message.")
                    continue

                # Extract bucket name and object key
                bucket_name = event['Records'][0]['s3']['bucket']['name']
                object_key_encoded = event['Records'][0]['s3']['object']['key']
                object_key = urllib.parse.unquote(object_key_encoded).replace("+", " ")

                # Fetch object metadata
                s3_metadata = s3.head_object(Bucket=bucket_name, Key=object_key)
                file_size = s3_metadata['ContentLength']
                content_type = s3_metadata['ContentType']
                last_modified = s3_metadata['LastModified']

                # Insert metadata into RDS
                insert_metadata_into_rds(connection, object_key, bucket_name, file_size, content_type, last_modified)
                print("\nMessage processed and deleted from SQS. Metadata stored in RDS.")
                sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])

                # Prompt user for next action
                while True:
                    action = input("\nChoose next action: [P]rocess another S3 event, [V]iew stored metadata, or [E]xit: ").strip().lower()
                    if action == 'p':
                        print("Waiting for new S3 object events...")
                        break
                    elif action == 'v':
                        fetch_all_metadata_from_rds(connection)
                    elif action == 'e':
                        print("Exiting script.")
                        connection.close()
                        sys.exit(0)
                    else:
                        print("Invalid input. Please enter 'P', 'V', or 'E'.")

            except json.JSONDecodeError:
                print("Error: Failed to parse SQS message JSON. Skipping message.")


if __name__ == "__main__":
    connection = connect_to_rds()
    ensure_table_exists(connection)
    process_s3_event(connection)
