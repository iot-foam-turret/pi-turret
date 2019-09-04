"""Function to detect motion on a video feed"""
import time
from cv2 import cv2
from pi_turret.camera.webcam_frames import WebcamFrames


def handle_new_frame(frame, past_frame, min_area):
    (h, w) = frame.shape[:2]
    # r = 500 / float(w)
    # dim = (500, int(h * r))
    # frame = cv2.resize(frame, dim, cv2.INTER_AREA) # We resize the frame
    # We apply a black & white filter
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)  # Then we blur the picture

    # if the first frame is None, initialize it because there is no frame for
    # comparing the current one with a previous one
    if past_frame is None:
        past_frame = gray
        return past_frame, None

    # check if past_frame and current have the same sizes
    (h_past_frame, w_past_frame) = past_frame.shape[:2]
    (h_current_frame, w_current_frame) = gray.shape[:2]
    # This shouldnt occur but this is error handling
    if h_past_frame != h_current_frame or w_past_frame != w_current_frame:
        print('Past frame and current frame do not have the same sizes {0} {1} {2} {3}'.format(
            h_past_frame, w_past_frame, h_current_frame, w_current_frame))
        return None, None

    # compute the absolute difference between the current frame and first frame
    frame_delta = cv2.absdiff(past_frame, gray)
    # then apply a threshold to remove camera motion and other false positives (like light changes)
    _, thresh = cv2.threshold(frame_delta, 50, 255, cv2.THRESH_BINARY)
    # dilate the thresholded image to fill in holes, then find contours on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    
    contours, _ = cv2.findContours(
        thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cnts = cnts[0] if imutils.is_cv2() else cnts[1]

    motion = []
    # loop over the contours
    for c in contours:
        # if the contour is too small or too big, ignore it
        area = cv2.contourArea(c)
        if area < min_area or area > (h * w) / 2:
            continue
        print(f"Motion detected! {area}")
        motion.append(c)
    return None, motion


def test_motion_tracking():
    """Testing motion tracking"""
    # Motion detection sensitivity
    min_area = 300
    past_frame = None
    print("Starting motion detection")
    try:
        # for frame in PiCamFrames():
        frames = 0
        start = time.time()
        frame_source = WebcamFrames()
        # out = cv2.VideoWriter("video.mp4", cv2.VideoWriter_fourcc(*'MP4V'), 10, (1280, 720))
        for frame in frame_source:
            frames += 1
            new_past_frame, motion = handle_new_frame(
                frame, past_frame, min_area)
            if motion is not None:
                for c in motion:
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                if len(motion) > 0:
                    # out.write(frame)
            
            past_frame = new_past_frame
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
            cv2.imshow('frame', rgb)
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
    test_motion_tracking()
