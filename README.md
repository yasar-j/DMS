# Driver Safety System (DMS)



\

An advanced **AI-based Driver Monitoring & Safety System** built using **Python, MediaPipe, YOLOv8, OpenCV, and Pygame**.

The system detects:

* 😴 Driver Drowsiness
* 👀 Driver Distraction
* 📱 Mobile Phone Usage

and simulates intelligent vehicle safety responses including:

* Driver alerts
* Speed limitation
* Emergency auto parking
* Hazard indicators
* Smart traffic-aware parking

---

# 📌 Features

## 😴 Drowsiness Detection

Uses **MediaPipe Face Mesh** and **Eye Aspect Ratio (EAR)** analysis to detect sleepy eyes and fatigue.

### Alert Levels

| Detection Count       | Action                     |
| --------------------- | -------------------------- |
| 1st Time              | "Please Be Awake!" warning |
| 2nd Time              | Speed limited to 60 km/h   |
| 3rd Time              | Speed limited to 40 km/h   |
| 4th Time              | Auto Parking Activated     |
| Continuous Drowsiness | Emergency Auto Parking     |

---

## 👀 Driver Distraction Detection

Tracks head movement and face orientation using MediaPipe.

If the driver looks away from the road:

* ⚠ "Focus On The Road" alert is displayed.

---

## 📱 Mobile Phone Detection

Uses **YOLOv8 Object Detection** to detect mobile phone usage while driving.

If a phone is detected:

* 📱 "Mobile Phone Detected" warning appears.

---

# 🧠 Technologies Used

* Python
* OpenCV
* MediaPipe
* YOLOv8
* Pygame
* NumPy

---

# 🎮 Simulation Features

The system includes a realistic driving simulation using **Pygame**:

* Dynamic traffic system
* Multiple vehicle types
* Realistic engine sounds
* Brake sounds
* Indicator sounds
* Horn simulation
* Speedometer UI
* Gear system
* Hazard lights
* Auto parking logic
* Collision effects
* Dashboard controls

---

# 🚦 Intelligent Auto Parking System

When the driver becomes dangerously drowsy:

1. Vehicle searches for safe parking space
2. Checks nearby traffic
3. Changes lane safely
4. Activates indicators & hazard lights
5. Parks automatically

The parking system includes:

* Traffic-aware lane checking
* Speed adaptation
* Gap creation logic
* Collision avoidance

---

# 🖥️ System Workflow

1. Webcam captures driver video
2. MediaPipe analyzes:

   * Eye movement
   * Face landmarks
   * Head direction
3. YOLOv8 detects mobile phones
4. AI decides safety actions
5. Pygame simulates vehicle behavior

---

# 📂 Project Structure

```bash
DMS/
│
├── DMS.py
├── yolov8n.pt
├── README.md
└── requirements.txt
```

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/yasar-j/DMS.git
cd DMS
```

---

## 2️⃣ Install Requirements

```bash
pip install -r requirements.txt
```

Or manually install:

```bash
pip install pygame numpy opencv-python mediapipe ultralytics
```

---

# ▶️ Run Project

```bash
python DMS.py
```

---

# 🎮 Controls

| Key   | Function              |
| ----- | --------------------- |
| ← / → | Move Vehicle          |
| ↑     | Accelerate            |
| ↓     | Brake                 |
| 1     | Gear P                |
| 2     | Gear R                |
| 3     | Gear N                |
| 4     | Gear D                |
| Q     | Left Indicator        |
| E     | Right Indicator       |
| Z     | Hazard Lights         |
| SPACE | Handbrake             |
| L     | Headlights            |
| H     | Horn                  |
| P     | Manual Auto Park Test |
| R     | Reset System          |
| ESC   | Exit                  |

---

# 📸 Output

The system displays:

* Driver alerts
* Speed restrictions
* Drowsiness warnings
* Phone detection warnings
* Auto parking simulation
* Real-time dashboard UI

---

# 🎯 Applications

* Driver Monitoring Systems (DMS)
* Advanced Driver Assistance Systems (ADAS)
* Smart Vehicles
* Accident Prevention Systems
* AI Transportation Research

---

# 🔮 Future Improvements

* Real vehicle integration
* GPS support
* Voice assistant alerts
* Cloud monitoring
* Deep learning optimization
* Night vision support
* Steering control integration

---

# 🛡️ Objective

This project aims to reduce road accidents caused by:

* Driver fatigue
* Distraction
* Mobile phone usage

through intelligent real-time monitoring and automated safety responses.

---

# 👨‍💻 Developed Using

* MediaPipe Face Mesh
* YOLOv8
* OpenCV
* Pygame
* Python AI Technologies

---

# ⭐ GitHub Repository

Repository Link:
https://github.com/yasar-j/DMS

---
