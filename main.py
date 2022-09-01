import board
import time

from routines.pet.pet import Pet
# from routines.pet.helpers.assistant import assistant as watson_assistant

def main():
	pet = Pet()
	pet.boot()
	pet.run()

main()
