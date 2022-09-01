import json
from os.path import join, dirname
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

##########
# IBM CLOUD: Use the following code only to
# authenticate to IBM Cloud.
##########
with open('routines/general/credentials.json') as f:
    creds = json.load(f)

authenticator = IAMAuthenticator(creds["ibm_speech_to_text_api"])
speech_to_text = SpeechToTextV1(
    authenticator=authenticator
)
speech_to_text.set_service_url(creds["ibm_speech_to_text_url"])

##########
# IBM CLOUD PAK FOR DATA: Use the following code
# only to authenticate to IBM Cloud Pak for Data.
##########

# from ibm_cloud_sdk_core.authenticators import CloudPakForDataAuthenticator
# authenticator = CloudPakForDataAuthenticator(
#     '{username}',
#     '{password}',
#     'https://{cpd_cluster_host}{:port}'
# )
# speech_to_text = SpeechToTextV1(
#     authenticator=authenticator
# )
# speech_to_text.set_service_url('{url}')

class Speech_To_Text(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)
        self.text = ''
        
    def on_data(self, data):
        #print(data)
        print(json.dumps(data, indent=2))
        result = ''

        for i in range(len(data['results'])) :
            result += data['results'][i]['alternatives'][0]['transcript']
        
        self.text = result
        return self.text

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))

def convert_speech_to_text():
    converter = Speech_To_Text()
    with open('routines/audioIO/helpers/recorded.wav',
                  'rb') as audio_file:
        audio_source = AudioSource(audio_file)
        speech_to_text.recognize_using_websocket(
            audio=audio_source,
            content_type='audio/wav',
            recognize_callback=converter,
            model='en-US_BroadbandModel',
            max_alternatives=3)
    return converter.text
