# tracker.py
from deep_sort_realtime.deepsort_tracker import DeepSort

class PersonTracker:
    def __init__(self):
        self.tracker = DeepSort(
            max_age=70,
            n_init=3,
            nms_max_overlap=1.0,
            max_cosine_distance=0.2,
            nn_budget=100,
            embedder="mobilenet",
            half=True,
            bgr=True,
            embedder_gpu=True
        )

    def update(self, detections, frame):
        if len(detections) == 0:
            return []
        ds_input = []
        for d in detections:
            x1, y1, x2, y2, conf = d
            w = x2 - x1
            h = y2 - y1
            ds_input.append(([x1, y1, w, h], conf, "person"))
        tracks = self.tracker.update_tracks(ds_input, frame=frame)
        results = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            tid = track.track_id
            x1, y1, x2, y2 = map(int, track.to_ltrb())
            results.append([x1, y1, x2, y2, tid])
        return results
