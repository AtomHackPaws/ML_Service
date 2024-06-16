import aiobotocore.session
from aiobotocore.session import AioBaseClient, AioSession
from app.config import settings


class S3Service:
    session: AioSession | None = None
    s3_client: AioBaseClient | None = None

    @classmethod
    async def _get_s3_session(cls) -> AioSession:
        if cls.session is None:
            cls.session = aiobotocore.session.get_session()
        return cls.session

    @classmethod
    async def get_s3_client(cls) -> AioBaseClient:
        if cls.s3_client is None:
            session_ = await cls._get_s3_session()
            cls.s3_client = await session_.create_client(
                service_name="s3",
                endpoint_url=settings.MINIO_LINK,
                aws_access_key_id=settings.MINIO_ROOT_USER,
                aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
            ).__aenter__()
        return cls.s3_client

    @classmethod
    async def get_object(cls, img_name: str) -> dict:
        return await cls.s3_client.get_object(  # type: ignore
            Bucket=settings.MINIO_BUCKET, Key=img_name
        )  # type: ignore

    @classmethod
    async def put_object(cls, filename: str, file: bytes) -> dict:
        return await cls.s3_client.put_object(  # type: ignore
            Bucket=settings.MINIO_BUCKET, Key=filename, Body=file
        )  # type: ignore

    @classmethod
    async def close_s3_session(cls) -> None:
        if cls.s3_client is not None:
            await cls.s3_client.close()
            cls.session = None
            cls.s3_client = None
