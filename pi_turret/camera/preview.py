"""Preview a camera feed"""
from cv2 import cv2

def preview(frames):
    """Preview a camera feed"""
    for frame in frames:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        cv2.imshow('frame', rgb)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    #cv2.imwrite('capture.jpg', frame)
    cv2.destroyAllWindows()
