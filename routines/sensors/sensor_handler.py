import time
import board
from digitalio import DigitalInOut, Direction

class Sensors:
    def __init__(self):
        top_pin = board.D4
        left_pin = board.D22
        right_pin = board.D27

        self.top_pad = DigitalInOut(top_pin)
        self.left_pad = DigitalInOut(left_pin)
        self.right_pad = DigitalInOut(right_pin)

        self.top_pad.direction = Direction.INPUT
        self.left_pad.direction = Direction.INPUT
        self.right_pad.direction = Direction.INPUT

        # self.process = None
    
    # def terminate_if_scanning(self):
    #     if (self.process is not None):
    #         self.process.terminate()
    #         self.process = None
    
    def check_inputs(self):
        if self.top_pad.value:
            return (True, "top")
        
        if self.left_pad.value:
            return (True, "left")
        
        if self.right_pad.value:
            return (True, "right")
        
        return False