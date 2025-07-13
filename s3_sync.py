import os
import json
import hashlib
from pathlib import Path
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def load_config(config_path='config.json'):
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        exit(1)
    with open(config_path, 'r') as f:
        return json.load(f)

def get_s3_client(access_key, secret_key, region='us-east-1'):
    return boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

def etag_matches(local_path, etag):
    if not os.path.exists(local_path):
        return False

    hash_md5 = hashlib.md5()
    with open(local_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)

    local_md5 = hash_md5.hexdigest()
    return etag.strip('"') == local_md5

def should_download(s3_obj, local_path):
    if not os.path.exists(local_path):
        return True

    local_size = os.path.getsize(local_path)
    s3_size = s3_obj['Size']
    local_mtime = int(os.path.getmtime(local_path))
    s3_mtime = int(s3_obj['LastModified'].timestamp())

    if local_size == s3_size and local_mtime == s3_mtime:
        print(f"⏩ Skipping (same size & mtime): {local_path}")
        return False

    if '-' not in s3_obj['ETag']:
        if etag_matches(local_path, s3_obj['ETag']):
            print(f"⏩ Skipping (same checksum): {local_path}")
            return False

    return True

def download_from_s3(bucket, prefix, local_dir, s3):
    print(f"🔍 Starting download from bucket: '{bucket}', prefix: '{prefix}'")
    paginator = s3.get_paginator('list_objects_v2')

    try:
        page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
    except ClientError as e:
        print(f"❌ Failed to list bucket objects: {e}")
        return

    found_files = False

    for page in page_iterator:
        if 'Contents' not in page:
            print("⚠️ No files found under this prefix.")
            continue

        print(f"📦 Found {len(page['Contents'])} objects in this page.")
        for obj in page['Contents']:
            key = obj['Key']
            if key.endswith('/'):
                print(f"📁 Skipping folder key: {key}")
                continue

            found_files = True
            rel_path = os.path.relpath(key, prefix)
            local_path = os.path.join(local_dir, rel_path)

            if should_download(obj, local_path):
                Path(local_path).parent.mkdir(parents=True, exist_ok=True)
                print(f"⬇️ Downloading: {key} -> {local_path}")
                try:
                    s3.download_file(bucket, key, local_path)
                    os.utime(local_path, (obj['LastModified'].timestamp(), obj['LastModified'].timestamp()))
                except ClientError as e:
                    print(f"❌ Failed to download {key}: {e}")
            else:
                print(f"✅ Already up to date: {key}")

    if not found_files:
        print("🚫 No downloadable files found.")

if __name__ == "__main__":
    try:
        config = load_config()
        s3 = get_s3_client(
            config['access_key'],
            config['secret_key'],
            config.get('region', 'us-east-1')
        )
        download_from_s3(
            config['bucket'],
            config.get('prefix', ''),
            config.get('local_dir', './downloaded'),
            s3
        )
    except NoCredentialsError:
        print("❌ AWS credentials not found or invalid.")
    except KeyboardInterrupt:
        print("\n🛑 Download interrupted by user (Ctrl+C). Exiting gracefully.")
