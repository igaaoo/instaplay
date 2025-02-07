import base64
import datetime
import hashlib
import time
import uuid
import threading
import cv2
from flask import Flask
from flask_cors import CORS
from camera.gestureDetection import detect_gesture
from camera.videoCapture import start_video_capture
from processing.bufferManager import add_frame_to_buffer
from processing.videoSaver import save_video_with_watermark
from server.services.partidas_service import salvar_partida, salvar_video, finalizar_partida
import server.server as server  # Importa o servidor Flask

def frame_to_base64(frame):
    _, buffer = cv2.imencode('.jpg', frame)  # Converte o frame para JPG
    frame_base64 = base64.b64encode(buffer).decode('utf-8')  # Codifica como Base64
    return frame_base64

def gesture_detection():
    """Executa a detecção de gestos"""
    cap, fps = start_video_capture()
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    unique_key = str(uuid.uuid1())
    codigo = hashlib.md5(unique_key.encode()).hexdigest()

    partida = {
        "codigo": codigo,
        "pagamento": False,
        "data_inicio": datetime.datetime.now(),
        "data_fim": None,
        "videos": [],
    }

    start_time = time.time()
    # set time to 10min
    time_end = 6000

    partida_id = salvar_partida(partida)

    while True:
        success, frame = cap.read()
        if not success:
            print("Erro ao capturar o frame da câmera.")
            break

        add_frame_to_buffer(frame)
        gesture = detect_gesture(frame)

        if gesture:
            print("Gesto detectado! Salvando vídeo dos últimos 30 segundos.")
            is_first_frame = True

            if is_first_frame:
                thumbnail_base64 = frame_to_base64(frame)
                is_first_frame = False

            save_path = save_video_with_watermark(fps)

            if save_path:
                print(f"Vídeo salvo com sucesso em: {save_path}")
                salvar_video(partida_id, save_path, thumbnail_base64, datetime.datetime.now())
            else:
                print("Erro ao salvar o vídeo.")

        cv2.imshow("Instaplay", frame)

        if cv2.waitKey(1) & 0xFF == ord('q') or (time.time() - start_time) > time_end:
            finalizar_partida(partida_id, datetime.datetime.now())
            break


    cap.release()
    cv2.destroyAllWindows()

def run_flask_server():
    """Executa o servidor Flask"""
    server.app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Criar threads para rodar os dois processos em paralelo
    thread_gesture = threading.Thread(target=gesture_detection)
    thread_server = threading.Thread(target=run_flask_server)

    # Iniciar as threads
    thread_gesture.start()
    thread_server.start()

    # Aguardar a conclusão das threads
    thread_gesture.join()
    thread_server.join()
