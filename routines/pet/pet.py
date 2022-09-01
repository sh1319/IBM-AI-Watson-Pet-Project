import board 
import time
import multiprocessing
from gpiozero import Servo

from routines.displays.display_handler import Displays
from routines.audioIO.audioIO_handler import AudioIO
from routines.sensors.sensor_handler import Sensors

from routines.general.pet import initialise_assistant, background_assistant
from routines.general.pet_db import WatsonPet
from routines.general.assistant_pet import assistant 
from routines.pet.helpers.wifi_checker import internet_connected
from routines.pet.helpers.bluetooth_wifi_config import try_wifi_setup

class Pet:
    def __init__(self):
        print("Action: Initialising Hardware")
        i2c = board.I2C()
        #self.servo1 = Servo(24)
        #self.servo2 = Servo(10)
        self.audioIO = AudioIO(i2c)
        self.displays = Displays(i2c)
        self.sensors = Sensors()
        self.background = None
        self.pet = None
        print("Success: Initialised")

        print("Action: Setting Initial State")
        self.displays.static("smile")
        print("Success: Set")
    
    def boot(self):
        print('Action: Checking Internet Connection')
        if (internet_connected() is False):
            print('Fail: Not Connectied - Starting BT Wifi Setup')
            try:
                self.audioIO.play_prerecorded('connect_to_wifi', self.displays)
                try_wifi_setup()
            except:
                raise Exception("Fatal: Error setting up wifi")
        print('Success: Connected')
        self.pet = WatsonPet()
        self.displays.pet = self.pet
        initialise_assistant(self.pet, self.displays, self.speak, self.block_until_sensor_pressed)
    
    def run(self): 
        self.background = multiprocessing.Process(target=background_assistant, args=(self.pet, self.speak, self.listen, self.block_until_sensor_pressed, self.audioIO.yt_player))
        self.background.start()
        while True:
            inputs = self.sensors.check_inputs()
            if inputs is not False:
                state, side = inputs
                if side == "top":
                    print('top touched')
                    self.stop_music_if_playing()
                    self.audioIO.tpa.fixed_gain = 0
                    assistant(self.pet, self.speak, self.listen, self.block_until_sensor_pressed, self.audioIO.yt_player, "hey")
                else:
                    print('side touched')
                    self.displays.static('love')
                    if side == 'left':
                        self.pet.updateEmo(self.pet.getInfo('pet','TOUCH1'))
                        """
                        self.servo1.min()
                        time.sleep(1)
                        self.servo1.mid()
                        time.sleep(0.5)
                        self.servo1.min()
                        time.sleep(0.5)
                        self.servo1.mid()
                        time.sleep(0.5)
                        """
                    if side == 'right':
                        self.pet.updateEmo(self.pet.getInfo('pet','TOUCH2'))
                        """
                        self.servo2.max()
                        time.sleep(1)
                        self.servo2.mid()
                        time.sleep(0.5)
                        self.servo2.max()
                        time.sleep(0.5)
                        self.servo2.mid()
                        time.sleep(0.5)
                        """
                    time.sleep(1)
            else:
                self.displays.static('smile')
                
    
    def stop_music_if_playing(self):
        print('stopping')
        if self.audioIO.yt_player.media_player is not None:
            print(' was playing')
            self.audioIO.yt_player.media_player.stop()
    
    def speak(self, prerecorded=False, text="Hey", loop=False, loop_interval=False):
        self.displays.animate('talk')
        if prerecorded is False:
            self.audioIO.play_dynamic(text, self.displays, loop, loop_interval)
        else:
            self.audioIO.play_prerecorded(text, self.displays, loop, loop_interval)
        self.displays.static('smile')
        
    def listen(self, duration=5):
        self.displays.animate('play') #TODO: Change to think animation
        response = self.audioIO.get_user_response(self.displays, duration)
        self.displays.static("smile")
        return response    
    
    def block_until_sensor_pressed(self):
        while True:
            inputs = self.sensors.check_inputs()
            if inputs is not False:
                state, side = inputs
                return side
