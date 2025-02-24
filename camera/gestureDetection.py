import cv2
import mediapipe as mp
import time

# Inicializar MediaPipe Pose e o módulo de desenho
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils  # Para desenhar os pontos do corpo
last_detection_time = 0
COOLDOWN_PERIOD = 5  # em segundos

# Configuração dinâmica de frames necessários
cap = cv2.VideoCapture(0)  # Iniciar a câmera
fps = cap.get(cv2.CAP_PROP_FPS) or 30  # Obter FPS da câmera, default para 30 se não disponível
GESTURE_FRAMES = int(fps * 2)  # Número de frames consecutivos para considerar gesto

# Variáveis para detecção baseada em frequência
gesture_counter = 0

def detect_gesture(frame):
    global last_detection_time, gesture_counter
    current_time = time.time()
    
    # Converte o frame para RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)
    
    # Verificar se o corpo foi detectado
    if results.pose_landmarks:
        # Pega os landmarks específicos para verificar a posição dos braços
        left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        left_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
        left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
        
        right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        right_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
        right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        
        # Verifica se o braço esquerdo ou direito está levantado
        left_arm_raised = left_wrist.y < left_elbow.y < left_shoulder.y
        right_arm_raised = right_wrist.y < right_elbow.y < right_shoulder.y
        
        if left_arm_raised or right_arm_raised:
            # Aumenta o contador de frames consecutivos com o braço levantado
            gesture_counter += 1
            print(f"Braço levantado: {gesture_counter}")
            
            if gesture_counter >= GESTURE_FRAMES:
                if current_time - last_detection_time > COOLDOWN_PERIOD:
                    print("Gesto detectado! Iniciar salvamento")
                    last_detection_time = current_time
                    gesture_counter = 0  # Reseta o contador
                    return "raised_arm"
        else:
            gesture_counter = 0

    return None

