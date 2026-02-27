from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import exifread

def get_decimal_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1]
    seconds = dms[2]
    
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return float(decimal)

def extract_metadata(image_path):
    data = {"lat": None, "lng": None, "time": None, "make": None}
    
    with open(image_path, 'rb') as f:
        # 1. Try ExifRead for robust GPS hunting
        tags = exifread.process_file(f)
        
        if 'GPS GPSLatitude' in tags:
            lat_dms = [float(x.num) / float(x.den) for x in tags['GPS GPSLatitude'].values]
            lat_ref = tags['GPS GPSLatitudeRef'].printable
            lng_dms = [float(x.num) / float(x.den) for x in tags['GPS GPSLongitude'].values]
            lng_ref = tags['GPS GPSLongitudeRef'].printable
            
            data["lat"] = get_decimal_from_dms(lat_dms, lat_ref)
            data["lng"] = get_decimal_from_dms(lng_dms, lng_ref)
            
        if 'EXIF DateTimeOriginal' in tags:
            data["time"] = tags['EXIF DateTimeOriginal'].printable
            
    return data

# Test it on your MSI
# print(extract_metadata("your_test_image.jpg"))