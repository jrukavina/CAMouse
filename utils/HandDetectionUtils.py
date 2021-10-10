import time
from enum import Enum

from utils.MathUtils import *


class FingersPose(Enum):
    OTHER = 0
    INDEX_UP = 1
    INDEX_MIDDLE_UP = 2
    INDEX_MIDDLE_RING_UP = 3


class ThumbPose(Enum):
    STRAIGHT = 0
    BENT = 1


class HandPoseElement(object):
    def __init__(self, fp=FingersPose, tp=ThumbPose):
        self.fingersPose = fp
        self.thumbPose = tp
        self.time = time.time()


class PoseHistory(object):
    def __init__(self, capacity=100):
        self.list = list()
        self.capacity = capacity
        self.lastClick = 0
        self.toggled = False

    def add(self, element):
        self.list.insert(0, element)
        if self.size() > self.capacity:
            self.list.pop()

    def get(self, index: int):
        return self.list[index]

    # returns first element added between given time interval (in seconds) and now, or return default element
    # def getClosestToTargetTime(self, seconds: float):
    #     targetTime = time.time() - seconds
    #     index = 0
    #     lastDeltaTime = np.Inf
    #     for pose in self.list:
    #         deltaTime = math.fabs(pose.time - targetTime)
    #         if deltaTime < lastDeltaTime:
    #             lastDeltaTime = deltaTime
    #             index += 1
    #         else:
    #             return self.get(index - 1)
    #
    #     # else return default
    #     return HandPoseElement(FingersPose.OTHER, ThumbPose.STRAIGHT)

    def logClick(self):
        self.lastClick = time.time()

    def timeSinceLastClick(self):
        return time.time() - self.lastClick

    def size(self):
        return len(self.list)


class GestureDetector(object):

    def __init__(self, history):
        self.history = history

    def fingersUp(self, handLandmarks):
        # array of up fingers; [index f., middle f., ring f., pinky f.]
        return [handLandmarks[8].y < handLandmarks[6].y, handLandmarks[12].y < handLandmarks[10].y,
                handLandmarks[16].y < handLandmarks[14].y, handLandmarks[20].y < handLandmarks[18].y]

    def handPose(self, handLandmarks):
        fingersUp = self.fingersUp(handLandmarks)
        if fingersUp == [True, False, False, False]:
            fp = FingersPose.INDEX_UP
        elif fingersUp == [True, True, False, False]:
            fp = FingersPose.INDEX_MIDDLE_UP
        elif fingersUp == [True, True, True, False]:
            fp = FingersPose.INDEX_MIDDLE_RING_UP
        else:
            fp = FingersPose.OTHER

        thumb_cmc = handLandmarks[1]
        thumb_mcp = handLandmarks[2]
        thumb_ip = handLandmarks[3]
        thumb_tip = handLandmarks[4]
        # straightLine = lineFromPoints(thumb_cmc.x, thumb_cmc.y, thumb_tip.x, thumb_tip.y)
        # palmLength = distance(thumb_cmc.x, thumb_cmc.y, thumb_tip.x, thumb_tip.y)
        # if (thumb_ip.y - thumb_tip.y) / palmLength > 0.1 and distFromLine(thumb_ip.x, thumb_ip.y,
        #                                                                   straightLine) / palmLength > 0.125:
        fst, snd = (thumb_ip, thumb_mcp) if thumb_ip.x <= thumb_mcp.x else (thumb_mcp, thumb_ip)
        k1 = slope(thumb_cmc.x, thumb_cmc.y, thumb_mcp.x, thumb_mcp.y)
        k2 = slope(thumb_ip.x, thumb_ip.y, thumb_tip.x, thumb_tip.y)
        if (k1 * k2 == -1.0 or abs((k2 - k1) / (1 + k1 * k2)) > 1.2) \
                and Line.isPointAbove(fst.x, fst.y, snd.x, snd.y, thumb_tip.x, thumb_tip.y):
            tp = ThumbPose.BENT
        else:
            tp = ThumbPose.STRAIGHT

        return HandPoseElement(fp, tp)

    def handIsPointing(self, handLandmarks):
        fingersUp = self.fingersUp(handLandmarks)
        return fingersUp[0] and not fingersUp[-1]

    def toggleRecognized(self):
        for element in self.history.list:
            if element.time > self.history.lastClick:
                if element.fingersPose != FingersPose.INDEX_UP or element.thumbPose != ThumbPose.BENT:
                    return False  # don't toggle mouse

            else:  # all poses up to last click are INDEX_UP and thumb BENT
                self.history.toggled = True
                return True

    def untoggleRecognized(self):
        for i in range(5):
            if self.history.get(i).thumbPose == ThumbPose.BENT:
                return False
        return True

    # def thumbClicked(self, currentHandLandmarks, oldHandLandmarks, treshold=0.8):
    #     return distance(currentHandLandmarks[4].x, currentHandLandmarks[4].y, currentHandLandmarks[2].x,
    #                          currentHandLandmarks[2].y) / distance(oldHandLandmarks[4].x, oldHandLandmarks[4].y,
    #                                                                     oldHandLandmarks[2].x,
    #                                                                     oldHandLandmarks[2].y) < treshold
    #
    # def indexMovedDown(self, currentHandLandmarks, oldHandLandmarks, treshold=0.8):
    #     return distance(currentHandLandmarks[8].x, currentHandLandmarks[8].y, currentHandLandmarks[6].x,
    #                          currentHandLandmarks[6].y) / distance(oldHandLandmarks[8].x, oldHandLandmarks[8].y,
    #                                                                     oldHandLandmarks[6].x,
    #                                                                     oldHandLandmarks[6].y) < treshold
    #
    # def handMoved(self, currentHandLandmarks, oldHandLandmarks, treshold=1.05):
    #     return (distance(currentHandLandmarks[13].x, currentHandLandmarks[13].y, oldHandLandmarks[13].x,
    #                           oldHandLandmarks[13].y) / self.screen_width) > treshold and (
    #                distance(currentHandLandmarks[9].x, currentHandLandmarks[9].y, oldHandLandmarks[9].x,
    #                              oldHandLandmarks[9].y)) / self.screen_width > treshold
