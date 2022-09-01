import multiprocessing
import time

from adafruit_ht16k33.matrix import Matrix8x8x2

from routines.displays.animate.thinking import animate as animate_think
from routines.displays.animate.talking import animate as animate_talk
from routines.displays.animate.playing import animate as animate_play
from routines.displays.animate.scanning import animate as animate_scanning

from routines.displays.static.smile import display as display_smile
from routines.displays.static.connect import display as display_connect
from routines.displays.static.love import display as display_love
from routines.displays.static.option import display as display_option
from routines.displays.static.sad import display as display_sad

class Displays:
    def __init__(self, i2c):
        self.i2c = i2c
        self.process = None
        
        self.pet = None
        self.left_eye = Matrix8x8x2(i2c, address=0x70)
        self.right_eye = Matrix8x8x2(i2c, address=0x71)
        self.left_mouth = Matrix8x8x2(i2c, address=0x73)
        self.right_mouth = Matrix8x8x2(i2c, address=0x72)
    
    def terminate_if_displaying(self):
        if (self.process is not None):
            self.process.terminate()
            time.sleep(0.1)
            self.process = None
        
    def animate(self, animation="think"):
        self.terminate_if_displaying()

        if (animation == "talk"):
            self.process = multiprocessing.Process(target=animate_talk, args=(self.left_eye, self.right_eye, self.left_mouth, self.right_mouth))
        elif (animation == "play"):
            self.process = multiprocessing.Process(target=animate_play, args=(self.left_eye, self.right_eye, self.left_mouth, self.right_mouth))
        elif (animation == "think"):
            self.process = multiprocessing.Process(target=animate_think, args=(self.left_eye, self.right_eye, self.left_mouth, self.right_mouth))
        elif (animation == "scan"):
            self.process = multiprocessing.Process(target=animate_scanning, args=(self.left_eye, self.right_eye, self.left_mouth, self.right_mouth))

        self.process.start()
    
    def static(self, image="smile"):
        self.terminate_if_displaying()

        if (image == "smile"):
            if self.pet is not None and self.pet.getInfo('pet','EMO') <= 3:
                display_sad(self.left_eye, self.right_eye, self.left_mouth, self.right_mouth)
            else:
                display_smile(self.left_eye, self.right_eye, self.left_mouth, self.right_mouth)
        elif (image == "connect"):
            display_connect(self.left_eye, self.right_eye, self.left_mouth, self.right_mouth)
        elif (image == "love"):
            display_love(self.left_eye, self.right_eye, self.left_mouth, self.right_mouth)
        elif (image == "option"):
            display_option(self.left_eye, self.right_eye, self.left_mouth, self.right_mouth)
            
