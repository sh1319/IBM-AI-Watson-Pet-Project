from email.mime import audio
import time
import json
import os
import random
import datetime
from beautiful_date import days,hours,minutes
from gcsa.google_calendar import GoogleCalendar

from routines.general.authorization import authorize_twitter,checkToken,authorize_google
from routines.general.assistant_pet import assistant 
from routines.general.spotipy_rasp_player import spotify_player


### helper function 
def get_next(events):
    try:
        return next(events)
    except StopIteration:
        return None

### Connect to Wifi via Bluetooth

def initialise_assistant(pet, displays, speak, block_until_sensor_pressed):
    print("Action: Checking Connection To Calendar")
    if pet.getInfo(table='user',column='CALENDAR') == 0:
        # db data indicate not connected 
        print("Fail: Not Connected - Prompt To Connect")
        #audioIO.play_prerecorded('prompt_calendar_conn')
        speak(True, "prompt_calendar_conn")
        displays.static('option')
        side = block_until_sensor_pressed()
        if side == "left":
            print("Success: Calendar Connection Skipped")
        elif side == "right":
            if os.path.exists('routines/general/google_token.pickle') == True:
                os.remove('routines/general/google_token.pickle')
            token = checkToken()
            if token == False:
                authorize_google(speak)
            #audioIO.play_prerecorded('calendar_conn_success')
            speak(True, "calendar_conn_success")
            pet.updateInfo(column='CALENDAR',value=1)
            print("Success: Calendar Connection Established")

    else:
        # indicated connect, yet check whether token is valid
        token = checkToken()
        if token == False:
            speak(True,"not_connect_to_google")
            displays.static('option')
            side = block_until_sensor_pressed()
            if side == "left":
                print("Success: Calendar Connection Skipped")
                pet.updateInfo('CALENDAR',0)
            elif side == 'right':
                authorize_google(speak)
                speak(True, "calendar_conn_success")
                print("Success: Calendar Connection Established")

    
    print("Action: Checking Connection To Twitter")
    if pet.getInfo(table='user',column='TWITTER') == 0:
        print("Fail: Not Connected - Prompt To Connect")
        #audioIO.play_prerecorded('prompt_twitter_conn')
        speak(True,"prompt_twitter_conn")
        displays.static('option')
        side = block_until_sensor_pressed()
        if side == "left":
            print("Success: Twitter Account Skipped")
        elif side == "right":
            api = authorize_twitter(speak)
            #audioIO.play_prerecorded('twitter_conn_success')
            speak(True, "twitter_conn_success")
            pet.updateInfo(column='TWITTER',value=1)
            print("Success: Twitter Account Established")
    else:
        print("Success: Connected")
        
    print("Action: Checking Connection to Spotify")
    if pet.getInfo(table='user',column='SPOTIFY') == 0:
        print("Fail: Not Connected - Prompt To Connect")
        #audioIO.play_prerecorded('prompt_spotify_conn')
        speak(True, "prompt_spotify_conn")
        displays.static('option')
        side = block_until_sensor_pressed()
        if side == "left":
            print("Success: Spotify Connection Skipped")
        elif side == "right":
            print('right')
            if os.path.exists('routines/general/.cache-Watson'):
                os.remove('routines/general/.cache-Watson') # delete preset token cuz that should be wrong 
            temp = spotify_player(speak)
            pet.updateInfo(column='SPOTIFY',value=1) # Do not need to know if premium or not
            print("Success: Spotify Account Connected")  

    else:
        temp = spotify_player(speak) # try running it in case something went wrong ? should not require it tho
        print("Success: Connected")
    displays.static('smile')
        
