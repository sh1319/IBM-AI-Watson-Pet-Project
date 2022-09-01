import vlc 
import pafy
import time
import multiprocessing
from googleapiclient.discovery import build

YOUTUBE_API_VERSION = 'v3'
YOUTUBE = 'youtube'

def youtube_search(query):
    # use youtube to search for videos and output the video id
    # query: the content that would type into search bar when using youtube to search for things 
    youtube = build(YOUTUBE,YOUTUBE_API_VERSION,developerKey="AIzaSyCia8cXK0Txg_131rJ40UzhtfHefC0bqlk")
    search_response = youtube.search().list(
        q=query,
        part='id,snippet'
    ).execute()

    videos = []
    videoids = []

    for search_result in search_response.get('items',[]):
        if search_result['id']['kind'] == 'youtube#video':
            videoids.append(search_result['id']['videoId'])
            videos.append(search_result['snippet']['title'])

    if len(videos)!=0:
        return videoids[0]
    else:
        print("cannot find any videos for the query") #TODO prerecord
        return None


class vlc_media_player:
    def __init__(self, change_gain_cb):
        self.media_player = None
        self.inst = vlc.Instance('--no-xlib --quiet ')
        # vlc State: 1 Opening, 2 Buffering, 3 Playing, 4 Paused
        self.playing = set([1,2,3,4])
        self.change_gain_cb = change_gain_cb
        self.player_process = None
    
        
    def youtube_player(self,query):

        urlid = youtube_search(query)
        if urlid is not None:
            # if able to find some audio files
            fulurl = "https://www.youtube.com/watch?v=" + urlid
            #print(fulurl)
            video = pafy.new(fulurl)
            best_audio = video.getbestaudio()
            audio_streaming_link = best_audio.url
            #print(audio_streaming_link)
            
            media = self.inst.media_new(audio_streaming_link)
            
            self.media_player = self.inst.media_player_new()
            self.media_player.set_media(media)
            self.media_player.play()
            time.sleep(1)
            
            return True
        else:
            return None
    
    def is_playing(self):
        # check whether the youtube streamer is playing music
        if self.media_player is not None and self.media_player.is_playing() is True:
            return True
        else:
            return False
    
    def pause(self):
        # pause the music played
        if self.media_player is not None and self.media_player.is_playing() is True:
            self.media_player.pause()
    
    def resume(self):
        # restart the music played 
        if self.media_player is not None and self.media_player.is_playing() is False:
            self.media_player.pause()

if __name__ == '__main__':  
     player = vlc_media_player()
     player.youtube_player("children audio books")
            




