#https://www.digikey.co.uk/en/maker/blogs/2021/how-to-control-servo-motors-with-a-raspberry-pi
import time
import multiprocessing

from gpiozero import Servo

from routines.motors.animate.play import animate as animate_play

class Motors:
    def __init__(self):
        self.process = None
        self.left_arm = Servo(10)
        self.right_arm = Servo(24)

        
    def terminate_if_moving(self):
        if (self.process is not None):
            self.process.terminate()
            self.process = None
    
    def play(self):
        self.terminate_if_moving()
        self.process = multiprocessing.Process(target=animate_play, args=(self.left_arm, self.right_arm))
        self.process.start()
