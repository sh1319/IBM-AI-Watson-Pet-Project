from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from gcsa.google_calendar import GoogleCalendar
from newscatcherapi import NewsCatcherApiClient


import random
import string
import json
import datetime
import os
import spotipy
from beautiful_date import days

from routines.general.nlu_pet import extractKeyword,emo
from routines.general.calendar_pet import * 
from routines.general.twitter_func import * 
from routines.general.spotipy_rasp_player import spotify_player as spotipy_player
from routines.general.authorization import authorize_twitter,authorize_google,checkToken
from routines.general.youtube_streamer import vlc_media_player

YOUTUBE_API_VERSION = 'v3'
YOUTUBE = 'youtube'

def assistant(pet, speak, listen, block_until_sensor_pressed, yt_player, instr="hey"):

    #########################
    # Setting Up
    #########################
    # IBM Assistant
    # load credentials.json
    with open('routines/general/credentials.json') as f:
        creds = json.load(f)

    authenticator = IAMAuthenticator(creds["ibm_assistant_api"])
    assistant = AssistantV2(version='2022-05-01',authenticator=authenticator)
    assistant.set_service_url(creds["ibm_assistant_url"])
    
    
    spotify_player = None
    #yt_player = None
    calendar = None
    twitter_api = None
    
    if pet.getInfo('user','AUDIO_PLAYING')==1:
        spotify_player = spotipy_player(speak)
        if spotify_player.setDevice() == True:
            spotify_player.pause()
    

    # NewsCatcherAPI
    newscatcherapi = NewsCatcherApiClient(x_api_key=creds["newscatcher_api"])

    #########################
    # Create Sessions
    #########################
    session = assistant.create_session(creds["ibm_assistant_id"]).get_result()

    #########################
    # Message
    #########################
    # first cycle the input is instr 
    # => hey / sing / feel / podcast / calendar
    #  instr='hey': User touch top sensor and want to ask the Pet to do something
    #  instr="feel" : Watson Pet would ask for users' feeling and how their day was. 
    #  instr="podcast": Watson Pet would ask if user would like to listen to some podcast
    #  instr="sing" : Watson Pet would ask if the user would like to listen to some music
    #  instr="calendar" : Watson Pet would ask if the user want to list and report all of today's schedules 
    status = ''

    # Global variables for feeling 
    mode = 0 # either 1 or 2 
    choice = 0 # 1 for playing music, 2 for playing podcast
    genre = '' # the genre of music to search depending on feelings 
    keyword = '' # the keyword extracted from user speech

    ########
    # Pass messages to watson assistant
    ########
    message = assistant.message(
            creds["ibm_assistant_id"],
            session['session_id'],
            input={'text': instr},
            ).get_result()

    output = message["output"]["generic"][0]["text"].split("#")
    # FORMAT of output: 1. reply message .... 
    #                   2. reply message .... #status
    #                   3. reply message .... #status#param
    response = output[0]
    print("pet:"+response)
    if '=' in response:
        # it is a prerecorded audio file name
        file_name = response[:-1]
        speak(True,file_name)
    elif response != '':
        # this is not prerecorded and need to process via text to speech
        speak(False, response)

    if len(output) >= 2:
        status = output[1]
    else:
        status = ""
    
    print(status)
    if instr == 'feel':
        status = 'A'
        reply = ''

    ############################# 
    # while loop until detect end (status = 'D')
    ##############################
    while(status!='D'):
        if status == 'E':
            # Add event(check if clashes)
            startT,endT,event = convertT(output[2])
            speech_text = checkClash(calendar,startT,endT, speak)
            if speech_text == 'unclash':
                try:
                    calendar.add_event(event)
                except:
                    speech_text = 'error'
        elif status == 'H1':
            # Delete Event(part one) 
            if len(output)==3:
                startT,endT,query = convertT4(output[2])
                # obtain events that satisfied the requirement 
                events = calendar.get_events(time_min=startT,time_max=endT, query=query)
                count = 0
                memo = []
                say = 'Here is the following: \n'
                for event in events:
                    count += 1
                    say += str(count) + '. ' + event.summary + " starts at " + event.start.strftime("%I:%M %p, %d %B") + ".\n"
                    memo.append(event.id)
                print(count)
                if count == 0:
                    say = 'I cannot find any event that matches.'
                else:
                    say = 'I found ' + str(count) + ' events. \n' + say
                print('Pet:' + say) 
                speak(False, say) 
                speech_text = str(count) 
                status = ''
        elif status == 'A':
            ##################
            # Analysis emotion  
            ##################
            response = listen() 
            reply += response 
            
            # if not match length required, ask users to talk a bit more
            while(len(reply) <= 15):
                print('pet: can you talk a bit more?')
                speak(True, "emotion_talk_a_bit_more")
                response = listen()  
                reply += response 
            feeling = emo(reply)
            ###############
            # Extract keyword
            ###############
            output = extractKeyword(reply,news=False)
            if output != '':
                keywords_list = output.split(',')
                keyword = keywords_list[random.randint(0,len(keywords_list)-1)]
            if feeling != '':
                # when emotion can be identified, play some music to confort user
                if feeling == 'sad':
                    genre = 'happy'
                elif feeling == 'frustrated':
                    genre = 'chill'
                elif feeling == 'excited':
                    genre = 'party'
                else:
                    print(feeling)
            mode = random.randint(1,2)

            if keyword == '':
                # no keyword identified and can only play music but not podcast on keyword
                print('Pet: do you want some music to chill you up?')
                speak(True, "emotion_play_music_to_chill")
                choice = 1 
            else:
                # keyword identified hence could randomly select one
                choice = random.randint(1,2) 
                # choice = 1, music, choice = 2 podcast
                if choice == 1:
                    print('Pet: do you want some music to chill you up?')
                    speak(True, "emotion_play_music_to_chill")
                else:
                    msg = 'do you want some podcast about ' + keyword
                    speak(False, msg) 

            
            speech_text = listen()

            status = ''
        elif status == 'T1' :
            # Twitter
            message, userid, res = getDirectMessage(twitter_api, 5)
            print(message) 
            speak(False, message)
            if res == True :
                speech_text = 'havemessage'
            else :
                speech_text = 'nomessage'    
            status = '' 
        else:
            speech_text = listen() 

        # pass message to assistant ------------------------- #
        message = assistant.message(
            creds["ibm_assistant_id"],
            session['session_id'],
            input={'text': speech_text},
            ).get_result()

        for i in range(len(message["output"]["generic"])):
            output = message["output"]["generic"][i]["text"].split("#")
            response = output[0]
            # FORMAT of output: 1. reply message .... 
            #                   2. reply message .... #status
            #                   3. reply message .... #status#param
            if "=" in response:
                file_name = response[:-1]
                speak(True,file_name)
            elif response != '':
                speak(False, response)
            if len(output) >= 2: 
                status = output[1]
            print("pet:"+response)
            print(status)

            #########################
            ### check auth status ###
            #########################
            
            if status != '':
                if status[0] == 'T' and twitter_api== None:
                    # requires twitter
                    if pet.getInfo('user','TWITTER') == 0:
                        print('Pet: Detected that you are not linked to twitter account. Do you want to link now?')
                        speak(True, "not_connect_to_twitter")
                        side = block_until_sensor_pressed()
                        if side == "left":
                            print("Success: Twitter Account Skipped")
                            status = 'D'
                        elif side == "right":
                            twitter_api = authorize_twitter(speak)
                            speak(True,"twitter_conn_success")
                            pet.updateInfo(column='TWITTER',value=1)
                            print("Success: Twitter Account Established")                        
                    
                    else:
                        twitter_api = authorize()

                elif status in {'H1','H2','E','C','F','G'} and calendar == None: 
                    # requires calendar 
                    if pet.getInfo('user','CALENDAR') == 0:
                        print('Pet: Detected that you are not linked to google calendar. Do you want to link now?')
                        speak(True, "not_connect_to_google")
                        side = block_until_sensor_pressed()
                        if side == "left":
                            print("Success: Calendar Connection Skipped")
                            status = 'D'
                        elif side == "right":
                            token = checkToken()
                            if token == False:
                                authorize_google(speak)
                                token = checkToken()
                            calendar = GoogleCalendar(credentials=token)
                            speak(True,"calendar_conn_success" )
                            pet.updateInfo(column='CALENDAR',value=1)
                            print("Success: Calendar Connection Established")                     

                    else:
                        token = checkToken()
                        if token == False:
                            print('Your token has expired, do you want to authorize it now? If so, tickle my right arm.')
                            speak(True, "calendar_token_expire")
                            authorize_google(speak)
                            side = block_until_sensor_pressed()
                            if side == "left":
                                print("Success: Calendar Connection Skipped")
                                pet.updateInfo('CALENDAR',0)
                                break
                            elif side == "right":
                                authorize_google(speak)
                                token = checkToken()
                                calendar = GoogleCalendar(credentials=token)
                                speak(True, "calendar_conn_success")
                                print("Success: Calendar Connection Established")
                                break
                        else:   
                            calendar = GoogleCalendar(credentials=token)
                
                elif status in {'P','S','R'}:
                    if spotify_player == None:
                        # require spotify
                        if pet.getInfo('user','SPOTIFY') == 0:
                            print('Pet:Detected that you are not connected to spotify account, do you want to link now? Otherwise I will use youtube instead.')
                            speak(True, "not_connect_to_spotify")
                            side = block_until_sensor_pressed()
                            if side == "left":
                                print("Success: Spotify Connection Skipped")
                                break
                            elif side == "right":
                                print('right')
                                if os.path.exists('routines/general/.cache-Watson'):
                                    os.remove('routines/general/.cache-Watson') # delete preset token cuz that should be wrong 
                                spotify_player = spotify_player(speak)
                                pet.updateInfo(column='SPOTIFY',value=1) # Do not need to know if premium or not
                                print("Success: Spotify Account Connected")
                                break
                        else:
                            spotify_player = spotipy_player(speak)

            if len(status) > 1:
                if status == 'H2':
                    # Delete event step2
                    if len(output)==3:
                        list = json.loads(output[2])
                        for i in list:
                            index = int(i)-1
                            calendar.delete_event(memo[index])
                    print("Pet: I have successfully delete it from your calendar!")
                    speak(True, "calendar_delete_event")
                    status = ""
                
                if status[0] == 'T':
                    # twitter : get direct message - decide to reply
                    if status[1] == '2':
                        reply = status.split(':')
                        res = sendDirectMessage(twitter_api, reply[1], userid = userid)
                        if res == 1 :
                            print("Message " + reply[1] + " successfully replied!") 
                            response = "Message " + reply[1] + " successfully replied!"
                            speak(False,response)
                        status = 'D'
                    # twitter : get latest tweet
                    elif status[1] == '3': 
                        username = status.split(':') 
                        content, twitterid = getLatestTweet(twitter_api) 
                        print(content)
                        speak(False, content)
                        status = ''
                    # twitter : get latest tweet - decide to reply
                    elif status[1] == '4':
                        text = status.split(':')
                        content, success = replyTweet(twitter_api,text[1], twitterid)
                        print(content) 
                        if success == True:
                            speak(True, "twitter_tweet_reply_success")
                        else:
                            speak(True, "twitter_tweet_reply_failure")
                        status = 'D'
                    # twitter : post tweet
                    elif status[1] == '5':
                        text = status.split(':')
                        content, success = postTweet(twitter_api, text[1])
                        print(content)    
                        if success == True:
                            
                            speak(True, "twitter_post_tweet_success")
                        else:   
                            speak(True, "twitter_post_tweet_failure")                    
                        status = 'D'
                    # twitter : send direct message - match user
                    elif status[1] == '6':
                        val = status.split(':')
                        username = val[1]
                        print("username1 : " + status)
                        content, val = matchUser(twitter_api, username)  
                        print(content) 
                        if val == 0:
                            speak(True, "twitter_user_not_found" )
                            status = 'D'
                        elif val == 1:
                            speak(False, content)
                            status = ''
                    # twitter : send direct message - set message context
                    elif status[1] == '7':
                        text = status.split(':')
                        res = sendDirectMessage(twitter_api,text[1],username = username)  
                        if res == 1 :
                            print("Message " + text[1] + " sent!") 
                            response = "Message " + text[1] + " sent!"
                            speak(False, response)
                        status = 'D'   
            else:
                if status == 'N':
                    # news with particular topic
                    # nlu processing 
                    keyword = extractKeyword(output[2])
                    print(keyword)
                    # find news using keywords
                    search_res = newscatcherapi.get_search(q=keyword,
                                         lang='en',
                                         countries = 'GB',
                                         page_size = 1
                                         )
                    print('Pet: Okay, let me find them .... might take a while') 
                    speak(True, "wait_for_newsfind")
                    output = ''
                    for i,article in enumerate(search_res['articles']):
                        output += str(i+1) + ' ' + article['title'] + '. ' + article['summary'] + '. ' 
                    
                    print('Pet:'+output) 
                    speak(False, output)
                    status='D'

                if status == 'B':
                    # audio book
                    book = output[2]
                    if 'audiobook' not in book and 'audio book' not in book:
                        book += ' audiobook'
                    try:
                        if yt_player.youtube_player(book) is None: 
                            print('Sorry I cannot find it via youtube') 
                            speak(True, "youtube_notfind")
                            
                    except Exception as e:
                        print(str(e))
                        print('Sorry I am not able to play this for you at the moment. Please try again later')
                        speak(True, "audiobook_error")

                    status = 'D'
                if status == 'S':
                    # particular song
                    song = output[2]
                    if spotify_player is not None and spotify_player.checkPremium() == True:
                        print('spotify')

                        if spotify_player.setDevice() == True:
                            try:
                                spotify_player.play(song)
                                pet.updateInfo('AUDIO_PLAYING',1)
                            except:
                                try:
                                    if yt_player.youtube_player(song) is None:
                                        print('Sorry I cannot find it') 
                                        speak(True, "youtube_notfind")
                                except:
                                    print('Some error occur, please try again later') 
                                    speak(True, "error")
                                
                        else:
                            print('Cannot find pet, will play it via youtube') 
                            speak(True, "spotify_cannot_find_device")
                            try:
                                if yt_player.youtube_player(song) is None:
                                    print('Sorry I cannot find it') 
                                    speak(True, "youtube_notfind")
                            except:
                                print('Some error occur, please try again later') 
                                speak(True, "error")
                        
                    else:
                        print('youtube')
                        try:
                            if yt_player.youtube_player(song) is None:
                                print('Sorry I cannot find it') 
                                speak(True, "youtube_notfind")
                        except:
                            print('Some error occur, please try again later') 
                            speak(True, "error")
                    status = 'D'

                    m = pet.getInfo('user','MUSIC') + 1
                    pet.updateInfo('MUSIC',m)

                if status == 'P':
                    # podcast 
                    podcast = output[2]
                    if spotify_player is not None and spotify_player.checkPremium() == True:
                        if spotify_player.setDevice() == True:
                            try:
                                spotify_player.play(podcast)
                                pet.updateInfo('AUDIO_PLAYING',1)
                            except:
                                try:
                                    if yt_player.youtube_player(podcast) is None:
                                        print('Sorry I cannot find it') 
                                        speak(True, "youtube_notfind")

                                except Exception as e:
                                    print(1)
                                    print(e)
                                    print('Some error occur, please try again later')
                                    speak(True, "error")
                                
                        else:
                            print('Cannot find pet, will play it via youtube') 
                            speak(True, "spotify_cannot_find_device")
                            try:
                                if yt_player.youtube_player(podcast) is None:
                                    print('Sorry I cannot find it')
                                    speak(True, "youtube_notfind")
                            except Exception as e:
                                print(2)
                                print(e)
                                print('Some error occur, please try again later')
                                speak(True, "error")
                    else:
                        try:
                            if yt_player.youtube_player(podcast) is None:
                                print('Sorry I cannot find it') 
                                speak(True, "youtube_notfind")
                        except Exception as e:
                            print(3)
                            print(e)
                            print('Some error occur, please try again later') 
                            speak(True, "error")
                    status = 'D' 
                    if podcast != 'global news podcast' and podcast != 'CNN Tonight':
                        p = pet.getInfo('user','PODCAST') + 1
                        pet.updateInfo('PODCAST',p)

                if status == 'R':
                    # random song/podcast 
                    print(genre)
                    print(mode)
                    print(keyword)
                    print(choice)

                    song_name = f'%{random.choice(string.ascii_lowercase)}%'
                    if spotify_player != None:
                        # linked to spotify
                        if choice != 2:
                            # play music 
                            if genre !='':
                                if mode == 1:
                                    song_name = f'%{random.choice(string.ascii_lowercase)}%' + 'AND genre:' + genre
                                    # get spotify recommendations + genre
                                    name = spotify_player.get_recommended(genre)
                                    if name != False:
                                        song_name = name
                            else:
                                if mode == 1:
                                    # get favourite
                                    name = spotify_player.get_top_tracks()
                                    if name != False:
                                        song_name = name
                        else:
                            # play podcast
                            song_name = keyword + ' podcasts'
                    else:
                        # cannot get spotify data so youtube straight away 
                        if choice != 2:
                            if genre != '':
                                song_name = genre + ' songs'
                        else:
                            # play podcast
                            song_name = keyword + ' podcasts'

                    print(song_name)

                    if spotify_player is not None and spotify_player.checkPremium() == True:   
                        if spotify_player.setDevice() == True:
                            if choice != 2:
                                try:
                                    spotify_player.play(song_name)
                                    pet.updateInfo('AUDIO_PLAYING',1)
                                except:
                                    try:
                                        if yt_player.youtube_player(song_name) is None:
                                            speak(True, "youtube_notfind")
                                    except:
                                        print('Some error occur, please try again later')
                                        speak(True, "error")
                            else:
                                # play podcast
                                try:
                                    spotify_player(song_name,type='show')
                                except:
                                    try:
                                        if yt_player.youtube_player(song_name) is None:
                                            speak(True, "youtube_notfind")
                                    except:
                                        print('Some error occur, please try again later') 
                                        speak(True, "error")      
                        else:
                            # cannot find devices use youtube directly
                            print('Cannot find pet') 
                            speak(True, "spotify_cannot_find_device")
                            try:
                                if yt_player.youtube_player(song_name) is None:
                                    speak(True, "youtube_notfind")
                            except:
                                print('Some error occur, please try again later') 
                                speak(True, "error")
                    status = 'D'

                if status == 'E': 
                    # Add event 
                    if len(output) <= 2:
                        status = ""
                    elif len(output) == 3 and output[2]=='1':
                        try:
                            calendar.add_event(event)
                            status = ''
                            print("I have successfuly added the event to your calendar!")   
                            speak(True, "calendar_add_event")
                        except:
                            print("unexpected error")
                            speak(True, "error")
                    
                if status == 'C':
                    # Ask for today's plan
                    local_tz = datetime.datetime.now().astimezone().tzinfo
                    d = datetime.date.today()
                    local_date = datetime.datetime(d.year,d.month,d.day,tzinfo=local_tz)
                    events = calendar.get_events(time_min = local_date, time_max = local_date+1*days, single_events= True, order_by='startTime')

                    count = 0
                    say = "Pet: The following is your plan. \n"
                    for event in events:  
                        count += 1  
                        say += event.summary + " starts at " + event.start.strftime("%I:%M %p, %d %B") + ". \n"
                    
                    if count == 0:
                        print("Pet: You do not have any plan today!")
                        speak(True, "calendar_no_plan_today" )
                    else:
                        print(say)
                        speak(False, say)
                    status = ''

                if status == 'F':
                    # daily/particular day event
                    if len(output) == 3:
                        print(output[2])
                        startT,endT,query = convertT2(output[2])
                        print(startT,endT)
                        events = calendar.get_events(time_min = startT, time_max = endT,query = query, single_events= True, order_by='startTime')
                       
                        count = 0
                        say = ""
                        for event in events:  
                            count += 1  
                            say += str(count) + ". " + event.summary + " starts at " + event.start.strftime("%I:%M %p, %d %B") + ". \n"
                        if count == 0:
                            print("Pet: I cannot find any event that match your requirement") 
                            speak(True,"calendar_cannot_find_event" )
                        else:
                            say_text = 'You have ' + str(count) + 'events today. Here is the following \n' + say
                            print('Pet:' + say_text) 
                           
                            speak(False, say_text)

                        status = 'D'

                if status == 'G':
                    # ask for next one or several plans
                    if len(output) == 3:
                        num,time,q = convertT3(output[2])
                        now = datetime.datetime.now(tz = datetime.datetime.now().astimezone().tzinfo)
                        events = calendar.get_events(time_min = now,time_max = time, query = q,single_events= True, order_by='startTime')

                        count = 0
                        say = ''
                        for event in events:
                            if event.start >= now:
                                count += 1
                                say += str(count) + ". " + event.summary + " starts at " + event.start.strftime("%I:%M %p, %d %B") + ". \n"
                            if count > num:
                                break

                        if count == 0:
                            print("Pet: I cannot find any event that match your requirement") 
                            speak(True, "calendar_cannot_find_event" )
                        elif count < num:
                            say = "There is only "+ str(count) + " events found. Here is the following. \n" + say
                            print('Pet:' + say)
                           
                            speak(False, say)
                        status = 'D'        

    assistant.delete_session(creds["ibm_assistant_id"], session['session_id']).get_result()
