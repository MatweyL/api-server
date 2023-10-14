from server.common.config import BaseServiceConfig


class MinioUploaderConfig(BaseServiceConfig):
    host: str
    user: str
    password: str
    max_retries: int
    before_retry_timeout_s: int
    bucket_name: str

    class Config:
        env_prefix = 'minio_'


minio_uploader_config = MinioUploaderConfig()
