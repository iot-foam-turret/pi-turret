"""Function to detect motion on a video feed"""
import time
import cv2
import os.path
from pi_turret.camera.webcam_frames import WebcamFrames

my_path = os.path.abspath(os.path.dirname(__file__))
haarFacePath = os.path.join(my_path, "./haar_cascades/frontalface_default.xml")
haarProfilePath = os.path.join(
    my_path, "./haar_cascades/haarcascade_profileface.xml")
haarBodyPath = os.path.join(
    my_path, "./haar_cascades/haarcascade_fullbody.xml")
haarUpperBodyPath = os.path.join(
    my_path, "./haar_cascades/haarcascade_upperbody.xml")


class Tracker:

    def __init__(self, haarPaths):
        self.tracked_id = 1
        self.detectors = list(map(lambda haarPath: cv2.CascadeClassifier(haarPath), haarPaths))

    def detect_faces(self, frame):
        """
        Return an array of (x, y, w, h) for each detected face.
        """
        # convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = []
        # detect all faces in the input frame
        for detector in self.detectors:
            detected = detector.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=9,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            faces = faces + list(detected)

        # check to see if a face was found
        if len(faces) > 0:
            return faces
        return None

    def intersects(self, left, right):
        (xl, yl, wl, hl) = left
        (xr, yr, wr, hr) = right
        return not ((xl + wl) < xr or xl > (xr + wr) or yl > (yr + hr) or (yl + hl) < yr)

    def track_faces(self, old_faces, new_faces):
        tracked_faces = []
        for new_face in new_faces:
            match_found = False
            (x, y, w, h) = new_face
            for old_face in old_faces:
                (ox, oy, ow, oh, old_id) = old_face
                if self.intersects(new_face, (ox, oy, ow, oh)):
                    match_found = True
                    tracked_faces.append((x, y, w, h, old_id))
            if not match_found:
                face_id = self.tracked_id
                tracked_faces.append((x, y, w, h, face_id))
                self.tracked_id += 1

        return tracked_faces

def test_tracking():
    """Testing face tracking"""
    tracker = Tracker([haarFacePath])
    print("Starting face tracking")
    try:
        # for frame in PiCamFrames():
        frames = 0
        start = time.time()
        frame_source = WebcamFrames()
        # out = cv2.VideoWriter("video.mp4", cv2.VideoWriter_fourcc(*'MP4V'), 10, (1280, 720))
        tracked = []
        for frame in frame_source:
            frames += 1
            faces = tracker.detect_faces(frame)
            if faces is not None:
                tracked = tracker.track_faces(tracked, faces)
                if tracked is not None:
                    for c in tracked:
                        (x, y, w, h, face_id) = c  # cv2.boundingRect(c)
                        print(f"Face Bounds: x: {x} y: {y} w:{w} h:{h}")
                        cv2.rectangle(
                            frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, str(face_id), (x, y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))
            else:
                # Considering not reseting this immediately
                tracked = []

            # out.write(frame)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
            cv2.imshow('Face Tracking', rgb)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        print("Exiting")
        # out.release()
        cv2.destroyAllWindows()
        end = time.time()
        fps = frames / (end - start)
        print(f"Estimated fps: {fps}")


if __name__ == '__main__':
    test_tracking()
