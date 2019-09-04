"""Iterator that loops over frames from your webcam."""
from cv2 import cv2
from pi_turret.camera.preview import preview


class WebcamFrames:
    """Iterator that loops over frames from your webcam."""

    def __init__(self, video_port=0):
        self.cap = cv2.VideoCapture(video_port)


    def __del__(self):
        self.cap.release()


    def __iter__(self):
        return self


    def __next__(self):
        ret, frame = self.cap.read()
        if not ret:
            raise StopIteration
        return frame


if __name__ == "__main__":
    preview(WebcamFrames())
