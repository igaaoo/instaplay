import datetime
import cv2
import numpy as np
from config import VIDEO_PATH, WATERMARK_PATH
from processing.bufferManager import get_buffer_frames
import uuid

def generate_new_path_name():
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    unique_key = str(uuid.uuid1())
    return f"{now}-{unique_key}.mp4"

def save_video_with_watermark(fps):
    frames = get_buffer_frames()
    if not frames:
        print("Buffer vazio. Nenhum vídeo para salvar.")
        return None

    new_path = generate_new_path_name()
    # Remova os últimos segundos de frames para evitar salvar o gesto
    frames_to_remove = int(fps * 2)
    frames = frames[:-frames_to_remove]

    # Defina o caminho do vídeo como .mp4
    video_path_mp4 = new_path.replace('.avi', '.mp4')

    # Inicialize o escritor de vídeo com a resolução do primeiro frame e o codec H264 para MP4
    frame_height, frame_width = frames[0].shape[:2]
    out = cv2.VideoWriter(f"{VIDEO_PATH}{video_path_mp4}", cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    # Carregar o logo com transparência (RGBA)
    logo = cv2.imread(WATERMARK_PATH, cv2.IMREAD_UNCHANGED)
    if logo is None:
        print("Erro ao carregar a marca d'água. Verifique o caminho do arquivo.")
        return None

    # Redimensionar o logo, se necessário
    logo_height, logo_width = logo.shape[:2]
    scaling_factor = 100 / logo_width
    logo = cv2.resize(logo, (int(logo_width * scaling_factor), int(logo_height * scaling_factor)))

    # Separar os canais do logo (RGBA)
    b, g, r, alpha = cv2.split(logo)
    overlay_color = cv2.merge((b, g, r))
    mask = cv2.merge((alpha, alpha, alpha)) / 255.0
    mask_inv = 1 - mask

    # Verificar se o VideoWriter foi corretamente criado
    if not out.isOpened():
        print("Erro ao abrir o VideoWriter.")
        return None

    # Processo de adicionar a marca d'água e salvar os frames
    for frame in frames:
        overlay = frame.copy()
        
        # Calcular a posição do logo no canto inferior direito
        x_position = frame_width - logo.shape[1] - 10
        y_position = frame_height - logo.shape[0] - 10

        # Definir a região de interesse (ROI) no frame onde o logo será inserido
        roi = overlay[y_position:y_position + logo.shape[0], x_position:x_position + logo.shape[1]]

        # Aplicar a máscara ao ROI
        roi = roi * mask_inv + overlay_color * mask
        overlay[y_position:y_position + logo.shape[0], x_position:x_position + logo.shape[1]] = roi

        # Escrever o frame com a marca d'água no arquivo de vídeo
        out.write(overlay)

    out.release()
    print("Vídeo salvo com sucesso em formato MP4.")
    return video_path_mp4
