import os
from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS
from datetime import datetime
from math import sin, cos, sqrt, atan2, radians, pow

LOCATION = "E:\\Development\\Resources"

def _convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    if value is not None and value[0]is not None and value[1] is not None and value[2] is not None:
        d = float(value[0][0]) / float(value[0][1])
        m = float(value[1][0]) / float(value[1][1])
        s = float(value[2][0]) / float(value[2][1])
        return d + (m / 60.0) + (s / 3600.0)
    else:
        return 0

def DetermineDistance(point1, point2):
    # approximate radius of earth in km
    R = 6373.008

    lat1 = radians(point1.latitude)
    lon1 = radians(point1.longitude)
    alt1 = point1.altitude
    lat2 = radians(point2.latitude)
    lon2 = radians(point2.longitude)
    alt2 = point2.altitude

    dalt = abs(alt1 - alt2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return sqrt(pow(R * c * 1000, 2) + pow(dalt, 2))

def convert_altitude(value):
    if value is not None and value[0] is not None and value[1] is not None:
        return value[0] / value[1]
    else:
        return 0

class DistanceTime(object):
    def __init__(self, distance, time):
        self.distance = distance
        self.time = time
    def GetSpeed(self):
        return (self.distance / 1000) / (self.time / 60 / 60)

class GPSData(object):
    def __init__(self, createdDate, latitude, longitude, altitude):
        self.createDate = createdDate
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude

    def GetDetails(self):
        return "{0}: {1}, {2}".format(
            datetime.strftime(self.createDate, '%c'), 
            self.latitude, 
            self.longitude)
    
    def __lt__(self, other):
         return self.createDate < other.createDate

def get_tags(items):    
    ret = {}
    for key, value in items.items():       
        decoded = GPSTAGS.get(key) or TAGS.get(key)
        ret[decoded] = value
    return ret


def main():
    for root, dirs, files in os.walk(LOCATION): 
        gpsData = []
        tagValues = []
        timeDeltas = []
        for name in files:
            image = Image.open(os.path.join(LOCATION, name))
            info = image._getexif()
            ret = get_tags(info)  
            if ret['GPSInfo'] is not None:
                ret['GPSInfo'] = get_tags(ret['GPSInfo'])
            tagValues.append(ret) 

        for item in tagValues:
            gpsData.append(
                GPSData(
                    datetime.strptime(item.get('DateTimeDigitized'),  "%Y:%m:%d %H:%M:%S"),
                    _convert_to_degress(item.get('GPSInfo').get('GPSLatitude')),
                    _convert_to_degress(item.get('GPSInfo').get('GPSLongitude')),
                    convert_altitude(item.get('GPSInfo').get('GPSAltitude'))
                )
            )
        gpsData = [x for x in gpsData if x.latitude != 0 and x.longitude != 0]
        gpsData.sort()
        for x in range(0, len(gpsData) - 1):
            distance = DetermineDistance(gpsData[x], gpsData[x+1])
            time = (gpsData[x+1].createDate - gpsData[x].createDate).total_seconds()
            if time != 0:
                timeDeltas.append(DistanceTime(distance, time))

        for x in timeDeltas:
            if x.distance != 0:                
                print("{0} m in {1} seconds, with a speed of {2} km/h".format(x.distance, x.time, x.GetSpeed()))
            
        averageSpeed = (sum(c.distance for c in timeDeltas) / 1000) / (sum(c.time for c in timeDeltas) / 60 / 60)
        print("Average Speed: {0} km/h".format(averageSpeed))

main()