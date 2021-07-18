import cv2
import mediapipe as mp
import time
from numba import jit, cuda

# @jit(target="cuda")
class handDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.7, trackingCon=0.7):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackingCon = trackingCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackingCon)

        self.mpDraw = mp.solutions.drawing_utils

    # detects hands and draws landmark pts and connections
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)

        return img

    # Returns a list containing x and y position of each landmark
    def findPosition(self, img, handNo=0, draw=True):

        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

        return lmList

    # returns left or right hand
    def hand_LR(self):
        hd = None
        if self.results.multi_hand_landmarks:
            for handedness in self.results.multi_handedness:
                for h in handedness.classification:
                    # print(h.label)
                    # cv2.putText(flipped, h.label, (500, 40), cv2.FONT_ITALIC, 1, (0, 0, 0), 3)
                    hd = h.label

        return hd


def main():
    cTime = 0
    pTime = 0

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    detector = handDetector()

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        # if len(lmList) != 0:
        #     print(lmList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
