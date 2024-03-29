"""
Track chart drawing methods
"""
import sys
import math
import datetime
from PIL import Image, ImageDraw, ImageOps
import geo
import csv
import json
import gps_to_mileage
import dateutil.parser as dp
import pickle
import lidar_util
import class_i as aar

import pirail

GPS_THRESHOLD = 9
AA = 0.40 # Complementary filter constant

def new(args):
    """
    New Trackchart
    """
    (size, margin, first, last, known_file, data_file) = args
    pixel_per_mile = float(size[0]-3*margin) / (last-first)
    return {'image': Image.new("1", size, "white"),
            'margin': margin,
            'mileposts': (first, last, pixel_per_mile),
            'known_file': known_file,
            'data_file': data_file,
            'G': gps_to_mileage.Gps2Miles(known_file),
            'D': [],
    }

def draw_title(tc, title="PiRail"):
    im = tc['image']
    margin = tc['margin']
    draw = ImageDraw.Draw(im)
    (x_size, y_size) = draw.textsize(title)
    x = margin
    y = im.size[1] - y_size - 1
    draw.text((x, y), title)
    del draw

def parse_line(line):
    if line[1] == "SKY":
        obj = json.loads(" ".join(line[2:-1]))
    elif line[1] == "TPV":
        obj = json.loads(" ".join(line[2:-1]))
    elif line[1] == "ATT":
        obj = json.loads(" ".join(line[2:-1]))
    elif line[1] in ["CONFIG", "LIDAR", "LOG"]:
        return None
    elif line[1] == "G":
        obj = {
            'lat': float(line[2]),
            'lon': float(line[3]),
        }
        try:
            obj.update({'alt': float(line[4]),})
        except ValueError:
            pass
        try:
            obj.update({'epx': float(line[5]),})
        except ValueError:
            pass
        try:
            obj.update({'epy': float(line[6]),})
        except ValueError:
            pass
        try:
            obj.update({'epv': float(line[7]),})
        except ValueError:
            pass
        try:
            obj.update({'speed': float(line[8]),})
        except ValueError:
            pass
        try:
            obj.update({'eps': float(line[9]),})
        except ValueError:
            pass
        try:
            obj.update({'track': float(line[10]),})
        except ValueError:
            pass
    elif line[1] == "A":
        obj = {
            'acc_x': float(line[2]),
            'acc_y': float(line[3]),
            'acc_z': float(line[4]),
            'gyro_x': float(line[5]),
            'gyro_y': float(line[6]),
            'gyro_z': float(line[7]),
        }
    elif line[1] == "L":
        obj = {
            'lidar': eval(line[2]),
        }
    elif line[1] == "M":
        return None
    else:
        print(line)
        sys.exit(1)

    if not 'time' in obj: 
        obj.update({'time': line[0]})
    if not 'class' in obj: 
        obj.update({'class': line[1]})

    return obj

