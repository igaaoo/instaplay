import cv2
from camera.videoCapture import start_video_capture
from camera.gestureDetection import detect_gesture
from processing.bufferManager import add_frame_to_buffer
from processing.videoSaver import save_video_with_watermark
from server.server import app

def main():
    # Inicializa a captura de vídeo
    cap, fps = start_video_capture()
    
    while True:
        success, frame = cap.read()
        if not success:
            print("Erro ao capturar o frame da câmera.")
            break
        
        # Adiciona o frame ao buffer para possível salvamento posterior
        add_frame_to_buffer(frame)

        # Detecta o gesto e desenha os pontos no frame
        gesture = detect_gesture(frame)
        if gesture == "ok":
            print("Gesto  detectado! Salvando vídeo dos últimos 30 segundos.")
            save_path = save_video_with_watermark(fps)
            
            # Confirma se o vídeo foi salvo corretamente
            if save_path:
                print(f"Vídeo salvo com sucesso em: {save_path}")
            else:
                print("Erro ao salvar o vídeo.")

        # Exibe o frame atualizado com os pontos da mão na janela de preview
        cv2.imshow("Instaplay", frame)

        # Fecha a janela ao pressionar 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libera a câmera e fecha a janela
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
    app.run()
