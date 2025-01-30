import base64
import collections
import datetime
import hashlib
import time
import uuid
from camera.gestureDetection import detect_gesture
from camera.videoCapture import start_video_capture
import cv2
from processing.bufferManager import add_frame_to_buffer
from processing.videoSaver import save_video_with_watermark
from server.services.partidas_service import salvar_partida_com_videos

def frame_to_base64(frame):
    _, buffer = cv2.imencode('.jpg', frame)  # Converte o frame para JPG
    frame_base64 = base64.b64encode(buffer).decode('utf-8')  # Codifica como Base64
    return frame_base64

def main():
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
    time_end = 60
    while True:
        success, frame = cap.read()
        if not success:
            print("Erro ao capturar o frame da câmera.")
            break
        
        add_frame_to_buffer(frame)

        gesture = detect_gesture(frame)
        if gesture:
            print("Gesto  detectado! Salvando vídeo dos últimos 30 segundos.")
            is_first_frame = True

            if is_first_frame:
                thumbnail_base64 = frame_to_base64(frame)
                is_first_frame = False

            print(f"tumb {thumbnail_base64}")
            save_path = save_video_with_watermark(fps)
            
            if save_path:
                print(f"Vídeo salvo com sucesso em: {save_path}")
                partida["videos"].append({
                    "path": save_path,
                    "thumbnail": thumbnail_base64, 
                    "pagamento": False,
                    "created_at": datetime.datetime.now()
                })

            else:
                print("Erro ao salvar o vídeo.")

        cv2.imshow("Instaplay", frame)

        if cv2.waitKey(1) & 0xFF == ord('q') or (time.time() - start_time) > time_end:
            partida["data_fim"] = datetime.datetime.now()
            break

    salvar_partida_com_videos(partida)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
    # app.run()
