# ICL-IBM-AI-Watson-Pet
 The AI Watson pet is an AI ornament with the characteristics of a pet, designed to target the impact of social isolation for the elderly. The pet will interact with its owner, and perform various actions depending on what the owner wants it to do. This will give the owners the mental health benefits of having a pet, without the responsibility and expenses of actually caring for one. The aim of the project is to create a smart pet with AI technology to interact with its owner successfully.

## Video Link:
https://drive.google.com/drive/folders/1X8JHZ7TH7rixMnBctJGE3ZhGvCP7YAib?usp=sharing

## Audio MP3 Link:
https://drive.google.com/drive/folders/1X8JHZ7TH7rixMnBctJGE3ZhGvCP7YAib?usp=sharing

## Trello Project Board Link:
https://trello.com/invite/b/4JAl3sjE/0ff0876919062a6ea0753fef662f85e3/ai-watson-pet

## Hardware Part Info

This repo contains all the code required to run your own Watson AI Pet!

Folders 'CAD/Model1' and 'CAD/Model2' contain the CAD files required to 3D print your own pet!
The "App" folder contains the code for the mobile app as described in the software part.

The external components should then be wired up to the correct ports as seen in the circuit diagram in the main report.
Required Components:
1. 4 x Adafruit Bicolor LED Square Pixel Matrix with I2C Backpack
2. 3 x Adafruit Momentary Capactive Touch Sensor
3. 2 x Servo Motors
4. 1 x Adafruit Stereo 2.8W Class D Audio Amplifier
5. 1 x Adafruit I2S MEMS Microphone Breakout Board

Correct wiring, at least for I2S devices, can be checked using the command:
> sudo i2cdetect -y 1

This will reveal the I2S devices that the RPi can see and communicate with. If wired correctly, there should be devices at 0x70, 0x71, 0x72, 0x73 and 0x58. (You will need to solder the pins on the back of the LED matricies to change their address, or else they will all try to be address 0x70). If the program takes a while to load or doesn't show all of these devices, check your SDA and SCL connections.

A Raspberry Pi Model 3B was used for this project with the following specs:
Required Specs:
1. Quad Core 1.2GHz Broadcom BCM2837 64bit CPU
2. 1GB RAM
3. BCM43438 wireless LAN and Bluetooth Low Energy (BLE) on board
4. 40-pin extended GPIO

Useful for debugging:
1. Full size HDMI
2. 4 USB 2 ports

To run the pet, be sure to install the required packages using:

> sudo pip3 install <package_name>

Required packages include those in routines/general/requirements.txt and the following:
1. adafruit-circuitpython-ht16k33
2. python3-pil
3. adafruit_tpa2016
4. gpiozero
5. digitalio

Then, you should be able to run the main program (ideally at startup) with:

> sudo python3 main.py

The program requires sudo access as the BlueTooth Wifi module requires this to change the wifi settings and reboot the system. (This is why the packages must also be installed with sudo).

### Sub-Modules
Pet sub-modules can be found in 'routines/' as well as 'handlers' for each sub-module that are responsible for the functionality and proper-operation of that sub-module.

- routines/audioIO controls the speaker and microphone with functions to handle both pre-recorded and dynamic playback (using Text-To-Speech), as well as getting a user response (using speech to text).

- routines/displays controls all of the LEDs using a bunch of predefined scripts and 8x8 images to fill them up. It supports both static images and animations (for things such as speaking or thinking)

- routines/general contains all the code from the software side of the project and is the real brains behind the assistant.

- routines/motors contains the code to drive the motors. This should happen when the pet is touched or bored and seeking attention.

- routines/pet contains the Pet object that contains and controls all other classes listed here. It has control of everything (can start or terminate any other process) and it used to synchronise everything. As such, it has defined some higher level functions such as speak() and listen() which controls the speakers and starts the thinking animation on the displays for example. It also handles the logic of what to do when it is touch and when to launch the assistant.

- routines/sensors contains the code to read from the GPIO touch tensors on the top and the side and contains a function which returns which side has been pressed.

When the main program is run as above, the routines/pet class is instantiated and from there everything else is created, checked and controlled. The main process to run this class is then blocked in a while True loop so that the program nevver terminates and the assistant will always be available once it has finished a request.

## Software Part Info
The software sessions codes are mostly within routines/general folder. There is an extra Readme file in that folder explaining those functions.
### Setting up 
The following set up are required for Watson AI Pet project. These are required for using the APIs. 

#### Spotify
1. Go to https://developer.spotify.com/dashboard/login and login to the developer dashboard. (This requries a spotify account)
2. Create an APP or use a exising one if you wish. 
3. Go to 'Edit Settings' and set the redirect url (normally set: https://localhost/)
4. Edit 'USER AND ACCESS' to add your spotify account to it as well as other people's account
5. Copy the client id and client secret and paste them into the routines/general/credentials.json file 

#### Youtube and Google Calendar
1. Follow instructions on https://developers.google.com/workspace/guides/create-project and create a google cloud project
2. On the left top corner select Navigation Menu and navigate to 'API and Services' followed by 'Library'
3. Search for youtube and enable 'Youtube Data API v3'. Search for calendar and enable 'Google Calendar API'  
4. Click credentials and select API key and copy that to routines/general/credentials.json in google_developerkey
5. Click credentials and select OAuth Client ID and select TV and limited Input Device and click create
6. Select the TV and limited Input Device and download credentials
7. Copy the cliend id and cliend secret in the downloaded json file and past them into routines/general/credentials.json


#### Mongodb Atlas
1. Go to https://account.mongodb.com/account/login and create a Mongodb Atlas account 
2. Create a new Cluster
3. Click Connect and select Connect with your application
4. Set the driver to Python and version to 3.4 or later.
5. Follow the instructions on page and copy the url below into routines/general/credentials.json


#### IBM
1. You need to have an IBM cloud account for this proejct.(For our project, Trail account is used.)
2. Go to IBM cloud dashboard and search for 'assistnat', 'natural language understanding','speech to text' and 'text to speech' services.
3. Create all services and set with same location and select the plan you desire, the lite plan should work.

##### For IBM assistant 
1. Open the assistant service, on the top right,click the user haed and switch to classic experience.
2. Copy the API key and URL below to routines/general/credentials.json
3. Click 'Launch' and create assistant
4. Click 'Add dialog skill' and choose 'Upload Skill'
5. Upload the file assistant.json
6. Go back to the page with Assistants, select the 3 dots on the right of the assistant just created and go to settings
7. Copy the assistant_id to routines/general/credentials.json

##### For IBM natural language understanding, speech to text and text to speech services
1. Open the natural language understanding service, copy the API and URL below to corresponding positions in routines/general/credentials.json 
