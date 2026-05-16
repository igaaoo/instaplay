import cv2
import threading
import queue


class VideoCapture:
    """
    Threaded video capture — a dedicated background thread reads frames
    continuously so the main loop never blocks on I/O.

    The internal queue holds at most 2 frames; stale frames are dropped so
    the consumer always gets the most recent image.
    """

    def __init__(self, source=0, width: int = 1280, height: int = 720):
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.fps: float = self.cap.get(cv2.CAP_PROP_FPS) or 30.0

        self._queue: queue.Queue = queue.Queue(maxsize=2)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="VideoCaptureThread")
        self._thread.start()

    # ------------------------------------------------------------------
    # Internal capture loop (runs in background thread)
    # ------------------------------------------------------------------

    def _loop(self) -> None:
        while not self._stop.is_set():
            ok, frame = self.cap.read()
            if not ok:
                continue
            # Keep the queue fresh — drop the oldest frame if full
            if self._queue.full():
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    pass
            self._queue.put(frame)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def read(self):
        """
        Returns (True, frame) with the latest captured frame.
        Blocks up to 1 second; returns (False, None) on timeout.
        """
        try:
            return True, self._queue.get(timeout=1.0)
        except queue.Empty:
            return False, None

    def release(self) -> None:
        """Stop the capture thread and release the underlying device."""
        self._stop.set()
        self._thread.join(timeout=2.0)
        self.cap.release()
