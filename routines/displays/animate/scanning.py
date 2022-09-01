import time
from PIL import Image

def animate(left_eye, right_eye, left_mouth, right_mouth, delay=0.5):

    eye_left = Image.open('routines/displays/images/eyes/scanning_left.png')
    eye_mid_left = Image.open('routines/displays/images/eyes/scanning_mid_left.png')
    eye_mid = Image.open('routines/displays/images/eyes/scanning_center.png')
    eye_mid_right = Image.open('routines/displays/images/eyes/scanning_mid_right.png')
    eye_right = Image.open('routines/displays/images/eyes/scanning_right.png')

    mouth_left = Image.open('routines/displays/images/mouth/neutral_left.png')
    mouth_right = Image.open('routines/displays/images/mouth/neutral_right.png')

    left_mouth.image(mouth_left)
    right_mouth.image(mouth_right)

    while True:
        set_eyes_and_delay(left_eye, right_eye, delay, eye_mid)
        set_eyes_and_delay(left_eye, right_eye, delay, eye_mid_right)
        set_eyes_and_delay(left_eye, right_eye, delay, eye_right)
        set_eyes_and_delay(left_eye, right_eye, delay, eye_mid_right)
        set_eyes_and_delay(left_eye, right_eye, delay, eye_mid)
        set_eyes_and_delay(left_eye, right_eye, delay, eye_mid_left)
        set_eyes_and_delay(left_eye, right_eye, delay, eye_left)
        set_eyes_and_delay(left_eye, right_eye, delay, eye_mid_left)

def set_eyes_and_delay(left_eye, right_eye, delay, image):
    left_eye.image(image)
    right_eye.image(image)
    time.sleep(delay)  