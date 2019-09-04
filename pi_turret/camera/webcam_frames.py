import cv2


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
    for frame in WebcamFrames():
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        cv2.imshow('frame', rgb)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    #cv2.imwrite('capture.jpg', frame)
    cv2.destroyAllWindows()
