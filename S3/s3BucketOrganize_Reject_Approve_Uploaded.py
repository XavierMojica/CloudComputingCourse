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
