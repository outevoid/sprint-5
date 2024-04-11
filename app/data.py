import boto3

SECRET_KEY = "11234567trewq1234"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

BUCKET_NAME = "async5"

session = boto3.session.Session()

s3 = session.client(
    aws_access_key_id="YCAJEdXIo95AU_tNDpncMk3ez",
    aws_secret_access_key="YCNRHS2x6icxDACH3ISA1C3o19axj24H94tVKuH8",
    service_name="s3",
    endpoint_url="https://storage.yandexcloud.net",
)
