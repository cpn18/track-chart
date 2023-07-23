"""
Track chart drawing methods
"""
import math
import datetime
from PIL import Image, ImageDraw, ImageOps
import geo
import gps_to_mileage
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

def draw_title(track_chart, title=None):
    """
    Draw the title
    """
    image = track_chart['image']
    margin = track_chart['margin']
    draw = ImageDraw.Draw(image)
    if title is None:
        title = datetime.datetime.now().strftime("PiRail %Y-%m-%d")
    (_x_size, y_size) = draw.textsize(title)
    xpixel = margin
    ypixel = image.size[1] - y_size - 1
    draw.text((xpixel, ypixel), title, fill=COLORS['black'])
    del draw

def mile_to_pixel(track_chart, mileage):
    """
    Convert mileage to pixel value
    """
    margin = track_chart['margin']
    (_first, _last, pixel_per_mile) = track_chart['mileposts']
    return int(1.5*margin+mileage*pixel_per_mile+0.5)

def mileage_to_string(obj):
    """
    Format a mileage
    """
    mileage = float(obj['mileage'])
    if 'mileage_offset' in obj['metadata']:
        mileage -= obj['metadata']['mileage_offset']
    return "%0.2f" % mileage

def bearing_delta(bearing1, bearing2):
    """
    Calculate diffence in bearings
    """
    delta = (bearing2 - bearing1)
    if delta > 180:
        delta -= 360
    elif delta < -180:
        delta += 360
    return delta

def rotated_text(draw, text, degrees):
    """
    Rotate Text
    """
    (x_size, y_size) = draw.textsize(text)
    txt_image = Image.new("L", (x_size+2, y_size+2), "black")
    drawable = ImageDraw.Draw(txt_image)
    drawable.text((1, 1), text, fill="white")
    return (ImageOps.invert(txt_image.rotate(degrees, expand=True)), x_size, y_size)

def survey_station(image, draw, xpixel, margin, metadata):
    """
    Draw Survey Station Text
    """
    if 'survey' in metadata:
        survey = metadata['survey']
        (survey_image, x_size, y_size) = rotated_text(draw, survey, 90)
        image.paste(survey_image, ((int(xpixel-y_size/2), image.size[1]-margin-x_size)))

def border(track_chart):
    """
    Draw a page border
    """
    image = track_chart['image']
    margin = track_chart['margin']
    draw = ImageDraw.Draw(image)
    draw.line((margin, margin, image.size[0]-margin, margin),fill=COLORS['black'])
    draw.line((image.size[0]-margin, margin, image.size[0]-margin, image.size[1]-margin),fill=COLORS['black'])
    draw.line((image.size[0]-margin, image.size[1]-margin, margin, image.size[1]-margin),fill=COLORS['black'])
    draw.line((margin, image.size[1]-margin, margin, margin),fill=COLORS['black'])
    del draw

def milepost_symbol(draw, xpixel, y_size, margin, obj):
    """
    Draw a milepost symbol
    """
    name = obj['metadata']['name']
    alt_name = obj['metadata'].get('alt_name', None)

    # Vertical
    draw.line((xpixel, 2*margin, xpixel, y_size*0.5),fill=COLORS['black'])
    draw.line((xpixel, y_size*0.75, xpixel, y_size),fill=COLORS['black'])
    # Diamond
    draw.line((xpixel, margin, xpixel+0.5*margin, 1.5*margin),fill=COLORS['black'])
    draw.line((xpixel+0.5*margin, 1.5*margin, xpixel, 2*margin),fill=COLORS['black'])
    draw.line((xpixel, 2*margin, xpixel-0.5*margin, 1.5*margin),fill=COLORS['black'])
    draw.line((xpixel-0.5*margin, 1.5*margin, xpixel, margin),fill=COLORS['black'])
    # Labels
    draw.text((xpixel+0.5*margin, margin), name,fill=COLORS['black'])
    if alt_name is not None:
        draw.text((xpixel-0.5*margin-draw.textsize(alt_name)[0], margin), alt_name,fill=COLORS['black'])

