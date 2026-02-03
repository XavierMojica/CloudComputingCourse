"""
AWS Lambda: S3 File Validation and Routing
Put the Python Code in the Lambda > Functions > Code Source
Make sure to Press DEPLOY

This Lambda function is triggered by S3 object creation events and validates
files uploaded to the `incoming/` prefix of an S3 bucket.

Function behavior:
- Processes only objects stored under the `incoming/` folder
- Validates file extensions (pdf, jpg, jpeg, png)
- Enforces a maximum file size of 1 MB
- Routes approved files to `approved/`
- Routes rejected files to `rejected/`, including rejection reasons
- Uses an S3 copy-then-delete pattern to move objects

This function is designed as a serverless file-validation gate to enforce
upload policies and protect downstream processing pipelines.
"""






import boto3
import urllib.parse
import os
s3=boto3.client("s3")
ALLOWED_EXT = ['pdf', 'jpg', 'jpeg', 'png']
MAX_SIZE = 1 * 1024 * 1024
def lambda_handler(event, context):
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    size = event['Records'][0]["s3"]['object']['size'] 
    if not key.startswith('incoming/'):
        print("SkIPPEd (not in incoming/): ", key)
        return {"statusCode": 200, "message": "Skipped (not incoming/)"}
    filename = key.split("/")[-1]
    ext = filename.split(".")[-1].lower().strip() if "." in filename else ""
    #decide approval/rejection + reason 
    reasons = []
    if ext not in ALLOWED_EXT: 
        reasons.append(f"Extension not allowed: {ext}")
    if size > MAX_SIZE:
        reasons.append(f"File too large: {size} bytes (max {MAX_SIZE} bytes)")
    if len(reasons) == 0:
        decision = "APPROVED"
        target_key = key.replace("incoming/", "approved/", 1)
        reason_text = "Valid file"
    else:
        decision = "REJECTED"
        target_key = key.replace("incoming/", "rejected/", 1) 
        reason_text = " | ".join(reasons)
    #Move file (copy then delete)
    s3.copy_object(
        Bucket=bucket,
        CopySource={"Bucket": bucket, "Key": key},
        Key=target_key
    )
    s3.delete_object(Bucket=bucket, Key=key)

    print(f"{decision}: {filename} -> {reason_text}")
    print(f"Reason: {reason_text}")
    print(f"Details: ext={ext}, size = {size}")
    return {
        "statusCode": 200,
        "decision": decision, 
        "reason": reason_text, 
        "original_key": key, 
        "moved_to": target_key, 
        "ext": ext, 
        "size": size

    }