def read_data(tc):
    tc['D'] = []
    queue = []
    first = last = None

    try:
        with open(tc['data_file']+".pickle","rb") as f:
            tc['D'] = pickle.load(f)
        return
    except:
        pass

    if tc['data_file'] is None:
        return

    with open(tc['data_file']) as f:
        used = current = 0
        for line in csv.reader(f, delimiter=' ', quotechar="'"):
            print(line)
            if line[0][0] == "#" or line[-1] != '*':
                continue
            if line[1] == "SKY":
                obj = json.loads(" ".join(line[2:-1]))
                used = count = 0
                for s in obj['satellites']:
                    count += 1
                    if s['used']:
                        used += 1
            elif line[1] == "TPV":
                obj = json.loads(" ".join(line[2:-1]))
                if used < 10:
                    continue
                if not('lat' in obj and 'lon' in obj and 'time' in obj):
                    continue
                if first is None:
                    first = obj
                else:
                    last = obj
                    start_time = dp.parse(first['time']).timestamp()
                    start_lat = first['lat']
                    start_lon = first['lon']
                    end_time = dp.parse(last['time']).timestamp()
                    end_lat = last['lat']
                    end_lon = last['lon']
                    for q in queue:
                        q_time = dp.parse(q[0]).timestamp()
                        # time ratio
                        ratio = (q_time - start_time) / (end_time - start_time)
                        # latitiude
                        q_lat = (end_lat - start_lat) * ratio + start_lat 
                        # longitude
                        q_lon = (end_lon - start_lon) * ratio + start_lon 
                        #print(ratio, q_lat, q_lon, q)
                        obj = parse_line(q)
                        if obj is not None:
                            obj['lat'] = q_lat
                            obj['lon'] = q_lon
                            tc['D'].append(obj)
                    queue = []
                    first = last
                tc['D'].append(parse_line(line))
            else:
                queue.append(line)

    print ("entries", len(tc['D']))

    # Calculate Yaw/Pitch/Roll
    # Based on:
    # https://github.com/ozzmaker/BerryIMU/blob/master/python-BerryIMU-gryo-accel-compass/berryIMU-simple.py
    gyroXangle = gyroYangle = gyroZangle = CFangleX = CFangleY = CFangleZ = 0
    last_time = None
    for obj in tc['D']:
        if obj['class'] != "ATT":
            continue
        if 'roll' in obj:
            continue
        if last_time is not None:
            DT = (pirail.parse_time(obj['time']) - pirail.parse_time(last_time)).total_seconds()
            last_time = obj['time']
        else:
            DT = 0

        gyroXangle+=obj['gyro_x']*DT;
        gyroYangle+=obj['gyro_y']*DT;
        gyroZangle+=obj['gyro_z']*DT;
        AccXangle = math.degrees((float) (math.atan2(obj['acc_y'],obj['acc_z'])+math.pi));
        AccYangle = math.degrees((float) (math.atan2(obj['acc_z'],obj['acc_x'])+math.pi));
        AccZangle = math.degrees((float) (math.atan2(obj['acc_y'],obj['acc_x'])+math.pi));
        # Complementary Filter
        CFangleX=AA*(CFangleX+obj['gyro_x']*DT) +(1 - AA) * AccXangle;
        CFangleY=AA*(CFangleY+obj['gyro_y']*DT) +(1 - AA) * AccYangle;
        CFangleZ=AA*(CFangleZ+obj['gyro_z']*DT) +(1 - AA) * AccZangle;

        obj['roll'] = CFangleY
        obj['pitch'] = CFangleX
        obj['yaw'] = CFangleZ


    # Calculate Mileage
    for obj in tc['D']:
        if 'mileage' not in obj:
            obj['mileage'], obj['certainty'] = tc['G'].find_mileage(obj['lat'], obj['lon'])

    tc['D'] = sorted(tc['D'], key=lambda k: k['mileage'], reverse=False)

    with open(tc['data_file'] + ".pickle", "wb" ) as f:
        pickle.dump(tc['D'], f, pickle.HIGHEST_PROTOCOL)


def mile_to_pixel(tc, m):
    """
    Convert mileage to pixel value
    """
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    return int(1.5*margin+m*pixel_per_mile+0.5)

def mileage_to_string(m):
    """
    Format a mileage
    """
    return "%0.2f" % float(m)

def bearing_delta(b1, b2):
    """
    Calculate diffence in bearings
    """
    delta = (b2 - b1)
    if delta > 180:
        delta -= 360
    elif delta < -180:
        delta += 360
    return delta

def rotated_text(draw, t, degrees):
    """
    Rotate Text
    """
    (x_size, y_size) = draw.textsize(t)
    txt = Image.new("L", (x_size+2, y_size+2), "black")
    d = ImageDraw.Draw(txt)
    d.text((1, 1), t, fill=255)
    return (ImageOps.invert(txt.rotate(degrees, expand=True)), x_size, y_size)

def border(tc):
    """
    Draw a page border
    """
    im = tc['image']
    margin = tc['margin']
    draw = ImageDraw.Draw(im)
    draw.line((margin, margin, im.size[0]-margin, margin))
    draw.line((im.size[0]-margin, margin, im.size[0]-margin, im.size[1]-margin))
    draw.line((im.size[0]-margin, im.size[1]-margin, margin, im.size[1]-margin))
    draw.line((margin, im.size[1]-margin, margin, margin))
    del draw

