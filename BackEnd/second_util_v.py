# Python
from typing import Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed

# FastAPI
from fastapi import UploadFile

# AWS
from boto3.session import Session

# APP
from config import BUCKET_NAME as bucket_name


class S3Manager:
    def __init__(self, s3, upload_id: str, file: UploadFile) -> None:
        self.s3 = s3
        self.upload_id: str = upload_id
        self.file: UploadFile = file


def upload_part(part_info):
    """
    Uploads a part of the large file to S3 bucket
    """
    # Get the part from file
    s3_data, part_number, start, end = part_info

    # Init S3 manager
    s3_manager: S3Manager = s3_data
    
    # Upload part
    s3_manager.file.file.seek(start)
    
    data = s3_manager.file.file.read(end - start + 1)
    response = s3_manager.s3.upload_part(
        Bucket=bucket_name,
        Key=s3_manager.file.filename,
        PartNumber=part_number,
        UploadId=s3_manager.upload_id,
        Body=data
    )
    return {'PartNumber': part_number, 'ETag': response['ETag']}


def get_part_info_list(s3_data: S3Manager, part_number, file_size, part_size):
    start = part_number * part_size
    end = min((part_number + 1) * part_size - 1, file_size - 1)
    part_number = part_number + 1
    return (s3_data, part_number, start, end)


def run_in_thread(aws_mag_con: Session, file: UploadFile) -> dict:
    # S3 client
    file_key = file.filename
    s3 = aws_mag_con.client('s3')
    response = s3.create_multipart_upload(Bucket=bucket_name, Key=file_key)

    # Upload file
    upload_id: str = response['UploadId']
    file_size: int = file.size
    part_size: int = 100 * 1024**2
    s3_data: S3Manager = S3Manager(s3, upload_id, file)
    num_parts: int = (file_size + part_size - 1) // part_size
    
    # Get part info list
    part_info_list: list = [get_part_info_list(
        s3_data, i, file_size, part_size
    ) for i in range(num_parts)]

    # Thread pool
    pool = ThreadPoolExecutor(max_workers=4)
    part_s: Iterator = pool.map(upload_part, part_info_list)
    as_completed(part_s)

    # Complete upload
    part_responses: list = [part for part in part_s]

    parts = [{'PartNumber': pr['PartNumber'], 'ETag': pr["ETag"]}
             for pr in part_responses]

    try:
        response = s3.complete_multipart_upload(
            Bucket=bucket_name,
            Key=file_key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        return {"message": "Success"}
    except Exception as e:
        s3.abort_multipart_upload(
            Bucket=bucket_name, Key=file_key, UploadId=upload_id)
        return {"message": f"Some problems {e}"}
