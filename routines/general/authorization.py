import sys
import requests
import json
import time 
import pickle
import os
import datetime
import tweepy
from requests_oauthlib import OAuth1Session 
from google.oauth2.credentials import Credentials
from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event
from google.auth.transport.requests import Request
import paho.mqtt.client as mqtt

with open('routines/general/credentials.json') as f:
    creds = json.load(f)

# twitter
consumer_key = creds["twitter_key"]
consumer_secret = creds["twitter_secret"]

# google
client_id = creds["google_client_id"]
client_secret = creds["google_client_secret"]

# device id
with open('routines/general/petID.json') as f:
    info = json.load(f)
    deviceid = str(info['pet']['id'])

# control status of mqtt
msg_start = ""
msg_pin = ""

# mqtt on_message function
def on_message(client, userdata, message): 
    global msg_start, msg_pin
    if message.topic == "device" + deviceid + "/start" :
        msg_start = message.payload.decode()
    elif message.topic == "device" + deviceid + "/pin" :
        msg_pin = message.payload.decode()

############################
###Twitter Authorization ###
############################

# Request an OAuth Request Token. First step of the 3-legged OAuth flow.
def request_token():
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri='oob')

    url = "https://api.twitter.com/oauth/request_token"

    try:
        response = oauth.fetch_request_token(url)
        resource_owner_oauth_token = response.get('oauth_token')
        resource_owner_oauth_token_secret = response.get('oauth_token_secret')
    except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(120)
    
    return resource_owner_oauth_token, resource_owner_oauth_token_secret

# Exchange the OAuth Request Token obtained previously for the user’s Access Tokens.
def get_user_access_tokens(resource_owner_oauth_token, resource_owner_oauth_token_secret, authorization_pin):
    success = 0
    oauth = OAuth1Session(consumer_key, 
                            client_secret=consumer_secret, 
                            resource_owner_key=resource_owner_oauth_token, 
                            resource_owner_secret=resource_owner_oauth_token_secret, 
                            verifier=authorization_pin)
    
    url = "https://api.twitter.com/oauth/access_token"

    try: 
        response = oauth.fetch_access_token(url)
        access_token = response['oauth_token']
        access_token_secret = response['oauth_token_secret']
        user_id = response['user_id']
        screen_name = response['screen_name']
        success = 1
    except:
            success = 0
            return "","","","",success
            

    return(access_token, access_token_secret, user_id, screen_name, success)


# Twitter authorization process
def authorize_twitter(speak):
    global msg_start, msg_pin
    msg_start = ""
    msg_pin = ""

    # create mqtt client
    client = mqtt.Client() 
    client.tls_set() 
    client.username_pw_set(username="raspberrypi", password="Rasp49424D") 
    
    # connect to mqtt broker, initialization
    try:
        connected = client.connect("d851a8d133194cb9b8218e5189aee38c.s1.eu.hivemq.cloud",port=8883)
        #print(connected)
        while(connected):
            client.connect("d851a8d133194cb9b8218e5189aee38c.s1.eu.hivemq.cloud",port=8883)
            print("reconnecting")
        topic = [("device" + deviceid + "/start",0), ("device" + deviceid + "/pin",0)]
        client.subscribe(topic)
        client.on_message = on_message
    except:
        pass
    
    #generate authorization url
    resource_owner_oauth_token, resource_owner_oauth_token_secret = request_token()
    authorization_url = f"https://api.twitter.com/oauth/authorize?oauth_token={resource_owner_oauth_token}"

    print('Pet: Please input the device id and press enter button.')
    speak(True, "authorize_enter_device_id")
    
    api = ""
    success = 0
    while(True):
        client.loop()

        # when message "hello" received from user, guide user to complete the authorization process
        if msg_start == "hello":
            topic1 = "device" + deviceid + "/account"            
            topic2 = "device" + deviceid + "/url"
            
            client.publish(topic1, "twitter")
            client.publish(topic2, authorization_url)  
            msg_start =""
            print('Pet: Please press the get button, then follow the instruction below.')
            speak(True,"authorize_press_get" )

        # when pin is received
        if msg_pin != "" :
            authorization_pin = msg_pin
            access_token, access_token_secret, user_id, screen_name, success = get_user_access_tokens(resource_owner_oauth_token, resource_owner_oauth_token_secret, authorization_pin)
            
            if success == 0 : # when fail to get the access token
                msg_pin = ""
                resource_owner_oauth_token, resource_owner_oauth_token_secret = request_token()
                authorization_url = f"https://api.twitter.com/oauth/authorize?oauth_token={resource_owner_oauth_token}"
                client.publish(topic, authorization_url)  
                print('Pet: Something wrong happens. Please press get button again to get a new url, and enter the pin again.') 
                speak(True, "authorize_error_try_again")
                continue
            else :  # otherwise, create instance of Twitter API
                with open('routines/general/twitter_auth.json', 'w') as fp:
                    twitter_auth = {"consumer_key":consumer_key, "comsumer_secret":consumer_secret,"user_id":user_id, "access_token":access_token, "access_token_secret":access_token_secret}
                    json.dump(twitter_auth, fp,  indent=4)              
                auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret,access_token, access_token_secret)
                # calling the api
                api = tweepy.API(auth)        
                client.disconnect()
                print('Pet: Successfully authorize account:', screen_name)
                break

    return api


###########################
###Spotify Authorization###
###########################

