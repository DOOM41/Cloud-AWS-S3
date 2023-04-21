from fastapi import UploadFile

from boto3.session import Session
from boto3.s3.transfer import TransferConfig
from botocore.client import Config

from config import BUCKET_NAME


def run_in_thread(aws_mag_con: Session, file: UploadFile) -> dict:
    """
        Multipart uploading file in AWS S3
    """
    MB: int = 1024**2
    s3: Config = aws_mag_con.client('s3')
    config: TransferConfig = TransferConfig(
        multipart_threshold=100*MB,
        max_concurrency=4
    )
    # Upload file
    try:
        s3.upload_fileobj(
            Fileobj=file.file,
            Bucket=BUCKET_NAME,
            Key=file.filename,
            Config=config
        )
        return {"message": "Success"}
    except Exception as e:
        return {"message": f"Some problems {e}"}
