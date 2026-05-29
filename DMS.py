import pygame
import sys
import numpy as np
import cv2
import mediapipe as mp
from ultralytics import YOLO

# ---------------- INIT ----------------
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI DRIVER SAFETY SYSTEM - ULTIMATE v3")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)
big_font = pygame.font.Font(None, 55)

# ---------------- GAME STATE ----------------
# ---------------- GAME STATE ----------------
car_x = (WIDTH - 60) // 2   # horizontal center
car_y = (HEIGHT - 110) // 2 # vertical center
car_speed = 8
road_speed = 5
lanes = [250, 500, 750, 1000]
score = 0
auto_park = False
parked = False
running = True

gear = "D"
left_indicator = False
right_indicator = False
hazard_on = False
handbrake = False
headlights_on = True
lights_blinking = False

# ---------------- TRAFFIC ----------------
traffic = []

vehicle_types = ["sedan", "suv", "truck"]

for _ in range(6):
    v_type = np.random.choice(vehicle_types)

    if v_type == "sedan":
        width, height = 60, 110
    elif v_type == "suv":
        width, height = 70, 130
    elif v_type == "truck":
        width, height = 80, 180

    traffic.append({
        "x": np.random.choice(lanes),
        "y": HEIGHT + np.random.randint(400,1200),  # spawn south
        "speed":  np.random.choice([60, 80, 120, 160, 200, 230], p=[0.15,0.15,0.2,0.2,0.15,0.15]),         # 60 → 230 km/h
        "w": width,
        "h": height,
        "type": v_type,
        "color": (
            np.random.randint(50,255),
            np.random.randint(50,255),
            np.random.randint(50,255)
        )
    })
parked_cars = []

shake_timer = 0
shake_intensity = 0

crashed = False
crash_cooldown = 0

alert_message = ""
alert_timer = 0
ALERT_DURATION = 3   # seconds

gear = "D"   # D = Drive, P = Park

# ---------------- SPEED LIMIT RECOVERY TIMER ----------------
SPEED_RESET_TIME = 300   # 5 minutes
speed_limit_start_time = None
speed_restored = False
speed_limited = False
speed_limit_value = 120
remaining = 0
pause_drowsy_detection = False


# ---------------- DROWSINESS ALERT COUNTER ----------------
drowsiness_alert_counter = 0

DROWSY_ALERT_COOLDOWN = 5   # seconds between alerts
last_drowsy_alert_time = 0

# ---------------- DROWSINESS TIMER ----------------
DROWSY_TRIGGER_SECONDS = 3
drowsy_start_time = None
DISTRACTION_TRIGGER_SECONDS = 2
distraction_start_time = None
# ---------------- DISTRACTION + PHONE STABILITY ----------------
DISTRACTION_CONFIRM_FRAMES = 15
PHONE_CONFIRM_FRAMES = 18
distraction_counter = 0
phone_counter = 0
# ---------------- SOUND ----------------
pygame.mixer.init(44100, -16, 2, 512)
sample_rate = 44100

# ---------------- ENGINE ACCELERATION SOUND ----------------
# ---------------- REALISTIC ENGINE SOUND ----------------
sample_rate = 44100
duration = 0.6

t_engine = np.linspace(0, duration, int(sample_rate * duration), False)

# Engine harmonics
base = np.sin(2 * np.pi * 90 * t_engine)      # low engine rumble
harm1 = np.sin(2 * np.pi * 180 * t_engine)    # harmonic
harm2 = np.sin(2 * np.pi * 360 * t_engine)    # higher harmonic

# combine
engine_wave = 1.2 * base + 0.8 * harm1 + 0.5 * harm2

# throttle vibration
engine_wave *= (1 + 0.15 * np.sin(2 * np.pi * 12 * t_engine))

# normalize
engine_wave = engine_wave / np.max(np.abs(engine_wave)) * 0.95

engine_sound = pygame.sndarray.make_sound(
    np.repeat(np.int16(engine_wave * 32767)[:, np.newaxis], 2, axis=1)
)

# ---------------- BRAKE SOUND ----------------
# ---------------- REALISTIC BRAKE SOUND ----------------
# ---------------- REALISTIC BRAKE SOUND ----------------
duration = 0.4
t_brake = np.linspace(0, duration, int(sample_rate * duration), False)

