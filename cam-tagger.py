from datetime import datetime, timedelta

from gpx import GPX
from exif import Image

#from PIL import Image
#import piexif



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

def add_gps_to_image(input_image_path, output_image_path, latitude, longitude):
    # Convert latitude and longitude to EXIF format
    def to_deg(value, ref):
        degrees = int(value)
        minutes = int((value - degrees) * 60)
        seconds = round((value - degrees - minutes / 60) * 3600, 6)
        return [(degrees, 1), (minutes, 1), (int(seconds * 1000000), 1000000)], ref

    # Determine latitude and longitude references
    lat_ref = "N" if latitude >= 0 else "S"
    lon_ref = "E" if longitude >= 0 else "W"

    # Convert to absolute values for EXIF
    latitude = abs(latitude)
    longitude = abs(longitude)

    # Open the image
    image = Image.open(input_image_path)

    # Load existing EXIF data or create new
    exif_dict = piexif.load(image.info.get("exif", b""))
    gps_ifd = exif_dict.get("GPS", {})

    # Add GPS data
    gps_ifd[piexif.GPSIFD.GPSLatitude] = to_deg(latitude, lat_ref)[0]
    gps_ifd[piexif.GPSIFD.GPSLatitudeRef] = lat_ref.encode()
    gps_ifd[piexif.GPSIFD.GPSLongitude] = to_deg(longitude, lon_ref)[0]
    gps_ifd[piexif.GPSIFD.GPSLongitudeRef] = lon_ref.encode()

    # Update EXIF data
    exif_dict["GPS"] = gps_ifd
    exif_bytes = piexif.dump(exif_dict)

    # Save the image with updated EXIF
    image.save(output_image_path, "jpeg", exif=exif_bytes)
    print(f"GPS data added to {output_image_path}")

def __main__():
    gpxFile = "./samples/gpx/activity_18778134543.gpx"
    points = getGPXPoints(gpxFile)
    points = offsetGPXPoints(points, 60*2)
    print("First Recorded Point:")
    print(points[0])

    imageFile = "./samples/pics/DSC02954.JPG"
    imageDateTime = getImageDateTime(imageFile)
    print("Image Timestamp:", imageDateTime)

    closestPoint = getClosestImageGPXPoint(points, imageDateTime)
    print("Closest GPX Point:", closestPoint)

    #input_image = "samples/pics/DSC02954.JPG"  # Replace with your input image path
    #output_image = "samples/pics/DSC02954-NEW.JPG"  # Replace with your desired output image path
    #latitude = 50.26117385365068912506103515625
    #longitude = 9.10273267887532711029052734375
#
    #add_gps_to_image(input_image, output_image, latitude, longitude)

if __name__ == "__main__":
    __main__()


