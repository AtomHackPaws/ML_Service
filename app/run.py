from io import BytesIO
import io
from typing import List
from PIL import Image
import numpy as np
import cv2
import os
from app.YOLO.yolo import YOLO
from PIL import Image

from app.S3.S3Service import S3Service
import asyncpg

    
class Service:
    def __init__(self):
        self.model = YOLO(
            model     = "app/YOLO/weights/v1.onnx",
            classes   = "app/YOLO/weights/atomic.yaml",
            score_thr = 0.1,
            conf_thr  = 0.1,
            iou_thr   = 0.1
        )
        self.conn = None 

    async def get_images(self, list_names: List[str]):
        output = []
        try:
            await S3Service.get_s3_client()
            for name in list_names:
                img = await S3Service.get_object(name)
                img = await img["Body"].read()
                img = self.bytes2numpy(img)
                img = img[:,:,:3]

                detects = self.model.detect(img)
                labels, scores = self.model.defects_info(detects)
                img_det = self.model.draw(img, detects)
                
                marked_name = name.split('.')[0] + "_marked." + "png"

                img_det = img_det.astype(np.uint8)
                
                image_pil = Image.fromarray(img_det)

                # Преобразование объекта PIL в байты
                img_byte_arr = io.BytesIO()
                image_pil.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                await S3Service.put_object(marked_name,  img_bytes )
                
                output.append({
                    "name": name,
                    "marked_name": marked_name,
                    "labels": list(map(lambda x: int(x), labels)),
                    "scores": list(map(lambda x: float(x), scores))
                })
            return output

        finally:
            await S3Service.close_s3_session()

    def bytes2numpy(self, object: bytes) -> np.ndarray:
        buf = BytesIO(object)
        img = Image.open(buf)
        return np.asarray(img, dtype="float32")

    def detect_image(self, image):
        detect = self.model.detect(image)
        image  = self.model.draw(image, detect)


    def test_on_hiden_dataset(self, path):
        with open("output/submission.csv", "w") as f:
            for file in os.listdir(path):
                print(f"Работа с изображением: {file}")
                image = cv2.imread(f"{path}{file}")
                detections = self.model.detect(image)
                h, w = image.shape[:2]

                for detect in detections:
                    x1, y1, x2, y2 = detect["box"].astype(int)
                    x1 /= w
                    y1 /= h
                    x2 /= w
                    y2 /= h

                    cls_id = detect["ID"]
                    center = [(x1 + y1) / 2, (x2 + y2) / 2]
                    width  = (x2 - x1)
                    height = (y2 - y1)

                    f.write(f"{file.split('.')[-2]};{cls_id};{center[0]};{center[1]};{width};{height}\n")