# rubber friction sound
friction = np.sin(2*np.pi*140*t_brake) * np.exp(-2*t_brake)

# light squeal
squeal = 0.4 * np.sin(2*np.pi*900*t_brake) * np.exp(-4*t_brake)

brake_wave = friction + squeal

brake_wave = brake_wave / np.max(np.abs(brake_wave)) * 0.95

brake_sound = pygame.sndarray.make_sound(
    np.repeat(np.int16(brake_wave * 32767)[:, np.newaxis], 2, axis=1)
)

# ---------------- INDICATOR CLICK SOUND ----------------
duration = 0.05
t_tick = np.linspace(0, duration, int(sample_rate * duration), False)

click = np.sign(np.sin(2 * np.pi * 1200 * t_tick))
click *= np.exp(-20 * t_tick)

click = click / np.max(np.abs(click))

indicator_sound = pygame.sndarray.make_sound(
    np.repeat(np.int16(click * 32767)[:, np.newaxis], 2, axis=1)
)

t_beep = np.linspace(0, 0.4, int(sample_rate * 0.4))
wave_beep = 0.5 * np.sin(2 * np.pi * 1000 * t_beep)
beep = np.int16(wave_beep * 32767)
beep_sound = pygame.sndarray.make_sound(np.repeat(beep[:, np.newaxis], 2, axis=1))

# ---------------- REALISTIC CAR HORN ----------------
duration = 1.0
t_horn = np.linspace(0, duration, int(sample_rate * duration), False)

# Real car horn dual-tone (around 400Hz & 500Hz typical)
tone1 = np.sin(2 * np.pi * 420 * t_horn)
tone2 = np.sin(2 * np.pi * 510 * t_horn)

# Slight modulation for realism
modulation = 0.02 * np.sin(2 * np.pi * 5 * t_horn)

# Combine tones
wave_horn = (0.5 * tone1 + 0.5 * tone2) * (1 + modulation)

# Smooth envelope (fade in/out)
attack = int(0.05 * sample_rate)
release = int(0.1 * sample_rate)
envelope = np.ones_like(wave_horn)
envelope[:attack] = np.linspace(0, 1, attack)
envelope[-release:] = np.linspace(1, 0, release)

wave_horn *= envelope

# Normalize
wave_horn = wave_horn / np.max(np.abs(wave_horn))

horn_auto = np.int16(wave_horn * 32767)

auto_park_horn = pygame.sndarray.make_sound(
    np.repeat(horn_auto[:, np.newaxis], 2, axis=1)
)
alarm_playing = False
horn_sound = auto_park_horn



# ---------------- CAMERA + MODELS ----------------
cap = cv2.VideoCapture(0)

mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
mp_hands = mp.solutions.hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
yolo_model = YOLO("yolov8n.pt")

