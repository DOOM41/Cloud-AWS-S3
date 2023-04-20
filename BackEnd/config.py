from dotenv import load_dotenv
import os

load_dotenv()

BUCKET_NAME: str = os.environ.get("BUCKET_NAME")
