import cv2
import mediapipe as mp
import time
import math

# Inicializar MediaPipe Hands e o módulo de desenho
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils  # Para desenhar os pontos da mão
last_detection_time = 0
COOLDOWN_PERIOD = 5  # em segundos
MIN_DISTANCE_OK = 0.05  # Distância máxima entre polegar e indicador para detectar "OK"

# Configuração dinâmica de frames necessários para 2 segundos
cap = cv2.VideoCapture(0)  # Iniciar a câmera
fps = cap.get(cv2.CAP_PROP_FPS) or 30  # Obter FPS da câmera, default para 30 se não disponível
GESTURE_FRAMES = int(fps)  # Número de frames consecutivos para considerar 2 segundos

# Variáveis para detecção baseada em frequência
gesture_counter = 0
detected_gesture = None

def calculate_distance(point1, point2):
    """Calcula a distância euclidiana entre dois pontos."""
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

def detect_gesture(frame):
    global last_detection_time, gesture_counter, detected_gesture
    current_time = time.time()
    
    # Converte o frame para RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    # Verificar se alguma mão foi detectada
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            # Desenha os pontos da mão e as conexões
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=4),
                                      mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2))

            # Pontos específicos para verificar o gesto "OK"
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
            pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
            index_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]

            # Distância entre a ponta do polegar e do dedo indicador para o gesto "OK"
            thumb_index_distance = calculate_distance(thumb_tip, index_finger_tip)

            # Verificação do gesto "OK"
            if (thumb_index_distance < MIN_DISTANCE_OK and  # Polegar e indicador próximos
                middle_finger_tip.y < index_finger_mcp.y and  # Médio, anelar e mindinho estendidos
                ring_finger_tip.y < index_finger_mcp.y and
                pinky_tip.y < index_finger_mcp.y):

                # Desenha o landmark em verde
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                                          mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2))
                
                # Aumenta o contador de frames consecutivos com o gesto "OK"
                gesture_counter += 1
                
                if gesture_counter >= GESTURE_FRAMES:
                    if current_time - last_detection_time > COOLDOWN_PERIOD:
                        last_detection_time = current_time
                        gesture_counter = 0  # Reseta o contador
                        detected_gesture = "ok"
                        return "ok"
            else:
                # Reseta o contador se o gesto não for consistente
                detected_gesture = None
                gesture_counter = 0

    return None
