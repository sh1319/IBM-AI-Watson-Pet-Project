import subprocess
import time

def play_dynamic_track(loop, loop_interval):
	print("Hellooooo")
	to_play = 'routines/audioIO/helpers/to_play.wav'
	print(to_play)

	if (loop is False):
		print("no loop")
		subprocess.run(['aplay', to_play])
		return
	
	while True:
		print("looping")
		subprocess.run(['aplay', to_play])
		time.sleep(loop_interval)
