import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe's Pose solution and drawing utilities
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    """Calculates the angle between three points."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# --- Main Program ---

cap = cv2.VideoCapture(0)

# Video Recording Setup
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
output_path = 'pushup_session_smart.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, 20.0, (frame_width, frame_height))


counter = 0
state = 'get_ready' 
feedback = ''
visibility_threshold = 0.8

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

       
        avg_back_angle = 0
        avg_elbow_angle = 0

        try:
            landmarks = results.pose_landmarks.landmark

            # --- 1. GET COORDINATES & VISIBILITY ---
            l_shoulder_val = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            l_elbow_val = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
            l_hip_val = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            l_ankle_val = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
            r_shoulder_val = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            r_elbow_val = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
            r_hip_val = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
            r_ankle_val = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

            # --- 2. CHECK VISIBILITY OF KEY LANDMARKS ---
            is_body_visible = all(lm.visibility > visibility_threshold for lm in [l_shoulder_val, l_elbow_val, l_hip_val, r_shoulder_val, r_elbow_val, r_hip_val])

            l_shoulder, l_elbow, l_wrist, l_hip, l_ankle = [l_shoulder_val.x, l_shoulder_val.y], [l_elbow_val.x, l_elbow_val.y], [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y], [l_hip_val.x, l_hip_val.y], [l_ankle_val.x, l_ankle_val.y]
            r_shoulder, r_elbow, r_wrist, r_hip, r_ankle = [r_shoulder_val.x, r_shoulder_val.y], [r_elbow_val.x, r_elbow_val.y], [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y], [r_hip_val.x, r_hip_val.y], [r_ankle_val.x, r_ankle_val.y]

            # --- 3. CALCULATE ANGLES AND FORM ---
            avg_elbow_angle = (calculate_angle(l_shoulder, l_elbow, l_wrist) + calculate_angle(r_shoulder, r_elbow, r_wrist)) / 2
            avg_back_angle = (calculate_angle(l_shoulder, l_hip, l_ankle) + calculate_angle(r_shoulder, r_hip, r_ankle)) / 2
            
            form_feedback = "GOOD FORM"
            if calculate_angle(l_hip, l_shoulder, l_elbow) > 65 or calculate_angle(r_hip, r_shoulder, r_elbow) > 65:
                form_feedback = "TUCK ELBOWS"

            # --- 4. SIMPLIFIED AND MORE ROBUST STATE MACHINE LOGIC ---
            if state == 'get_ready':
               
                if is_body_visible and avg_back_angle > 145 and avg_elbow_angle > 155:
                    state = 'ready'
                    feedback = form_feedback
                else:
                    feedback = "GET INTO PLANK POSITION"

            elif state == 'up':
                feedback = form_feedback
                if avg_elbow_angle < 90:
                    state = 'down'

            elif state == 'down':
                feedback = form_feedback
                if avg_elbow_angle > 155:
                    counter += 1
                    state = 'ready'
                    feedback = "REP COUNTED!"

        except Exception as e:
            state = 'get_ready' 
            feedback = "NO BODY DETECTED"

        # --- 5. RENDER THE UI ---
        
        if "TUCK ELBOWS" in feedback: feedback_box_color = (0, 0, 255)
        elif "GOOD" in feedback: feedback_box_color = (0, 150, 0)
        elif "COUNTED" in feedback: feedback_box_color = (200, 100, 0)
        elif "DETECTED" in feedback: feedback_box_color = (0, 165, 255)
        else: feedback_box_color = (128, 0, 0)

        # Main Status Box
        cv2.rectangle(image, (0, 0), (250, 73), (50, 50, 50), -1)
        cv2.putText(image, 'REPS', (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image, 'STATUS', (130, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(image, state.upper(), (120, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Dynamic Feedback Box
        cv2.rectangle(image, (250, 0), (640, 73), feedback_box_color, -1)
        (text_width, _), _ = cv2.getTextSize(feedback, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        text_x = 250 + (390 - text_width) // 2
        cv2.putText(image, feedback, (text_x, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
        # NEW: Debug view to show angles
        cv2.putText(image, f"BACK: {int(avg_back_angle)}", (15, frame_height - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image, f"ELBOW: {int(avg_elbow_angle)}", (15, frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

        out.write(image)
        cv2.imshow('Smart Push-Up Trainer', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
out.release()
cv2.destroyAllWindows()
