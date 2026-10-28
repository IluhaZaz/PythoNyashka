from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
import boto3
from botocore.client import Config


class S3Config(BaseSettings):
    endpoint_url: str = Field(default="http://localhost:9000")
    access_key: str = Field(default="minioadmin")
    secret_key: SecretStr = Field(default="minioadmin")
    bucket_name: str = Field(default="media")

    model_config = SettingsConfigDict(env_prefix="s3_")


class S3Client:
    def __init__(self, config: S3Config):
        self.config = config
        self.client = boto3.client(
            "s3",
            endpoint_url=config.endpoint_url,
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key.get_secret_value(),
            config=Config(signature_version="s3v4"),
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.client.head_bucket(Bucket=self.config.bucket_name)
        except Exception:
            self.client.create_bucket(Bucket=self.config.bucket_name)

    def upload_file(self, file_bytes: bytes, file_key: str, content_type: str) -> None:
        self.client.put_object(
            Bucket=self.config.bucket_name,
            Key=file_key,
            Body=file_bytes,
            ContentType=content_type,
        )

    def get_file(self, file_key: str) -> bytes:
        response = self.client.get_object(
            Bucket=self.config.bucket_name,
            Key=file_key,
        )
        return response["Body"].read()