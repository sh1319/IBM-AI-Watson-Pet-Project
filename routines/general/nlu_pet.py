import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, KeywordsOptions, ClassificationsOptions

def extractKeyword(x,news=True):
    # extracts keyword from the text passed in
    with open('routines/general/credentials.json') as f:
        creds = json.load(f)

    authenticator = IAMAuthenticator(creds["ibm_nlu_api"])
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-05-01',
        authenticator=authenticator
    )
    natural_language_understanding.set_service_url(creds["ibm_nlu_url"])
    # NLU has a limit of a minimum of 15 char, if less than that, repeat unitl reaches that limit
    while len(x) <= 15:
        x += ' ' + x
    response = natural_language_understanding.analyze(
        text=x,
        features=Features(keywords=KeywordsOptions())).get_result()

    # print(json.dumps(response['keywords'], indent=2))
    keyword = ''
    for i,word in enumerate(response['keywords']):
        if news == True:
            # extrating news topic from phrases 
            # such as extract 'bitcoin' from 'news about bitcoin' 
            if word['text']!= 'news' and word['text']!= 'new':
                keyword = word['text']
        else:
            # extract all possible keywords in the phrase
            if i != 0:
                keyword += ','
            keyword += word['text'] 
    return keyword

def emo(speech_text):
    with open('routines/general/credentials.json') as f:
        creds = json.load(f)

    authenticator = IAMAuthenticator(creds["ibm_nlu_api"])
    nlu_service = NaturalLanguageUnderstandingV1(version='2019-07-12',authenticator=authenticator)
    nlu_service.set_service_url(creds["ibm_nlu_url"])
   
    response = nlu_service.analyze(
        text=speech_text,
        features=Features(classifications=ClassificationsOptions(model="tone-classifications-en-v1"))).get_result(),
                        
    res_list = response[0]['classifications']
    emotion = ""
    max_confidence = 0.00
    threshold = 0.5 # only when confidences passes this, emotion would be considered as valid
    for emo in res_list:
        confidence = emo['confidence']
        if confidence >= threshold and confidence > max_confidence:
            emotion = emo['class_name']
            max_confidence = confidence
    # print(emotion)
    print(max_confidence)
    return emotion

# if __name__ == '__main__':  
#     output = extractKeyword('news about Donauld Trump')
#     print(output)