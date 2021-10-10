import time
from threading import Thread, Event

import cv2


class FPSCounter(object):
    def __init__(self, checkpoint=10):
        self.checkpoint = checkpoint
        self.count = 0

    def start(self):
        self.iteration = 0
        self.fps = 0
        self.t1 = time.time()

    def update(self):
        self.iteration += 1
        self.count += 1
        if self.hasNewValue():
            self.fps = self.iteration / (time.time() - self.t1)

    def hasNewValue(self):
        return self.iteration >= self.checkpoint

    def getFPS(self):
        self.iteration = 0
        self.t1 = time.time()
        return self.fps

    def reset(self):
        self.iteration = 0
        self.fps = 0


class WebCamStream(object):
    def __init__(self, src=0, fps=30):
        print('Starting camera...')
        fps = min(30, fps)
        self.capture = cv2.VideoCapture(src, cv2.CAP_ANY)  # cv2.CAP_DSHOW -> faster startup
        self.capture.set(cv2.CAP_PROP_FPS, fps)
        # self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        # self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.newFrame = False
        self.sleepTime = 1. / fps - 0.001
        print('Done')
        self.scalingFactor = 1.
        succ, test = self.capture.read()
        if not succ:
            raise Exception("No video stream! Check if video source has been set up correctly.")
        self.height, self.width, _ = tuple(int(i * self.scalingFactor) for i in test.shape)
        self.lock = Event()
        self.slowed = False
        self.running = False
        self.thread = None
        self.frame = None
        self.pauseTime = 0.2

    def update(self):
        while self.running:
            if self.capture.isOpened():
                self.newFrame, self.frame = self.capture.read()
                if self.scalingFactor != 1.0:
                    self.newFrame = False
                    self.frame = cv2.resize(self.frame, (self.width, self.height), interpolation=cv2.INTER_AREA)
                    self.newFrame = True
                self.lock.set()
                if self.slowed:
                    time.sleep(self.pauseTime)
                # else:
                #     time.sleep(self.sleepTime)

    def frameIsAvailable(self):
        return self.newFrame

    def getFrame(self):
        self.newFrame = False
        return self.frame

    def start(self):
        self.running = True
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False

    def terminate(self):
        self.stop()
        self.capture.release()
        self.thread.join()

    def getLock(self):
        return self.lock

    def isPaused(self):
        return self.slowed

    def pauseFor(self, pauseTime):
        self.slowed = True
        self.pauseTime = pauseTime

    def limitFPS(self, fps):
        self.pauseFor(1. / fps)

    def continuous(self):
        self.slowed = False


# if __name__ == '__main__':
#
#     stream = WebCamStream()
#     lock = stream.getLock()
#     stream.start()
#     counter = FPSCounter()
#     counter.start()
#
#     while True:
#         while not stream.frameIsAvailable():
#             # time.sleep(0.001)
#             lock.wait()
#             lock.clear()
#
#         img = stream.getFrame()
#
#         counter.update()
#         if counter.hasNewValue():
#             text = str(round(counter.getFPS(), 1)) + ' FPS'
#             print(text)