def milepost_symbol(draw, x, y_size, margin, name, alt_name):
    """
    Draw a milepost symbol
    """
    # Vertical
    draw.line((x, 2*margin, x, y_size*0.5))
    draw.line((x, y_size*0.75, x, y_size))
    # Diamond
    draw.line((x, margin, x+0.5*margin, 1.5*margin))
    draw.line((x+0.5*margin, 1.5*margin, x, 2*margin))
    draw.line((x, 2*margin, x-0.5*margin, 1.5*margin))
    draw.line((x-0.5*margin, 1.5*margin, x, margin))
    # Labels
    draw.text((x+0.5*margin, margin), name)
    if alt_name is not None:
        draw.text((x-0.5*margin-draw.textsize(alt_name)[0], margin), alt_name)

def mileposts(tc, from_file=False):
    """
    Draw mileposts
    """
    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']

    draw = ImageDraw.Draw(im)
    if not from_file:
        #print(first)
        #print(last)
        for mileage in range(int(first), int(last+1)):
            x = mile_to_pixel(tc, mileage-first)
            milepost_symbol(draw, x, (im.size[1]-margin), margin, "MP%d" % mileage, None)
    else:
        for obj in tc['G'].get_points(ktype='K', kclass='MP'):
            #print (obj)

            mileage = obj['mileage']
            if not (first <= mileage <= last):
                continue

            metadata = obj['metadata']
            if 'alt_name' not in metadata:
                metadata['alt_name'] = None

            x = mile_to_pixel(tc, mileage-first)
            milepost_symbol(draw, x, (im.size[1]-margin),
                            margin, metadata['name'], metadata['alt_name'])

            # Survey Station
            if 'survey' in metadata: 
                survey_station = metadata['survey']
                (w, x_size, y_size) = rotated_text(draw, survey_station, 90)
                im.paste(w, ((x-y_size-3, im.size[1]-margin-x_size)))
    del draw

def mainline(tc):
    """
    Draw mainline
    """
    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)
    y = (im.size[1]-margin)*0.625
    start = end = None

    for obj in tc['G'].get_points(ktype='K', kclass='E'):
        mileage = obj['mileage']

        if start is None or mileage < start:
            start = mileage
        if end is None or mileage > end:
            end = mileage

    if start is None or start < first:
        start = first
    if end is None or end > last:
        end = last

    x1 = max(margin, mile_to_pixel(tc, start-first))
    x2 = min(im.size[0] - margin, mile_to_pixel(tc, end-first))
    draw.line((x1, y, x2, y))

    del draw

def bridges_and_crossings(tc, xing_type=None):
    """
    Draw bridges and crossings
    """
    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)

    y = int((im.size[1]-margin)*0.625)
    for obj in tc['G'].get_points(ktype='K'):
        mileage = obj['mileage']
        xtype = obj['class']
        metadata = obj['metadata']

        if not (first <= mileage <= last) or xtype not in ['U', 'O', 'X']:
            continue

        if xing_type is not None and xtype != xing_type:
            continue

        x = mile_to_pixel(tc, mileage-first)
        if xtype == 'U':
            # Draw underpass
            draw.line((x-5, y, x+5, y), fill=255)
            draw.line((x, y-margin, x, y+margin))
        elif xtype == 'O':
            # Draw overpass
            draw.line((x, y-margin, x, y-5))
            draw.line((x, y+5, x, y+margin))
        elif xtype == 'X':
            # Draw road
            draw.line((x, y-margin, x, y+margin))

        # Draw description
        if 'name' in metadata:
            text = metadata['name']
        elif 'street' in metadata:
            text = metadata['street']
        else:
            if xtype == 'X':
                text = "pvt"
            else:
                text = ""
        if 'crossing' in metadata:
            text += " (" + metadata['crossing'] + ")"

        if len(text) > 0:
            description = ("%s %s" % (mileage_to_string(mileage), text)).strip()
            (w, x_size, y_size) = rotated_text(draw, description, 90)
            im.paste(w, (int(x-y_size/2), int(y-1.5*margin-x_size)))
    del draw

