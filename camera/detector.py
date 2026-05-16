import cv2
import threading
import queue
import numpy as np
from ultralytics import YOLO
from camera.pose_utils import has_both_hands_raised

# ---------------------------------------------------------------------------
# Singleton model — loaded once, reused forever
# ---------------------------------------------------------------------------

_model: YOLO | None = None
_model_lock = threading.Lock()


def _get_model() -> YOLO:
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:  # double-checked locking
                _model = YOLO("yolov8n-pose.pt")
    return _model


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resize_for_inference(frame: np.ndarray, width: int = 640) -> np.ndarray:
    """Downscale frame to `width` pixels wide (aspect ratio preserved)."""
    h, w = frame.shape[:2]
    if w == width:
        return frame
    new_h = int(h * width / w)
    return cv2.resize(frame, (width, new_h), interpolation=cv2.INTER_LINEAR)


# ---------------------------------------------------------------------------
# PoseDetector
# ---------------------------------------------------------------------------

class PoseDetector:
    """
    Runs YOLOv8-pose inference in a background thread.

    Usage
    -----
    detector = PoseDetector()
    detector.submit(frame)          # non-blocking — drop frame if busy
    players = detector.get_result() # list of person indices with hands raised
    detector.stop()
    """

    def __init__(self, inference_width: int = 640, skip_frames: int = 2, conf: float = 0.5):
        self._model = _get_model()
        self._inference_width = inference_width
        self._conf = conf
        self._skip_frames = skip_frames

        # Single-slot queue — we only care about the *latest* frame
        self._frame_queue: queue.Queue = queue.Queue(maxsize=1)
        self._result: list[int] = []
        self._result_lock = threading.Lock()

        self._frame_counter = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(
            target=self._inference_loop, daemon=True, name="PoseDetectorThread"
        )
        self._thread.start()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def submit(self, frame: np.ndarray) -> None:
        """
        Send a frame for pose inference.
        Frames are skipped according to `skip_frames` to reduce CPU/GPU load.
        If the inference thread is still busy the frame is silently dropped.
        """
        self._frame_counter += 1
        if self._frame_counter % self._skip_frames != 0:
            return
        # Replace any pending frame — always keep the newest
        if self._frame_queue.full():
            try:
                self._frame_queue.get_nowait()
            except queue.Empty:
                pass
        self._frame_queue.put(frame.copy())

    def get_result(self) -> list[int]:
        """
        Return the list of person indices (0-based) whose both hands are raised.
        Non-blocking — returns the last computed result immediately.
        """
        with self._result_lock:
            return list(self._result)

    def stop(self) -> None:
        """Signal the inference thread to exit and wait for it."""
        self._stop.set()
        self._thread.join(timeout=2.0)

    # ------------------------------------------------------------------
    # Background inference loop
    # ------------------------------------------------------------------

    def _inference_loop(self) -> None:
        while not self._stop.is_set():
            try:
                frame = self._frame_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            small = _resize_for_inference(frame, self._inference_width)

            results = self._model(small, verbose=False, conf=self._conf)

            raised: list[int] = []

            for result in results:
                if result.keypoints is None:
                    continue

                # shape: (N_persons, 17, 3)  — columns: x, y, confidence
                kps_all = result.keypoints.data.cpu().numpy()

                for person_idx, kps in enumerate(kps_all):
                    if has_both_hands_raised(kps):
                        raised.append(person_idx)

            with self._result_lock:
                self._result = raised