def mileposts(track_chart, from_file=False, mod=1):
    """
    Draw mileposts
    """
    image = track_chart['image']
    margin = track_chart['margin']
    (first, last, _pixel_per_mile) = track_chart['mileposts']

    draw = ImageDraw.Draw(image)

    mp_list = []
    if from_file:
        # Read Mileposts from file
        for obj in track_chart['G'].get_points(ktype='K', kclass='MP'):
            mp_list.append(obj)
    else:
        # Create Milepost Listing
        for mileage in range(int(first), int(last+1)):
            mp_list.append({
                'mileage': mileage,
                'metadata': {
                    'name': "MP%d" % mileage,
                    'alt_name': None,
                }
            })

    # Filter and draw the mileposts
    post_count = 0
    for obj in mp_list:
        mileage = obj['mileage']
        if not first <= mileage <= last:
            continue

        post_count += 1

        if post_count % mod != 0:
            continue

        xpixel = mile_to_pixel(track_chart, mileage-first)

        milepost_symbol(
            draw,
            xpixel,
            (image.size[1]-margin),
            margin,
            obj
        )

        # Survey Station
        survey_station(image, draw, xpixel, margin, obj['metadata'])

    del draw

def mainline(track_chart):
    """
    Draw mainline
    """
    image = track_chart['image']
    margin = track_chart['margin']
    (first, last, _pixel_per_mile) = track_chart['mileposts']
    draw = ImageDraw.Draw(image)
    ypixel = (image.size[1]-margin)*0.625
    start = end = None

    for obj in track_chart['G'].get_points(ktype='K', kclass='E'):
        mileage = obj['mileage']

        if start is None or mileage < start:
            start = mileage
        if end is None or mileage > end:
            end = mileage

    if start is None or start < first:
        start = first
    if end is None or end > last:
        end = last

    xpixel1 = max(margin, mile_to_pixel(track_chart, start-first))
    xpixel2 = min(image.size[0] - margin, mile_to_pixel(track_chart, end-first))
    draw.line((xpixel1, ypixel, xpixel2, ypixel), fill=COLORS['black'])

    del draw

def bridges_and_crossings(track_chart, xing_type=None):
    """
    Draw bridges and crossings
    """
    image = track_chart['image']
    margin = track_chart['margin']
    (first, last, _pixel_per_mile) = track_chart['mileposts']
    draw = ImageDraw.Draw(image)

    ypixel = int((image.size[1]-margin)*0.625)
    for obj in track_chart['G'].get_points(ktype='K'):
        mileage = obj['mileage']
        xtype = obj['class']
        metadata = obj['metadata']

        if not first <= mileage <= last or xtype not in ['U', 'O', 'X']:
            continue

        if xing_type is not None and xtype != xing_type:
            continue

        # Angled crossings
        offset = margin * math.tan(math.radians(90 - metadata.get('angle', 90)))
        if (last - first) > 1:
            offset /= last - first

        # Get X based on mileage
        xpixel = mile_to_pixel(track_chart, mileage-first)

        if xtype == 'U':
            # Draw underpass
            draw.line((xpixel-5, ypixel, xpixel+5, ypixel), fill=COLORS['white'])
            draw.line((xpixel-offset, ypixel-margin, xpixel+offset, ypixel+margin), fill=COLORS['black'])
        elif xtype == 'O':
            # Draw overpass
            draw.line((xpixel-offset, ypixel-margin, xpixel, ypixel-5), fill=COLORS['black'])
            draw.line((xpixel, ypixel+5, xpixel+offset, ypixel+margin), fill=COLORS['black'])
        elif xtype == 'X':
            # Draw road
            draw.line((xpixel-offset, ypixel-margin, xpixel+offset, ypixel+margin), fill=COLORS['black'])

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
            description = ("%s %s" % (mileage_to_string(obj), text)).strip()
            (text_image, x_size, y_size) = rotated_text(draw, description, 90)
            image.paste(text_image, (int(xpixel-y_size/2), int(ypixel-1.5*margin-x_size)))

        # Survey Station
        survey_station(image, draw, xpixel, margin, metadata)

    del draw

