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

    frame_height, frame_width = frames[0].shape[:2]
    out = cv2.VideoWriter(f"{VIDEO_PATH}{video_path_mp4}", cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    # Carregar o logo com canal alpha (RGBA)
    logo = cv2.imread(WATERMARK_PATH, cv2.IMREAD_UNCHANGED)
    if logo is None:
        print("Erro ao carregar a marca d'água. Verifique o caminho do arquivo.")
        return None

    # Redimensionar para 15% da largura do frame — proporcional à resolução
    target_width = max(80, int(frame_width * 0.15))
    logo_h, logo_w = logo.shape[:2]
    target_height = int(logo_h * target_width / logo_w)
    interp = cv2.INTER_AREA if target_width < logo_w else cv2.INTER_CUBIC
    logo = cv2.resize(logo, (target_width, target_height), interpolation=interp)

    # Separar canais e pré-calcular máscaras em float32 (evita artefatos de arredondamento)
    b, g, r, alpha = cv2.split(logo)
    overlay_color = cv2.merge((b, g, r)).astype(np.float32)
    mask = alpha.astype(np.float32) / 255.0
    mask = np.stack([mask, mask, mask], axis=2)  # (H, W, 3)
    mask_inv = 1.0 - mask

    logo_h, logo_w = logo.shape[:2]
    x_pos = frame_width - logo_w - 20
    y_pos = frame_height - logo_h - 20

    if not out.isOpened():
        print("Erro ao abrir o VideoWriter.")
        return None

    for frame in frames:
        roi = frame[y_pos:y_pos + logo_h, x_pos:x_pos + logo_w].astype(np.float32)
        blended = (roi * mask_inv + overlay_color * mask).astype(np.uint8)
        frame[y_pos:y_pos + logo_h, x_pos:x_pos + logo_w] = blended
        out.write(frame)

    out.release()
    print("Vídeo salvo com sucesso em formato MP4.")
    return video_path_mp4
