
import os
import exifread
import stat
import time
from datetime import datetime
from math import sin, cos, sqrt, atan2, radians

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

def DetermineDistance(point1, point2):
    # approximate radius of earth in km
    R = 6373.008

    lat1 = radians(point1.latitude)
    lon1 = radians(point1.longitude)
    lat2 = radians(point2.latitude)
    lon2 = radians(point2.longitude)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c    

def _convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m / 60.0) + (s / 3600.0)

def getGPS(tags):
    latitude = tags.get('GPS GPSLatitude')
    latitude_ref = tags.get('GPS GPSLatitudeRef')
    longitude = tags.get('GPS GPSLongitude')
    longitude_ref = tags.get('GPS GPSLongitudeRef')
    if latitude:
        lat_value = _convert_to_degress(latitude)
        if latitude_ref.values != 'N':
            lat_value = -lat_value
    else:
        return {}
    if longitude:
        lon_value = _convert_to_degress(longitude)
        if longitude_ref.values != 'E':
            lon_value = -lon_value
    else:
        return {}
    return {'latitude': lat_value, 'longitude': lon_value}

def getDate(tag):
    return datetime.strptime(str(tag.get("Image DateTime")), "%Y:%m:%d %H:%M:%S")

def get_info(file_name):
    time_format = "%m/%d/%Y %I:%M:%S %p"
    file_stats = os.stat(file_name)
    modification_time = time.strftime(time_format,time.localtime(file_stats[stat.ST_MTIME]))
    access_time = time.strftime(time_format,time.localtime(file_stats[stat.ST_ATIME]))
    return modification_time, access_time

def main():
    picture_details = []
    for root, dir, files in os.walk(r"E:\Development\Picture time estimates\Resources"):    
        picture_tags = [exifread.process_file(os.path.join(root, x), 'rb') for x in files]
        for picture_tag in picture_tags:            
            gpsDetails = getGPS(picture_tag)
            picture_details.append(
                GPSData(
                    getDate(picture_tag),
                    gpsDetails.get("latitude"), 
                    gpsDetails.get("longitude"),
                    picture_tag.get("GPS GPSAltitude")
                )
            )        
    
    picture_details = [x for x in picture_details if x.latitude is not None and x.longitude is not None]
    picture_details.sort()

    for x in range(0, len(picture_details) - 1):
        distance = DetermineDistance(picture_details[x], picture_details[x+1])
        time = DetermineTime()
        print(distance)    

main()