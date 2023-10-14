from __future__ import annotations

import asyncio
import os
from io import BytesIO

import miniopy_async
from miniopy_async import Minio

from server.adapters.outbound.s3_uploader.models import UploadingResponse

try:
    from server.common.logs import logger
except ImportError:
    import logging

    logger = logging
    logger.warning('failed to import project logger; use default logging')


class MinioUploader:

    def __init__(self, host: str, user: str, password: str, max_retries: int, before_retry_timeout_s: int):
        self._host = host
        self._client = Minio(
            host[host.find('://') + 3:],
            access_key=user,
            secret_key=password,
            secure=True if "https" in host else False
        )
        self._max_retries = max_retries
        self._before_retry_timeout_s = before_retry_timeout_s

    async def upload(self, bucket_name: str, file_name: str, file: BytesIO) -> UploadingResponse:
        is_saved = False
        retries = 0
        file_length = file.tell()
        file.seek(0)
        while not is_saved:
            try:
                await self._client.put_object(bucket_name, file_name, file, file_length)
            except (miniopy_async.error.S3Error, BaseException) as e:
                if isinstance(e, miniopy_async.error.S3Error) and e.code == "NoSuchBucket":
                    raise e
                elif retries >= self._max_retries:
                    break
                else:
                    logger.warning(f'[{retries}|{self._max_retries}] retry: data saving failed; '
                                   f'sleep {self._before_retry_timeout_s} s and retry')
                    await asyncio.sleep(self._before_retry_timeout_s)
                retries += 1
            else:
                is_saved = True
        if not is_saved:
            logger.critical(f"data saving failed after {self._max_retries} retries")
        return UploadingResponse(success=is_saved,
                                 image_url=os.path.join(self._host, bucket_name, file_name))