def townlines(tc):
    """
    Draw townlines
    """
    box_size = 10
    offset = 2
    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)

    y = int((im.size[1]-margin)*0.5)
    for obj in tc['G'].get_points(ktype='K', kclass='TL'):
        mileage = obj['mileage']
        metadata = obj['metadata']
        if not (first <= mileage <= last):
            continue

        x = mile_to_pixel(tc, mileage-first)

        # Town 1
        description = metadata['name'].split("/")[0]
        (w, x_size1, y_size1) = rotated_text(draw, description, 90)
        im.paste(w, (int(x-y_size1-3), int(y-(x_size1/2))))
        # Town 2
        description = metadata['name'].split("/")[1]
        (w, x_size2, y_size2) = rotated_text(draw, description, 90)
        im.paste(w, (int(x), int(y-(x_size2/2))))
        # Dashed Town Line
        if x_size2 > x_size1:
            x_size1 = x_size2
        x_size1 = int(math.ceil(x_size1/10.0)*10)
        for y1 in range(int(y-x_size1/2), int(y+x_size1/2), 10):
            draw.line((x, y1, x, y1+2))
            draw.line((x, y1+7, x, y1+10))
    del draw

def stations(tc):
    """
    Draw Stations
    """
    box_size = 10
    offset = 2
    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)

    y = int((im.size[1]-margin)*0.625)
    for obj in tc['G'].get_points(ktype='K', kclass='S'):
        mileage = obj['mileage']
        metadata = obj['metadata']
        if not(first <= mileage <= last):
            continue

        x = mile_to_pixel(tc, mileage-first)
        #print(obj)
        if 'offset' in metadata:
            offset = metadata['offset']
        else:
            offset = 0

        if offset != 0:
            if offset > 0:
                # Above the mainline
                offset = 2+pixel_per_mile*0.01*offset
            elif offset < 0:
                # Below the mainline
                offset = -(2+pixel_per_mile*0.01*abs(offset)+1.5*box_size)

            # Draw symbol
            draw.polygon((x-box_size/2, y-offset,
                          x-box_size/2, y-offset-box_size,
                          x, y-offset-1.5*box_size,
                          x+box_size/2, y-offset-box_size,
                          x+box_size/2, y-offset
                         ), fill=255, outline=0)

        # Draw description
        if 'name' in metadata:
            text = metadata['name']
        elif 'street' in metadata:
            text = metadata['street']
        else:
            text = "pvt"

        if 'crossing' in metadata:
            text += " (" + metadata['crossing'] + ")"

        y1 = int((im.size[1]-margin)*0.7)
        (x_size, y_size) = draw.textsize(text)
        draw.text((int(x-x_size/2), int(y1)), text)
        y1 += y_size
        m_str = mileage_to_string(mileage)
        (x_size, y_size) = draw.textsize(m_str)
        draw.text((int(x-x_size/2), int(y1)), m_str)
    del draw

def yardlimits(tc):
    """
    Draw Yardlimits
    """
    line_length = 10
    offset = 2
    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)

    y = int((im.size[1]-margin)*0.625)
    for obj in tc['G'].get_points(ktype='K', kclass='YL'):
        label = obj['class']
        mileage = obj['mileage']
        metadata = obj['metadata']
        if not(first <= mileage <= last):
            continue

        x = mile_to_pixel(tc, mileage-first)

        (x_size1, y_size1) = draw.textsize(label)
        m_str = mileage_to_string(mileage)
        (x_size2, y_size2) = draw.textsize(m_str)

        if offset > 0:
            # Above the mainline
            offset = 2
            draw.line((x, y-offset, x, y-offset-line_length))
            y1 = y-offset-line_length-y_size1-y_size2
        else:
            # Below the mainline
            offset = 2
            draw.line((x, y+offset, x, y+offset+line_length))
            y1 = y+offset+line_length

        # Draw description
        draw.text((int(x-x_size1/2), int(y1)), label)
        draw.text((int(x-x_size2/2), int(y1+y_size1)), m_str)
    del draw

def controlpoints(tc):
    """
    Draw Control Points
    """
    line_length = 10
    offset = 2
    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)

    y = int((im.size[1]-margin)*0.625)
    for obj in tc['G'].get_points(ktype='K'):
        label = obj['class']
        if label not in ['CRF', 'CRT', 'CLF', 'CLT']:
            continue
        mileage = obj['mileage']
        metadata = obj['metadata']

        #print(obj)
        
        if not(first <= mileage <= last):
            continue

        x = mile_to_pixel(tc, mileage-first)
        y_start = y
        y_size = 0.01 * pixel_per_mile
        start_offset = metadata['start']
        end_offset = metadata['end']

        if start_offset > 0:
            # above the mainline
            y_start = y - start_offset*y_size
        elif start_offset < 0:
            # below the mainline
            y_start = y - start_offset*y_size
    
        if label[2] == 'F':
            if label[1] == 'R':
                y_end = y_start - end_offset*y_size
                x_end = x + abs(end_offset)*y_size
            else:
                y_end = y_start - end_offset*y_size
                x_end = x + abs(end_offset)*y_size
        else:
            if label[1] == 'R':
                y_end = y_start - end_offset*y_size
                x_end = x - abs(end_offset)*y_size
            else:
                y_end = y_start - end_offset*y_size
                x_end = x - abs(end_offset)*y_size

        draw.line((x, y_start, x_end, y_end))
    del draw

