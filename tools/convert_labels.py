"""
Первичная подготовка данных.
Перевод лэйблов из формата (x, y, w, h) в (x1, y1, x2, y2).
Имеется возможность визуализации разметки.
"""
import numpy as np
import shutil
import cv2
import os


VISION = True  # Визуализация

inp_path = "/mnt/linux-860/RAW_Data_HACK/dataset"  # Путь к сырым данным
out_path = "/mnt/linux-860/NEW_Data_HACK"  # Путь к новому датасету

colors = np.random.uniform(0, 255, size=(5, 3))

for file in os.listdir(inp_path):
    if file.split(".")[-1] == "txt":
        print(f"Работа с файлом: {file}")

        name  = file.split(".")[-2]
        image = cv2.imread(f"{inp_path}/{name}.jpg")
        h, w  = image.shape[:2]

        # Чтение исходной разметки
        with open(f"{inp_path}/{file}", "r") as f:
            lines = [line.rstrip("\n").split(" ") for line in f]

        # Запись разметки в новом формате
        with open(f"{out_path}/labels/{file}", "w") as f:
            for l in lines:

                # f.write(f"{l[0]} {l[1]} {l[2]} {l[3]} {l[4]}\n")

                x1 = float(l[1]) - float(l[3]) / 2
                y1 = float(l[2]) - float(l[4]) / 2
                x2 = float(l[1]) + float(l[3]) / 2
                y2 = float(l[2]) + float(l[4]) / 2

                f.write(f"{l[0]} {str(x1)} {str(y1)} {str(x1)} {str(y2)} {str(x2)} {str(y1)} {str(x2)} {str(y2)}\n")

                if VISION:
                    x1 = int(x1 * w)
                    y1 = int(y1 * h)
                    x2 = int(x2 * w)
                    y2 = int(y2 * h)
                    cv2.rectangle(image, (x1, y1), (x2, y2), colors[int(l[0])], 3)

        if VISION:
            cv2.imwrite(f"{out_path}/vision/{name}.jpg", image)

        # Копирование оригинала изображения
        shutil.copyfile(f"{inp_path}/{name}.jpg", f"{out_path}/images/{name}.jpg")