# Spotify authorization process
def authorize_spotify(authorization_url, speak):
    global msg_start, msg_pin
    msg_start = ""
    msg_pin = ""

    # create mqtt client
    client = mqtt.Client() 
    client.tls_set() 
    client.username_pw_set(username="raspberrypi", password="Rasp49424D") 
    authorization_token = ""

    # connect to mqtt broker, initialization
    try:
        connected = client.connect("d851a8d133194cb9b8218e5189aee38c.s1.eu.hivemq.cloud",port=8883)
        print(connected)
        while(connected):
            client.connect("d851a8d133194cb9b8218e5189aee38c.s1.eu.hivemq.cloud",port=8883)
            print("reconnecting")
        topic = [("device" + deviceid + "/start",0), ("device" + deviceid + "/pin",0)]
        client.subscribe(topic)
        client.on_message = on_message
    except:
        pass

    print('Pet: Please input the device id and press enter button.') 
    speak(True, "authorize_enter_device_id")

    while(True):
        client.loop()
        # when message "hello" received from user, guide user to complete the authorization process
        if msg_start == "hello": 
            topic1 = "device" + deviceid + "/account"            
            topic2 = "device" + deviceid + "/url"

            client.publish(topic1, "spotify")
            client.publish(topic2, authorization_url)  
            print("received from device/start : " + msg_start)  
            msg_start = ""
            print('Pet: Please press the get button, then follow the instruction below.')
            speak(True,"authorize_press_get")

        if msg_pin != "" :
                authorization_token = msg_pin
                client.disconnect()
                break

    return authorization_token


###########################
###Google Authorization###
###########################

# get google access token
def getGoogleToken(device_code):
    while(True):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {'client_id' :client_id, 
                'client_secret' : client_secret,
                'device_code' : device_code,
                'grant_type' : 'urn:ietf:params:oauth:grant-type:device_code',
        }

        response = requests.post('https://oauth2.googleapis.com/token', headers=headers, data=data)

        authorize_msg = (response._content).decode("utf-8")
        authorize_msg_dict = json.loads(authorize_msg)
        if 'access_token' in authorize_msg_dict:
            token = Credentials(
                    token=authorize_msg_dict['access_token'],
                    refresh_token=authorize_msg_dict['refresh_token'],
                    client_id=client_id,
                    client_secret=client_secret,
                    scopes=[authorize_msg_dict['scope']],
                    token_uri="https://oauth2.googleapis.com/token"
            )
            with open('routines/general/google_token.pickle', 'wb') as token_file: # TODO remember to change it back
                    pickle.dump(token, token_file)
            
            return True                    

        time.sleep(5)


def checkToken(path = 'routines/general/google_token.pickle'):
    # check if the google auth token is still valid
    # check whether credentials exists
    if os.path.exists(path):
        # if token exists load it 
        with open(path, 'rb') as token_file:
            token = pickle.load(token_file)

        if not token.valid and token.expired and token.refresh_token:
            try:
                token.refresh(Request())
                with open('routines/general/google_token.pickle', 'wb') as token_file:
                    pickle.dump(token, token_file)
                return token
            except:
                print('refresh token revolk')
                # if refresh failure (refresh token revolk or smth)
                return False
        else:
            return token
    else:
        # cannot find the file so need auth
        return False

# Google calendar authorization process - 2-legged Oauth
def authorize_google(speak):
    global msg_start
    msg_start = ""

    #ask for request token
    data = {
        'client_id': '157524462645-g3lt8g1e1htmob6al3k0i1k46f2ktkrk.apps.googleusercontent.com',
        'scope': ['https://www.googleapis.com/auth/calendar'],
    }

    response = requests.post('https://oauth2.googleapis.com/device/code', data=data)
    request_msg = (response._content).decode("utf-8")

    request_msg_dict = json.loads(request_msg)
    device_code = request_msg_dict['device_code']
    user_code = request_msg_dict['user_code']
    verification_url = request_msg_dict['verification_url']
    print(user_code)
    print(verification_url)

    #create mqtt client
    client = mqtt.Client() 
    client.tls_set() 
    client.username_pw_set(username="raspberrypi", password="Rasp49424D") 

    # connect to mqtt broker, initialization
    try:
        connected = client.connect("d851a8d133194cb9b8218e5189aee38c.s1.eu.hivemq.cloud",port=8883)
        while(connected):
            client.connect("d851a8d133194cb9b8218e5189aee38c.s1.eu.hivemq.cloud",port=8883)
            print("reconnecting")
        topic = [("device" + deviceid + "/start",0), ("device" + deviceid + "/pin",0)]
        client.subscribe(topic)
        client.on_message = on_message
    except:
        pass    

    print('Pet: Please input the device id and press enter button.')
    speak(True, "authorize_enter_device_id")


    while(True):
        client.loop()
        # when message "hello" received from user, guide user to complete the authorization process
        if msg_start == "hello":
            topic1 = "device" + deviceid + "/account"            
            topic2 = "device" + deviceid + "/url"

            client.publish(topic1,"google")  
            client.publish(topic2,user_code)

            msg_start = ""
            print('Pet:  Please press the get button, then follow the instruction below.')
            speak(True, "authorize_press_get")
            getGoogleToken(device_code)

            client.disconnect()
            break


if __name__ == '__main__': 
    token = checkToken()
    if token == False:
        authorize_google()
    gc = GoogleCalendar(credentials=token)
    event = Event("event", start = datetime.datetime(2022,6,25,23,0,0))
    gc.add_event(event)
    local_tz = datetime.datetime.now().astimezone().tzinfo
    events = gc.get_events(time_min = datetime.datetime.now(tz=local_tz))
    for i in events:
        print(i.summary)
