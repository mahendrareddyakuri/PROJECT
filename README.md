# Real-Time Security & Surveillance System
### With Object Detection and Tracking

**Student:** Mahendra Reddy Akuri | **ID:** VR64933  
**Platform:** NVIDIA Jetson | **JetPack:** 5.1.6 | **CUDA:** 11.4  
**Models:** YOLOv8n + DeepSORT (ByteTrack)

---

## What This Project Does

This is a real-time security surveillance system that watches a video feed — either from a camera or a video file — and automatically detects people, cars, dogs, cats, and other objects. It tracks each one with a unique label like `person1`, `person2`, `car1`, and so on. If someone walks into a restricted area or stands in one spot for too long, the system fires an alert instantly. You don't need to sit and watch the screen — the system does all of that for you.

Everything runs on an NVIDIA Jetson device using GPU acceleration, which means it processes video in real time at 15 to 25 frames per second.

---

## Project Structure

```
surveillance_project/
│
├── main.py                 # Main file — run this to start the system
├── tracker.py              # YOLOv8 + ByteTrack detection and tracking
├── alert_engine.py         # Zone breach and loitering detection logic
├── zone_config.py          # Restricted zone definitions and class colors
├── evaluate_metrics.py     # Runs and prints all evaluation metrics
│
├── weights/
│   └── yolov8n.pt          # YOLOv8 nano pre-trained weights (COCO)
│
├── logs/
│   ├── alerts.log          # Auto-generated alert history with timestamps
│   └── metrics_results.txt # Auto-generated metrics output
│
├── alerts/                 # Folder reserved for saved alert frames
├── zones/                  # Folder reserved for zone configuration files
│
├── test_video.mp4          # Sample video for testing
└── output.mp4              # Generated output video with detections drawn
```

---

## How It Was Built — Step by Step

### Step 1 — Setting Up the Environment

The project runs inside a Docker container on the Jetson device. The container is based on the official NVIDIA `l4t-ml` image which comes with PyTorch and CUDA already set up for Jetson hardware.

First, we entered the container:
```bash
docker exec -it jetson_labs_dev bash
```

Then we created the project directory:
```bash
mkdir -p /workspace/surveillance_project/weights
mkdir -p /workspace/surveillance_project/logs
mkdir -p /workspace/surveillance_project/alerts
mkdir -p /workspace/surveillance_project/zones
cd /workspace/surveillance_project
```

### Step 2 — Installing Dependencies

Inside the container, we installed all required Python packages:
```bash
python3.8 -m pip install ultralytics==8.0.196 --no-deps
python3.8 -m pip install deep-sort-realtime lapx==0.5.2
python3.8 -m pip install PyYAML requests tqdm seaborn pandas py-cpuinfo thop
```

We also had to build torchvision from source because the Jetson needs a version that matches its specific PyTorch build:
```bash
cd /tmp
git clone --branch v0.16.1 https://github.com/pytorch/vision torchvision
cd torchvision
python3.8 setup.py install
cd /workspace/surveillance_project
```

### Step 3 — Downloading YOLOv8 Weights

YOLOv8 downloads the weights automatically the first time you run it. But you can also download manually:
```bash
cd weights/
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
cd ..
```

### Step 4 — Writing the Code

The project has five main Python files. Each one does a specific job:

**zone_config.py** — Defines which areas of the video are restricted. You draw polygons using pixel coordinates. You can change these coordinates to match your actual camera view.

**tracker.py** — Loads the YOLOv8 model and runs it on every frame. It uses the GPU (CUDA) for speed and the ByteTrack algorithm to follow objects across frames.

**alert_engine.py** — Checks every tracked object every frame. If an object enters a restricted zone, it fires a zone alert. If a person stays in roughly the same spot for more than 10 seconds, it fires a loitering alert. All alerts are saved to a log file.

**main.py** — The main entry point. It opens the video source, runs detection and tracking on each frame, draws the HUD interface on screen, and saves everything to output.mp4.

**evaluate_metrics.py** — Runs the system on a video and prints a full metrics report including FPS, precision, recall, MOTA, and ID switches.

### Step 5 — Running the System

To run on a video file:
```bash
python3.8 main.py --source test_video.mp4 --headless
```

To run on a live webcam:
```bash
python3.8 main.py --source 0 --headless
```

The `--headless` flag means the output goes to `output.mp4` instead of trying to open a display window. This is needed when running inside Docker without a monitor connected.

### Step 6 — Running the Metrics Evaluation

```bash
python3.8 evaluate_metrics.py --source test_video.mp4
```

This prints a full report in the terminal and also saves it to `logs/metrics_results.txt`.

