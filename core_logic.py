import cv2
import numpy as np
from ultralytics import YOLO
from collections import deque

from deep_sort.deep_sort.tracker import Tracker
from deep_sort.deep_sort import nn_matching
from deep_sort.deep_sort.detection import Detection
from deep_sort.tools import generate_detections as gdet

class VehicleCounter:
    def __init__(self, video_path):
        self.model = YOLO("yolov8s.pt")
        encoder = gdet.create_box_encoder("config/mars-small128.pb", batch_size=1)
        metric = nn_matching.NearestNeighborDistanceMetric("cosine", 0.4, None)
        self.tracker = Tracker(metric)
        self.encoder = encoder
        self.class_names = open("config/coco.names").read().strip().split("\n")
        self.colors = np.random.randint(0, 255, size=(len(self.class_names), 3))
        self.cap = cv2.VideoCapture(video_path)
        self.counting_areas = []
        self.points = [deque(maxlen=32) for _ in range(1000)]
        self.track_status = {}

    def run(self, zones):
        zone_config = self.process_zones(zones)
        for frame_idx in range(int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))):
            ret, frame = self.cap.read()
            if not ret:
                break

            results = self.model(frame)
            bboxes, confidences, class_ids = [], [], []

            for result in results:
                for data in result.boxes.data.tolist():
                    x1, y1, x2, y2, conf, cls_id = data
                    if conf > 0.5:
                        bboxes.append([int(x1), int(y1), int(x2 - x1), int(y2 - y1)])
                        confidences.append(conf)
                        class_ids.append(int(cls_id))

            names = [self.class_names[i] for i in class_ids]
            features = self.encoder(frame, bboxes)
            dets = [Detection(bbox, conf, name, feat) for bbox, conf, name, feat in zip(bboxes, confidences, names, features)]

            self.tracker.predict()
            self.tracker.update(dets)

            for track in self.tracker.tracks:
                if not track.is_confirmed() or track.time_since_update > 1:
                    continue

                x1, y1, x2, y2 = map(int, track.to_tlbr())
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                track_id = track.track_id
                class_name = track.get_class()
                color = tuple(map(int, self.colors[self.class_names.index(class_name)]))

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{track_id} - {class_name}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                while track_id >= len(self.points):
                    self.points.append(deque(maxlen=32))

                self.points[track_id].append((cx, cy))
                for i in range(1, len(self.points[track_id])):
                    if self.points[track_id][i - 1] and self.points[track_id][i]:
                        cv2.line(frame, self.points[track_id][i - 1], self.points[track_id][i], color, 2)

            # Draw zones
            for i in range(0, len(zone_config), 2):
                if i + 1 < len(zone_config):
                    cv2.line(frame, zone_config[i], zone_config[i + 1], (0, 255, 255), 2)

            yield frame

    def process_zones(self, raw_zones):
        return raw_zones.copy()