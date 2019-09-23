"""Function to detect motion on a video feed"""
import time
import os.path
import cv2
import pi_turret.config as config
from pi_turret.camera.webcam_frames import WebcamFrames

# pylint: disable=invalid-name
my_path = os.path.abspath(os.path.dirname(__file__))
haarFacePath = os.path.join(my_path, "haar_cascades/frontalface_default.xml")
haarProfilePath = os.path.join(
    my_path, "haar_cascades/haarcascade_profileface.xml")
haarBodyPath = os.path.join(
    my_path, "haar_cascades/haarcascade_fullbody.xml")
haarUpperBodyPath = os.path.join(
    my_path, "haar_cascades/haarcascade_upperbody.xml")


def tracked_id():
    """
    Tracking id generator
    """
    base_id = 0
    while True:
        base_id += 1
        yield base_id


class Tracker:
    """
    Tracker
    """

    def __init__(self, haarPaths):
        self.detectors = list(map(cv2.CascadeClassifier, haarPaths))

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
        if faces:
            return faces
        return None


def intersects(left, right):
    """
    Returns true if two rectangles overlap
    """
    (xl, yl, wl, hl) = left
    (xr, yr, wr, hr) = right
    return not ((xl + wl) < xr or xl > (xr + wr) or yl > (yr + hr) or (yl + hl) < yr)


def track_faces(old_faces, new_faces, id_generator):
    """
    Returns array of faces with identifiers
    """
    tracked_faces = []
    for new_face in new_faces:
        match_found = False
        (x, y, w, h) = new_face
        for old_face in old_faces:
            (ox, oy, ow, oh, old_id) = old_face
            if intersects(new_face, (ox, oy, ow, oh)):
                match_found = True
                tracked_faces.append((x, y, w, h, old_id))
        if not match_found:
            face_id = next(id_generator)
            tracked_faces.append((x, y, w, h, face_id))

    return tracked_faces


def test_tracking(output_filename=None, show_ui=False):
    """Testing face tracking"""
    tracker = Tracker([haarFacePath])
    print("Starting face tracking")
    try:
        # for frame in PiCamFrames():
        frames = 0
        start = time.time()
        if output_filename is not None:
            out = cv2.VideoWriter(
                f"{output_filename}.avi", cv2.VideoWriter_fourcc(*'H264'), 10, config.CAMERA_RESOLUTION)
        tracked = []
        skipped_frames = 0
        id_generator = tracked_id()
        for frame in WebcamFrames():
            frames += 1
            faces = tracker.detect_faces(frame)
            if faces is not None:
                found_faces = track_faces(tracked, faces, id_generator)
                if found_faces is not None and found_faces:
                    tracked = found_faces
                    # pylint: disable=invalid-name
                    for c in tracked:
                        (x, y, w, h, face_id) = c  # cv2.boundingRect(c)
                        # pylint: enable=invalid-name
                        print(f"Face Bounds: x: {x} y: {y} w:{w} h:{h}")
                        cv2.rectangle(
                            frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, str(face_id), (x, y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))
            else:
                skipped_frames += 1
                if skipped_frames > 15:
                    # Not reseting this immediately
                    # tracked = []
                    pass
            if output_filename is not None:
                out.write(frame)
            if show_ui:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
                cv2.imshow('Face Tracking', rgb)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        print("Exiting")
        if out is not None:
            out.release()
        cv2.destroyAllWindows()
        end = time.time()
        fps = frames / (end - start)
        print(f"Estimated fps: {fps}")


if __name__ == '__main__':
    test_tracking(output_filename="test-face-tracking", show_ui=True)