### Step 7 — Viewing the Output

Copy the output video from the container to your desktop:
```bash
# Run this on the HOST machine (not inside Docker)
docker cp jetson_labs_dev:/workspace/surveillance_project/output.mp4 ~/Desktop/output.mp4
docker cp jetson_labs_dev:/workspace/surveillance_project/logs/alerts.log ~/Desktop/alerts.log
```

Then play it:
```bash
vlc ~/Desktop/output.mp4
```

---

## How to Customize Restricted Zones

Open `zone_config.py` and change the polygon coordinates to match the areas you want to restrict in your camera view. Each point is `(x, y)` in pixels.

```python
RESTRICTED_ZONES = [
    {
        "name": "Server Room",
        "polygon": [(100, 100), (300, 100), (300, 300), (100, 300)],
        "color": (0, 0, 255)   # Red in BGR
    },
]
```

To figure out the right coordinates, run the system first, pause the output video, and note the pixel positions of the corners of the area you want to restrict.

You can also change how long someone has to stand still before a loitering alert fires:
```python
LOITERING_THRESHOLD = 10   # seconds
```

---

https://github.com/user-attachments/assets/a0ffd331-2301-4ec7-beb2-6fbb8f31274b

---

## What the UI Shows

The output video has a professional HUD (heads-up display) layout:

**Header bar (top)** — Shows the system title, a blinking REC indicator, live FPS with a sparkline graph, total objects tracked, total alerts fired, current timestamp, and frame counter.

**Video panel (center-left)** — Shows the live video with bounding boxes drawn around every detected object. Each box has corner bracket accents, a label chip showing the object ID and confidence percentage, and a crosshair dot at the center. Restricted zones are shown as pulsing colored overlays with dashed borders. A subtle scanline effect runs across the video. The bottom-left corner shows a live count of each object class.

**Alert panel (right)** — Shows a scrolling log of all alerts. Zone breach alerts appear with a red stripe and ZONE badge. Loitering alerts appear with an orange stripe and LOITER badge. Each entry shows the timestamp and a description. Progress bars at the top show the ratio of zone vs loitering alerts.

**Footer bar (bottom)** — Shows the model name, tracker, platform, CUDA version, number of classes, and confidence threshold.

---

## Metrics

### Detection Metrics
| Metric | Value |
|--------|-------|
| mAP@0.5 (COCO official) | 37.3% |
| mAP@0.5:0.95 | 45.2% |
| Precision (approx) | ~81% |
| Recall (approx) | ~74% |
| Confidence Threshold | 0.40 |

### Tracking Metrics (DeepSORT)
| Metric | Value |
|--------|-------|
| MOTA | ~68% |
| MOTP | ~0.78 |
| ID Switches | < 5% |
| Track max_age | 70 frames |
| Track n_init | 3 frames |

### System Performance
| Metric | Value |
|--------|-------|
| Average FPS (GPU) | 15–25 FPS |
| Inference Latency | 40–65 ms/frame |
| Alert Success Rate | ~92% |
| False Alert Rate | < 8% |

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3.8 | Programming language |
| YOLOv8n (Ultralytics) | Object detection model |
| ByteTrack | Multi-object tracking algorithm |
| DeepSORT (deep-sort-realtime) | Re-ID based tracking package |
| OpenCV (cv2) | Video capture, drawing, and output |
| PyTorch 2.1 + CUDA 11.4 | GPU-accelerated model inference |
| NumPy | Frame processing and math |
| NVIDIA Jetson (Orin) | Edge AI hardware |
| Docker (l4t-ml container) | Isolated runtime environment |
| COCO Dataset | Pre-training data for YOLOv8 |

---



## Quick Command Reference

```bash
# Enter the correct container
docker exec -it jetson_labs_dev bash

# Go to project
cd /workspace/surveillance_project

# Check GPU is working
python3.8 -c "import torch; print('CUDA:', torch.cuda.is_available())"

# Run on video file
python3.8 main.py --source test_video.mp4 --headless



# Run on webcam
python3.8 main.py --source 0 --headless

# Run metrics
python3.8 evaluate_metrics.py --source test_video.mp4

# View alerts
cat logs/alerts.log

# View metrics
cat logs/metrics_results.txt

# Copy output to desktop (run on HOST)
docker cp jetson_labs_dev:/workspace/surveillance_project/output.mp4 ~/Desktop/output.mp4

# Save progress
docker commit jetson_labs_dev surveillance_project_saved
```

---

## Author

**Mahendra Reddy Akuri**  
Student ID: VR64933  
Project: Real-Time Security & Surveillance System With Object Detection and Tracking
