import time
from PIL import Image

def display(left_eye, right_eye, left_mouth, right_mouth):

    eye_center = Image.open('routines/displays/images/eyes/pointy_center.png')
    mouth_left = Image.open('routines/displays/images/mouth/sad_left.png')
    mouth_right = Image.open('routines/displays/images/mouth/sad_right.png')

    left_eye.image(eye_center)
    right_eye.image(eye_center)
    left_mouth.image(mouth_left)
    right_mouth.image(mouth_right)
