import json
import asyncpg
import uuid
from faststream import FastStream
from faststream.kafka import KafkaBroker

from typing import List
from pydantic import BaseModel
from app.run import Service
from app.config import settings

broker = KafkaBroker(settings.KAFKA_URL)
app = FastStream(broker)


class PhotoTopic(BaseModel):
    id: uuid.UUID
    photo: List[str]
    user: int


class Data(BaseModel):
    photo: PhotoTopic


@broker.subscriber("photo")
async def handler(msg: Data):
    conn = await asyncpg.connect(host=settings.POSTGRES_HOST,
                                 port=settings.POSTGRES_PORT,
                                 user=settings.POSTGRES_USER,
                                 password=settings.POSTGRES_PASSWORD,
                                 database=settings.POSTGRES_DATABASE)
    ser = Service()
    output = await ser.get_images(msg.photo.photo)
    update_data = {"id": msg.photo.id, "result": json.dumps(output)}
            
    query = f"UPDATE result SET result = $2 WHERE id = $1"
    await conn.execute(query,update_data["id"], update_data["result"] )
    await conn.close()