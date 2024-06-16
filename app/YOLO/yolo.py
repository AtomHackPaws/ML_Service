import onnxruntime
import numpy as np
import yaml
import cv2


class YOLO:
    def __init__(self, model: str, classes: str, score_thr: float, conf_thr: float, iou_thr: float):
        self.font      = cv2.FONT_HERSHEY_SIMPLEX
        self.model     = model
        self.classes   = classes
        self.score_thr = score_thr
        self.conf_thr  = conf_thr
        self.iou_thr   = iou_thr
        self.create_session()

    def create_session(self) -> None:
        opt_session = onnxruntime.SessionOptions()
        opt_session.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL

        self.session   = onnxruntime.InferenceSession(self.model, providers=["CPUExecutionProvider"])
        self.model_inp = self.session.get_inputs()
        self.model_out = self.session.get_outputs()
        self.inp_names = [self.model_inp[i].name for i in range(len(self.model_inp))]
        self.out_names = [self.model_out[i].name for i in range(len(self.model_out))]
        self.inp_height, self.inp_width = self.model_inp[0].shape[2:]

        with open(self.classes, "r") as f:
            file = yaml.safe_load(f)
            self.classes = file["names"]
            self.colors = [[0, 255, 0], [255, 255, 0], [0, 0, 255], [0, 255, 255], [255, 0 , 255]]
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (self.inp_width, self.inp_height))
        image = image / 255
        image = image.transpose(2, 0, 1)
        image = image[np.newaxis, :, :, :].astype(np.float32)
        return image

    def convert(self, x):
        # (x, y, w, h) -> (x1, y1, x2, y2)
        y = np.copy(x)
        y[..., 0] = x[..., 0] - x[..., 2] / 2 
        y[..., 1] = x[..., 1] - x[..., 3] / 2
        y[..., 2] = x[..., 0] + x[..., 2] / 2
        y[..., 3] = x[..., 1] + x[..., 3] / 2
        return y 

    def postprocess(self, outputs, img):
        height, width = img.shape[:2]
        pred   = np.squeeze(outputs).T
        scores = np.max(pred[:, 4:], axis=1)
        pred   = pred[scores > self.conf_thr, :]
        scores = scores[scores > self.conf_thr]
        class_ids = np.argmax(pred[:, 4:], axis=1)
        inp_shape = np.array([self.inp_width, self.inp_height, self.inp_width, self.inp_height])

        boxes  = pred[:, :4]
        boxes  = np.divide(boxes, inp_shape, dtype=np.float32)
        boxes *= np.array([width, height, width, height])
        boxes  = boxes.astype(np.int32)
        index  = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=self.score_thr, nms_threshold=self.iou_thr)
        detect = []
        for bbox, score, label in zip(self.convert(boxes[index]), scores[index], class_ids[index]):
            detect.append({"ID": label, "conf": score, "box": bbox})
        return detect

    def detect(self, img: np.ndarray) -> list:
        inp_img = self.preprocess(img)
        outputs = self.session.run(self.out_names, {self.inp_names[0]: inp_img})[0]
        out_img = self.postprocess(outputs, img)
        return out_img
    
    def defects_info(self, detections):
        labels = []
        scores = []
        for detect in detections:
            labels.append(detect["ID"])
            scores.append(detect["conf"])
        return labels, scores


    def draw(self, img, detections):
        for detect in detections:
            x1, y1, x2, y2 = detect["box"].astype(int)
            cls_id = detect["ID"]
            conf   = detect["conf"]

            label = f"{self.classes[cls_id]}: {conf:.2f}"
            color = self.colors[cls_id]
            

            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

            (label_w, label_h), _ = cv2.getTextSize(label, self.font, 0.5, 1)

            x = x1
            y = y1-10 if y1-10 > label_h else y1+10

            cv2.rectangle(img, (x, y-label_h), (x +label_w, y+label_h), color, cv2.FILLED)
            cv2.putText(img, label, (x, y), self.font, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        return img 
