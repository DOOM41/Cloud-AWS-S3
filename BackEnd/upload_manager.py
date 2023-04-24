from fastapi import UploadFile


class Part():
    def __init__(self, id, e_tag, upload_id) -> None:
        self.id: int = id
        self.e_tag: str = e_tag
        self.upload_id: str = upload_id

    def to_dict(self):
        return {
            'PartNumber': self.id,
            'ETag': self.e_tag
        }


class UploadManager():
    def __init__(self, s3_client, bucket_name) -> None:
        self.s3_client = s3_client
        self.buket_name: str = bucket_name
        self.parts_by_file_key: dict = {}

    def create_multipart_upload(self, file_key: str) -> dict:
        response = self.s3_client.create_multipart_upload(
            Bucket=self.buket_name,
            Key=file_key
        )
        return response

    def upload_part(self, file_key: str, upload_id: str, chunk_index, file_part: UploadFile) -> dict:
        response = self.s3_client.upload_part(
            Bucket=self.buket_name,
            Key=file_key,
            PartNumber=chunk_index,
            UploadId=upload_id,
            Body= file_part.file.read()
        )
        part: Part = Part(chunk_index, response['ETag'], upload_id)
        self.add_part(file_key, part)
        return part

    def complete_multipart_upload(self, file_key: str, upload_id: str, parts: list) -> dict:
        return self.s3_client.complete_multipart_upload(
            Bucket=self.buket_name,
            Key=file_key,
            UploadId=upload_id,
            MultipartUpload={
                'Parts': parts
            }
        )

    def add_part(self, file_key: str, part: Part):
        if file_key in self.parts_by_file_key:
            self.parts_by_file_key[file_key].append(part)
        else:
            self.parts_by_file_key[file_key] = [part]

    def get_parts_and_upload_id(self, file_key: str) -> tuple:
        parts = [part.to_dict() for part in self.parts_by_file_key[file_key]]
        parts.sort(key=lambda part: part['PartNumber'])
        upload_id = self.parts_by_file_key[file_key][0].upload_id
        return parts, upload_id

    def remove_file_key(self, file_key: str):
        del self.parts_by_file_key[file_key]

    def get_upload_id(self, file_key: str) -> str:
        return self.parts_by_file_key[file_key][0].upload_id