def smooth_data(tc, input_data=None, mileage_threshold=0.01, track_threshold=45, write_file=True):
    (first, last, pixel_per_mile) = tc['mileposts']
    if input_data is None:
        input_data = tc['D']

    print("Input=%d" % len(input_data))
    data = []
    used = 0
    for obj in input_data:
        if obj['class'] == "SKY":
            used=0
            for s in obj['satellites']:
                if s['used']:
                    used += 1
            print(used, len(obj['satellites']))
            continue
        elif obj['class'] != "TPV":
            continue

        if used < GPS_THRESHOLD:
            print(used, "less than", GPS_THRESHOLD)
            continue

        print(obj)

        used = 0

        mileage = obj['mileage']
        if not (first <= mileage <= last):
            continue
        #if obj['speed'] <= obj['eps']:
        #    print("too slow", obj)
        #    continue
        try:
            print(mileage)
            new_obj = {
                'class': obj['class'],
                'speed': obj['speed'],
                'eps': obj['eps'],
                'lat': obj['lat'],
                'lon': obj['lon'],
                'alt': obj['alt'],
                'track': obj['track'],
                'mileage': obj['mileage'],
            }
            data.append(new_obj)
        except KeyError as ex:
            print("skipped", ex, obj)

    # Ensure the list is sorted by mileage
    data = sorted(data, key=lambda k: k['mileage'], reverse=False)

    # smooth, looking at all measurements +/-
    smooth_data = []
    for i in range(0, len(data)):
        lat = [data[i]['lat']]
        lon = [data[i]['lon']]
        alt = [data[i]['alt']]
        mileage = data[i]['mileage']
        # work backwards
        j = i-1
        while j >= 0 and data[j]['mileage'] >= mileage-mileage_threshold/2:
            lat.append(data[j]['lat'])
            lon.append(data[j]['lon'])
            alt.append(data[j]['alt'])
            j -= 1
        # work forwards
        j = i + 1
        while j < len(data) and data[j]['mileage'] <= mileage+mileage_threshold/2:
            lat.append(data[j]['lat'])
            lon.append(data[j]['lon'])
            alt.append(data[j]['alt'])
            j += 1
        # Average
        new_lat = avg_3_of_5(lat)
        new_lon = avg_3_of_5(lon)
        new_alt = avg_3_of_5(alt)
        mileage, certainty = tc['G'].find_mileage(new_lat, new_lon)
        obj = {
            'class': data[i]['class'],
            'speed': data[i]['speed'],
            'eps': data[i]['eps'],
            'lat': new_lat,
            'lon': new_lon,
            'alt': new_alt,
            'mileage': mileage,
            'certainty': certainty,
            'track': data[i]['track']
        }

        if i == 0:
            smooth_data.append(obj)
            last_obj = obj
        else:
            d = geo.great_circle(last_obj['lat'], last_obj['lon'],
                                 obj['lat'], obj['lon'])
            b = geo.bearing(last_obj['lat'], last_obj['lon'],
                            obj['lat'], obj['lon'])

            if d > mileage_threshold:
                print("Inserted: %f @ %d" % (d,b))
                smooth_data.append(obj)
                last_obj = obj

    # Ensure we're still sorted
    smooth_data = sorted(smooth_data, key=lambda k: k['mileage'], reverse=False)

    for i in range(1,len(smooth_data)):
        b = geo.bearing(smooth_data[i-1]['lat'], smooth_data[i-1]['lon'],
                        smooth_data[i]['lat'], smooth_data[i]['lon'])
        smooth_data[i]['track'] = b
    if len(smooth_data) > 2:
        smooth_data[0]['track'] = smooth_data[1]['track']

    # save result
    if write_file:
        with open("smoothdata_tmp.csv", "w") as f:
            f.write("Mileage,Latitude,Longitude,Altitude,Track\n")
            for obj in smooth_data:
                f.write("%f %f %f %f %f\n" % (
                        obj['mileage'],
                        obj['lat'],
                        obj['lon'],
                        obj['alt'],
                        obj['track'],
                        ))

    print("Smooth=%d" % len(smooth_data))
    return smooth_data

