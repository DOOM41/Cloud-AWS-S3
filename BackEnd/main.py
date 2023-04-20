# FastAPI
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Uvicorn
import uvicorn

# AWS
from boto3.session import Session

# UTILS
from utils import run_in_thread

app = FastAPI(
    title="AWS App"
)

aws_mag_con: Session = Session(profile_name="default")

origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    result: dict = run_in_thread(aws_mag_con, file)
    return result

if __name__ == '__main__':
    uvicorn.run(app)
