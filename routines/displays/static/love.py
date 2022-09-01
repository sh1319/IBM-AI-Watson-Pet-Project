import time
from PIL import Image

def display(left_eye, right_eye, left_mouth, right_mouth):

    eye_left = Image.open('routines/displays/images/eyes/heart_left.png')
    eye_right = Image.open('routines/displays/images/eyes/heart_right.png')
    mouth_left = Image.open('routines/displays/images/mouth/cheek_tongue_left.png')
    mouth_right = Image.open('routines/displays/images/mouth/cheek_tongue_right.png')

    left_eye.image(eye_left)
    right_eye.image(eye_right)
    left_mouth.image(mouth_left)
    right_mouth.image(mouth_right)
