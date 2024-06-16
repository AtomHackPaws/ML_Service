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

class Inference(BaseModel):
    user: int
    src: List[str]
    src_marked: List[str]

broker_send = broker.publisher("photo_out")


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
    src_marked = [item['marked_name'] for item in output]
    await broker_send.publish(
        Inference(user=msg.photo.user,
                  src=msg.photo.photo,
                  src_marked=src_marked),
        topic="photo_out"
    )