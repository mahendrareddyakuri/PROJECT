# main.py
import cv2
import numpy as np
import time
import argparse
from ultralytics import YOLO
from tracker import PersonTracker
from alert_engine import AlertEngine
from zone_config import RESTRICTED_ZONES

def draw_zones(frame):
    """Draw restricted zones on frame."""
    overlay = frame.copy()
    for zone in RESTRICTED_ZONES:
        pts = np.array(zone["polygon"], np.int32).reshape((-1, 1, 2))
        cv2.fillPoly(overlay, [pts], zone["color"])
        cv2.polylines(frame, [pts], True, zone["color"], 2)
        # Zone label
        cx = int(sum(p[0] for p in zone["polygon"]) / len(zone["polygon"]))
        cy = int(sum(p[1] for p in zone["polygon"]) / len(zone["polygon"]))
        cv2.putText(frame, f"RESTRICTED: {zone['name']}", (cx-60, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

def draw_tracks(frame, tracks, alerts_this_frame):
    """Draw bounding boxes and IDs."""
    alerted_ids = {a.get("track_id") for a in alerts_this_frame if "track_id" in a}
    for track in tracks:
        x1, y1, x2, y2, tid = track
        color = (0, 0, 255) if tid in alerted_ids else (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"ID: {tid}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

def draw_fps(frame, fps):
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

def draw_alert_banner(frame, alerts):
    """Show active alerts at the bottom of the frame."""
    h, w = frame.shape[:2]
    y = h - 20 * len(alerts) - 10
    for alert in alerts[-5:]:  # show last 5 alerts max
        cv2.putText(frame, alert["message"], (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
        y += 22

def main(source):
    print("[INFO] Loading YOLOv8 model...")
    model = YOLO("weights/yolov8n.pt")

    print("[INFO] Loading DeepSORT tracker...")
    tracker = PersonTracker()

    alert_engine = AlertEngine()
    recent_alerts = []

    print(f"[INFO] Opening video source: {source}")
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"[ERROR] Cannot open video source: {source}")
        return

    frame_count = 0
    start_time = time.time()

    print("[INFO] Starting surveillance loop. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[INFO] End of stream.")
            break

        frame_count += 1
        t0 = time.time()

        # --- DETECTION ---
        results = model(frame, classes=[0], conf=0.4, verbose=False)  # class 0 = person
        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                detections.append([x1, y1, x2, y2, conf])

        # --- TRACKING ---
        tracks = tracker.update(detections, frame)
        active_ids = [t[4] for t in tracks]
        alert_engine.cleanup_lost_tracks(active_ids)

        # --- ALERT CHECKS ---
        frame_alerts = []
        for track in tracks:
            x1, y1, x2, y2, tid = track
            center = ((x1 + x2) // 2, (y1 + y2) // 2)

            zone_alerts = alert_engine.check_restricted_zone(tid, center)
            loiter_alerts = alert_engine.check_loitering(tid, center)

            for a in zone_alerts + loiter_alerts:
                a["track_id"] = tid
                frame_alerts.append(a)
                recent_alerts.append(a)

        recent_alerts = recent_alerts[-10:]  # keep last 10

        # --- DRAWING ---
        draw_zones(frame)
        draw_tracks(frame, tracks, frame_alerts)
        draw_alert_banner(frame, recent_alerts)

        fps = 1.0 / (time.time() - t0 + 1e-9)
        draw_fps(frame, fps)

        # Person count
        cv2.putText(frame, f"People: {len(tracks)}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        cv2.imshow("Surveillance System", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Quit requested.")
            break

    cap.release()
    cv2.destroyAllWindows()
    total_time = time.time() - start_time
    avg_fps = frame_count / total_time
    print(f"[INFO] Done. Processed {frame_count} frames in {total_time:.1f}s — avg {avg_fps:.1f} FPS")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, default="0",
                        help="Video source: 0 for webcam, or path to video file")
    args = parser.parse_args()

    source = int(args.source) if args.source.isdigit() else args.source
    main(source)
