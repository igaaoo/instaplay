from collections import deque
from config import BUFFER_SIZE

buffer = deque(maxlen=BUFFER_SIZE)

def add_frame_to_buffer(frame):
    buffer.append(frame)

def get_buffer_frames():
    return list(buffer)
