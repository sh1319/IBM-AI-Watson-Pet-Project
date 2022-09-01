import time
from PIL import Image

def animate(left_eye, right_eye, left_mouth, right_mouth, delay=0.5):

    eye_top_left = Image.open('routines/displays/images/eyes/pointy_top_left.png')
    eye_left = Image.open('routines/displays/images/eyes/pointy_left.png')
    eye_center = Image.open('routines/displays/images/eyes/pointy_center.png')
    eye_right = Image.open('routines/displays/images/eyes/pointy_right.png')
    eye_top_right = Image.open('routines/displays/images/eyes/pointy_top_right.png')
    eye_top_center = Image.open('routines/displays/images/eyes/pointy_top_center.png')

    mouth_left = Image.open('routines/displays/images/mouth/open_left.png')
    mouth_right = Image.open('routines/displays/images/mouth/open_right.png')

    left_mouth.image(mouth_left)
    right_mouth.image(mouth_right)

    while True:
        set_eyes_and_delay(left_eye, right_eye, delay, eye_center)
        set_eyes_and_delay(left_eye, right_eye, delay, eye_right)
        set_eyes_and_delay(left_eye, right_eye, delay, eye_top_right)
        set_eyes_and_delay(left_eye, right_eye, delay, eye_top_center)
        set_eyes_and_delay(left_eye, right_eye, delay, eye_top_left)
        set_eyes_and_delay(left_eye, right_eye, delay, eye_left)

def set_eyes_and_delay(left_eye, right_eye, delay, image):
    left_eye.image(image)
    right_eye.image(image)
    time.sleep(delay)  