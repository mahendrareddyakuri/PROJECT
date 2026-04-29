# alert_engine.py
import time
import cv2
import os
import numpy as np
from zone_config import RESTRICTED_ZONES, LOITERING_THRESHOLD

class AlertEngine:
    def __init__(self):
        self.person_timestamps = {}
        self.person_positions = {}
        self.alerts_triggered = set()
        self.log_file = "logs/alerts.log"
        os.makedirs("logs", exist_ok=True)
        os.makedirs("alerts", exist_ok=True)

    def point_in_polygon(self, point, polygon):
        x, y = point
        n = len(polygon)
        inside = False
        px, py = polygon[0]
        for i in range(1, n + 1):
            cx, cy = polygon[i % n]
            if ((py > y) != (cy > y)) and (x < (cx - px) * (y - py) / (cy - py) + px):
                inside = not inside
            px, py = cx, cy
        return inside

    def get_bbox_center(self, bbox):
        x1, y1, x2, y2 = bbox
        return (int((x1 + x2) / 2), (int(y1 + y2) / 2))

    def check_restricted_zone(self, track_id, center):
        alerts = []
        for zone in RESTRICTED_ZONES:
            if self.point_in_polygon(center, zone["polygon"]):
                alert_key = f"zone_{track_id}_{zone['name']}"
                if alert_key not in self.alerts_triggered:
                    self.alerts_triggered.add(alert_key)
                    msg = f"[ALERT] Person ID {track_id} entered restricted zone: {zone['name']}"
                    alerts.append({"type": "zone", "message": msg, "zone": zone})
                    self.log_alert(msg)
        return alerts

    def check_loitering(self, track_id, center):
        now = time.time()
        alerts = []
        if track_id not in self.person_timestamps:
            self.person_timestamps[track_id] = now
            self.person_positions[track_id] = center
            return alerts
        prev = self.person_positions[track_id]
        dist = np.sqrt((center[0] - prev[0])**2 + (center[1] - prev[1])**2)
        if dist > 80:
            self.person_timestamps[track_id] = now
            self.person_positions[track_id] = center
        else:
            elapsed = now - self.person_timestamps[track_id]
            alert_key = f"loiter_{track_id}"
            if elapsed > LOITERING_THRESHOLD and alert_key not in self.alerts_triggered:
                self.alerts_triggered.add(alert_key)
                msg = f"[ALERT] Person ID {track_id} loitering for {int(elapsed)}s"
                alerts.append({"type": "loiter", "message": msg})
                self.log_alert(msg)
        return alerts

    def log_alert(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        full_msg = f"[{timestamp}] {message}"
        print(full_msg)
        with open(self.log_file, "a") as f:
            f.write(full_msg + "\n")

    def cleanup_lost_tracks(self, active_ids):
        for tid in list(self.person_timestamps.keys()):
            if tid not in active_ids:
                self.person_timestamps.pop(tid, None)
                self.person_positions.pop(tid, None)
                self.alerts_triggered = {
                    k for k in self.alerts_triggered
                    if not k.endswith(f"_{tid}") and not k.startswith(f"loiter_{tid}")
                }
