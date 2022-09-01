import tweepy
import difflib
import json
from routines.general.authorization import authorize_twitter

# Post tweet
def postTweet(api, tweet):
    try:
        if api.update_status(tweet):
            msg = 'Successfully posted!'
            success = 1
            return msg, success
    except tweepy.errors.TweepyException as e:
        success = 0
        msg = 'Sorry, something went wrong. Please try again later.'
        return msg, success
    
# Get direct messages from twitter
def getDirectMessage(api, num):
    with open('routines/general/twitter_auth.json') as f:  #load current user id
        info = json.load(f)  
        
    response = api.get_direct_messages(count = num)

    message =  "Sorry, no new message."
    userid = 0
    res = False

    # if the sender is user itself, reply with "Sorry, no new message"
    if( response[0]._json['message_create']['sender_id']== info["user_id"]):
        message = message 
    # otherwise, report new message to user
    else:
        for i in range(len(response)) :
            #print(i)
            #print(response[i]._json['message_create']['message_data']['text'])
            user_id = response[i]._json['message_create']['sender_id']

            #print(type(user_id))
            if(user_id != info["user_id"]) :
                username = api.get_user(user_id = int(user_id))._json['name']
                message = "New message from " + username + ": " + response[i]._json['message_create']['message_data']['text']
                userid = user_id
                res = True
                break
    return message, userid, res
    
#  Do fuzzy match to find accurate username    
def matchUser(api, username,cutoff = 0.5) :
    # calling the api
    user_list = []
    user_id = []

    response = api.get_followers()
    for i in range (len(response)):
        user_list.append(response[i]._json['name'])
        user_id.append(response[i]._json['id'])

    # get accurate username from list of followers
    close_match = difflib.get_close_matches(username, user_list, 1, cutoff)
    print("username" + username)
    print("user_list" + user_list[0])
    if len(close_match) == 0 :
        message = 'Sorry, user not found'
        val = 0
    else:
        position = user_list.index(close_match[0])
        recipient_id = user_id[position]
        message = 'What content do you want to send to ' + close_match[0] + '?'
        val = 1

    return message, val

# Send direct messages to specific user 
def sendDirectMessage(api, text, userid = 0, username = '') :
    # calling the api
    recipient_id = 0

    if userid != 0 : # when the userid is given
        recipient_id = userid
    else:
        user_list = []
        user_id = []

        response = api.get_followers()
        for i in range (len(response)):
            user_list.append(response[i]._json['name'])
            user_id.append(response[i]._json['id'])

        close_match = difflib.get_close_matches(username, user_list, 1, 0.5)        
        position = user_list.index(close_match[0])
        recipient_id = user_id[position]

    # sending the direct message
    api.send_direct_message(recipient_id, text)

    return 1

# Get latest tweet from home page
def getLatestTweet(api,num=1):
    #tweet = api.user_timeline(screen_name = 'BorisJohnson', exclude_replies = True)[0]
    #This function can only work if user know accurate screen_name, which is quite hard to be implemented now

    tweet = api.home_timeline(exclude_replies = True)[0] # get tweets from homepage
    content = tweet.text
    username = tweet.user._json['name']
    tweetid = str(tweet.id)
    message = "Tweet from " + username + ": " + content
    return message, tweetid

# Reply to specific tweet
def replyTweet(api, text, tweetid):
    try:
        api.update_status(status = text, in_reply_to_status_id = tweetid , auto_populate_reply_metadata=True)
        message = 'Successfully replied.'
        success = True
    # except Exception as e:
    #     message = {'message' : str(e)}
    except:
        message = 'Sorry, you cannot reply.'
        success = False
    
    return message, success

# Check authorization status
def authorize():
    with open('routines/general/credentials.json') as f:
        creds = json.load(f)

    consumer_key = creds["twitter_key"]
    consumer_secret = creds["twitter_secret"]
    with open('routines/general/twitter_auth.json') as f:
        twitter_auth = json.load(f)
        access_token = twitter_auth["access_token"]
        access_token_secret = twitter_auth["access_token_secret"]
    if (access_token != "") and (access_token_secret != "") : # check authorization status
        auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret,access_token, access_token_secret)
        api = tweepy.API(auth)  
    else :
        api = authorize_twitter() 
    return api
