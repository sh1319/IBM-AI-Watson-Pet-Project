import datetime
import json
from tracemalloc import start
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from beautiful_date import days,hours

def convertT(data):
    # grab events
    # data is a string that can be converted to json file
    log = json.loads(data)
    local_tz = datetime.datetime.now().astimezone().tzinfo
    startdate = log["startdate"].split("-")

    duration = "day"
    if log["starttime"]=="":
        startT = datetime.datetime(int(startdate[0]),int(startdate[1]),int(startdate[2]),
                                   tzinfo=local_tz)
    else:
        duration = "hour"
        starttime = log["starttime"].split(":")
        startT = datetime.datetime(int(startdate[0]),int(startdate[1]),int(startdate[2]),
                                   int(starttime[0]),int(starttime[1]),int(starttime[2]),
                                   tzinfo=local_tz)
    
    # if end point not specific, calculate it cuz need it for clashes 
    if log["enddate"] == "" and log["endtime"] == "":
        if duration == "day":
            endT = startT + 1*days
        else:
            endT = startT + 1*hours
    else:
        if log["enddate"] != "":
            enddate = log["enddate"].split("-")
            if log["endtime"] != "":
                endtime = log["endtime"].split(":")
                endT = datetime.datetime(int(enddate[0]),int(enddate[1]),int(enddate[2]),
                                         int(endtime[0]),int(endtime[1]),int(endtime[2]),
                                         tzinfo=local_tz)
            else:
                endT = datetime.datetime(int(enddate[0]),int(enddate[1]),int(enddate[2]),
                                         tzinfo=local_tz)
                pass
        else:
            endtime = log["endtime"].split(":")
            endT = datetime.datetime(int(startdate[0]),int(startdate[1]),int(startdate[2]),
                                         int(endtime[0]),int(endtime[1]),int(endtime[2]),
                                         tzinfo=local_tz)


    # create event 
    event = Event(
            "event",
            start = startT,
            end = endT,
        )
    if log["name"] != "":
        event.summary = log["name"]
    if log["location"] != "":
        event.location = log["location"]
    return startT,endT,event

def convertT2(data):
    # daily plan
    log = json.loads(data)
    local_tz = datetime.datetime.now().astimezone().tzinfo
    d = datetime.date.today()
    local_date = datetime.datetime(d.year,d.month,d.day,tzinfo=local_tz)

    if log["startdate"] == "":
        startD = local_date
    else:
        startdate = log["startdate"].split("-")
        startD = datetime.datetime(int(startdate[0]),int(startdate[1]),int(startdate[2]),
                                   tzinfo=local_tz)
    if log["starttime"] != "":
        starttime = log["starttime"].split(":")
        startT = startD + datetime.timedelta(hours=int(starttime[0]),minutes=int(starttime[1]),seconds=int(starttime[2]))
    else:
        startT = startD

    if log["enddate"]== "":
        endT = startD
    else:
        enddate = log["enddate"].split("-")
        endT = datetime.datetime(int(enddate[0]),int(enddate[1]),int(enddate[2]),
                                         tzinfo=local_tz)
    if log["endtime"] == "":
        endT = endT + datetime.timedelta(hours=0,minutes=0,seconds=0) #might be this line's problem
    else:
        endtime = log["endtime"].split(":")
        print(log["endtime"])
        endT = endT + datetime.timedelta(hours=int(endtime[0]),minutes=int(endtime[1]),seconds=int(endtime[2]))

    if log["name"]=="":
        query = log["location"]
    else:
        query = log["name"] + "," + log["location"]
    return startT,endT,query



def convertT3(data):
    # next plan
    log = json.loads(data)
    local_tz = datetime.datetime.now().astimezone().tzinfo
    d = datetime.date.today()

    if log["number"] == "":
        num = 1
    else:
        num = int(log["number"])
    
    if log["date"] != "":
        date = log["date"].split("-")
        t = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),23,59,59,tzinfo=local_tz)
    else:
        t = None
    
    if log["eventlocation"]=="":
        query = None
    else:
        query = log["eventlocation"]
    return num,t,query

def convertT4(data):
    # delete plan
    log = json.loads(data)
    local_tz = datetime.datetime.now().astimezone().tzinfo
    d = datetime.date.today()
    local_date = datetime.datetime(d.year,d.month,d.day,tzinfo=local_tz)

    if log["startdate"] == "" and log["starttime"] == "":
        startT = None
    else:
        if log["startdate"] == "":
            startD = local_date
        else:
            startdate = log["startdate"].split("-")
            startD = datetime.datetime(int(startdate[0]),int(startdate[1]),int(startdate[2]),
                                   tzinfo=local_tz)
        if log["starttime"]!= "":
            starttime = log["starttime"].split(":")
            startT = startD + datetime.timedelta(hours=int(starttime[0]),minutes=int(starttime[1]),seconds=int(starttime[2]))
        else:
            startT = startD


    if log["enddate"] == "" and log["endtime"] == "":
        endT = None
    else:
        if log["enddate"] == "":
            endT = startD
        else:
            enddate = log["enddate"].split("-")
            endT = datetime.datetime(int(enddate[0]),int(enddate[1]),int(enddate[2]),
                                   tzinfo=local_tz)
        if log["endtime"]!= "":
            endtime = log["endtime"].split(":")
            endT = endT + datetime.timedelta(hours=int(endtime[0]),minutes=int(endtime[1]),seconds=int(endtime[2]))
    
    
    query = convertQ(log["location"],log["name"])

    return startT,endT,query


def checkClash(calendar,startT,endT):
    count = 0
    events = calendar.get_events(datetime.datetime.now(),endT)
    for event in events:
        #print(event.end)
        if (event.end > startT and event.end <= endT) or (event.start > startT and event.start <= endT):
            if count == 0:
                print("Event clashes! Clashed events include: ")
                print(event.summary + " starts at " + event.start.strftime("%I:%M %p, %d %B %Y") + " and ends at " + event.end.strftime("%I:%M %p, %d %B %Y"))
            else:
                print("and " + event.summary + " starts at " + event.start.strftime("%I:%M %p, %d %B %Y") + " and ends at " + event.end.strftime("%I:%M %p, %d %B %Y"))
            count += 1
    if count == 0:
        return 'unclash'
    else:
        return 'clash'


def convertQ(a,b):
    if a == "":
        if b == "":
            return None
        else:
            return b
    else:
        return a + " " + b