# ---------------- ML FUNCTION ----------------
def get_ml_data():
    success, frame = cap.read()
    if not success:
        return False, False, False, 0.3, 0.0

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hand_results = mp_hands.process(rgb)

    drowsy = False
    distracted = False
    phone_detected = False
    hand_near_face = False
    ear = 0.3
    yaw = 0.0

    # ---------------- FACE ANALYSIS ----------------
    results = mp_face_mesh.process(rgb)
    if results.multi_face_landmarks:
        lm = results.multi_face_landmarks[0].landmark

        # EAR
        top = np.array([lm[159].x, lm[159].y])
        bottom = np.array([lm[145].x, lm[145].y])
        left = np.array([lm[33].x, lm[33].y])
        right = np.array([lm[133].x, lm[133].y])
        ear = np.linalg.norm(top - bottom) / np.linalg.norm(left - right)

        

        # Head pitch
        forehead = lm[10].y
        chin = lm[152].y
        pitch = chin - forehead

        # Drowsy condition (more strict)
        drowsy = ear < 0.21 and pitch > 0.24

        # Yaw (left-right rotation)
        nose = lm[1].x
        face_left = lm[234].x
        face_right = lm[454].x
        yaw = (nose - face_left) / (face_right - face_left) - 0.5

        # Only strong head turn counts
        if abs(yaw) > 0.32:
            distracted = True
    


    # ---------------- YOLO PHONE DETECTION ----------------
       # ---------------- YOLO PHONE DETECTION (IMPROVED) ----------------
    # ---------------- YOLO PHONE DETECTION (FIXED FOR EAR USAGE) ----------------
    # ---------------- YOLO PHONE DETECTION (CRASH-PROOF) ----------------
    frame_small = cv2.resize(frame, (640, 480))
    yolo_results = yolo_model(frame_small, imgsz=640, verbose=False)

    frame_h, frame_w, _ = frame.shape

    face_center_x = None
    face_center_y = None

    # Get face center from mediapipe landmarks
    if results.multi_face_landmarks:
        lm = results.multi_face_landmarks[0].landmark
        face_center_x = int(lm[1].x * frame_w)
        face_center_y = int(lm[1].y * frame_h)

    for r in yolo_results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = yolo_model.names[cls_id]

            if label == "cell phone" and conf > 0.25:

                x1, y1, x2, y2 = box.xyxy[0]

            # ⭐ STEP 5 ADD HERE
                cv2.rectangle(frame,(int(x1),int(y1)),(int(x2),int(y2)),(0,255,0),2)
                cv2.putText(frame,f"{label} {conf:.2f}",
                        (int(x1),int(y1)-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,0),2)


                x_center = int((x1 + x2) / 2)
                y_center = int((y1 + y2) / 2)

                # Extra validation: phone must be near face
                if face_center_x is not None:
                    distance = np.sqrt(
                        (x_center - face_center_x) ** 2 +
                        (y_center - face_center_y) ** 2
                    )

                    if distance < 350:
                        phone_detected = True
                else:
                    phone_detected = True
    # ⭐ STEP 6 ADD HERE
    cv2.imshow("Driver Camera", frame)
    cv2.waitKey(1)

    return drowsy, distracted, phone_detected, ear, yaw
# ✅ REMOVED RESTRICTIVE HAND/YAW CHECK - EAR CALLS NOW WORK!
# The old logic killed ear detection by requiring hand_near_face

# ---------------- 360 TRAFFIC CHECK ----------------
def check_safe_zone(car_x, car_y, traffic):

    front_safe = True
    back_safe = True
    left_safe = True
    right_safe = True

    SAFE_FRONT = 180
    SAFE_BACK = 220
    SAFE_SIDE = 120

    for t in traffic:

        dx = t['x'] - car_x
        dy = t['y'] - car_y

        # front
        if abs(dx) < 80 and 0 < dy < SAFE_FRONT:
            front_safe = False

        # rear
        if abs(dx) < 80 and -SAFE_BACK < dy < 0:
            back_safe = False

        # left
        if -SAFE_SIDE < dx < -20 and abs(dy) < 120:
            left_safe = False

        # right
        if 20 < dx < SAFE_SIDE and abs(dy) < 120:
            right_safe = False

    return front_safe, back_safe, left_safe, right_safe

# ---------------- DRAW CAR ----------------
def draw_car(x, y):
    body_color = (150,150,150) if parked else (50,200,50)
    pygame.draw.rect(screen, body_color, (x,y,60,110), border_radius=12)
    pygame.draw.rect(screen,(20,20,20),(x+10,y+10,40,30),border_radius=5)

    pygame.draw.rect(screen,(0,0,0),(x-5,y+15,10,25))
    pygame.draw.rect(screen,(0,0,0),(x+55,y+15,10,25))
    pygame.draw.rect(screen,(0,0,0),(x-5,y+70,10,25))
    pygame.draw.rect(screen,(0,0,0),(x+55,y+70,10,25))

    blink = pygame.time.get_ticks()//400 % 2 == 0

    if (left_indicator or hazard_on or (auto_park and blink)) or lights_blinking:
        pygame.draw.circle(screen,(255,150,0),(x+5,y+5),6)

    if (right_indicator or hazard_on or (auto_park and blink)) or lights_blinking:
        pygame.draw.circle(screen,(255,150,0),(x+55,y+5),6)

    headlight_color = (255,255,200) if headlights_on else (100,100,100)
    if lights_blinking and blink:
        headlight_color = (255,255,0)

    pygame.draw.circle(screen, headlight_color, (x+15,y+85),8)
    pygame.draw.circle(screen, headlight_color, (x+45,y+85),8)

