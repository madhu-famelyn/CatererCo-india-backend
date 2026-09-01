import os
import uuid
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models.caterer import Caterer
from models.user import User
from core.deps import get_current_user
from pydantic import BaseModel

router = APIRouter(tags=["gallery"])

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "")
AWS_S3_BASE_URL = os.getenv("AWS_S3_BASE_URL", "")


from dotenv import load_dotenv

def is_s3_configured() -> bool:
    load_dotenv(override=True)
    key_id = os.getenv("AWS_ACCESS_KEY_ID", "")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    bucket = os.getenv("AWS_S3_BUCKET", "")
    return bool(
        key_id
        and "YOUR_ACCESS_KEY" not in key_id
        and secret_key
        and "YOUR_SECRET_KEY" not in secret_key
        and bucket
    )


def get_s3_client():
    load_dotenv(override=True)
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "ap-south-1"),
    )


def _get_my_caterer(db: Session, current_user: User) -> Caterer:
    from sqlalchemy import func
    caterer = db.query(Caterer).filter(
        (Caterer.owner_id == current_user.id) | (func.lower(Caterer.email) == current_user.email.lower())
    ).first()
    if not caterer:
        raise HTTPException(status_code=403, detail="No caterer profile found for your account")
    return caterer


def list_caterer_gallery_from_s3_or_local(caterer_id: str) -> list:
    """Lists images directly from AWS S3 folder (or local directory fallback) with zero database storage."""
    prefix = f"gallery/{caterer_id}/"

    if is_s3_configured():
        try:
            load_dotenv(override=True)
            bucket = os.getenv("AWS_S3_BUCKET")
            base_url = os.getenv("AWS_S3_BASE_URL", "")
            region = os.getenv("AWS_REGION", "ap-south-1")

            s3 = get_s3_client()
            res = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
            contents = res.get("Contents", [])
            # Sort by last modified date (newest first)
            contents.sort(key=lambda x: x["LastModified"], reverse=True)
            urls = []
            for obj in contents:
                key = obj["Key"]
                if key.endswith("/"):
                    continue
                if base_url:
                    file_url = f"{base_url.rstrip('/')}/{key}"
                else:
                    file_url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
                urls.append(file_url)
            return urls
        except Exception as e:
            print(f"[S3 List Gallery Error] {e}")
            return []
    else:
        # Local static directory fallback
        caterer_dir = os.path.join(os.getcwd(), "static_uploads", "gallery", caterer_id)
        if not os.path.exists(caterer_dir):
            return []
        files = os.listdir(caterer_dir)
        files.sort(key=lambda f: os.path.getmtime(os.path.join(caterer_dir, f)), reverse=True)
        return [f"http://localhost:8000/static_uploads/gallery/{caterer_id}/{f}" for f in files if not f.startswith(".")]


class DeletePhotoRequest(BaseModel):
    url: str


# ── /me routes (authenticated caterer) ───────────────────────

@router.get("/caterers/me/gallery")
def get_my_gallery(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    caterer = _get_my_caterer(db, current_user)
    urls = list_caterer_gallery_from_s3_or_local(caterer.id)
    return {"gallery": urls}


@router.post("/caterers/me/gallery", status_code=201)
async def upload_gallery_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Uploads photo directly to AWS S3 under prefix gallery/{caterer_id}/ without saving in DB."""
    caterer = _get_my_caterer(db, current_user)
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    s3_key = f"gallery/{caterer.id}/{filename}"
    contents = await file.read()

    if is_s3_configured():
        try:
            load_dotenv(override=True)
            bucket = os.getenv("AWS_S3_BUCKET")
            s3 = get_s3_client()
            content_type = file.content_type or "image/jpeg"
            s3.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=contents,
                ContentType=content_type,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")
    else:
        # Local fallback directory
        caterer_dir = os.path.join(os.getcwd(), "static_uploads", "gallery", caterer.id)
        os.makedirs(caterer_dir, exist_ok=True)
        with open(os.path.join(caterer_dir, filename), "wb") as f:
            f.write(contents)

    # Return refreshed gallery directly from S3
    urls = list_caterer_gallery_from_s3_or_local(caterer.id)
    return {"gallery": urls}


@router.delete("/caterers/me/gallery", status_code=200)
def delete_gallery_photo(
    data: DeletePhotoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deletes photo directly from AWS S3 bucket key."""
    caterer = _get_my_caterer(db, current_user)
    target_url = data.url.strip()

    if is_s3_configured():
        try:
            load_dotenv(override=True)
            bucket = os.getenv("AWS_S3_BUCKET")
            base_url = os.getenv("AWS_S3_BASE_URL", "")

            # Extract key from URL
            if base_url and target_url.startswith(base_url):
                s3_key = target_url.replace(base_url.rstrip('/') + "/", "")
            else:
                # Find prefix after amazonaws.com/
                parts = target_url.split(".amazonaws.com/")
                s3_key = parts[1] if len(parts) > 1 else target_url

            s3 = get_s3_client()
            s3.delete_object(Bucket=bucket, Key=s3_key)
        except Exception as e:
            print(f"[S3 Delete Error] {e}")
    else:
        # Delete from local fallback directory
        filename = os.path.basename(target_url)
        local_path = os.path.join(os.getcwd(), "static_uploads", "gallery", caterer.id, filename)
        if os.path.exists(local_path):
            os.remove(local_path)

    urls = list_caterer_gallery_from_s3_or_local(caterer.id)
    return {"gallery": urls}


# ── Public gallery by caterer ID ─────────────────────────────

@router.get("/caterers/{caterer_id}/gallery")
def get_public_gallery(caterer_id: str, db: Session = Depends(get_db)):
    caterer = db.query(Caterer).filter(Caterer.id == caterer_id).first()
    if not caterer:
        raise HTTPException(status_code=404, detail="Caterer not found")
    urls = list_caterer_gallery_from_s3_or_local(caterer_id)
    return {"gallery": urls}
