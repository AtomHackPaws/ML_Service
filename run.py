from io import BytesIO
from PIL import Image
import numpy as np
import asyncio
import cv2
import os
from YOLO.yolo import YOLO

from S3.S3Service import S3Service


class Service:

    def __init__(self):
        self.model = YOLO(
            model     = "YOLO/weights/v8.onnx",
            classes   = "YOLO/weights/atomic.yaml",
            score_thr = 0.1,
            conf_thr  = 0.1,
            iou_thr   = 0.1
        )

    async def get_images(self, list_names):
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

                output.append({
                    "img": img_det.tobytes(),
                    "name": name,
                    "labels": labels,
                    "scores": scores
                })

            # print(output)
            # return output
        finally:
            await S3Service.close_s3_session()

    def bytes2numpy(self, object: bytes) -> np.ndarray:
        buf = BytesIO(object)
        img = Image.open(buf)
        return np.asarray(img, dtype="float32")

    def detect_image(self, image):
        # for file in os.listdir(path):
        # image = cv2.imread(f"{path}{file}")
        detect = self.model.detect(image)
        image  = self.model.draw(image, detect)
        # cv2.imwrite(f"output/{file.split('.')[0]}.jpg", image)

    # def on_video(self, path):
    #     video = cv2.VideoCapture(f"input/{path}")
    #     hist  = []
    #     while True:
    #         ret, image = video.read()
    #         if not ret:
    #             break
    #         detect = self.model.detect(image)
    #         hist.append(detect)

    #     image = self.model.draw(image, detect)

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

ser = Service()

# ser.test_on_hiden_dataset("/mnt/linux-860/NEW_Data_HACK/images/")

list_names = ["5 (126).jpg"]

if __name__ == "__main__":
    asyncio.run(ser.get_images(list_names))
