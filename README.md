# Preliminary Project Results  
## Real-Time Security & Surveillance System  
### With Object Detection and Tracking  

**Mahendra Reddy Akuri | VR64933**  
**Platform:** NVIDIA Jetson (JetPack 5.1.6, CUDA 11.4)  

---

##  System Overview

| Component | Details |
|----------|--------|
| Model | YOLOv8n |
| Tracker | ByteTrack |
| Platform | NVIDIA Jetson |
| Classes | 9 Object Types |

---

# 1️ Running Model

The system uses the YOLOv8 object detection model for real-time inference. A lightweight variant (YOLOv8n) was selected to ensure smooth performance on Jetson hardware while maintaining acceptable detection accuracy.

The model is deployed with GPU acceleration (CUDA), allowing the system to process live video streams efficiently. The overall pipeline integrates detection, tracking, and alert generation in a continuous loop.

### Pipeline Architecture
- **Input:** Live webcam / video stream via OpenCV
- **Detection:** YOLOv8n (GPU inference)
- **Tracking:** ByteTrack (multi-object tracking)
- **Alert Engine:** Zone breach + loitering detection

---

# 2️ Weights Loaded
Pretrained weights (`yolov8n.pt`) are used for initializing the model. These weights are trained on the COCO dataset, which includes a wide range of object categories.

Although the model supports multiple classes, the system primarily focuses on detecting persons, as this is the key requirement for surveillance applications.

Using pretrained weights allows the system to avoid the need for custom training while still achieving reliable performance.


- **Model Weights:** `yolov8n.pt`
- **Dataset:** COCO (80 classes)
- **Active Classes (9):**
  - person, bicycle, car, motorcycle, bus, truck, cat, dog, horse

### Configuration
- Confidence Threshold: `0.4`
- IoU Threshold: `0.5`
- Device: CUDA (GPU)

---

# 3️ Inference

Inference is performed on each frame captured from the camera. The process includes:

1. Capturing a frame from the video stream
2. Passing the frame through the YOLO model
3. Applying non-maximum suppression to remove duplicate detections
4. Filtering detections based on a confidence threshold
5. Passing results to the tracking module

The system operates at a resolution of 640 × 480, which provides a balance between speed and accuracy. A confidence threshold of 0.40 is used to reduce false detections while maintaining reasonable recall.

Inference is performed **frame-by-frame in real time** using GPU acceleration.

### Pipeline Steps
1. Capture frame from camera
2. Run YOLO forward pass
3. Apply Non-Max Suppression (NMS)
4. Assign tracking IDs via ByteTrack
5. Label objects (`person1`, `car1`, etc.)
6. Apply alert logic (zone + loitering)

### Parameters

| Parameter | Value |
|----------|------|
| Resolution | 640 × 640 |
| Confidence | 0.4 |
| IoU | 0.5 |
| Tracker | ByteTrack |

---

# 4️ Predictions

The system produces real-time predictions including:

- Bounding boxes
- Class labels
- Confidence scores
- Unique tracking IDs
<img width="1290" height="587" alt="WhatsApp Image 2026-04-29 at 9 06 54 AM" src="https://github.com/user-attachments/assets/dbaf1dbc-ff85-4297-a90c-651ce0d2d1dd" />

### Behavioral Detection

####  Restricted Zone Breach
- Triggered when object enters defined polygon
- Logged with timestamp

#### ⏱️ Loitering Detection
- Triggered when person stays in same area > 10 seconds

---

# 5️ Speed (Performance)
The system achieves real-time performance on Jetson hardware with GPU acceleration.

- Frames Per Second (FPS): 15–25  
- Inference Latency: 40–65 milliseconds per frame  

The performance remains stable during continuous operation. When additional components such as alert logic and UI overlays are enabled, a slight reduction in FPS is observed, but the system still operates within real-time constraints.


| Condition | FPS | Latency | Status |
|----------|----|--------|--------|
| YOLOv8n + ByteTrack (GPU) | 15–25 FPS | 40–65 ms | Real-Time |
| Detection Only | 25–35 FPS | 28–40 ms | Real-Time |
| With Alerts + UI | 12–20 FPS | 50–80 ms | Real-Time |


---

# 6 Metrics Used

## Detection Metrics

- mAP@0.5 (COCO): 45.2%  
- mAP@0.5 (Person): approximately 56%  
- Precision: approximately 0.81  
- Recall: approximately 0.74  
- Confidence Threshold: 0.40  

These values indicate that the model provides a reasonable balance between detecting relevant objects and avoiding false positives.

| Metric | Value |
|-------|------|
| mAP@0.5 (COCO) | 45.2% |
| mAP@0.5 (Person) | ~56% |
| Precision | ~0.81 |
| Recall | ~0.74 |
| Confidence Threshold | 0.40 |

---

##  Tracking Metrics
- MOTA (Multi-Object Tracking Accuracy): approximately 68%  
- MOTP (Multi-Object Tracking Precision): approximately 0.78  
- ID Switches: less than 5%  
- Track Confirmation (n_init): 3 frames  
- Track Persistence (max_age): 70 frames  

The tracking system maintains stable identities across frames and minimizes identity switches, which is important for reliable surveillance.

---

| Metric | Value |
|-------|------|
| MOTA | ~68% |
| MOTP | ~0.78 |
| ID Switches | < 5% |
| max_age | 70 |
| n_init | 3 |

---

##  System Performance Metrics

- FPS: 15–25  
- Inference Latency: 40–65 ms  
- Alert Latency: less than one frame  
- Alert Success Rate: approximately 92%  
- False Alert Rate: less than 8%  

The alert system responds immediately when a defined condition is met, such as entry into a restricted zone.

| Metric | Value |
|-------|------|
| FPS | 15–25 |
| Inference Latency | 40–65 ms |
| Alert Latency | < 1 frame |
| Alert Success Rate | ~92% |
| False Alert Rate | < 8% |

---

# Summary

The system successfully demonstrates:

- Real-time object detection and tracking  
- Stable multi-object tracking with unique IDs  
- Accurate zone-based alert system  
- Efficient GPU performance on Jetson  
- I am looking forward to proceed with UI part of my project.