def elevation(tc):
    """
    Draw Elevation profile
    """
    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)

    y = int((im.size[1]-margin))
    y_range = 200

    edata = smooth_data(tc, mileage_threshold=0.01)

    # Check for empty list
    if len(edata) == 0:
        return

    emin = emax = edata[0]['alt']
    for i in range(1,len(edata)):
        emin = min(emin, edata[i]['alt'])
        emax = max(emax, edata[i]['alt'])

    # baseline
    #draw.text((int(1.5*margin), im.size[1]-margin), "Base = %d" % emin)
    #draw.line((margin, im.size[1]-margin, im.size[0]-margin, im.size[1]-margin))

    # loop over the list
    min_display = max_display = False
    for j in range(1, len(edata)):
        x1 = mile_to_pixel(tc, edata[j-1]['mileage']-first)
        x2 = mile_to_pixel(tc, edata[j]['mileage']-first)
        y1 = y - (edata[j-1]['alt'] - emin) * (y_range/emax)
        y2 = y - (edata[j]['alt'] - emin) * (y_range/emax)
        draw.line((x1, y1, x2, y2))
        if edata[j]['alt'] == emax and not max_display:
            txt = "%dft" % emax
            (x_size, y_size) = draw.textsize(txt)
            draw.text((int(x2-x_size/2), y2-y_size), txt)
            max_display = True
        elif edata[j]['alt'] == emin and not min_display:
            txt = "%dft" % emin
            (x_size, y_size) = draw.textsize(txt)
            draw.text((int(x2-x_size/2), y2), txt)
            min_display = True

    del draw

def avg_3_of_5(data):
    if len(data) == 0:
        retval = 0
    if len(data) < 5:
        retval = sum(data) / len(data)
    else:
        retval = (sum(data) - min(data) - max(data)) / (len(data) - 2)
    return retval

def curvature(tc):
    """
    Draw Curvature
    """
    bearing_threshold = 0

    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)

    y = int((im.size[1]-margin)*0.80)

    tangent_length = pixel_per_mile*0.02

    cdata = smooth_data(tc, mileage_threshold=0.010)

    # Check for empty list
    if len(cdata) == 0:
        return

    # loop over the list
    last_x = mile_to_pixel(tc, cdata[0]['mileage']-first)
    last_y = y
    last_i = 0
    for i in range(1, len(cdata)):
        bdiff = bearing_delta(cdata[i-1]['track'], cdata[i]['track'])
        if abs(bdiff) > 45:
            continue
        x = mile_to_pixel(tc, cdata[i]['mileage']-first)
        yval = y - bdiff
        #print(cdata[i]['mileage'],cdata[last_i]['track'], cdata[i]['track'],bdiff)
        draw.line((last_x,last_y,x,yval))
        draw.point((x, y))
        last_x = x
        last_y = yval
        last_i = i

    del draw