# ---------------- SPEEDOMETER ----------------
def draw_speedometer(speed):

    # TOP RIGHT POSITION
    center = (WIDTH - 120, 120)
    radius = 80

    # Background circle
    pygame.draw.circle(screen, (30,30,40), center, radius)
    pygame.draw.circle(screen, (255,255,255), center, radius, 3)

    # Speed ticks
    for i in range(0, 181, 20):

        angle = np.radians(180 - i)

        x1 = center[0] + (radius - 10) * np.cos(angle)
        y1 = center[1] - (radius - 10) * np.sin(angle)

        x2 = center[0] + radius * np.cos(angle)
        y2 = center[1] - radius * np.sin(angle)

        pygame.draw.line(screen,(200,200,200),(x1,y1),(x2,y2),2)

    # Convert game speed to km/h
    kmh = int(abs(speed) * 20)

    # Needle angle
    angle = np.radians(180 - min(kmh,120) / 120 * 180)

    nx = center[0] + (radius - 15) * np.cos(angle)
    ny = center[1] - (radius - 15) * np.sin(angle)

    pygame.draw.line(screen,(255,0,0),center,(nx,ny),4)
    pygame.draw.circle(screen,(255,255,255),center,6)

    # Digital speed text
    speed_text = font.render(f"{kmh} km/h", True, (255,255,0))
    screen.blit(speed_text,(center[0]-40,center[1]+40))
# ---------------- CONTROLS DISPLAY ----------------
# ---------------- CONTROLS DISPLAY (IMPROVED UI) ----------------
def draw_controls():
    panel_width = 260
    panel_height = 220
    panel_x = 20
    panel_y = HEIGHT - panel_height - 20

    # Panel background
    panel_surface = pygame.Surface((panel_width, panel_height))
    panel_surface.set_alpha(200)
    panel_surface.fill((25, 30, 45))
    screen.blit(panel_surface, (panel_x, panel_y))

    # Border
    pygame.draw.rect(screen, (80, 180, 255), (panel_x, panel_y, panel_width, panel_height), 2)

    # Title
    title = big_font.render("CONTROLS", True, (255, 255, 255))
    screen.blit(title, (panel_x + 20, panel_y + 10))

    controls = [
        ("1 - 4", "Gears"),
        ("Q / E", "Indicators"),
        ("Z", "Hazard"),
        ("SPACE", "Handbrake"),
        ("L", "Lights"),
        ("H", "Horn"),
        ("R", "Reset"),
        ("ESC", "Exit")
    ]

    start_y = panel_y + 50

    for key, action in controls:
        key_text = font.render(key, True, (255, 220, 120))
        action_text = font.render(action, True, (220, 220, 220))

        screen.blit(key_text, (panel_x + 15, start_y))
        screen.blit(action_text, (panel_x + 120, start_y))

        start_y += 22

