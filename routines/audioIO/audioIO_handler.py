import multiprocessing
import subprocess
import time

import adafruit_tpa2016

from ibm_watson.websocket import AudioSource

from routines.audioIO.helpers.text_to_speech import text_to_speech
from routines.audioIO.helpers.speech_to_text import convert_speech_to_text
from routines.audioIO.helpers.play_prerecorded_track import play_prerecorded_track
from routines.audioIO.helpers.play_dynamic_track import play_dynamic_track

from routines.general.youtube_streamer import vlc_media_player

class AudioIO:
    def __init__(self, i2c):
        self.tpa = adafruit_tpa2016.TPA2016(i2c)
        self.speaker_process = None
        self.mic_process = None
        self.yt_player = vlc_media_player(self.change_gain)

    def change_gain(self, gain):
        self.tpa.fixed_gain = gain

    def wait_to_finish(self):
        print('waiting?')
        self.yt_player.pause()
        if self.speaker_process is not None:
                self.speaker_process.join()
        print('end wait')
    
    def get_user_response(self, displays, duration=5):
        self.wait_to_finish()
        print("Action: Recording")
        displays.animate('scan')
        self.mic_process = subprocess.call(['arecord --device=dmic_sv2 -c2 -r 44100 -f S32_LE -t wav -d 5 -v routines/audioIO/helpers/recorded.wav'], shell=True)
        print("Success: Recorded")
        print("Action: Converting to Text")
        text = convert_speech_to_text()
        print("Heard: " + text)
        displays.static('smile')
        return text

    def play_dynamic(self, text, displays, loop=False, loop_interval=5):
        self.wait_to_finish()
        print("Action: Converting Text To Speech")
        displays.animate('scan')
        text_to_speech(text)
        print("Success: Converted")
        displays.animate('talk')
        self.speaker_process = multiprocessing.Process(target=play_dynamic_track, args=(loop, loop_interval))
        self.speaker_process.start()
        self.speaker_process.join()
        displays.static('smile')
    
    def play_prerecorded(self, message, displays, loop=False, loop_interval=5):
        self.wait_to_finish()
        displays.animate('talk')
        self.speaker_process = multiprocessing.Process(target=play_prerecorded_track, args=(message+'.wav', loop, loop_interval))
        self.speaker_process.start()
        self.speaker_process.join()
        displays.static('smile')

