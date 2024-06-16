"""
Нарезка исходных изображений и разметку на патчи.
Имеется возможность визуализации разметки.
"""
import numpy as np
import cv2
import os


VISION  = True  # Визуализация
WINDOW  = 640   # Размер окна
STRIDE  = 320   # Шаг скользящего окна

inp_path = "/mnt/linux-860/NEW_Data_HACK"  # Путь к сырым данным
out_path = "/mnt/linux-860/Dataset_HACK"   # Путь к новому датасету

colors = np.random.uniform(0, 255, size=(5, 3))

act_c = 0  # Счётчик патчей с дефектами
emp_c = 0  # Счётчик патчей без дефектов

def IoU(box1, box2, thr):
    # Координаты пересечения
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    # Площади исходных боксов
    sBox1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    sBox2 = (box2[2] - box2[0]) * (box2[3] - box2[1])

    # Площадь пересечения
    sInter = max(0, x2 - x1) * max(0, y2 - y1)

    iou = sInter / float(sBox1 + sBox2 - sInter)
    return [x1, y1, x2, y2] if iou > thr else None


for file in os.listdir(f"{inp_path}/images/"):
    if file.split(".")[-1] == "jpg":
        print(f"Работа с изображением: {file}")

        name  = file.split(".")[-2]
        image = cv2.imread(f"{inp_path}/images/" + file)
        height, width = image.shape[:2]
        print()

        # Координаты боксов
        boxes = []
        with open(f"{inp_path}/labels/{name}.txt", "r") as f:
            lines = [line.rstrip("\n").split(" ") for line in f]
            for l in lines:
                boxes.append([
                    l[0],
                    float(l[1]) * width,
                    float(l[2]) * height,
                    float(l[7]) * width,
                    float(l[8]) * height
                ])

        for h in range(WINDOW, height, STRIDE):
            for w in range(WINDOW, width, STRIDE):
                # Координаты патча
                frame = [w - WINDOW, h - WINDOW, w - 1, h - 1]

                # Боксы, пересекающиеся с патчем
                inter_boxes = []
                for bbox in boxes:
                    inter = IoU(frame, bbox[1:], 0.05)
                    if inter:
                        inter_boxes.append([bbox[0]] + inter)

                # Пропуск избыточных пустых патчей 
                # if len(inter_boxes) == 0 and (emp_c >= act_c):
                if len(inter_boxes) == 0:
                    continue

                # Сохранение оригинального патча
                crop  = image[h - WINDOW:h, w - WINDOW:w].copy()
                cv2.imwrite(f"{out_path}/images/{name}_{w}_{h}.jpg", crop)

                with open(f"{out_path}/labels/{name}_{w}_{h}.txt", "a") as f:
                    for bbox in inter_boxes:

                        x1 = bbox[1] - (w - WINDOW)
                        y1 = bbox[2] - (h - WINDOW)
                        x2 = bbox[3] - (w - WINDOW)
                        y2 = bbox[4] - (h - WINDOW)

                        if VISION:
                            cv2.rectangle(crop, (int(x1), int(y1)), (int(x2), int(y2)), colors[int(bbox[0])], 1)

                        center = [((x1 + x2) / 2) / WINDOW, ((y1 + y2) / 2) / WINDOW]
                        width1  = (x2 - x1) / WINDOW
                        height1 = (y2 - y1) / WINDOW

                        x1 /= WINDOW
                        y1 /= WINDOW
                        x2 /= WINDOW
                        y2 /= WINDOW

                        f.write(f"{bbox[0]} {str(center[0])} {str(center[1])} {str(width1)} {str(height1)}\n")
                        # f.write(f"{bbox[0]} {str(x1)} {str(y1)} {str(x1)} {str(y2)} {str(x2)} {str(y1)} {str(x2)} {str(y2)}\n")

                if len(inter_boxes) > 0:
                    act_c += 1
                else:
                    emp_c += 1

                if VISION:
                    cv2.imwrite(f"{out_path}/vision/{name}_{w}_{h}.jpg", crop)
