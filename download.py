from dotenv import load_dotenv
from os import getenv
import boto3
from botocore.credentials import InstanceMetadataProvider, InstanceMetadataFetcher
from os import makedirs, path
import pandas as pd


load_dotenv()

data_dir, bucket = getenv("SEED_DIR"), getenv("S3_BUCKET")
makedirs(data_dir, exist_ok=True, mode=777)

locations = pd.read_csv(getenv("LOCATION_FILE"))
locations.to_csv(path.join(data_dir, "locations.csv"), index=False)

provider = InstanceMetadataProvider(
    iam_role_fetcher=InstanceMetadataFetcher(timeout=1000, num_attempts=2)
)
credentials = provider.load().get_frozen_credentials()
client = boto3.client(
    "s3",
    region_name=getenv("AWS_REGION"),
    aws_access_key_id=credentials.access_key,
    aws_secret_access_key=credentials.secret_key,
    aws_session_token=credentials.token,
)

files = client.list_objects_v2(Bucket=bucket, Prefix=data_dir)
for file in files["Contents"]:
    file_path = path.join(data_dir, file["Key"])
    client.download_file(bucket, file_path, file_path)
