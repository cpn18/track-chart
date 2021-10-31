"""
Track chart drawing methods
"""
import sys
import os
import math
import datetime
from PIL import Image, ImageDraw, ImageOps
import geo
import csv
import json
import gps_to_mileage
import dateutil.parser as dp
import lidar_util
import class_i as aar

import pirail

TIME_THRESHOLD = 3600 # seconds
MILEAGE_THRESHOLD = 0.005 # miles
STRING_WIDTH = 2 # pixels

AA = 0.40 # Complementary filter constant
MS_TO_MPH = 2.23694 # m/s to MPH

COLORS = {
    "black": (0,0,0),
    "red": (255,0,0),
    "green": (0,255,0),
    "blue": (0,0,255),
    "white": (255,255,255),
    "grey": (128,128,128),
    "orange": (255,165,0),
}

def new(args):
    """
    New Trackchart
    """
    (size, margin, first, last, known_file, data_file) = args
    pixel_per_mile = float(size[0]-3*margin) / (last-first)
    return {'image': Image.new("RGB", size, "white"),
            'margin': margin,
            'mileposts': (first, last, pixel_per_mile),
            'known_file': known_file,
            'data_file': data_file,
            'G': gps_to_mileage.Gps2Miles(known_file),
    }

def is_newer(file1, file2):
    stat1 = os.stat(file1)
    stat2 = os.stat(file2)
    return stat1.st_atime > stat2.st_atime

def draw_title(tc, title="PiRail"):
    im = tc['image']
    margin = tc['margin']
    draw = ImageDraw.Draw(im)
    (x_size, y_size) = draw.textsize(title)
    x = margin
    y = im.size[1] - y_size - 1
    draw.text((x, y), title)
    del draw

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
    d.text((1, 1), t, fill="white")
    return (ImageOps.invert(txt.rotate(degrees, expand=True)), x_size, y_size)

def border(tc):
    """
    Draw a page border
    """
    im = tc['image']
    margin = tc['margin']
    draw = ImageDraw.Draw(im)
    draw.line((margin, margin, im.size[0]-margin, margin),fill=COLORS['black'])
    draw.line((im.size[0]-margin, margin, im.size[0]-margin, im.size[1]-margin),fill=COLORS['black'])
    draw.line((im.size[0]-margin, im.size[1]-margin, margin, im.size[1]-margin),fill=COLORS['black'])
    draw.line((margin, im.size[1]-margin, margin, margin),fill=COLORS['black'])
    del draw

def milepost_symbol(draw, x, y_size, margin, name, alt_name):
    """
    Draw a milepost symbol
    """
    # Vertical
    draw.line((x, 2*margin, x, y_size*0.5),fill=COLORS['black'])
    draw.line((x, y_size*0.75, x, y_size),fill=COLORS['black'])
    # Diamond
    draw.line((x, margin, x+0.5*margin, 1.5*margin),fill=COLORS['black'])
    draw.line((x+0.5*margin, 1.5*margin, x, 2*margin),fill=COLORS['black'])
    draw.line((x, 2*margin, x-0.5*margin, 1.5*margin),fill=COLORS['black'])
    draw.line((x-0.5*margin, 1.5*margin, x, margin),fill=COLORS['black'])
    # Labels
    draw.text((x+0.5*margin, margin), name,fill=COLORS['black'])
    if alt_name is not None:
        draw.text((x-0.5*margin-draw.textsize(alt_name)[0], margin), alt_name,fill=COLORS['black'])

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
    draw.line((x1, y, x2, y), fill=COLORS['black'])

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
            draw.line((x-5, y, x+5, y), fill=COLORS['white'])
            draw.line((x, y-margin, x, y+margin), fill=COLORS['black'])
        elif xtype == 'O':
            # Draw overpass
            draw.line((x, y-margin, x, y-5), fill=COLORS['black'])
            draw.line((x, y+5, x, y+margin), fill=COLORS['black'])
        elif xtype == 'X':
            # Draw road
            draw.line((x, y-margin, x, y+margin), fill=COLORS['black'])

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
            draw.line((x, y1, x, y1+2),fill=COLORS['black'])
            draw.line((x, y1+7, x, y1+10),fill=COLORS['black'])
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
                         ), fill=COLORS['black'], outline=COLORS['black'])

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
        draw.text((int(x-x_size/2), int(y1)), text, fill=COLORS['black'])
        y1 += y_size
        m_str = mileage_to_string(mileage)
        (x_size, y_size) = draw.textsize(m_str)
        draw.text((int(x-x_size/2), int(y1)), m_str, fill=COLORS['black'])

        # Survey Station
        if 'survey' in metadata: 
            survey_station = metadata['survey']
            (w, x_size, y_size) = rotated_text(draw, survey_station, 90)
            im.paste(w, ((x-y_size-3, im.size[1]-margin-x_size)))

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
        if 'label' in metadata:
            label = metadata['label']

        if not(first <= mileage <= last):
            continue

        x = mile_to_pixel(tc, mileage-first)

        (x_size1, y_size1) = draw.textsize(label)
        m_str = mileage_to_string(mileage)
        (x_size2, y_size2) = draw.textsize(m_str)

        if metadata['offset'] > 0:
            # Above the mainline
            draw.line((x, y-offset, x, y-offset-line_length),fill=COLORS['black'])
            y1 = y-metadata['offset']-line_length-y_size1-y_size2
        else:
            # Below the mainline
            draw.line((x, y+offset, x, y+offset+line_length),fill=COLORS['black'])
            y1 = y+metadata['offset']+line_length

        # Draw description
        draw.text((int(x-x_size1/2), int(y1)), label,fill=COLORS['black'])
        draw.text((int(x-x_size2/2), int(y1+y_size1)), m_str,fill=COLORS['black'])
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

        draw.line((x, y_start, x_end, y_end),fill=COLORS['black'])
    del draw

