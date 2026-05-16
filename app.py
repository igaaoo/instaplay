import base64
import datetime
import hashlib
import os
import time
import uuid
import threading
import cv2
import pygame

from camera.camera import VideoCapture
from camera.detector import PoseDetector
from processing.bufferManager import add_frame_to_buffer
from processing.videoSaver import save_video_with_watermark
from server.services.partidas_service import salvar_partida, salvar_video, finalizar_partida
import server.server as server

COOLDOWN_PERIOD = 5  # seconds between consecutive gesture triggers
SESSION_DURATION = 6000  # seconds before auto-ending a match (~100 min)
SOUND_REPLAY = "static/replay.mp3"
SOUND_START  = "static/start.mp3"

pygame.mixer.init()

def play_sound(path: str) -> None:
    """Play a sound file in a daemon thread so it never blocks the main loop."""
    def _play():
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Erro ao tocar som: {e}")
    threading.Thread(target=_play, daemon=True).start()


def frame_to_base64(frame) -> str:
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')


def gesture_detection() -> None:
    """Main game loop: capture → buffer → pose inference → save clip on gesture."""
    cap = VideoCapture(source='http://192.168.15.58:4747/video')
    detector = PoseDetector(inference_width=640, skip_frames=2)

    codigo = hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()
    partida = {
        "codigo": codigo,
        "pagamento": False,
        "data_inicio": datetime.datetime.now(),
        "data_fim": None,
        "videos": [],
    }
    partida_id = salvar_partida(partida)
    print(f"Partida iniciada | Codigo: {codigo}")
    play_sound(SOUND_START)

    start_time = time.time()
    last_trigger_time = 0.0
    hands_raised_since: float | None = None  # timestamp when hands first went up
    SUSTAINED_SECONDS = 2.0

    try:
        while True:
            success, frame = cap.read()
            if not success:
                print("Erro ao capturar frame da câmera.")
                continue

            # Keep frame in rolling buffer for later video export
            add_frame_to_buffer(frame)

            # Submit to background inference (skips frames internally)
            detector.submit(frame)

            players_raised = detector.get_result()
            current_time = time.time()

            if players_raised:
                if hands_raised_since is None:
                    hands_raised_since = current_time  # start the clock
            else:
                hands_raised_since = None  # reset if hands go down

            sustained = (
                hands_raised_since is not None
                and (current_time - hands_raised_since) >= SUSTAINED_SECONDS
            )

            if sustained and (current_time - last_trigger_time) > COOLDOWN_PERIOD:
                last_trigger_time = current_time
                hands_raised_since = None  # reset so it needs 2s again next time
                play_sound(SOUND_REPLAY)
                print(f"Mãos levantadas detectadas (jogadores: {players_raised})! Salvando vídeo...")

                thumbnail_base64 = frame_to_base64(frame)
                save_path = save_video_with_watermark(cap.fps)

                if save_path:
                    print(f"Vídeo salvo: {save_path}")
                    salvar_video(partida_id, save_path, thumbnail_base64, datetime.datetime.now())
                else:
                    print("Erro ao salvar o vídeo.")

            cv2.imshow("Instaplay", frame)

            elapsed = current_time - start_time
            if cv2.waitKey(1) & 0xFF == ord('q') or elapsed > SESSION_DURATION:
                finalizar_partida(partida_id, datetime.datetime.now())
                break

    finally:
        detector.stop()
        cap.release()
        cv2.destroyAllWindows()


def run_flask_server() -> None:
    server.app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)


if __name__ == '__main__':
    thread_server = threading.Thread(target=run_flask_server, name="FlaskThread", daemon=True)
    thread_gesture = threading.Thread(target=gesture_detection, name="GestureThread")

    thread_server.start()
    thread_gesture.start()

    thread_gesture.join()
    os._exit(0)  # force-kill Flask (and any other threads) when the game loop exits
