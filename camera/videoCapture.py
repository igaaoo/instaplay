import cv2

def start_video_capture():
    # cap = cv2.VideoCapture('http://192.168.19.30:4747/video')  # '0' para webcam; substituir por URL de câmera IP para acesso remoto
    cap = cv2.VideoCapture(0)  # '0' para webcam; substituir por URL de câmera IP para acesso remoto
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Captura o FPS da câmera
    fps = cap.get(cv2.CAP_PROP_FPS)
    return cap, fps