def townlines(track_chart):
    """
    Draw townlines
    """
    image = track_chart['image']
    margin = track_chart['margin']
    (first, last, _pixel_per_mile) = track_chart['mileposts']
    draw = ImageDraw.Draw(image)

    ypixel = int((image.size[1]-margin)*0.5)
    for obj in track_chart['G'].get_points(ktype='K', kclass='TL'):
        mileage = obj['mileage']
        metadata = obj['metadata']
        if not first <= mileage <= last:
            continue

        xpixel = mile_to_pixel(track_chart, mileage-first)

        # Town 1
        description = metadata['name'].split("/")[0]
        (text_image, x_size1, y_size1) = rotated_text(draw, description, 90)
        image.paste(text_image, (int(xpixel-y_size1-3), int(ypixel-(x_size1/2))))
        # Town 2
        description = metadata['name'].split("/")[1]
        (text_image, x_size2, _y_size2) = rotated_text(draw, description, 90)
        image.paste(text_image, (int(xpixel), int(ypixel-(x_size2/2))))
        # Dashed Town Line
        if x_size2 > x_size1:
            x_size1 = x_size2
        x_size1 = int(math.ceil(x_size1/10.0)*10)
        for ypixel1 in range(int(ypixel-x_size1/2), int(ypixel+x_size1/2), 10):
            draw.line((xpixel, ypixel1, xpixel, ypixel1+2),fill=COLORS['black'])
            draw.line((xpixel, ypixel1+7, xpixel, ypixel1+10),fill=COLORS['black'])
    del draw

