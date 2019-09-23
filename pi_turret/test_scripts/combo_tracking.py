"""
Testing combined tracking methods
"""
import io
import time
import cv2
import threading
import boto3
import pi_turret.config as config
from PIL import Image
from pi_turret.camera.webcam_frames import WebcamFrames
from pi_turret.test_scripts.face_tracking import Tracker, haarFacePath
from pi_turret.test_scripts.motion_tracking import handle_new_frame


def frame_to_bytes(frame):
    """
    Convert video frame to bytes
    """
    # convert opencv frame (with type()==numpy) into PIL Image
    pil_img = Image.fromarray(frame)
    stream = io.BytesIO()
    pil_img.save(stream, format='JPEG')  # convert PIL Image to Bytes
    bin_img = stream.getvalue()
    return bin_img


def compare_faces(client, target_image, source_image=None, source_key='public/bolo'):
    """
    Calls aws client's compare_faces with the source image or source key in S3 
    """
    target_bytes = frame_to_bytes(target_image)

    if source_image is not None:
        target_bytes = frame_to_bytes(source_image)
        source_image_payload = {'Bytes': source_image}
    else:
        source_image_payload = {
            'S3Object': {
                'Bucket': 'foam-turret-bolos-dev',
                'Name': source_key
            }
        }

    response = client.compare_faces(SimilarityThreshold=70,
                                    SourceImage=source_image_payload,
                                    TargetImage={'Bytes': target_bytes})

    for face_match in response['FaceMatches']:
        position = face_match['Face']['BoundingBox']
        confidence = str(face_match['Face']['Confidence'])
        left = str(position['Left'])
        top = str(position['Top'])
        print(
            f'The face at {left} {top} matches with {confidence}% confidence {time.time()}')
        if float(confidence) > 90:
            return position
    return None


def combo_tracking(stop_event, output_filename=None, show_ui=False, min_area=300, callback=None):
    """
    Use multiple tracking strategies to find a target
    """
    tracker = Tracker([haarFacePath])
    client = boto3.client('rekognition')

    try:
        frames = 0
        start = time.time()

        out = None
        if output_filename is not None:
            out = cv2.VideoWriter(
                f"{output_filename}.avi",
                cv2.VideoWriter_fourcc(*"H264"),
                10,
                config.CAMERA_RESOLUTION
            )

        past_frame = None
        cooldown_timestamp = time.time()
        for frame in WebcamFrames():
            if stop_event.is_set():
                break
            frames += 1
            new_past_frame, motion = handle_new_frame(
                frame, past_frame, min_area)

            if motion:
                faces = tracker.detect_faces(frame)
                if faces:
                    # Send frame to be checked
                    if new_past_frame is not None and new_past_frame.any() \
                            and cooldown_timestamp + 3 < time.time():
                        print("Comparing faces")
                        result = compare_faces(client, new_past_frame)
                        cooldown_timestamp = time.time()
                        if result:
                            face_x = result['Left'] * config.CAMERA_WIDTH
                            face_y = result['Top'] * config.CAMERA_HEIGHT
                            if callback is not None:
                                callback(face_x, face_y)

                    # pylint: disable=invalid-name
                    if show_ui:
                        for c in faces:
                            (x, y, w, h) = c  # cv2.boundingRect(c)
                            # pylint: enable=invalid-name
                            print(f"Face Bounds: x: {x} y: {y} w:{w} h:{h}")
                            cv2.rectangle(
                                frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.putText(frame, str("Face"), (x, y),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))

            if output_filename is not None:
                out.write(frame)
            if show_ui:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
                cv2.imshow('Face Tracking', rgb)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            past_frame = new_past_frame

    finally:
        print("Exiting")
        if out is not None:
            out.release()
        cv2.destroyAllWindows()
        end = time.time()
        fps = frames / (end - start)
        print(f"Estimated fps: {fps}")


if __name__ == "__main__":
    print("Combo Tracking")
    EVENT = threading.Event()
    combo_tracking(EVENT, show_ui=True, output_filename="test-combo-tracking")
