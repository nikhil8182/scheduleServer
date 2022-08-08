import datetime
import time
import requests
import pyrebase

config1 = {
    "apiKey": "AIzaSyAZcnME1iLaqUWHtnJWfnwvyp3_7h1Qdng",
    "authDomain": "smart-home-c08c4.firebaseapp.com",
    "databaseURL": "https://smart-home-c08c4-default-rtdb.firebaseio.com",
    "projectId": "smart-home-c08c4",
    "storageBucket": "smart-home-c08c4.appspot.com",
    "messagingSenderId": "867325064971",
    "appId": "1:867325064971:web:03089586292c3ed943540e",
    "measurementId": "G-01LGYRSE6M"
}

firebase1 = pyrebase.initialize_app(config1)
_db1 = firebase1.database()

config2 = {
    "apiKey": "AIzaSyC-UHZlYoFZX_otZDBOxlskclyebZFAtdc",
    "authDomain": "server-check-1c979.firebaseapp.com",
    "databaseURL": "https://server-check-1c979-default-rtdb.firebaseio.com",
    "storageBucket": "server-check-1c979.appspot.com",
}

firebase2 = pyrebase.initialize_app(config2)
db2 = firebase2.database()


def executeTheSchedule(scheduleData, uid, scheduleName):
    routineName = scheduleData['name']
    routineData = db1[uid]['SmartHome']['Scenes']['Schedule'][routineName]
    cusName = db1[uid]['name']
    _ids = db1[uid]['SmartHome']['Scenes']['Schedule'][routineName]['ids']
    status = scheduleData['status']
    print('schedule data = {}'.format(scheduleData))
    wait = scheduleData['wait']
    ip = db1[uid]['localServer']['staticIp']
    onlineServer = db1[uid]['noLocalServer']
    print('inside execute')
    try:
        trueDevices = db1[uid]['SmartHome']['Scenes']['Schedule'][routineName]['trueDevices']
    except:
        trueDevices = []
    print('true devices = ', trueDevices)
    print('status {} and wait is {} and online server = {} and customer name = {}'.format(status, wait, onlineServer,
                                                                                          cusName))
    if status and not wait and not onlineServer:
        print("i am going to execute!")

        for i in _ids:
            url = "http://" + str(ip) + "/" + str(i) + "/"
            print(f"url is : {url}")
            if i in trueDevices:
                requests.put(url, data={'Device_Status': True})
            else:
                requests.put(url, data={'Device_Status': False})
        _db1.child(uid).child('SmartHome').child('Scenes').child('Schedule').child(scheduleName).update({'wait': True})
        waitList.append(scheduleName)

    if status and not wait and onlineServer:
        print("i am going to execute online server!")
        # _db1.child(uid).child('SmartHome').child('Devices')
        devices = db1[uid]['SmartHome']['Devices']
        for x in devices:
            # print(x)
            id = db1[uid]['SmartHome']['Devices'][x]['id']
            if str(id) in _ids:
                # print('this is the id')
                # print(id)
                print('final true devices = ', trueDevices)
                print('final id = ', id)
                if str(id) in trueDevices:
                    print('iam trying ', id)
                    _db1.child(uid).child('SmartHome').child('Devices').child(x).update({'Device_Status': True})
                else:
                    print(' iam falsing ', id)
                    _db1.child(uid).child('SmartHome').child('Devices').child(x).update({'Device_Status': False})
        _db1.child(uid).child('SmartHome').child('schedule').child(scheduleName).update({'wait': True})
        waitList.append(scheduleName)


def schedule():
    currentTime = datetime.datetime.now().strftime('%H:%M')
    print(datetime.datetime.now().strftime('%I:%M:%S %p'))
    todaysDay = datetime.date.today().strftime('%a')
    for uids in db1:
        try:
            for scheduleName in db1[uids]['SmartHome']['Scenes']['Schedule']:
                scheduleTime = db1[uids]['SmartHome']['Scenes']['Schedule'][scheduleName]["time"]
                days = db1[uids]['SmartHome']['Scenes']['Schedule'][scheduleName]["days"]
                scheduledDaysList = []

                if days[0]:
                    scheduledDaysList.append('Sun')

                if days[1]:
                    scheduledDaysList.append('Mon')

                if days[2]:
                    scheduledDaysList.append('Tue')

                if days[3]:
                    scheduledDaysList.append('Wed')

                if days[4]:
                    scheduledDaysList.append('Thu')

                if days[5]:
                    scheduledDaysList.append('Fri')

                if days[6]:
                    scheduledDaysList.append('Sat')
                if scheduleTime == currentTime:
                    if todaysDay in scheduledDaysList:
                        print('Executing the schedule')
                        executeTheSchedule(db1[uids]['SmartHome']['Scenes']['Schedule'][scheduleName], uids,
                                           scheduleName)
                        print('schedules', db1[uids]['SmartHome']['Scenes']['Schedule'][scheduleName], uids,
                              scheduleName)

                for x in waitList:
                    if currentTime != db1[uids]['SmartHome']['Scenes']['Schedule'][x]["time"]:
                        _db1.child(uids).child('SmartHome').child('Scenes').child('Schedule').child(x).update(
                            {'wait': False})
                        waitList.remove(x)

                else:
                    pass

        except Exception as e:
            # print('exception is ', e)
            pass


def checkState():
    global state
    try:
        if str(datetime.datetime.now().time().minute) == '0' and state:
            db2.update({'schedule_status': True})
            state = False

        if str(datetime.datetime.now().time().minute) == '15' and state:
            db2.update({'schedule_status': True})
            state = False

        if str(datetime.datetime.now().time().minute) == '30' and state:
            db2.update({'schedule_status': True})
            state = False

        if str(datetime.datetime.now().time().minute) == '45' and state:
            db2.update({'schedule_status': True})
            state = False

        if str(datetime.datetime.now().time().minute) != '0' and str(
                datetime.datetime.now().time().minute) != '15' and str(
                datetime.datetime.now().time().minute) != '30' and str(datetime.datetime.now().time().minute) != '45':
            state = True

    except:
        pass


waitList = []
count = True
state = True

while count:
    time.sleep(1)
    db1 = _db1.get().val()
    print('wait list {}'.format(waitList))
    try:
        checkState()
        schedule()
    except:
        pass
