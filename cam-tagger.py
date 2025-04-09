from datetime import datetime, timedelta

from gpx import GPX
from exif import Image


def getImageDateTime(filePath):
    with open(filePath, 'rb') as image_file:
        image = Image(image_file)
        if image.has_exif:
            time_str = None
            if hasattr(image, 'datetime_original'):
                time_str = image.datetime_original
            elif hasattr(image, 'datetime'):
                time_str = image.datetime

            if time_str:
                # Exif datetime format is usually "YYYY:MM:DD HH:MM:SS"
                return datetime.strptime(time_str, '%Y:%m:%d %H:%M:%S')
            else:
                raise ValueError("No datetime information found in the image.")
        else:
            raise ValueError("No EXIF data found in the image.")
    return None

def getGPXPoints(filePath):
    gpx = GPX.from_file(filePath)
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append(point)
    return points

def offsetGPXPoints(gpxPoints, offsetInMin):
    offsetInSec = offsetInMin * 60
    for point in gpxPoints:
        point.time = point.time + timedelta(seconds=offsetInSec)
    return gpxPoints

def getClosestImageGPXPoint(gpxPoints, imageTimestamp, toleranceInMin=1):
    def datetimeToTimestamp(dateTime):
        return datetime.timestamp(dateTime)
    
    imageTimestamp = datetimeToTimestamp(imageTimestamp)
    closestPoint = gpxPoints[0]
    closestPointTimestamp = datetimeToTimestamp(closestPoint.time)

    for point in gpxPoints:
        closestPointTimestamp = datetimeToTimestamp(closestPoint.time)
        pointTimestamp = datetimeToTimestamp(point.time)
        # check if point is closer than the current closest point
        if abs(pointTimestamp - imageTimestamp) < abs(closestPointTimestamp - imageTimestamp):
            closestPoint = point
    
    if abs(closestPointTimestamp - imageTimestamp) > (toleranceInMin * 60):
        raise ValueError("No GPX point found within the specified tolerance.")
    
    return closestPoint

def __main__():
    gpxFile = "./samples/gpx/activity_18778134543.gpx"
    points = getGPXPoints(gpxFile)
    points = offsetGPXPoints(points, 60*2)
    print(points[0])

    imageFile = "./samples/pics/DSC02954.JPG"
    imageDateTime = getImageDateTime(imageFile)
    print("Image Timestamp:", imageDateTime)

    print("Closest GPX Point:", getClosestImageGPXPoint(points, imageDateTime))

if __name__ == "__main__":
    __main__()