indicator_timer = 0
auto_park_stage = "CHECK_FB"  
# stages:
# CHECK_FB → CHECK_LEFT → MERGE → REPEAT → PARK
# ---------------- MAIN LOOP ----------------
while running:
    current_time = pygame.time.get_ticks()/1000
    keys = pygame.key.get_pressed()
    active_alerts = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

    # ---------------- AUTO PARK ----------------
            if event.key == pygame.K_p:
                auto_park = True
                parked = False
                active_alerts.append("🅿 AUTO PARK MANUAL TEST ACTIVATED")

            elif event.key == pygame.K_o:
                auto_park = False
                active_alerts.append("AUTO PARK CANCELLED")

    # ---------------- EXIT / RESET ----------------
            elif event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_r:
                auto_park = False
                parked = False
                road_speed = 5
                car_x = 575
                gear = "D"
                drowsy_start_time = None
                speed_limit_value = 120
                drowsiness_alert_counter = 0
                speed_limited = False
                left_indicator = False
                right_indicator = False
                hazard_on = False
                indicator_timer = 0
                pygame.mixer.stop()

    # ---------------- GEARS ----------------
            elif event.key == pygame.K_1: gear = "P"
            elif event.key == pygame.K_2: gear = "R"
            elif event.key == pygame.K_3: gear = "N"
            elif event.key == pygame.K_4: gear = "D"

    # ---------------- INDICATORS ----------------
            elif event.key == pygame.K_q:
                left_indicator = not left_indicator
                right_indicator = False
                indicator_sound.play()

            elif event.key == pygame.K_e:
                right_indicator = not right_indicator
                left_indicator = False
                indicator_sound.play()

            elif event.key == pygame.K_z:
                hazard_on = not hazard_on
                left_indicator = right_indicator = False
                indicator_sound.play()

    # ---------------- OTHER CONTROLS ----------------
            elif event.key == pygame.K_SPACE:
                handbrake = not handbrake

            elif event.key == pygame.K_l:
                headlights_on = not headlights_on

            elif event.key == pygame.K_h:
                horn_sound.play()
    ml_drowsy, ml_distracted, ml_phone, current_ear, current_yaw = get_ml_data()

    if not auto_park:
        if keys[pygame.K_LEFT]:
            car_x -= car_speed

        if keys[pygame.K_RIGHT]:
            car_x += car_speed

        # ---------------- ACCELERATION LOCK WHEN SPEED LIMITED ----------------
        if keys[pygame.K_UP] and gear == "D":

            if not speed_limited:   # ✅ ONLY allow when NOT limited
                road_speed += 0.5

                if not pygame.mixer.get_busy():
                    engine_sound.play(maxtime=120)

            else:
        # 🚫 BLOCK acceleration completely
                pass
        

        if keys[pygame.K_UP] and gear=="R":
            if not speed_limited:
                road_speed -= 0.5
                if not pygame.mixer.get_busy():
                    engine_sound.play(maxtime=120)

        if keys[pygame.K_DOWN]:
            road_speed *= 0.95
            if not pygame.mixer.get_busy():
                brake_sound.play()
    

    if gear=="P": road_speed=0
    if gear=="N":
        road_speed*=0.97
        if abs(road_speed)<0.1:
            road_speed=0

    if handbrake: road_speed*=0.90

    # 🚗 SPEED LIMITER (ADD THIS)
    # 🚗 REALISTIC SPEED LIMITER (GRADUAL SLOWDOWN)
    # 🚗 ULTRA SMOOTH SPEED LIMITER (WORKS WITH AUTO PARK)

    if speed_limited:

        if speed_limit_value == 60:
            limit_speed = 3

        elif speed_limit_value == 40:
            limit_speed = 2

    # gradual slowdown like engine braking
        if road_speed > limit_speed:
            road_speed -= 0.02
            if road_speed < limit_speed:
                road_speed = limit_speed

        elif road_speed < -limit_speed:
            road_speed += 0.02
            if road_speed > -limit_speed:
                road_speed = -limit_speed

    else:
        road_speed = max(min(road_speed, 12), -6)

    # ---------------- AUTO SPEED RESTORE TIMER ----------------
    # ---------------- AUTO SPEED RESTORE TIMER ----------------
    if speed_limited and speed_limit_start_time is not None:

    # Pause timer if auto park is active
        if not auto_park:
            elapsed = current_time - speed_limit_start_time
            remaining = SPEED_RESET_TIME - elapsed

            if remaining <= 0 and not speed_restored:

                speed_limited = False
                speed_restored = True
            
                pause_drowsy_detection = False
                drowsiness_alert_counter = 2

                beep_sound.play()
                pygame.time.delay(150)
                beep_sound.play()

                alert_message = "✅ SPEED RESTORED"
                alert_timer = current_time

    
    car_x=max(0,min(WIDTH-60,car_x))

    # Drowsiness Timer
    # ---------------- DROWSINESS ALERT SYSTEM ----------------
    

    if ml_drowsy and not pause_drowsy_detection:

        if drowsy_start_time is None:
            drowsy_start_time = current_time

        elif current_time - drowsy_start_time >= DROWSY_TRIGGER_SECONDS:

            if current_time - last_drowsy_alert_time > DROWSY_ALERT_COOLDOWN:

                drowsiness_alert_counter += 1
                last_drowsy_alert_time = current_time
                drowsy_start_time = None

        # FIRST ALERT
            if drowsiness_alert_counter == 1:
                alert_message = "⚠ PLEASE BE AWAKE!"
                alert_timer = current_time
                beep_sound.play(maxtime=5000)

        # SECOND ALERT
            elif drowsiness_alert_counter == 2:

                speed_limited = True
                speed_limit_value = 60
                SPEED_RESET_TIME = 180 # 3 minutes
                speed_limit_start_time = current_time
                speed_restored = False
                
                

                alert_message = "⚠ SPEED LIMITED TO 60 km/h (3 MIN)"
                alert_timer = current_time

                beep_sound.play(maxtime=2000)

        # THIRD ALERT → 40 km/h for 7 minutes
            elif drowsiness_alert_counter == 3:

                speed_limited = True
                speed_limit_value = 40
                SPEED_RESET_TIME = 420   # 7 minutes
                speed_limit_start_time = current_time
                speed_restored = False

                alert_message = "⚠ SPEED LIMITED TO 40 km/h (7 MIN)"
                alert_timer = current_time

                beep_sound.play(maxtime=2000)   

        # FOUR ALERT
            elif drowsiness_alert_counter >= 4:
                auto_park = True
                hazard_on = True
                alert_message = "🚨 AUTO PARK ACTIVATED"
                alert_timer = current_time
                beep_sound.play(maxtime=2000)

    else:
        drowsy_start_time = None

    # ---------------- DISTRACTION STABILITY ----------------
    if ml_distracted:
          distraction_counter += 1
    else:
          distraction_counter = 0

    if distraction_counter > DISTRACTION_CONFIRM_FRAMES:
      active_alerts.append("👀 DISTRACTION ALERT!")
      ml_distracted = True
    else:
      ml_distracted = False


