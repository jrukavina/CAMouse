if __name__ == '__main__':
    import argparse
    import sys
    from tkinter import Tk
    # import time

    import cv2
    import mediapipe as mp
    import mouse
    import numpy as np

    from utils.AudioUtils import AudioPlayer
    from utils.HandDetectionUtils import *
    from utils.WebCamUtils import WebCamStream, FPSCounter


def cleanup():
    print('Exiting...')
    stream.terminate()
    if soundOn:
        audioPlayer.terminate()
    cv2.destroyAllWindows()
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cam-src", type=int, default=0, help="specify camera source (default is 0)")
    parser.add_argument("-m", "--mute", action="store_true", help="turn off audio feedback when clicking")
    parser.add_argument("-s", "--show-cam", action="store_true", help="show camera with diagnostic overlay")
    args = parser.parse_args()

    global soundOn
    soundOn = not args.mute
    if soundOn:
        global audioPlayer
        audioPlayer = AudioPlayer()

    text = ''
    font = cv2.FONT_HERSHEY_SIMPLEX
    line = cv2.LINE_AA

    global stream
    stream = WebCamStream(src=args.cam_src)
    lock = stream.getLock()
    stream.start()
    counter = FPSCounter()
    counter.start()

    mpHands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1,
                                       min_detection_confidence=0.8, min_tracking_confidence=0.5)
    mpDraw = mp.solutions.drawing_utils

    tk = Tk()
    screen_width, screen_height = tk.winfo_screenwidth(), tk.winfo_screenheight()
    del tk
    rectangle_scale = 0.35
    rectangle_height = int(stream.height * rectangle_scale)
    rectangle_width = int(rectangle_height * (screen_width / screen_height))

    vert_offset = 0.1
    relative_tracking_width_range = (
        ((stream.width - rectangle_width) / 2) / stream.width,
        ((stream.width / 2) + (rectangle_width / 2)) / stream.width)
    relative_tracking_height_range = (vert_offset, rectangle_scale + vert_offset)

    tracking_rectangle_p1 = (int((stream.width / 2) - (rectangle_width / 2)), int(vert_offset * stream.height))
    tracking_rectangle_p2 = (
        int((stream.width / 2) + (rectangle_width / 2)), rectangle_height + int(vert_offset * stream.height))

    last_mouse_x, last_mouse_y = 0, 0
    smoothening = 5
    disableNextClickFor = 0.35  # seconds

    history = PoseHistory()
    detector = GestureDetector(history)

    while True:
        while not stream.frameIsAvailable():
            # time.sleep(0.001)
            lock.wait()
            lock.clear()

        img = stream.getFrame()
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = mpHands.process(rgb_img)

        if results.multi_hand_landmarks:
            if stream.isPaused():
                stream.continuous()

            audioKey = 0

            for hand in results.multi_hand_landmarks:
                pose = detector.handPose(hand.landmark)
                if pose.fingersPose == FingersPose.OTHER:
                    break

                history.add(pose)

                index_tip = hand.landmark[8]
                mouse_x = np.interp(index_tip.x, relative_tracking_width_range, (0, screen_width - 1))
                mouse_y = np.interp(index_tip.y, relative_tracking_height_range, (0, screen_height - 1))
                # print(mouse_x, mouse_y)

                # ignore small movements
                if abs(last_mouse_x - mouse_x) / screen_width < 0.015 and abs(
                        last_mouse_y - mouse_y) / screen_height < 0.015:
                    mouse_x, mouse_y = last_mouse_x, last_mouse_y

                else:
                    mouse_x = last_mouse_x + (mouse_x - last_mouse_x) / smoothening
                    mouse_y = last_mouse_y + (mouse_y - last_mouse_y) / smoothening
                    mouse.move(screen_width - mouse_x, mouse_y)

                if history.toggled:
                    if detector.untoggleRecognized():
                        history.toggled = False
                        mouse.release('left')
                        audioKey = 1

                elif history.timeSinceLastClick() > disableNextClickFor and pose.thumbPose == ThumbPose.BENT:

                    if detector.toggleRecognized():
                        mouse.press('left')
                        audioKey = 1
                        continue  # toggle mouse and stop further mouse click logic

                    history.logClick()
                    # print('Click, frame ', str(counter.count))

                    if pose.fingersPose == FingersPose.INDEX_UP:
                        mouse.click('left')
                        audioKey = 1

                    elif pose.fingersPose == FingersPose.INDEX_MIDDLE_UP:
                        mouse.double_click('left')
                        audioKey = 2

                    elif pose.fingersPose == FingersPose.INDEX_MIDDLE_RING_UP:
                        mouse.click('right')
                        audioKey = 1

                last_mouse_x, last_mouse_y = mouse_x, mouse_y

                if args.show_cam:
                    x, y = int(index_tip.x * stream.width), int(index_tip.y * stream.height)
                    cv2.circle(img, (x, y), 10, (255, 0, 255), cv2.FILLED)
                    mpDraw.draw_landmarks(img, hand, mp.solutions.hands.HAND_CONNECTIONS)
                    # cv2.imwrite('images/' + str(counter.count) + '.jpeg', img)

            if soundOn:
                audioPlayer.play(audioKey)

        else:
            stream.limitFPS(5)

        counter.update()
        if counter.hasNewValue():
            # print(str(counter.getFPS()), ' FPS')
            text = str(round(counter.getFPS(), 1)) + ' FPS'

        if args.show_cam:
            img = cv2.flip(img, 1)
            cv2.putText(img, text, (5, 30), font, 1, (40, 0, 255), 2, line)
            cv2.rectangle(img, tracking_rectangle_p1, tracking_rectangle_p2, (255, 0, 0), 2)
            cv2.imshow('Camera', img)
            if cv2.waitKey(1) == ord('q'):
                cleanup()


if __name__ == '__main__':
    stream, audioPlayer, soundOn = None, None, None
    try:
        main()
    except KeyboardInterrupt:
        cleanup()
