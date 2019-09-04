"""Iterator that loops over frames from PiCamera."""
import io
import numpy as np
from cv2 import cv2
import picamera
from pi_turret.camera.preview import preview


class PiCamFrames:
    """Iterator that loops over frames from PiCamera."""

    def __init__(self, resolution=(640, 480)):
        self.camera = picamera.PiCamera()
        self.camera.resolution = resolution


    def __del__(self):
        self.camera.close()


    def __iter__(self):
        return self


    def __next__(self):
        stream = io.BytesIO()
        self.camera.capture(stream, format='jpeg', use_video_port=False)
        data = np.fromstring(stream.getvalue(), dtype=np.uint8)
        frame = cv2.imdecode(data, 1)

        if frame is None:
            raise StopIteration
        return frame


if __name__ == "__main__":
    preview(PiCamFrames())
