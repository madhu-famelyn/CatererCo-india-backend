import os
import uuid
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from core.deps import get_current_user
from models.user import User

router = APIRouter(prefix="/upload", tags=["upload"])

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "")
AWS_S3_BASE_URL = os.getenv("AWS_S3_BASE_URL", "")


def is_s3_configured() -> bool:
    return bool(
        AWS_ACCESS_KEY_ID
        and "YOUR_ACCESS_KEY" not in AWS_ACCESS_KEY_ID
        and AWS_SECRET_ACCESS_KEY
        and "YOUR_SECRET_KEY" not in AWS_SECRET_ACCESS_KEY
        and AWS_S3_BUCKET
    )


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
):
    """
    Uploads a file to AWS S3 (if credentials are set in .env) or local static storage fallback.
    Returns the public file URL.
    """
    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    filename = f"{uuid.uuid4().hex}{ext}"

    contents = await file.read()

    if is_s3_configured():
        try:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION,
            )
            content_type = file.content_type or "application/octet-stream"
            s3_client.put_object(
                Bucket=AWS_S3_BUCKET,
                Key=filename,
                Body=contents,
                ContentType=content_type,
            )

            if AWS_S3_BASE_URL:
                file_url = f"{AWS_S3_BASE_URL.rstrip('/')}/{filename}"
            else:
                file_url = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}"

            return {"url": file_url, "provider": "s3", "filename": filename}
        except (BotoCoreError, ClientError, Exception) as e:
            print(f"[S3 Upload Error] {e}")
            raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")
    else:
        # Local static upload fallback when AWS credentials are not yet configured in .env
        upload_dir = os.path.join(os.getcwd(), "static_uploads")
        os.makedirs(upload_dir, exist_ok=True)
        local_path = os.path.join(upload_dir, filename)

        with open(local_path, "wb") as f:
            f.write(contents)

        file_url = f"http://localhost:8000/static_uploads/{filename}"
        return {"url": file_url, "provider": "local_fallback", "filename": filename}