def smooth_data(tc, input_data=None, mileage_threshold=0.01, track_threshold=45, write_file=True):
    (first, last, pixel_per_mile) = tc['mileposts']

    data = []
    used = 0
    for line_no, obj in pirail.read(tc['data_file'], classes=['TPV'], args={
            'start-mileage': first,
            'end-mileage': last,
        }):

        if obj['num_used'] < pirail.GPS_THRESHOLD:
            continue

        try:
            data.append(obj)
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
                #print("Inserted: %f @ %d" % (d,b))
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

    #print("Smooth=%d" % len(smooth_data))
    return smooth_data

def string_chart_by_time(tc):
    """
    Draw a string chart
    x = mileage
    y = time
    """
    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)

    mintime = None
    maxtime = None
    timedata = []
    skip = False
    lastm = None
    speed = 0
    for line_no, obj in pirail.read(tc['data_file'], classes=['TPV'], args={
            'start-mileage': first,
            'end-mileage': last,
        }):
 
        if obj['num_used'] < pirail.GPS_THRESHOLD:
            continue
        #if obj['speed'] < obj['eps']:
        #    if skip:
        #        continue
        #    skip = True
        #else:
        #    skip = False
        mileage = obj['mileage']
        objtime = pirail.parse_time(obj['time'])
        speed = obj['speed']
        if mintime is None or objtime < mintime:
            mintime = objtime
        if maxtime is None or objtime > maxtime:
            maxtime = objtime
        if lastm is None or abs(mileage - lastm) >= MILEAGE_THRESHOLD:
            timedata.append({
                'time': objtime,
                'mileage': mileage,
                'speed': speed,
            })
            lastm = mileage

    timedata = sorted(timedata, key=lambda k: k['time'], reverse=False)

    lastx = lasty = lasttime = None
    for obj in timedata:
        mileage = obj['mileage']
        objtime = obj['time']
        speed = obj['speed'] * MS_TO_MPH
        x = mile_to_pixel(tc, mileage-first)
        y = (im.size[1]-2*margin) * (objtime - mintime).total_seconds() / (maxtime-mintime).total_seconds() + margin

        if lasttime is None:
            timediff = 0
        else:
            timediff = (objtime - lasttime).total_seconds()

        if speed > 25:
            color=COLORS['red']
        elif speed > 15:
            color=COLORS['orange']
        elif speed > 5:
            color=COLORS['green']
        else:
            color=COLORS['blue']

        if lastx is None or timediff > TIME_THRESHOLD:
            draw.point((x, y), fill=color)
        else:
            draw.line((lastx, lasty, x, y), fill=color, width=STRING_WIDTH)

        lastx = x
        lasty = y
        lasttime = objtime
        lastm = mileage

    for hour in range(mintime.hour, maxtime.hour+1):
        objtime = datetime.datetime(mintime.year, mintime.month, mintime.day, hour, 0, 0)
        x = 10
        y = (im.size[1]-2*margin) * (objtime - mintime).total_seconds() / (maxtime-mintime).total_seconds() + margin
        draw.text((x, y), "%d:00Z" % hour, fill=COLORS['blue'])

    del draw

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
        draw.line((x1, y1, x2, y2),fill=COLORS['black'])
        if edata[j]['alt'] == emax and not max_display:
            txt = "%dft" % emax
            (x_size, y_size) = draw.textsize(txt)
            draw.text((int(x2-x_size/2), y2-y_size), txt, fill=COLORS['black'])
            max_display = True
        elif edata[j]['alt'] == emin and not min_display:
            txt = "%dft" % emin
            (x_size, y_size) = draw.textsize(txt)
            draw.text((int(x2-x_size/2), y2), txt, fill=COLORS['black'])
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
        draw.line((last_x,last_y,x,yval),fill=COLORS['black'])
        draw.point((x, y), fill=COLORS['black'])
        last_x = x
        last_y = yval
        last_i = i

    del draw

