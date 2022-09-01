from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json

def text_to_speech(text):
    with open('routines/general/credentials.json') as f:
        creds = json.load(f)
    authenticator = IAMAuthenticator(creds["ibm_text_to_speech_api"])
    text_to_speech = TextToSpeechV1(authenticator=authenticator)
    text_to_speech.set_service_url(creds["ibm_text_to_speech_url"])

    with open('routines/audioIO/helpers/to_play.wav', 'wb') as audio_file:
        res = text_to_speech.synthesize(text, accept = 'audio/wav', voice = 'en-GB_JamesV3Voice').get_result()
        audio_file.write(res.content)
