import aiobotocore.session
from aiobotocore.session import AioBaseClient, AioSession
import asyncio


MINIO_LINK="http://81.200.149.209:9200"
MINIO_ROOT_USER="atom"
MINIO_ROOT_PASSWORD="atom_password"
MINIO_BUCKET="atomic-bucket"


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
                endpoint_url=MINIO_LINK,
                aws_access_key_id=MINIO_ROOT_USER,
                aws_secret_access_key=MINIO_ROOT_PASSWORD,
            ).__aenter__()
        return cls.s3_client

    @classmethod
    async def get_object(cls, img_name: str) -> dict:
        return await cls.s3_client.get_object(  # type: ignore
            Bucket=MINIO_BUCKET, Key=img_name
        )  # type: ignore

    @classmethod
    async def put_object(cls, filename: str, file: bytes) -> dict:
        return await cls.s3_client.put_object(  # type: ignore
            Bucket=MINIO_BUCKET, Key=filename, Body=file
        )  # type: ignore

    @classmethod
    async def close_s3_session(cls) -> None:
        if cls.s3_client is not None:
            await cls.s3_client.close()
            cls.session = None
            cls.s3_client = None

# async def main():
#     images = []
#     try:
#         await S3Service.get_s3_client()
#         image = await S3Service.get_object(path)
#         res = await image["Body"].read()
#         res = bytes2numpy(res)
#         print(res[:,:,:3].shape)
#     finally:
#         await S3Service.close_s3_session()


# if __name__ == "__main__":
#     asyncio.run(main())
