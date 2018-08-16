import time
def getTimeFromStamp(stamp):
    timeArray = time.localtime(int(stamp))
    return  time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

def dateStringMakerForFilter(dt):
    #2018-08-15+00:00:00
    return  dt.strftime("%Y-%m-%d+%H:%M:%S")