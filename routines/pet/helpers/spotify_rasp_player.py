import sys
import spotipy
import time

class spotify_player():
    def __init__(self):

        # token = spotipy.util.prompt_for_user_token(username='Watson', 
        #                            scope="user-read-playback-state streaming",
        #                            client_id='bf66e4d97d41425b98209012ed86ea63',
        #                            client_secret='71b2c447349c46e2959a84c1dd3a5fee' ,  
        #                            redirect_uri='https://localhost/')
        # 

        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id='bf66e4d97d41425b98209012ed86ea63',
                                     client_secret='71b2c447349c46e2959a84c1dd3a5fee', 
                                     redirect_uri='https://localhost/',
                                     username='Watson',     
                                     scope="user-read-playback-state streaming"
                                     )
        
        token_info = sp_oauth.validate_token(sp_oauth.cache_handler.get_cached_token())
        # check if current token exist
        
        if token_info:
            token = token_info["access_token"]
        else:
            sp_url = sp_oauth.get_authorize_url() # need to output to app
            # authorization steps on app and finally get url back
            print(sp_url)
            oauth_url = input()
            code = sp_oauth.parse_response_code(oauth_url)
            token = sp_oauth.get_access_token(code,as_dict=False)

        self.sp = spotipy.Spotify(auth=token)
        self.device_id=None
        devices = self.sp.devices()
        for d in devices['devices']:
            if d['name']=='raspotify (raspberrypi)':
                self.device_id = d['id']
        print(self.device_id)
        # could modify the user name to get different tokens 
        # later improvement: move client id and secret to another file to be loaded in

    def search_song(self,song_name):
        # attempting
        sp = self.sp
        search_result = sp.search(q=song_name,limit=1,offset=0,type='track')
        #print(search_result)
        print(type(search_result['tracks']['items'][0]))
        print(search_result['tracks']['items'][0]['uri'])
        return search_result['tracks']['items'][0]['uri']
        

    def play(self,query,limit=1,offset=0,type='track'):
        # current problem: when the song have multiple version cannot get the one might desire
        # this api itself is bad at looking for non english songs 
        sp = self.sp
        search_result = sp.search(q=query,limit=limit,offset=offset,type=type)
        #print(search_result)
        uri = search_result[type+'s']['items'][0]['uri']
        if type == 'track':
            sp.start_playback(device_id = self.device_id,uris = [uri])
        else:
            sp.start_playback(device_id = self.device_id,context_uri = uri)

    def resume(self):
        sp = self.sp
        sp.start_playback(device_id = self.device_id)
    
    def pause(self):
        sp = self.sp
        sp.pause_playback(device_id=self.device_id)