def stations(track_chart):
    """
    Draw Stations
    """
    box_size = 10
    offset = 2
    image = track_chart['image']
    margin = track_chart['margin']
    (first, last, pixel_per_mile) = track_chart['mileposts']
    draw = ImageDraw.Draw(image)

    ypixel = int((image.size[1]-margin)*0.625)
    for obj in track_chart['G'].get_points(ktype='K', kclass='S'):
        mileage = obj['mileage']
        metadata = obj['metadata']
        if not first <= mileage <= last:
            continue

        xpixel = mile_to_pixel(track_chart, mileage-first)
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
            draw.polygon((xpixel-box_size/2, ypixel-offset,
                          xpixel-box_size/2, ypixel-offset-box_size,
                          xpixel, ypixel-offset-1.5*box_size,
                          xpixel+box_size/2, ypixel-offset-box_size,
                          xpixel+box_size/2, ypixel-offset
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

        ypixel1 = int((image.size[1]-margin)*0.7)
        (x_size, y_size) = draw.textsize(text)
        draw.text((int(xpixel-x_size/2), int(ypixel1)), text, fill=COLORS['black'])
        ypixel1 += y_size
        m_str = mileage_to_string(obj)
        (x_size, y_size) = draw.textsize(m_str)
        draw.text((int(xpixel-x_size/2), int(ypixel1)), m_str, fill=COLORS['black'])

        # Survey Station
        survey_station(image, draw, xpixel, margin, metadata)

    del draw

def yardlimits(track_chart):
    """
    Draw Yardlimits
    """
    line_length = 10
    offset = 2
    image = track_chart['image']
    margin = track_chart['margin']
    (first, last, _pixel_per_mile) = track_chart['mileposts']
    draw = ImageDraw.Draw(image)

    ypixel = int((image.size[1]-margin)*0.625)
    for obj in track_chart['G'].get_points(ktype='K', kclass='YL'):
        label = obj['class']
        mileage = obj['mileage']
        metadata = obj['metadata']
        if 'label' in metadata:
            label = metadata['label']

        if not first <= mileage <= last:
            continue

        xpixel = mile_to_pixel(track_chart, mileage-first)

        (x_size1, y_size1) = draw.textsize(label)
        m_str = mileage_to_string(obj)
        (x_size2, y_size2) = draw.textsize(m_str)

        if metadata['offset'] > 0:
            # Above the mainline
            draw.line((xpixel, ypixel-offset, xpixel, ypixel-offset-line_length),fill=COLORS['black'])
            ypixel1 = ypixel-metadata['offset']-line_length-y_size1-y_size2
        else:
            # Below the mainline
            draw.line((xpixel, ypixel+offset, xpixel, ypixel+offset+line_length),fill=COLORS['black'])
            ypixel1 = ypixel+metadata['offset']+line_length

        # Draw description
        draw.text((int(xpixel-x_size1/2), int(ypixel1)), label,fill=COLORS['black'])
        draw.text((int(xpixel-x_size2/2), int(ypixel1+y_size1)), m_str,fill=COLORS['black'])
    del draw

def controlpoints(track_chart):
    """
    Draw Control Points
    """
    image = track_chart['image']
    margin = track_chart['margin']
    (first, last, pixel_per_mile) = track_chart['mileposts']
    draw = ImageDraw.Draw(image)

    ypixel = int((image.size[1]-margin)*0.625)
    for obj in track_chart['G'].get_points(ktype='K'):
        label = obj['class']
        if label not in ['CRF', 'CRT', 'CLF', 'CLT']:
            continue
        mileage = obj['mileage']
        metadata = obj['metadata']

        #print(obj)

        if not first <= mileage <= last:
            continue

        xpixel = mile_to_pixel(track_chart, mileage-first)
        y_start = ypixel
        y_size = 0.01 * pixel_per_mile
        start_offset = metadata['start']
        end_offset = metadata['end']

        if start_offset > 0:
            # above the mainline
            y_start = ypixel - start_offset*y_size
        elif start_offset < 0:
            # below the mainline
            y_start = ypixel - start_offset*y_size

        if label[2] == 'F':
            if label[1] == 'R':
                y_end = y_start - end_offset*y_size
                x_end = xpixel + abs(end_offset)*y_size
            else:
                y_end = y_start - end_offset*y_size
                x_end = xpixel + abs(end_offset)*y_size
        else:
            if label[1] == 'R':
                y_end = y_start - end_offset*y_size
                x_end = xpixel - abs(end_offset)*y_size
            else:
                y_end = y_start - end_offset*y_size
                x_end = xpixel - abs(end_offset)*y_size

        draw.line((xpixel, y_start, x_end, y_end),fill=COLORS['black'])
    del draw

def smooth_data(track_chart, mileage_threshold=0.01, write_file=True):
    """
    Smooth Data
    """
    (first, last, _pixel_per_mile) = track_chart['mileposts']

    data = []
    for _line_no, obj in pirail.read(track_chart['data_file'], classes=['TPV'], args={
            'start-mileage': first,
            'end-mileage': last,
        }):

        try:
            data.append(obj)
        except KeyError as ex:
            print("skipped", ex, obj)

    # Ensure the list is sorted by mileage
    data = sorted(data, key=lambda k: k['mileage'], reverse=False)

    # smooth, looking at all measurements +/-
    smoothed_data = []
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
        new_lat = pirail.avg_3_of_5(lat)
        new_lon = pirail.avg_3_of_5(lon)
        new_alt = pirail.avg_3_of_5(alt)
        mileage, certainty = track_chart['G'].find_mileage(new_lat, new_lon)
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
            smoothed_data.append(obj)
            last_obj = obj
        else:
            distance = geo.great_circle(last_obj['lat'], last_obj['lon'],
                                 obj['lat'], obj['lon'])
            bearing = geo.bearing(last_obj['lat'], last_obj['lon'],
                            obj['lat'], obj['lon'])

            if distance > mileage_threshold:
                #print("Inserted: %f @ %d" % (distance,bearing))
                smoothed_data.append(obj)
                last_obj = obj

    # Ensure we're still sorted
    smoothed_data = sorted(smoothed_data, key=lambda k: k['mileage'], reverse=False)

    for i in range(1,len(smoothed_data)):
        bearing = geo.bearing(smoothed_data[i-1]['lat'], smoothed_data[i-1]['lon'],
                        smoothed_data[i]['lat'], smoothed_data[i]['lon'])
        smoothed_data[i]['track'] = bearing
    if len(smoothed_data) > 2:
        smoothed_data[0]['track'] = smoothed_data[1]['track']

    # save result
    if write_file:
        with open("smoothdata_tmp.csv", "w") as smoothfile:
            smoothfile.write("Mileage,Latitude,Longitude,Altitude,Track\n")
            for obj in smoothed_data:
                smoothfile.write("%f %f %f %f %f\n" % (
                        obj['mileage'],
                        obj['lat'],
                        obj['lon'],
                        obj['alt'],
                        obj['track'],
                        ))

    #print("Smooth=%d" % len(smoothed_data))
    return smoothed_data

def string_chart_by_time(track_chart):
    """
    Draw a string chart
    x = mileage
    y = time
    """
    image = track_chart['image']
    margin = track_chart['margin']
    (first, last, _pixel_per_mile) = track_chart['mileposts']
    draw = ImageDraw.Draw(image)

    mintime = None
    maxtime = None
    timedata = []
    lastm = None
    speed = 0
    for _line_no, obj in pirail.read(track_chart['data_file'], classes=['TPV'], args={
            'start-mileage': first,
            'end-mileage': last,
        }):

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
        xpixel = mile_to_pixel(track_chart, mileage-first)
        ypixel = (image.size[1]-2*margin) * (objtime - mintime).total_seconds() / (maxtime-mintime).total_seconds() + margin

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
            draw.point((xpixel, ypixel), fill=color)
        else:
            draw.line((lastx, lasty, xpixel, ypixel), fill=color, width=STRING_WIDTH)

        lastx = xpixel
        lasty = ypixel
        lasttime = objtime
        lastm = mileage

    if mintime is not None:
        for hour in range(mintime.hour, maxtime.hour+1):
            objtime = datetime.datetime(mintime.year, mintime.month, mintime.day, hour, 0, 0)
            xpixel = 10
            ypixel = (image.size[1]-2*margin) * (objtime - mintime).total_seconds() / (maxtime-mintime).total_seconds() + margin
            draw.text((xpixel, ypixel), "%d:00Z" % hour, fill=COLORS['blue'])

    del draw

def elevation(track_chart):
    """
    Draw Elevation profile
    """
    image = track_chart['image']
    margin = track_chart['margin']
    (first, _last, _pixel_per_mile) = track_chart['mileposts']
    draw = ImageDraw.Draw(image)

    ypixel = int((image.size[1]-margin))
    y_range = 200

    edata = smooth_data(track_chart, mileage_threshold=0.01)

    # Check for empty list
    if len(edata) == 0:
        return

    emin = emax = edata[0]['alt']
    for i in range(1,len(edata)):
        emin = min(emin, edata[i]['alt'])
        emax = max(emax, edata[i]['alt'])

    # baseline
    #draw.text((int(1.5*margin), image.size[1]-margin), "Base = %d" % emin)
    #draw.line((margin, image.size[1]-margin, image.size[0]-margin, image.size[1]-margin))

    # loop over the list
    min_display = max_display = False
    for j in range(1, len(edata)):
        xpixel1 = mile_to_pixel(track_chart, edata[j-1]['mileage']-first)
        xpixel2 = mile_to_pixel(track_chart, edata[j]['mileage']-first)
        ypixel1 = ypixel - (edata[j-1]['alt'] - emin) * (y_range/emax)
        ypixel2 = ypixel - (edata[j]['alt'] - emin) * (y_range/emax)
        draw.line((xpixel1, ypixel1, xpixel2, ypixel2),fill=COLORS['black'])
        if edata[j]['alt'] == emax and not max_display:
            txt = "%dft" % emax
            (x_size, y_size) = draw.textsize(txt)
            draw.text((int(xpixel2-x_size/2), ypixel2-y_size), txt, fill=COLORS['black'])
            max_display = True
        elif edata[j]['alt'] == emin and not min_display:
            txt = "%dft" % emin
            (x_size, y_size) = draw.textsize(txt)
            draw.text((int(xpixel2-x_size/2), ypixel2), txt, fill=COLORS['black'])
            min_display = True

    del draw

def curvature(track_chart):
    """
    Draw Curvature
    """
    image = track_chart['image']
    margin = track_chart['margin']
    (first, _last, _pixel_per_mile) = track_chart['mileposts']
    draw = ImageDraw.Draw(image)

    ypixel = int((image.size[1]-margin)*0.80)

    cdata = smooth_data(track_chart, mileage_threshold=0.010)

    # Check for empty list
    if len(cdata) == 0:
        return

    # loop over the list
    last_x = mile_to_pixel(track_chart, cdata[0]['mileage']-first)
    last_y = ypixel
    for i in range(1, len(cdata)):
        bdiff = bearing_delta(cdata[i-1]['track'], cdata[i]['track'])
        if abs(bdiff) > 45:
            continue
        xpixel = mile_to_pixel(track_chart, cdata[i]['mileage']-first)
        yval = ypixel - bdiff
        draw.line((last_x,last_y,xpixel,yval),fill=COLORS['black'])
        draw.point((xpixel, ypixel), fill=COLORS['black'])
        last_x = xpixel
        last_y = yval

    del draw

def plot_value(track_chart, field="acc_z", scale=1):
    """
    Draw Random Data
    """
    image = track_chart['image']
    margin = track_chart['margin']
    (first, last, _pixel_per_mile) = track_chart['mileposts']
    draw = ImageDraw.Draw(image)

    yzpixel = int((image.size[1]-margin)*0.26)
    data = [None] * image.size[0]
    draw.text((margin, yzpixel), field.upper(), fill=COLORS['black'])

    # Read from file
    data_sum = data_count = 0
    for _line_no, obj in pirail.read(track_chart['data_file'], classes=["ATT"]):
        data_sum += obj[field]
        data_count += 1
    # Normalize data by subtracting the average
    data_avg = data_sum / data_count

    speed = eps = 0
    # Read from file again
    for _line_no, obj in pirail.read(track_chart['data_file'], classes=["TPV", "ATT"], args={
            'start-mileage': first,
            'end-mileage': last,
        }):
        mileage = obj['mileage']
        xpixel = mile_to_pixel(track_chart, mileage-first)
        if obj['class'] == "TPV":
            speed = obj['speed']
            eps = obj['eps']
        elif obj['class'] == "ATT":
            if speed < eps:
                pass
            else:
                data_point = obj[field] - data_avg
                # Look for maximum magnitude
                if data[xpixel] is None or abs(data_point) > abs(data[xpixel]):
                    data[xpixel] = data_point

    # Plot the data
    last_x = None
    for xpixel in range(margin, image.size[0]-2*margin):
        draw.point((xpixel,yzpixel), fill=COLORS['black'])
        if data[xpixel] is None:
            continue
        ypixel = yzpixel-scale*data[xpixel]
        if last_x is None:
            draw.point((xpixel,ypixel), fill=COLORS['red'])
        else:
            draw.line((xpixel,ypixel,last_x,last_y), fill=COLORS['red'])
        last_x = xpixel
        last_y = ypixel

    del draw

def accel(track_chart, scale=1, drawables=None):
    """
    Draw Acceleration Data
    """
    image = track_chart['image']
    margin = track_chart['margin']
    (first, last, _pixel_per_mile) = track_chart['mileposts']
    draw = ImageDraw.Draw(image)

    yxpixel = int((image.size[1]-margin)*0.10)
    yypixel = int((image.size[1]-margin)*0.18)
    yzpixel = int((image.size[1]-margin)*0.26)
    ygxpixel = int((image.size[1]-margin)*0.34)
    ygypixel = int((image.size[1]-margin)*0.42)
    ygzpixel = int((image.size[1]-margin)*0.50)
    yspixel = int((image.size[1]-margin)*0.58)

    acc_xp = [0] * image.size[0]
    acc_yp = [0] * image.size[0]
    acc_zp = [0] * image.size[0]
    gyro_xp = [0] * image.size[0]
    gyro_yp = [0] * image.size[0]
    gyro_zp = [0] * image.size[0]

    # default is plot acc_z and gryo_y
    if drawables is None:
        drawables = ['acc_z', 'gyro_y']

    if 'acc_x' in drawables:
        draw.text((margin, yxpixel), "ACC_X", fill=COLORS['red'])
    if 'acc_y' in drawables:
        draw.text((margin, yypixel), "ACC_Y", fill=COLORS['blue'])
    if 'acc_z' in drawables:
        draw.text((margin, yzpixel), "ACC_Z", fill=COLORS['green'])
    if 'gyro_x' in drawables:
        draw.text((margin, ygxpixel), "GYRO_X", fill=COLORS['red'])
    if 'gyro_y' in drawables:
        draw.text((margin, ygypixel), "GYRO_Y", fill=COLORS['blue'])
    if 'gypo_z' in drawables:
        draw.text((margin, ygzpixel), "GYRO_Z", fill=COLORS['green'])
    if 'speed' in drawables:
        draw.text((margin, yspixel), "SPEED", fill=COLORS['black'])

    mileage = None

    speed = 0

    with open("accel.csv", "w") as accel_file:
        accel_file.write("mileage acc_x acc_y acc_z gyro_x gyro_y gyro_z\n")

        # Read from file
        for _line_no, obj in pirail.read(track_chart['data_file'], args={
                'start-mileage': first,
                'end-mileage': last,
            }):
            #print(obj)
            mileage = obj['mileage']

            xpixel = mile_to_pixel(track_chart, mileage-first)

            if obj['class'] == "G" or obj['class'] == "TPV":
                # Speed
                speed = obj.get('speed', 0)
                if 'speed' in drawables:
                    draw.point((xpixel, yspixel-speed), fill=COLORS['black'])
            elif obj['class'] in ["A", "ATT"]:
                if speed == 100:
                    if 'speed' in drawables:
                        draw.point((xpixel, yxpixel), fill=COLORS['black'])
                        draw.point((xpixel, yypixel), fill=COLORS['black'])
                        draw.point((xpixel, yzpixel), fill=COLORS['black'])
                else:
                    acc_x = (obj['acc_x'])
                    if abs(acc_x) > acc_xp[xpixel]:
                        acc_xp[xpixel] = acc_x
                    acc_y = (obj['acc_y'])
                    if abs(acc_y) > acc_yp[xpixel]:
                        acc_yp[xpixel] = acc_y
                    acc_z = (obj['acc_z'] - 9.80665)
                    if abs(acc_z) > acc_zp[xpixel]:
                        acc_zp[xpixel] = acc_z
                    gyro_x = (obj['gyro_x'])
                    if abs(gyro_x) > gyro_xp[xpixel]:
                        gyro_xp[xpixel] = gyro_x
                    gyro_y = (obj['gyro_y'])
                    if abs(gyro_y) > gyro_yp[xpixel]:
                        gyro_yp[xpixel] = gyro_y
                    gyro_z = (obj['gyro_z'])
                    if abs(gyro_z) > gyro_zp[xpixel]:
                        gyro_zp[xpixel] = gyro_z
                    accel_file.write("%f %f %f %f %f %f %f %f %f\n" %( obj['mileage'], obj['lat'], obj['lon'], obj['acc_x'], obj['acc_y'], obj['acc_z'], obj['gyro_x'], obj['gyro_y'], obj['gyro_z']))

        for xpixel in range(margin, len(acc_xp)-2*margin):
            if 'acc_x' in drawables:
                draw.line((xpixel,yxpixel-scale*acc_xp[xpixel],xpixel-1,yxpixel-scale*acc_xp[xpixel-1]),fill=COLORS['red'])
            if 'acc_y' in drawables:
                draw.line((xpixel,yypixel-scale*acc_yp[xpixel],xpixel-1,yypixel-scale*acc_yp[xpixel-1]),fill=COLORS['blue'])
            if 'acc_z' in drawables:
                draw.line((xpixel,yzpixel-scale*acc_zp[xpixel],xpixel-1,yzpixel-scale*acc_zp[xpixel-1]),fill=COLORS['green'])
            if 'gyro_x' in drawables:
                draw.line((xpixel,ygxpixel-scale*gyro_xp[xpixel],xpixel-1,ygxpixel-scale*gyro_xp[xpixel-1]),fill=COLORS['red'])
            if 'gyro_y' in drawables:
                draw.line((xpixel,ygypixel-scale*gyro_yp[xpixel],xpixel-1,ygypixel-scale*gyro_yp[xpixel-1]),fill=COLORS['blue'])
            if 'gypo_z' in drawables:
                draw.line((xpixel,ygzpixel-scale*gyro_zp[xpixel],xpixel-1,ygzpixel-scale*gyro_zp[xpixel-1]),fill=COLORS['green'])

    del draw

def sidings(track_chart):
    """
    Draw Siding
    """
    image = track_chart['image']
    margin = track_chart['margin']
    (first, last, pixel_per_mile) = track_chart['mileposts']
    draw = ImageDraw.Draw(image)

    ypixel = int((image.size[1]-margin)*0.625)
    for obj in track_chart['G'].get_points(ktype='K', kclass='ST'):
        mileage = obj['mileage']
        if not first <= mileage <= last:
            continue

        metadata = obj['metadata']

        start_x = mile_to_pixel(track_chart,mileage - first)
        end_x = mile_to_pixel(track_chart,metadata['end'] - first)
        ypixel1 = ypixel - pixel_per_mile * 0.01 * int(metadata['offset'])
        draw.line((start_x, ypixel1, end_x, ypixel1),fill=COLORS['black'])

    del draw

def draw_gauge(track_chart):
    """
    Draw Gage
    """
    image = track_chart['image']
    margin = track_chart['margin']
    (first, last, _pixel_per_mile) = track_chart['mileposts']
    draw = ImageDraw.Draw(image)

    ypixel = int((image.size[1]-margin)*0.34)
    draw.text((margin, ypixel), aar.full_name, fill=COLORS['black'])

    data = [0] * 360
    ghost = [0] * 360
    total_slope = total_slope_count = 0
    # Read from file
    for _line_no, obj in pirail.read(track_chart['data_file']):
        if obj['class'] not in ["LIDAR", "L"]:
            continue
        mileage = obj['mileage']
        if not first <= mileage <= last:
            continue
        xpixel = mile_to_pixel(track_chart, mileage-first)

        lidar_util.process_scan(obj['lidar'], data, ghost)

        new_data = lidar_util.convert_to_xy(data, offset=2.1528056371157285)

        gauge,slope,_p1,_p2 = lidar_util.calc_gauge(new_data)

        if not aar.min_gauge <= gauge <= aar.max_gauge:
            #print(mileage, gauge)
            draw.point((xpixel,ypixel+(gauge-aar.standard_gauge)*2),fill=COLORS['red'])
        else:
            #draw.point((xpixel,ypixel), fill=COLORS['black'])
            pass
        total_slope += slope
        total_slope_count += 1

    if total_slope_count > 0:
        #print(total_slope/total_slope_count)
        pass

    del draw
