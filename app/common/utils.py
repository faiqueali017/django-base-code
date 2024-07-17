import os
import boto3
import requests

from django.conf import settings
from core.models import File

DEBUG = bool(int(os.environ.get("DEBUG", 0)))


def download_media(url, path="/app/temp/"):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.basename(url)
            filepath = os.path.join(path, filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            return filepath
        else:
            return None
    except Exception:
        return None


def remove_media(path):
    os.remove(path)


def get_file_extention(filename):
    return str(filename).split(".")[-1].lower()


def construct_s3_file_path(user_id, file_name):
    root = "testing" if DEBUG is True else "livedata"
    dir_name = "others" if user_id is None else f"users/{user_id}"
    file_path = f"{root}/{dir_name}/{file_name}"
    return file_path


def upload_media_to_s3(file_path, file_content):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    try:
        response = s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_path,
            Body=file_content,
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return True

        return False
    except Exception:
        return False


def get_file_type(file_name):
    file_extension = get_file_extention(file_name)

    image_extensions = ["jpg", "jpeg", "png", "gif", "bmp"]
    audio_extensions = ["mp3", "wav", "ogg", "flac"]
    video_extensions = ["mp4", "avi", "mkv", "mov"]

    if file_extension.lower() in image_extensions:
        return File.FileType.IMAGE
    elif file_extension.lower() in audio_extensions:
        return File.FileType.AUDIO
    elif file_extension.lower() in video_extensions:
        return File.FileType.VIDEO
    else:
        return None