def plot_value(tc, field="acc_z", scale=1):
    """
    Draw Random Data
    """
    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)

    yz = int((im.size[1]-margin)*0.26)
    data = [None] * im.size[0]
    draw.text((margin, yz), field.upper(), fill=COLORS['black'])

    # Read from file
    data_sum = data_count = 0
    for line_no, obj in pirail.read(tc['data_file'], classes=["ATT"]):
        data_sum += obj[field]
        data_count += 1
    # Normalize data by subtracting the average
    data_avg = data_sum / data_count

    # Read from file again
    for line_no, obj in pirail.read(tc['data_file'], classes=["TPV", "ATT"], args={
            'start-mileage': first,
            'end-mileage': last,
        }):
        mileage = obj['mileage']
        x = mile_to_pixel(tc, mileage-first)
        if obj['class'] == "TPV":
            speed = obj['speed']
            eps = obj['eps']
        elif obj['class'] == "ATT":
            if speed < eps:
                pass
            else:
                data_point = obj[field] - data_avg
                # Look for maximum magnitude
                if data[x] is None or abs(data_point) > abs(data[x]):
                    data[x] = data_point

    # Plot the data
    last_x = None
    for x in range(margin, im.size[0]-2*margin):
        draw.point((x,yz), fill=COLORS['black'])
        if data[x] is None:
            continue
        y = yz-scale*data[x]
        if last_x is None:
            draw.point((x,y), fill=COLORS['red'])
        else:
            draw.line((x,y,last_x,last_y), fill=COLORS['red'])
        last_x = x
        last_y = y

    del draw

def accel(tc, scale=1):
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
    ys = int((im.size[1]-margin)*0.58)
    
    ACCxp = [0] * im.size[0]
    ACCyp = [0] * im.size[0]
    ACCzp = [0] * im.size[0]
    GYRxp = [0] * im.size[0]
    GYRyp = [0] * im.size[0]
    GYRzp = [0] * im.size[0]

    draw.text((margin, yx), "AX", fill=COLORS['red'])
    draw.text((margin, yy), "AY", fill=COLORS['blue'])
    draw.text((margin, yz), "AZ", fill=COLORS['green'])
    draw.text((margin, ygx), "GX", fill=COLORS['red'])
    draw.text((margin, ygy), "GY", fill=COLORS['blue'])
    draw.text((margin, ygz), "GZ", fill=COLORS['green'])
    #draw.text((margin, ys), "S", fill=COLORS['black'])

    accel_threshold = 0.00

    mileage = None

    speed = 0

    last_x = None

    accel_file = open("accel.csv", "w")
    accel_file.write("mileage acc_x acc_y acc_z gyro_x gyro_y gyro_z\n")

    # Read from file
    for line_no, obj in pirail.read(tc['data_file'], args={
            'start-mileage': first,
            'end-mileage': last,
        }):
        #print(obj)
        mileage = obj['mileage']

        x = mile_to_pixel(tc, mileage-first)

        if obj['class'] == "G" or obj['class'] == "TPV":
            # Speed
            speed = obj['speed']
            #draw.point((x, ys-speed), fill=COLORS['black'])
        elif obj['class'] in ["A", "ATT"]:
            if speed == 100:
                #draw.point((x, yx), fill=COLORS['black'])
                #draw.point((x, yy), fill=COLORS['black'])
                #draw.point((x, yz), fill=COLORS['black'])
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
        draw.line((x,yx-scale*ACCxp[x],x-1,yx-scale*ACCxp[x-1]),fill=COLORS['red'])
        draw.line((x,yy-scale*ACCyp[x],x-1,yy-scale*ACCyp[x-1]),fill=COLORS['blue'])
        draw.line((x,yz-scale*ACCzp[x],x-1,yz-scale*ACCzp[x-1]),fill=COLORS['green'])
        draw.line((x,ygx-scale*GYRxp[x],x-1,ygx-scale*GYRxp[x-1]),fill=COLORS['red'])
        draw.line((x,ygy-scale*GYRyp[x],x-1,ygy-scale*GYRyp[x-1]),fill=COLORS['blue'])
        draw.line((x,ygz-scale*GYRzp[x],x-1,ygz-scale*GYRzp[x-1]),fill=COLORS['green'])

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
        draw.line((start_x, y1, end_x, y1),fill=COLORS['black'])

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
    draw.text((margin, y), aar.full_name, fill=COLORS['black'])

    data = [0] * 360
    ghost = [0] * 360
    total_slope = total_slope_count = 0
    # Read from file
    for line_no, obj in pirail(tc['data_file']):
        if obj['class'] not in ["LIDAR", "L"]:
            continue
        mileage = obj['mileage']
        if not(first <= mileage <= last):
            continue
        x = mile_to_pixel(tc, mileage-first)

        lidar_util.process_scan(obj['lidar'], data, ghost)

        new_data = lidar_util.convert_to_xy(data, offset=2.1528056371157285)

        gage,slope,p1,p2 = lidar_util.calc_gage(new_data)

        if not(aar.min_gauge <= gage <= aar.max_gauge):
            #print(mileage, gage)
            draw.point((x,y+(gage-aar.standard_gauge)*2),fill=COLORS['red'])
        else:
            #draw.point((x,y), fill=COLORS['black'])
            pass
        total_slope += slope
        total_slope_count += 1

    if total_slope_count > 0:
        #print(total_slope/total_slope_count)
        pass

    del draw
