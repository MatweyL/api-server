from server.adapters.outbound.s3_uploader.config import MinioUploaderConfig as ServerMinioUploaderConfig


class MinioUploaderConfig(ServerMinioUploaderConfig):

    class Config:
        env_prefix = 'minio_ml_worker_'


minio_uploader_config = MinioUploaderConfig()
