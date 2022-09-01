from unicodedata import name
import spotipy
import random 
from routines.general.authorization import authorize_spotify
import json

class spotify_player():
    def __init__(self,speak,premium=True):
        with open('routines/general/credentials.json') as f:
            creds = json.load(f)

        scope= "user-read-playback-state streaming user-top-read user-read-private user-read-email"
        
        # setup oauth service 
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=creds["spotify_client_id"],
                                     client_secret=creds["spotify_client_secret"], 
                                     redirect_uri=creds["spotify_redirect_url"],
                                     #username='Watson',     
                                     scope=scope,
                                     cache_path='routines/general/.cache-Watson'
                                     )
        
        # fetch token using oauth servie
        token_info = sp_oauth.validate_token(sp_oauth.cache_handler.get_cached_token())
        
        token = None
        if token_info:
            # if info could be fetched, generate token directly
            token = token_info["access_token"]
        else:
            # if not do the authorization via mobile app, and would keep trying until success
            while not token:
                try:
                    sp_url = sp_oauth.get_authorize_url() 
                    oauth_url = authorize_spotify(sp_url,speak)
                    code = sp_oauth.parse_response_code(oauth_url)
                    token = sp_oauth.get_access_token(code,as_dict=False)
                    #audioIO.play_prerecorded("spotify_conn_success") #TODO prerecord
                    speak(True, "spotify_conn_success")
                except spotipy.oauth2.SpotifyOauthError as e:
                    print("Pet: Failed authorize because " + e.reason)
                    msg = "Sorry, I cannot authorize because " + e.reason
                    #audioIO.play_dynamic(msg) #TODO dynamic
                    speak(False, msg)
                    

        self.sp = spotipy.Spotify(auth=token) 
        self.device_id = self.findDevice()
        print(self.sp.me()['display_name'])
        
    def checkPremium(self):
        # check if user has a premium account for spotify 
        sp= self.sp
        print('checkPremium')
        print('user: ' + sp.me()['display_name'])
        if sp.me()['product'] == 'open':
            print('not premium')
            return False
        elif sp.me()['product'] == 'premium':
            print('premium')
            return True

    def findDevice(self,name='raspotify'):
        # find and try to link to raspberry
        sp= self.sp
        for device in sp.devices()['devices']:
            if name in device['name']:
                print(device['id'])
                return device['id']
        print('Cannot find the raspberry pi')
        return None
    
    def setDevice(self):
        # check if raspberry is now connected and ready to stream music or not
        res = self.findDevice()
        if res != None:
            self.device_id = res
            print('find raspberry pi now')
            return True
        else:
            print('cannot find raspberry pi now')
            return False
         
    def play(self,query,limit=1,offset=0,type='track',q_type ='name'):
        # play music/podcast of specific name via spotify streaming
        # type='track': search for music
        # type='show' : search for podcast series
        # query: the name or id of the song
        # q_type: the type of query string, either 'name' or 'id'
        sp = self.sp
        if q_type == 'name':
            search_result = sp.search(q=query,limit=limit,offset=offset,type=type)
            uri = search_result[type+'s']['items'][0]['uri']
        else:
            uri = query
        if type == 'track':
            uri_list = [uri]
            sp.start_playback(device_id = self.device_id,uris=uri_list)
        else:
            sp.start_playback(device_id = self.device_id,context_uri=uri)
        return True

    def play_top_tracks(self):
        # play the one of the user's faviourite song 
        sp = self.sp
        search_result = sp.current_user_top_tracks(limit=5, offset=0, time_range='short_term')
        if len(search_result['tracks']['items']) != 0:
            pick = random.randint(0,len(search_result['tracks']['items'])-1)
            uri = search_result['tracks']['items'][pick]['uri']
            uri_list = [uri]
            sp.start_playback(device_id = self.device_id,uris=uri_list)
        else:
            return False

    def get_top_tracks(self):
        # get the name for one of the user's faviourite tracks
        sp = self.sp
        search_result = sp.current_user_top_tracks(limit=5, offset=0, time_range='short_term')
        if len(search_result['tracks']['items']) != 0:
            pick = random.randint(0,len(search_result['tracks']['items'])-1)
            name = search_result['tracks']['items'][pick]['name']
            return name
        else:
            return False

    def get_recommended(self,genre):
        # depending on genre and user's favourite tracks, find a song that user might like
        sp = self.sp
        seed_tracks=''
        search_result = sp.current_user_top_tracks(limit=4, offset=0, time_range='short_term')
        tracks_num = len(search_result['items'])
        for i in range(tracks_num):
            if i != 0:
                seed_tracks += ','
            seed_tracks += search_result['items'][i]['id']
        print(seed_tracks)
        
        if tracks_num == 0:
            # cannot do a recommendation 
            return False
        else:
            # do a recommendation 
            song = sp.recommendations(seed_tracks = seed_tracks, seed_genres = genre,limit=1)
            if len(song['tracks'])>0:
                return song['tracks'][0]['name']
            else:
                return False
            

    def resume(self):
        # restart the streaming 
        sp = self.sp
        sp.start_playback(device_id = self.device_id)
    
    def pause(self):
        # pause the streaming 
        sp = self.sp
        sp.pause_playback(device_id=self.device_id)
    
if __name__ == '__main__': 
    player = spotify_player()
    player.findDevice()
    player.checkPre
    