# ---------------- PHONE STABILITY ----------------
    if ml_phone:
        phone_counter += 1
    else:
        phone_counter = 0

    if phone_counter > PHONE_CONFIRM_FRAMES:
        active_alerts.append("📱 PHONE DETECTED!")
        ml_phone = True
    else:
        ml_phone = False

    serious = auto_park or ml_distracted or ml_phone

    if auto_park and not parked:
        if not alarm_playing:
            auto_park_horn.play(-1)
            alarm_playing=True
    elif serious and not alarm_playing:
        beep_sound.play(-1)
        alarm_playing=True
    elif not serious and not auto_park and alarm_playing:
        beep_sound.stop()
        auto_park_horn.stop()
        alarm_playing=False

    ## ---------------- ADVANCED AUTO PARK (REAL LOGIC) ----------------
    PARKING_LANE_X = lanes[0]

    MIN_SPEED = 3      # ≈ 60 km/h
    MAX_SPEED = 6

    if auto_park and not parked:

        front = False
        back = False

        left_front = False
        left_side = False
        left_back = False

    # ---------------- DETECT TRAFFIC ----------------
        for t in traffic:
            dx = t['x'] - car_x
            dy = car_y - t['y']

        # SAME LANE
            if abs(dx) < 70:
                if 0 < dy < 200:
                    front = True
                elif -200 < dy < 0:
                    back = True

        # LEFT LANE
            if -300 < dx < -80:

                if 0 < dy < 200:
                    left_front = True

                elif abs(dy) < 80:
                    left_side = True

                elif -200 < dy < 0:
                    left_back = True


    # ---------------- STEP 1: CREATE GAP ----------------
        gap_ready = False

        if front:
            road_speed *= 0.97   # slow down gently

        elif back:
            road_speed += 0.04   # accelerate slightly

        else:
            gap_ready = True


    # ---------------- STEP 2: LEFT LANE CHECK ----------------
        if gap_ready:

            left_blocked = left_front or left_side or left_back

        # 🚧 IF LEFT NOT SAFE → ADJUST SPEED (NOT STOP)
            if left_blocked:

            # Maintain minimum speed (60 km/h feel)
                if road_speed < MIN_SPEED:
                    road_speed += 0.03

            # If front-left → slow slightly
                if left_front:
                    road_speed *= 0.98

            # If left-back → slow slightly (let pass)
                if left_back:
                    road_speed *= 0.985

            # If vehicle slower than 60 → overtake
                for t in traffic:
                    dx = t['x'] - car_x
                    dy = car_y - t['y']

                    if -300 < dx < -80 and abs(dy) < 150:
                        if t["speed"] < 60:
                            road_speed += 0.05   # overtake


        # ✅ SAFE → LANE CHANGE
            else:
                STEER_SPEED = 2.5
                target_lane = max(PARKING_LANE_X, car_x - 250)

                diff = target_lane - car_x

                if abs(diff) > STEER_SPEED:
                    car_x += STEER_SPEED if diff > 0 else -STEER_SPEED


    # ---------------- STEP 3: FINAL PARK ----------------
        if abs(car_x - PARKING_LANE_X) < 5:

        # smooth slow down
            road_speed *= 0.96

            if abs(road_speed) < 0.3:
                road_speed = 0
                parked = True
                gear = "P"
                hazard_on = True
                auto_park = False
    # DRAW
    # -------- SCREEN SHAKE OFFSET --------
    offset_x = 0
    offset_y = 0

    if shake_timer > 0:
        offset_x = np.random.randint(-shake_intensity, shake_intensity)
        offset_y = np.random.randint(-shake_intensity, shake_intensity)
        shake_timer -= 1

    screen.fill((20,20,30))
    player_rect = pygame.Rect(car_x, car_y, 60, 110)

    for i in range(10):
        y_pos=int((5*score+i*150)%HEIGHT)
        for lane_x in lanes:
            pygame.draw.rect(screen,(200,200,100),
                 (lane_x-5+offset_x, y_pos+offset_y, 10, 80))
    # ---------------- TRAFFIC LOOP ----------------
    # ---------------- TRAFFIC LOOP (REAL SPEED) ----------------
    for t in traffic:

        traffic_speed = t["speed"] * 0.05
        player_speed = road_speed * 20 * 0.05

        relative_speed = traffic_speed - player_speed

        t['y'] -= relative_speed

        if t['y'] < -300:

            safe_spawn = False

            while not safe_spawn:

                new_x = np.random.choice(lanes[1:])
                new_y = HEIGHT + np.random.randint(400,1200)

        # ❌ Avoid spawning near player during parking
                if auto_park or parked:

                    dist_x = abs(new_x - car_x)
                    dist_y = abs(new_y - car_y)

            # Safe distance check
                    if dist_x < 120 and dist_y < 300:
                        continue   # retry spawn

                safe_spawn = True

            t['x'] = new_x
            t['y'] = new_y

            if auto_park and abs(car_x - PARKING_LANE_X) < 20:
    # stop spawning cars completely in that lane
                if t['x'] == PARKING_LANE_X:
                    t['x'] = np.random.choice(lanes[1:])

        if parked:
            if abs(t['x'] - car_x) < 80 and t['y'] > car_y - 150:
                t['y'] = car_y - 300


    # Collision check
        traffic_rect = pygame.Rect(t['x'], t['y'], t['w'], t['h'])
        if player_rect.colliderect(traffic_rect) and not crashed:
            crashed = True
            crash_cooldown = 120
            road_speed = 0
            shake_timer = 20
        shake_intensity = 15
        # ---------------- DRAW VEHICLE ----------------
        pygame.draw.rect(
            screen,
            t['color'],
            (t['x'] + offset_x, t['y'] + offset_y, t['w'], t['h']),
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            (30, 30, 40),
            (t['x'] + t['w']*0.2, t['y'] + 10, t['w']*0.6, 30),
            border_radius=5
        )

        # Wheels
        wheel_w = 12
        wheel_h = 30

        pygame.draw.rect(screen, (20,20,20),
                         (t['x']-6, t['y']+20, wheel_w, wheel_h))
        pygame.draw.rect(screen, (20,20,20),
                         (t['x']+t['w']-6, t['y']+20, wheel_w, wheel_h))
        pygame.draw.rect(screen, (20,20,20),
                         (t['x']-6, t['y']+t['h']-50, wheel_w, wheel_h))
        pygame.draw.rect(screen, (20,20,20),
                         (t['x']+t['w']-6, t['y']+t['h']-50, wheel_w, wheel_h))

        if t["type"] == "truck":
            pygame.draw.rect(
                screen,
                (100,100,100),
                (t['x'], t['y'] + t['h'] - 70, t['w'], 40),
                border_radius=6
            )

        pygame.draw.circle(screen, (255,255,180),
                           (t['x']+15, t['y']+t['h']-15), 6)
        pygame.draw.circle(screen, (255,255,180),
                           (t['x']+t['w']-15, t['y']+t['h']-15), 6)
        # HANDLE CRASH COOLDOWN
    if crashed:
        crash_cooldown -= 1
        if crash_cooldown <= 0:
            crashed = False
            road_speed = 2

    # ---------------- CAR Y POSITION BASED ON SPEED ----------------
    # ---------------- CAR Y POSITION BASED ON SPEED / AUTO PARK ----------------
    BASE_CAR_Y = HEIGHT - 140   # bottom of the screen
    CENTER_CAR_Y = HEIGHT // 2  # middle of the screen

    TARGET_Y = CENTER_CAR_Y if auto_park else BASE_CAR_Y - (BASE_CAR_Y - CENTER_CAR_Y) * min(road_speed / 230, 1)

