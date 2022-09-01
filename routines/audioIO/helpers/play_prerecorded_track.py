import subprocess
import time

def play_prerecorded_track(file_name, loop, loop_interval):
	print("Hellooooo")
	to_play = 'routines/audioIO/prerecorded/' + file_name
	print(to_play)

	if (loop is False):
		print("no loop")
		subprocess.run(['aplay', to_play])
		return
	
	while True:
		print("looping")
		subprocess.run(['aplay', to_play])
		time.sleep(loop_interval)