def background_assistant(pet, speak, listen, block_until_sensor_pressed, yt_player):
    ########################
    ### global variables ###
    ########################
    local_tz = datetime.datetime.now().astimezone().tzinfo
    d = datetime.date.today()
    record_day = datetime.datetime(d.year,d.month,d.day,tzinfo=local_tz)
    pet.last_active_time = datetime.datetime.now(tz=local_tz)

    # global var for alarming events
    events = None
    cur_event = None 
    alarm = 0 # if all the events have been alarmed 

    while(True):
        
        ######################
        ### GET THE TIME NOW 
        #####################
        d = datetime.date.today()
        day = datetime.datetime(d.year,d.month,d.day,tzinfo=local_tz)
        ## calculate working hours 
        w = pet.getWorkingHours()
        sw = day + w[0]*hours + w[1]*minutes
        ew = day + w[2]*hours + w[3]*minutes

        ############################
        # if inactive for 1h and is within working time 
        # ask to do smth
        ############################
        time_now = datetime.datetime.now(tz=local_tz)
        if time_now >= sw and time_now <= ew:
            # if the time now is within the working hour seek attention, otherwise do nothing
            time_dif = time_now - pet.last_active_time
            if time_dif.total_seconds() >= 3600: # could modify inactive time now
                r = random.uniform(0,1)
                if r <= 0.9:
                    r = random.uniform(0,1)
                    if r <= 0.5:
                        assistant(pet, speak, listen, block_until_sensor_pressed,yt_player,instr='feel')
                    else:
                        speak(True, "petme")

                else:
                    r = random.uniform(0,1)
                    if r <= pet.getInfo('user','RATIO'):
                        assistant(pet, speak, listen, block_until_sensor_pressed, yt_player,instr='sing')
                    else:
                        assistant(pet, speak, listen, block_until_sensor_pressed, yt_player,instr='podcast')
                
                # record this time as last_active time 
                time_now = datetime.datetime.now(tz=local_tz)
                pet.last_active_time = time_now
        
        ############################
        # emo decrease 
        # decrease 0.5 every 2h
        ############################
        time_now = datetime.datetime.now(tz=local_tz)
        time_dif = time_now - pet.last_active_time
        if time_dif.total_seconds() >= 2*(60*60):
            value = -1*round(0.5*time_dif.total_seconds()/(2*60*60),2)
            pet.updateEmo(value)
            pet.last_active_time = datetime.datetime.now(tz=local_tz)

        
        ###########
        ## ALARM ##
        ###########
        time_now = datetime.datetime.now(tz=local_tz)
        if cur_event is None:
            # if no cur_event, then alarm = 1 (all events reported)
            alarm = 1
        if alarm == 0:
            # if there is cur_event and alarm is 0 (not all events reported)
            startT = cur_event.start 
            time_now = datetime.datetime.now(tz=local_tz)
            if time_now >= startT:
                # if starttime is passed, ignore it and go to next event
                cur_event = get_next(events)
            elif startT > time_now and (startT-time_now).total_seconds() <= 1800:
                # if it is within 30minutes before the event start alarm it 
                speak(False,"Event_upcoming:" + cur_event.summary + " starts at " + cur_event.start.strftime("%I:%M %p, %d %B %Y") + " and ends at " + cur_event.end.strftime("%I:%M %p, %d %B %Y") )
                cur_event = get_next(events)
       
        
        #########################################################
        # load calendar if there is no cur_event and alarm == 0 #          
        #########################################################
        if pet.getInfo(table='user',column='CALENDAR') != 0 and cur_event is None and alarm==0:
            print('load calendar for alarm')
            token = checkToken()
            if token == False:
                authorize_google(speak)
                token = checkToken()
            calendar = GoogleCalendar(credentials=token) 
            print(day)
            time_now = datetime.datetime.now(tz=local_tz)
            events = calendar.get_events(time_min = time_now, time_max = day+1*days, single_events= True, order_by='startTime')
            cur_event = get_next(events)
            print(cur_event)
            if cur_event is None:
                alarm = 1


        ########################
        ### if the next day ####
        ########################
        if day != record_day:
            pet.updateInfo('REPORT_EVENT',0)
            pet.updateRatio()
            alarm = 0
            record_day = day

        
            

        
        
        
# def prompt_assistant(pet, speak, listen, block_until_sensor_pressed):
#     instr = listen()
#     if instr != '':
#         if pet.getInfo('user','REPORT_EVENT') == 0:
#             assistant(pet,speak, listen, block_until_sensor_pressed, 'calendar')
#             pet.updateInfo('REPORT_EVENT',1)
#         ### if emotion is below 2.5, ask for petting until emotion is above
#         if pet.getInfo('pet','EMO') <= 2.5:
#             #audioIO.play_dynamic('seek_attention')
#             speak(False, "Hello, is there anyone here, can you pet me?")
#             # TODO petting 
        
#         assistant(pet, speak, listen, block_until_sensor_pressed, instr)
        
        
#         local_tz = datetime.datetime.now().astimezone().tzinfo
#         pet.last_active_time = datetime.datetime.now(tz=local_tz)
        
