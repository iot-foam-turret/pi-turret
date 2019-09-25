"""
Testing combined tracking methods
"""
import io
import time
from typing import Callable
import threading
import cv2
import boto3
from boto3_type_annotations.rekognition import Client
from PIL import Image
import pi_turret.config as config
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


def compare_faces(client: Client, callback: Callable, target_image, source_image=None, source_key='public/bolo'):
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

    def compare_faces_target():
        response = client.compare_faces(SimilarityThreshold=70,
                                        SourceImage=source_image_payload,
                                        TargetImage={'Bytes': target_bytes})

        for face_match in response['FaceMatches']:
            position = face_match['Face']['BoundingBox']
            confidence = face_match['Face']['Confidence']
            similarity = face_match['Similarity']
            # left = str(position['Left'])
            # top = str(position['Top'])
            # print(f'The face at {left} {top} matches with {confidence}% confidence {time.time()}')
            if confidence > 90 and similarity > 90:
                callback(position)
                return
            callback(None)

    compare_faces_thread = threading.Thread(
        target=compare_faces_target, daemon=True)
    compare_faces_thread.start()


cooldown_timestamp = time.time()
match = None


def combo_tracking(stop_event, output_filename=None, show_ui=False, min_area=300, callback: Callable = None):
    """
    Use multiple tracking strategies to find a target
    """
    tracker = Tracker([haarFacePath])
    client: Client = boto3.client('rekognition')

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
        last_move = 0
        for frame in WebcamFrames():
            if stop_event.is_set():
                break
            frames += 1

            new_past_frame, motion = handle_new_frame(
                frame, past_frame, min_area)

            faces = None

            if motion:
                faces = tracker.detect_faces(frame)
                # print(f"Detecting faces took {time.time() - start_detect_faces} seconds.")
            if faces:
                # pylint: disable=invalid-name
                (x, y, w, h) = (None, None, 0, 0)
                face_found = False
                for face in faces:
                    (current_x, current_y, current_w, current_h) = face
                    face_size = current_w * current_h
                    if w * h < face_size and face_size < config.MAX_FACE_SIZE:
                        (x, y, w, h) = face
                        face_found = True
                # print(f"Face at {x + w/2}, {y + h/2}")
                now = time.time()
                if face_found and (now - last_move) > config.FACE_TRACKING_COOLDOWN:
                    callback(face_x=x + w/2, face_y=y + h/2)
                    last_move = now
                # Send frame to be checked
                if face_found and (cooldown_timestamp - now) > config.COMPARE_FACES_COOLDOWN:
                    face_image = frame[y:y+h, x:x+w]

                    def make_compare_faces_callback(x, y, w, h):
                        def compare_faces_callback(result):
                            # pylint: disable=global-statement
                            global match
                            global cooldown_timestamp
                            if result:
                                # face_x = (
                                #     result['Left'] + result['Width']/2) * config.CAMERA_WIDTH
                                # face_y = (
                                #     result['Top'] + result['Height']/2) * config.CAMERA_HEIGHT
                                match = (int(x + w/2), int(y + h/2))
                                # print(f"Match at {face_x}, {face_y}")
                                if callback is not None:
                                    callback(fire=True)
                            cooldown_timestamp = time.time()
                        return compare_faces_callback
                    compare_faces(client, make_compare_faces_callback(x, y, w, h), face_image)

            if output_filename is not None:
                out.write(frame)
            if show_ui:
                if match:
                    (match_x, match_y) = match
                    cv2.circle(frame, (match_x, match_y), 5, (0, 0, 255), 2)
                    # cv2.rectangle(frame, , (match_x + 4, match_y + 4), (255, 0, 0), 2)
                for c in motion or []:
                    (x, y, w, h) = cv2.boundingRect(c)
                    # print(f"Motion Bounds: x: {x} y: {y} w:{w} h:{h}")
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (255, 0, 0), 2)
                for c in faces or []:
                    (x, y, w, h) = c
                    # print(f"Face Bounds: x: {x} y: {y} w:{w} h:{h}")
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)
                    cv2.putText(frame, str("Face"), (x, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))

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
    combo_tracking(EVENT, show_ui=True)
