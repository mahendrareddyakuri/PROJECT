# tracker.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'deep_sort'))

import numpy as np
from deep_sort.deep_sort import DeepSort

class PersonTracker:
    def __init__(self, model_path="models/deep_sort/mars-small128.pb"):
        self.tracker = DeepSort(
            model_path,
            max_dist=0.2,
            min_confidence=0.3,
            nms_max_overlap=1.0,
            max_iou_distance=0.7,
            max_age=70,
            n_init=3,
            nn_budget=100,
            use_cuda=True
        )

    def update(self, detections, frame):
        """
        detections: list of [x1, y1, x2, y2, confidence]
        Returns: list of [x1, y1, x2, y2, track_id]
        """
        if len(detections) == 0:
            return []

        bboxes = np.array([[d[0], d[1], d[2]-d[0], d[3]-d[1]] for d in detections])  # xywh
        confidences = np.array([d[4] for d in detections])

        outputs = self.tracker.update(bboxes, confidences, frame)
        results = []
        for output in outputs:
            x1, y1, x2, y2, track_id = output
            results.append([int(x1), int(y1), int(x2), int(y2), int(track_id)])
        return results
