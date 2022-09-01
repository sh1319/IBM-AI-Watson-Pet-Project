import time
from PIL import Image

def display(left_eye, right_eye, left_mouth, right_mouth):

    eye = Image.open('routines/displays/images/bluetooth.png')

    left_eye.image(eye)
    right_eye.image(eye)
    left_mouth.fill(left_mouth.LED_OFF)
    right_mouth.fill(right_mouth.LED_OFF)
