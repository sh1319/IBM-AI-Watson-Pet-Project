import time
from PIL import Image

def animate(left_eye, right_eye, left_mouth, right_mouth, delay=0.3):
    eye_center = Image.open('routines/displays/images/eyes/circle_center.png')
    eye_right = Image.open('routines/displays/images/eyes/circle_right.png')
    eye_left = Image.open('routines/displays/images/eyes/circle_left.png')
    eye_blink = Image.open('routines/displays/images/eyes/happy_eye.png')
    eye_closed_left = Image.open('routines/displays/images/eyes/closed_left.png')
    eye_closed_right = Image.open('routines/displays/images/eyes/closed_right.png')

    mouth_left = Image.open('routines/displays/images/mouth/open_left.png')
    mouth_right = Image.open('routines/displays/images/mouth/open_right.png')
    mouth_tongue_left = Image.open('routines/displays/images/mouth/tongue_left.png')
    mouth_tongue_right = Image.open('routines/displays/images/mouth/tongue_right.png')

    while True:
        left_mouth.image(mouth_left)
        right_mouth.image(mouth_right)
        left_eye.image(eye_center)
        right_eye.image(eye_center)

        time.sleep(delay)
        left_eye.image(eye_left)
        right_eye.image(eye_left)
        time.sleep(delay)
        left_eye.image(eye_right)
        right_eye.image(eye_right)
        time.sleep(delay)
        left_eye.image(eye_blink)
        right_eye.image(eye_blink)
        time.sleep(delay)
        left_eye.image(eye_center)
        right_eye.image(eye_center)
        time.sleep(delay)
        left_eye.image(eye_closed_right)
        right_eye.image(eye_closed_left)
        left_mouth.image(mouth_tongue_left)
        right_mouth.image(mouth_tongue_right)
        time.sleep(0.7)

