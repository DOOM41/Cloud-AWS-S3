from typing import Iterator
import boto3
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from boto3.session import Session
from fastapi import UploadFile
from config import BUCKET_NAME as bucket_name

def upload_part(s3, upload_id, part_info, file: UploadFile):
    """
    Uploads a part of the large file to S3 bucket
    """
    part_number, start, end = part_info
    file.seek(start)
    data = file.read(end - start + 1)
    response = s3.upload_part(
        Bucket=bucket_name,
        Key=file.filename,
        PartNumber=part_number,
        UploadId=upload_id,
        Body=data
    )
    return {'PartNumber': part_number, 'ETag': response['ETag']}


def get_part_info_list(part_number, file_size, part_size):
    part_number = part_number + 1
    start = part_number * part_size
    end = min((part_number + 1) * part_size - 1, file_size - 1)
    return (part_number, start, end)


def run_in_thread(aws_mag_con: Session, file: UploadFile) -> dict:
    # S3 client
    file_key = file.filename
    s3 = aws_mag_con.client('s3')
    response = s3.create_multipart_upload(Bucket=bucket_name, Key=file_key)

    # Upload file
    upload_id: str = response['UploadId']
    file_size: int = file.size()
    part_size: int = 50 * 1024**2

    num_parts: int = (file_size + part_size - 1) // part_size

    part_info_list: list = [get_part_info_list(
        i, file_size, part_size) for i in range(num_parts)]

    # Thread pool
    pool = ThreadPoolExecutor(max_workers=5)
    part_s: Iterator = pool.map(upload_part, part_info_list)
    pool.shutdown(wait=True)

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
