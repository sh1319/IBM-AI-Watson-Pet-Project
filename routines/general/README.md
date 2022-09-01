# Software Part Functionalities
This folder includes all the files required to implement the software features of Watson Pet.  
[authorization.py](authorization.py): This file contains all the functions related to authorization, including the authorization process of google, twitter and spotify, as well as helper functions like check_Token().   
[assistant_pet.py](assistant_pet.py): It is the most important function in software session. It contains the whole flow of conversations and actions.  
[calendar_pet.py](calendar_pet.py): This contains a bundle of helper functions that deals with differnet request time, and other data such as location or event name. It convert the data of json style into dictionary style.   
[nlu_pet.py](nlu_pet.py): This function contains 2 functions which both uses IBM Natural Language Understanding Service to process user input. One is for emotion analysis, and the other one is for keyword extraction  
[pet_db.py](pet_db.py): This contians the functions that initalise the pet data and user data and linked to database. It also contains functions to update, fetch or generate new data from database.    
[pet.py](pet.py): This function contains the initialised steps for Watson Pet. It also contains a background process that is always running. The backgound process can remind user about their events, update emotion data etc.  
[spotipy_rasp_player.py](spotipy_rasp_player.py):This contains several function based on spotipy library that could either be use to search music/podcast, stream the music, and obtian some user information once authorization is done by the user. 
[twitter_func.py](twitter_func.py): This file contains all the twitter-related functions, including posting, getting and repling tweets, sending and getting direct messages and checking authorization status.  
[youtube_streamer.py](youtube_streamer.py):This involes some wrap up functions that could search youtube for some audio files and play them out using VLC.  




