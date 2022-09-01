from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os


def text_to_speech(text, path ):
    authenticator = IAMAuthenticator('AkbxKAQP2meShCq3W3ulh7olYWvjie0uGnB7zavLbulO')
    text_to_speech = TextToSpeechV1(authenticator=authenticator)
    text_to_speech.set_service_url('https://api.eu-gb.text-to-speech.watson.cloud.ibm.com/instances/d5c208e5-642e-4211-a396-c65243cd706a')

    with open(path, 'wb') as audio_file:
        res = text_to_speech.synthesize(text, accept = 'audio/wav', voice = 'en-GB_JamesV3Voice').get_result()
        audio_file.write(res.content)

'''assistant_pet.py'''
def record_assistant_pet():
    if not os.path.exists('assistant_pet_prerecorded'):
        os.makedirs('assistant_pet_prerecorded')
    #text_to_speech("Would you mind sharing more about your feeling right now?", 'assistant_pet_prerecorded/emotion_talk_a_bit_more.wav')
    #text_to_speech("How about listening to some music to chill you up?", 'assistant_pet_prerecorded/emotion_play_music_to_chill.wav')
    #text_to_speech("Sorry, I have not linked to your Twitter acccount yet, would you like me to link to it now?", 'assistant_pet_prerecorded/not_connect_to_twitter.wav')
    # twitter_conn_success.wav
    #text_to_speech("Sorry, I have not linked to your Google calendar yet, would you like me to link to it now?", 'assistant_pet_prerecorded/not_connect_to_google.wav')
    # calender_conn_success.wav
    #text_to_speech("Sorry, I have not linked to your Spotify account yet, would you like me to link to it now? Otherwise, I will use Youtube instead.", 'assistant_pet_prerecorded/not_connect_to_spotify.wav') #TODO change to touch if agree
    #text_to_speech("I have successfully delete it from your calendar!",'assistant_pet_prerecorded/calendar_delete_event.wav')
    #text_to_speech("Okay, let me find them .... might take a while",'assistant_pet_prerecorded/wait_for_newsfind.wav')
    #text_to_speech("I have successfuly added the event to your calendar!", 'assistant_pet_prerecorded/calendar_add_event.wav')
    #text_to_speech("Sorry, something wrong appears. Please try again later.", 'assistant_pet_prerecorded/error.wav')
    #text_to_speech("You do not have any plan today! Have a nice day!", 'assistant_pet_prerecorded/calendar_no_plan_today.wav')
    #text_to_speech("Sorry, I cannot find any event that matches your description.", 'assistant_pet_prerecorded/calendar_cannot_find_event.wav')
    #same as above
    #text_to_speech("Sorry, I am unable to play this for you at the moment. Please try again later", 'assistant_pet_prerecorded/audiobook_error.wav')
    #text_to_speech("Oops, your google account authorization status has expired, do you want to re-authorize it now? If so, please tickle my right arm.", 'assistant_pet_prerecorded/calendar_token_expire.wav')
    text_to_speech("Sorry, I cannot find it.", 'assistant_pet_prerecorded/youtube_notfind.wav')
    text_to_speech("Sorry, I cannot find a way to reach Spotify, will play it via Youtube", 'assistant_pet_prerecorded/spotify_cannot_find_device.wav')

'''youtube_streamer.py'''
def record_youtube_streamer():
    if not os.path.exists('youtube_streamer_prerecorded'):
        os.makedirs('youtube_streamer_prerecorded')
    #text_to_speech("Sorry, I cannot find any Youtube videos for the query.", 'youtube_streamer_prerecorded/youtube_cannot_find_video.wav')

'''authorization.py'''
def record_authorization():
    if not os.path.exists('authorization_prerecorded'):
        os.makedirs('authorization_prerecorded')    
    #text_to_speech("If you want me to link to your Twitter account, please touch my right arm.", 'authorization_prerecorded/twitter_ask_for_link.wav')
    #text_to_speech("Please open the app in your phone, go to the authorization page, input the device ID, and press enter button", 'authorization_prerecorded/authorize_enter_device_id.wav')
    #text_to_speech("Then, please press the get button, and follow the instruction below shown in your screen.",'authorization_prerecorded/authorize_press_get.wav' )
    #text_to_speech("Sorry, something wrong happens. Please press the get button again to get a new URL, and type in the pin again.", 'authorization_prerecorded/authorize_error_try_again.wav')
    # twitter_conn_success.wav
    # same as #2
    # same as #3
    # same as #2
    # same as #3
    # calendar_conn_success.wav

def record_twitter_func():
    if not os.path.exists('twitter_func_prerecorded'):
        os.makedirs('twitter_func_prerecorded')      
    #text_to_speech("Successfully replied.", 'twitter_func_prerecorded/twitter_tweet_reply_success.wav' )
    #text_to_speech("Sorry, you cannot reply to it.", 'twitter_func_prerecorded/twitter_tweet_reply_failure.wav')
    #text_to_speech("Successfully posted.", 'twitter_func_prerecorded/twitter_post_tweet_success.wav' )
    #text_to_speech("Sorry, something went wrong. Please try again later.", 'twitter_func_prerecorded/twitter_post_tweet_failure.wav')
    #text_to_speech("Sorry, user not found.", 'twitter_func_prerecorded/twitter_user_not_found.wav')

def record_ibm():
    '''greeting'''
    text_to_speech("Yes?", 'greeting1.wav')
    text_to_speech("What can I do for you?", 'greeting2.wav')
    text_to_speech("Hi, how can I help?", 'greeting3.wav')
    '''news'''
    text_to_speech("Which platform do you prefer? BBC or CNN ?", 'dailynews.wav')
    #text_to_speech("What is the name of the podcast")
    #text_to_speech("What is the name of the book")
    
    #text_to_speech("Do you want to play a particular song?")
    #text_to_speech("What is the song name again?")
    



if __name__ == '__main__': 
    #record_assistant_pet()
    #record_authorization()
    #record_youtube_streamer()
    #record_twitter_func()
    record_ibm()