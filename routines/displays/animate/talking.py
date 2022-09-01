import time
from PIL import Image

def animate(left_eye, right_eye, left_mouth, right_mouth, delay=0.3):
    eye_center = Image.open('routines/displays/images/eyes/pointy_center.png')
    mouth_left_open = Image.open('routines/displays/images/mouth/talking_open_left.png')
    mouth_right_open = Image.open('routines/displays/images/mouth/talking_open_right.png')
    mouth_left_closed = Image.open('routines/displays/images/mouth/talking_closed_left.png')
    mouth_right_closed = Image.open('routines/displays/images/mouth/talking_closed_right.png')

    left_eye.image(eye_center)
    right_eye.image(eye_center)
    while True:
        left_mouth.image(mouth_left_open)
        right_mouth.image(mouth_right_open)
        time.sleep(delay)
        left_mouth.image(mouth_left_closed)
        right_mouth.image(mouth_right_closed)
        time.sleep(delay)