def accel(tc):
    """
    Draw Acceleration Data
    """
    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)

    yx = int((im.size[1]-margin)*0.10)
    yy = int((im.size[1]-margin)*0.18)
    yz = int((im.size[1]-margin)*0.26)
    ygx = int((im.size[1]-margin)*0.34)
    ygy = int((im.size[1]-margin)*0.42)
    ygz = int((im.size[1]-margin)*0.50)
    #ys = int((im.size[1]-margin)*0.58)
    
    ACCxp = [0] * im.size[0]
    ACCyp = [0] * im.size[0]
    ACCzp = [0] * im.size[0]
    GYRxp = [0] * im.size[0]
    GYRyp = [0] * im.size[0]
    GYRzp = [0] * im.size[0]

    scale = 1

    draw.text((margin, yx), "AX")
    draw.text((margin, yy), "AY")
    draw.text((margin, yz), "AZ")
    draw.text((margin, ygx), "GX")
    draw.text((margin, ygy), "GY")
    draw.text((margin, ygz), "GZ")
    #draw.text((margin, ys), "S")

    accel_threshold = 0.00

    mileage = None

    speed = 0

    last_x = None

    accel_file = open("accel.csv", "w")
    accel_file.write("mileage acc_x acc_y acc_z gyro_x gyro_y gyro_z\n")

    # Read from file
    for obj in tc['D']:
        print(obj)
        mileage = obj['mileage']
        if not(first <= mileage <= last):
            continue

        x = mile_to_pixel(tc, mileage-first)

        if obj['class'] == "G" or obj['class'] == "TPV":
            # Speed
            speed = obj['speed']
            #draw.point((x, ys-speed))
        elif obj['class'] == "A" or obj['class'] == "ATT":
            if speed == 0:
                #draw.point((x, yx))
                #draw.point((x, yy))
                #draw.point((x, yz))
                pass
            else:
                ACCx = (obj['acc_x'])
                if abs(ACCx) > ACCxp[x]:
                    ACCxp[x] = ACCx
                ACCy = (obj['acc_y'])
                if abs(ACCy) > ACCyp[x]:
                    ACCyp[x] = ACCy
                ACCz = (obj['acc_z'] - 9.80665)
                if abs(ACCz) > ACCzp[x]:
                    ACCzp[x] = ACCz
                GYRx = (obj['gyro_x'])
                if abs(GYRx) > GYRxp[x]:
                    GYRxp[x] = GYRx
                GYRy = (obj['gyro_y'])
                if abs(GYRy) > GYRyp[x]:
                    GYRyp[x] = GYRy
                GYRz = (obj['gyro_z'])
                if abs(GYRz) > GYRzp[x]:
                    GYRzp[x] = GYRz
                accel_file.write("%f %f %f %f %f %f %f\n" %( obj['mileage'], obj['acc_x'], obj['acc_y'], obj['acc_z'], obj['gyro_x'], obj['gyro_y'], obj['gyro_z']))

    for x in range(margin, len(ACCxp)-2*margin):
        draw.line((x,yx-scale*ACCxp[x],x-1,yx-scale*ACCxp[x-1]))
        draw.line((x,yy-scale*ACCyp[x],x-1,yy-scale*ACCyp[x-1]))
        draw.line((x,yz-scale*ACCzp[x],x-1,yz-scale*ACCzp[x-1]))
        draw.line((x,ygx-scale*GYRxp[x],x-1,ygx-scale*GYRxp[x-1]))
        draw.line((x,ygy-scale*GYRyp[x],x-1,ygy-scale*GYRyp[x-1]))
        draw.line((x,ygz-scale*GYRzp[x],x-1,ygz-scale*GYRzp[x-1]))

    accel_file.close()
    del draw

def sidings(tc):
    """
    Draw Siding
    """
    line_length = 10
    offset = 2
    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)

    y = int((im.size[1]-margin)*0.625)
    for obj in tc['G'].get_points(ktype='K', kclass='ST'):
        mileage = obj['mileage']
        if not (first <= mileage <= last):
            continue

        metadata = obj['metadata']

        start_x = mile_to_pixel(tc,mileage - first)
        end_x = mile_to_pixel(tc,metadata['end'] - first)
        y1 = y - pixel_per_mile * 0.01 * int(metadata['offset'])
        draw.line((start_x, y1, end_x, y1))

    del draw

def gage(tc):
    """
    Draw Gage
    """
    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)

    y = int((im.size[1]-margin)*0.34)
    draw.text((margin, y), aar.full_name)

    data = [0] * 360
    ghost = [0] * 360
    total_slope = total_slope_count = 0
    # Read from file
    for obj in tc['D']:
        if obj['class'] != "L":
            continue
        mileage = obj['mileage']
        if not(first <= mileage <= last):
            continue
        x = mile_to_pixel(tc, mileage-first)

        lidar_util.process_scan(obj['lidar'], data, ghost)

        new_data = lidar_util.convert_to_xy(data, offset=2.1528056371157285)

        gage,slope,p1,p2 = lidar_util.calc_gage(new_data)

        if not(aar.min_gauge <= gage <= aar.max_gauge):
            print(mileage, gage)
            draw.point((x,y+(gage-aar.standard_gauge)*2))
        else:
            #draw.point((x,y))
            pass
        total_slope += slope
        total_slope_count += 1

    if total_slope_count > 0:
        print(total_slope/total_slope_count)

    del draw
