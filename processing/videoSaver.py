import cv2
import numpy as np
from config import VIDEO_PATH, WATERMARK_PATH
from processing.bufferManager import get_buffer_frames

def save_video_with_watermark(fps):
    frames = get_buffer_frames()
    if not frames:
        print("Buffer vazio. Nenhum vídeo para salvar.")
        return None

    # Calcular o número de frames a serem removidos para cortar os últimos 2 segundos
    frames_to_remove = int(fps)
    frames = frames[:-frames_to_remove]  # Excluir os últimos 2 segundos

    # Inicialize o escritor de vídeo com a resolução do primeiro frame
    frame_height, frame_width = frames[0].shape[:2]
    out = cv2.VideoWriter(VIDEO_PATH, cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width, frame_height))

    # Carregar o logo com transparência (RGBA)
    logo = cv2.imread(WATERMARK_PATH, cv2.IMREAD_UNCHANGED)
    logo_height, logo_width = logo.shape[:2]

    # Redimensionar o logo, se necessário
    scaling_factor = 100 / logo_width  # Ajusta a largura para 100 pixels (ajuste conforme necessário)
    logo = cv2.resize(logo, (int(logo_width * scaling_factor), int(logo_height * scaling_factor)))

    # Separar os canais do logo (RGBA)
    b, g, r, alpha = cv2.split(logo)
    overlay_color = cv2.merge((b, g, r))

    # Criar uma máscara e seu inverso com base no canal alfa
    mask = cv2.merge((alpha, alpha, alpha)) / 255.0
    mask_inv = 1 - mask

    # Verificar se o VideoWriter foi corretamente criado
    if not out.isOpened():
        print("Erro ao abrir o VideoWriter.")
        return None

    # Processo de adicionar a marca d'água e salvar os frames (exceto os últimos 2 segundos)
    for frame in frames:
        overlay = frame.copy()

        # Calcular a posição do logo no canto inferior direito
        x_position = frame_width - logo.shape[1] - 10  # Posição X com 10px de margem
        y_position = frame_height - logo.shape[0] - 10  # Posição Y com 10px de margem

        # Definir a região de interesse no frame onde o logo será inserido
        roi = overlay[y_position:y_position + logo.shape[0], x_position:x_position + logo.shape[1]]

        # Aplicar a máscara ao logo e ao ROI
        roi = roi * mask_inv + overlay_color * mask

        # Colocar o ROI modificado de volta no frame
        overlay[y_position:y_position + logo.shape[0], x_position:x_position + logo.shape[1]] = roi

        # Escrever o frame com a marca d'água
        out.write(overlay)

    out.release()
    return VIDEO_PATH
