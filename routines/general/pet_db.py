import pymongo
import random
import json
from pymongo.server_api import ServerApi

# 3 required files: petID.json, pet_info.json,user_info.json
# info => local => cloud 
class WatsonPet:
    def __init__(self):
        self.last_active_time = None
        
        ### fetch ID from file 
        with open('routines/general/petID.json') as f:
            info = json.load(f)
            self.id = info['pet']['id']
        self.query = {"_id":self.id}
        ### infos
        self.pet = {}
        self.user = {}

        ### connect to db
        with open('routines/general/credentials.json') as f:
            creds = json.load(f)
        self.conn_str=creds["mongodb_connstr"]
        client = pymongo.MongoClient(self.conn_str, server_api=ServerApi('1'))
        self.database = client["WatsonAIPet"]
        petinfo = self.database['petinfo']
        userinfo = self.database['userinfo']  

        ### fetch/ initialise pet info data 
        res_pet = None
        for x in petinfo.find({"_id":self.id}):
            res_pet = x

        if res_pet == None:
            self.pet["_id"] = self.id
            touch_mark = [0.5,0.2,0.05]
            random.shuffle(touch_mark)
            self.pet['TOUCH1'] = touch_mark[0]
            self.pet['TOUCH2'] = touch_mark[1]
            self.pet['TOUCH3'] = touch_mark[2]
            self.pet['EYE'] = random.randint(1,3)
            self.pet['MOUTH'] = random.randint(1,5)
            self.pet['VOICE'] = random.randint(0,1)
            print('pet: How shall I call you') #TODO modify to speech processing
            self.pet['OWNER'] = 'lily' #TODO
            self.pet['EMO'] = 8
            petinfo.insert_one(self.pet)
        else:
            self.pet = res_pet

        ### fetch/ initialise pet info data 
        res_user = None
        for x in userinfo.find({"_id":self.id}):
            res_user = x

        if res_user == None:
            self.user["_id"] = self.id
            self.user['SPOTIFY'] = 0
            self.user['CALENDAR'] = 0
            self.user['TWITTER'] = 0
            self.user['RATIO'] = round(random.uniform(0.2,0.8),2)
            self.user['MUSIC'] = 0
            self.user['PODCAST'] = 0
            self.user['START_ALARM'] = '7:0'
            self.user['END_ALARM'] = '22:0'
            self.user['REPORT_EVENT'] = 0
            self.user['AUDIO_PLAYING'] = 0
            self.user['BOOK'] = 0
            userinfo.insert_one(self.user)
        else:
            self.user = res_user

    

    def getInfo(self,table,column): # OK!
        #get a column data value from the a table
        if table == 'pet':
            return self.pet[column]
        elif table == 'user':
            return self.user[column]
        return 

    def getAllInfo(self,table): # OK!
        # get all info as a dict from the table
        if table == 'pet':
            return self.pet
        elif table == 'user':
            return self.user
        return

    def updateEmo(self,change): # OK!
        # update the emotion data by adding the changing value and update to db
        self.pet['EMO'] += change
        if self.pet['EMO'] > 10:
            self.pet['EMO'] = 10
        if self.pet['EMO'] < 0:
            self.pet['EMO'] = 0
        petinfo = self.database['petinfo']
        petinfo.update_one(self.query,{"$set":{'EMO':self.pet['EMO']}})
    
    def updateInfo(self,column,value): # OK!
        # update data of a specified column and update to db
        if column != '_id':
            self.user[column] = value
            userinfo = self.database['userinfo']
            userinfo.update_one(self.query,{"$set":{column:value}})
        
    def updateRatio(self): # OK!
        # calculate the new ratio via the formula and update to db
        m = self.user['MUSIC']
        p = self.user['PODCAST']
        r = self.user['RATIO']

        if (m+p)!= 0:
            rate  = 0.3
            ratio_mp = m/(m+p)
            value = round((ratio_mp - r)*rate + r,2)
            self.updateInfo('RATIO',value)

    def getWorkingHours(self):
        # extract working hours information from tables 
        s = self.user['START_ALARM']
        e = self.user['END_ALARM']
        res = [0,0,0,0]
        res[0],res[1] = int(s.split(':')[0]),int(s.split(':')[1])
        res[2],res[3] = int(e.split(':')[0]),int(e.split(':')[1])
        return res