# Smooth vertical movement (lerp)
    car_y += (CENTER_CAR_Y - car_y) * 0.1

    draw_car(car_x + offset_x, car_y + offset_y)
    if crashed:
        crash_text = big_font.render("💥 CRASHED!", True, (255, 0, 0))
        screen.blit(crash_text, (WIDTH//2 - 150, HEIGHT//2 - 40))
    draw_speedometer(road_speed)
    draw_controls()

    

    screen.blit(font.render(f"Gear: {gear}",True,(255,255,255)),(20,20))
    screen.blit(font.render(f"Handbrake: {handbrake}",True,(255,255,255)),(20,50))
    screen.blit(font.render(f"Lights: {'ON' if headlights_on else 'OFF'}",True,(255,255,255)),(20,80))
    screen.blit(font.render(f"EAR: {current_ear:.2f}",True,(255,255,255)),(20,110))
    screen.blit(font.render(f"Yaw: {current_yaw:.2f}",True,(255,255,255)),(20,140))
    # ---------------- SPEED LIMIT COUNTDOWN DISPLAY ----------------
    if speed_limited and speed_limit_start_time is not None:

        # Freeze timer when auto park starts
        if not auto_park:
            remaining = max(0, SPEED_RESET_TIME - (current_time - speed_limit_start_time))
    # if parked → keep previous remaining value (freeze)

        minutes = int(remaining // 60)
        seconds = int(remaining % 60)

        timer_text = font.render(
            f"Speed Restore In: {minutes:02}:{seconds:02}",
            True,
            (255,180,0)
    )

    
        screen.blit(timer_text,(20,230))
    screen.blit(font.render(f"Drowsy: {'YES' if ml_drowsy else 'NO'}",
                            True,(0,255,0) if not ml_drowsy else (255,0,0)),(20,170))

    if drowsy_start_time:
        remaining=max(0,DROWSY_TRIGGER_SECONDS-(current_time-drowsy_start_time))
        screen.blit(font.render(f"AutoPark in: {remaining:.1f}s",
                                True,(255,100,100)),(20,200))

    for i,msg in enumerate(active_alerts):
        screen.blit(big_font.render(msg,True,(255,50,50)),(50,220+i*60))
        # ---------------- MAIN ALERT MESSAGE ----------------
    if alert_message and current_time - alert_timer < ALERT_DURATION:
        alert_text = big_font.render(alert_message, True, (255,80,80))
        screen.blit(alert_text, (WIDTH//2 - 250, 300))


    # indicator ticking sound
    if (left_indicator or right_indicator or hazard_on):
        if pygame.time.get_ticks() - indicator_timer > 500:
          indicator_sound.play()
          indicator_timer = pygame.time.get_ticks()

    

    pygame.display.flip()
    clock.tick(60)
    score+=1

cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()