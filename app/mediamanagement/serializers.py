import os
import boto3
import time

from rest_framework import serializers
from rest_framework import status

from django.conf import settings
from core.models import File


class FileType:
    IMAGE = 0
    AUDIO = 1
    VIDEO = 2


ALLOWED_EXTENSIONS = ["jpeg", "jpg", "png", "mp3"]

DEBUG = bool(int(os.environ.get("DEBUG", 0)))


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            "file_id",
            "source_url",
            "file_type",
        ]


class FileUploadSerializer(serializers.Serializer):
    media = serializers.FileField(allow_empty_file=False)

    def get_file_extention(self, value):
        return str(value).split(".")[-1].lower()

    def get_file_type(self, file_extension):
        image_extensions = ["jpg", "jpeg", "png", "gif", "bmp"]
        audio_extensions = ["mp3", "wav", "ogg", "flac"]
        video_extensions = ["mp4", "avi", "mkv", "mov"]

        if file_extension.lower() in image_extensions:
            return FileType.IMAGE
        elif file_extension.lower() in audio_extensions:
            return FileType.AUDIO
        elif file_extension.lower() in video_extensions:
            return FileType.VIDEO
        else:
            return None

    def validate_file_type(self, value):
        extension = str(value).split(".")[-1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            return False
        return True

    def upload_to_s3(self, file_content, file_path):
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

    def upload_media(self, user_id=None):
        media = self.validated_data.get("media")
        if self.validate_file_type(media):
            # Form file uploading configs
            file_content = media.read()
            file_extension = self.get_file_extention(media)
            file_type = self.get_file_type(file_extension)
            root = "testing" if DEBUG is True else "livedata"
            dir_name = "others" if user_id is None else f"users/{user_id}"
            file_name = f"{int(time.time())}.{file_extension}"
            file_path = f"{root}/{dir_name}/{file_name}"

            # Upload to S3
            if self.upload_to_s3(file_content, file_path):
                s3_domain = settings.AWS_S3_CUSTOM_DOMAIN
                source_url = f"https://{s3_domain}/{file_path}"

                file_obj = File.objects.create(
                    source_url=source_url,
                    file_type=file_type,
                )
                response = FileSerializer(file_obj).data
                status_code = status.HTTP_200_OK
                return response, status_code

        message = {"message": "File type is not supported"}
        status_code = status.HTTP_400_BAD_REQUEST

        return message, status_code
