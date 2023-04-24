from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from boto3.session import Session
import uvicorn

from config import BUCKET_NAME
from upload_manager import UploadManager


app = FastAPI(title="AWS App")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

aws_session = Session(profile_name="default")
s3_client = aws_session.client('s3')

upload_manager: UploadManager = UploadManager(s3_client, BUCKET_NAME)


@app.post('/upload')
def upload_file(
    file: UploadFile = File(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...)
) -> dict:
    file_key = file.filename
    if chunk_index == 1:
        # Get first part and create manager
        response = upload_manager.create_multipart_upload(file_key)
        upload_id: str = response['UploadId']
        upload_manager.upload_part(
            file_key, upload_id, chunk_index, file
        )
        return {"message": f"Part {chunk_index} uploaded successfully"}
    elif chunk_index == total_chunks:
        # add last part
        upload_id: str = upload_manager.get_upload_id(file_key)
        upload_manager.upload_part(
            file_key, upload_id, chunk_index, file
        )
        parts, upload_id = upload_manager.get_parts_and_upload_id(file_key)

        # complete upload
        response = upload_manager.complete_multipart_upload(
            file_key, upload_id, parts
        )
        upload_manager.remove_file_key(file_key)
        return {"message": "File uploaded successfully"}
    
    upload_id: str = upload_manager.get_upload_id(file_key)
    upload_manager.upload_part(
        file_key, upload_id, chunk_index, file
    )

    return {"message": f"Part {chunk_index} uploaded successfully"}


if __name__ == '__main__':
    uvicorn.run(app="main:app", reload=True, port=8000)
