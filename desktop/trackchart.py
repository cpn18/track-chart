"""
Track chart drawing methods
"""
import math
from PIL import Image, ImageDraw, ImageOps
import geo

def new(args):
    """
    New Trackchart
    """
    (size, margin, prefix, first, last, alt_prefix, alt_factor, known_file, gps_file) = args
    pixel_per_mile = float(size[0]-3*margin) / (last-first)
    return {'image': Image.new("1", size, "white"),
            'margin': margin,
            'prefix': prefix,
            'mileposts': (first, last, pixel_per_mile),
            'alt_prefix': alt_prefix,
            'alt_factor': alt_factor,
            'known_file': known_file,
            'gps_file': gps_file}

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
        return delta - 360
    elif delta < -180:
        return 360 + delta
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

def milepost_symbol(draw, x, y_size, margin, prefix, m, alt_prefix, alt_factor):
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
    if m == int(m):
        str_format = "%s%d"
    else:
        str_format = "%s%0.2f"
    draw.text((x+0.5*margin, margin), str_format % (prefix, m))
    if not alt_prefix is None:
        alt_str = str_format % (alt_prefix, alt_factor-m)
        draw.text((x-0.5*margin-draw.textsize(alt_str)[0], margin), alt_str)

def mileposts(tc, from_file=False):
    """
    Draw mileposts
    """
    im = tc['image']
    margin = tc['margin']
    prefix = tc['prefix']
    (first, last, pixel_per_mile) = tc['mileposts']
    alt_prefix = tc['alt_prefix']
    alt_factor = tc['alt_factor']

    draw = ImageDraw.Draw(im)
    if from_file:
        with open(tc['known_file']) as f:
            for line in f:
                if line[0] == "#":
                    continue
                l = line.strip().split(",")
                m = float(l[3])
                if first <= m <= last and l[0] == "MP":
                    x = mile_to_pixel(tc, m-first)
                    milepost_symbol(draw, x, (im.size[1]-margin),
                                    margin, prefix, m, alt_prefix, alt_factor)
                    if l[4] != "":
                        # Survey Station
                        survey_station = l[4]
                        (w, x_size, y_size) = rotated_text(draw, survey_station, 90)
                        im.paste(w, ((x-y_size-3, im.size[1]-margin-x_size)))
    else:
        for m in range(first, last+1):
            x = mile_to_pixel(tc, m-first)
            milepost_symbol(draw, x, (im.size[1]-margin), margin, prefix, m, alt_prefix, alt_factor)
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
    with open(tc['known_file']) as f:
        for line in f:
            if line[0] == "#":
                continue
            l = line.strip().split(",")
            print(l)
            m = float(l[3])
            if l[0] == "E":
                if start is None or m < start:
                    start = m
                if end is None or m > end:
                    end = m
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
    with open(tc['known_file']) as f:
        for line in f:
            if line[0] == "#":
                continue
            l = line.strip().split(",")
            m = float(l[3])
            if first <= m <= last and (xing_type is None or l[0] == xing_type):
                x = mile_to_pixel(tc, m-first)
                if l[0] == 'U':
                    # Draw underpass
                    draw.line((x-3, y, x+3, y), fill=255)
                    draw.line((x, y-margin, x, y+margin))
                elif l[0] == 'O':
                    # Draw underpass
                    draw.line((x, y-margin, x, y-3))
                    draw.line((x, y+3, x, y+margin))
                elif l[0] == 'X':
                    # Draw road
                    draw.line((x, y-margin, x, y+margin))
                else:
                    continue

                # Draw description
                description = ("%s %s" % (mileage_to_string(l[3]), l[4])).strip()
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
    with open(tc['known_file']) as f:
        for line in f:
            if line[0] == "#":
                continue
            l = line.strip().split(",")
            m = float(l[3])
            if first <= m <= last:
                if l[0] == 'TL':
                    x = mile_to_pixel(tc, m-first)

                    # Town 1
                    description = l[4].split("/")[0]
                    (w, x_size1, y_size1) = rotated_text(draw, description, 90)
                    im.paste(w, (int(x-y_size1-3), y-(x_size1/2)))
                    # Town 2
                    description = l[4].split("/")[1]
                    (w, x_size2, y_size2) = rotated_text(draw, description, 90)
                    im.paste(w, (int(x), y-(x_size2/2)))
                    # Dashed Town Line
                    if x_size2 > x_size1:
                        x_size1 = x_size2
                    x_size1 = int(math.ceil(x_size1/10.0)*10)
                    for y1 in range(y-x_size1/2, y+x_size1/2, 10):
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
    with open(tc['known_file']) as f:
        for line in f:
            if line[0] == "#":
                continue
            l = line.strip().split(",")
            m = float(l[3])
            if first <= m <= last:
                if l[0] == 'S':
                    x = mile_to_pixel(tc, m-first)
                    offset = int(l[4])

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
                    y1 = int((im.size[1]-margin)*0.7)
                    (x_size, y_size) = draw.textsize(l[5])
                    draw.text((int(x-x_size/2), int(y1)), l[5])
                    y1 += y_size
                    mileage = mileage_to_string(l[3])
                    (x_size, y_size) = draw.textsize(mileage)
                    draw.text((int(x-x_size/2), int(y1)), mileage)
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
    with open(tc['known_file']) as f:
        for line in f:
            if line[0] == "#":
                continue
            l = line.strip().split(",")
            m = float(l[3])
            if first <= m <= last:
                if l[0] == 'YL':
                    x = mile_to_pixel(tc, m-first)
                    offset = int(l[4])

                    (x_size1, y_size1) = draw.textsize(l[0])
                    mileage = mileage_to_string(l[3])
                    (x_size2, y_size2) = draw.textsize(mileage)

                    if offset != 0:
                        if offset > 0:
                            # Above the mainline
                            offset = 2
                            draw.line((x, y-offset, x, y-offset-line_length))
                            y1 = y-offset-line_length-y_size1-y_size2
                        elif offset < 0:
                            # Below the mainline
                            offset = 2
                            draw.line((x, y+offset, x, y+offset+line_length))
                            y1 = y+offset+line_length

                    # Draw description
                    draw.text((int(x-x_size1/2), int(y1)), l[0])
                    draw.text((int(x-x_size2/2), int(y1+y_size1)), mileage)
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
    with open(tc['known_file']) as f:
        for line in f:
            if line[0] == "#":
                continue
            l = line.strip().split(",")
            m = float(l[3])
            if not (first <= m <= last):
                continue

            if l[0] != 'CRF' and l[0] != 'CRT' and l[0] != 'CLF' and l[0] != 'CLT':
                continue

            x = mile_to_pixel(tc, m-first)
            y_start = y
            y_size = 0.01 * pixel_per_mile
            print(y_size)
            start_offset = int(l[4])
            end_offset = int(l[5])
            (x_size1, y_size1) = draw.textsize(l[0])
            mileage = mileage_to_string(l[3])
            (x_size2, y_size2) = draw.textsize(mileage)

            if start_offset > 0:
                # above the mainline
                y_start = y - start_offset*y_size
            elif start_offset < 0:
                # below the mainline
                y_start = y - start_offset*y_size

            if l[0] == 'CRF':
                y_end = y_start - end_offset*y_size
                x_end = x + abs(end_offset)*y_size
            elif l[0] == 'CLF':
                y_end = y_start - end_offset*y_size
                x_end = x + abs(end_offset)*y_size
            elif l[0] == 'CRT':
                y_end = y_start - end_offset*y_size
                x_end = x - abs(end_offset)*y_size
            elif l[0] == 'CLT':
                y_end = y_start - end_offset*y_size
                x_end = x - abs(end_offset)*y_size

            draw.line((x, y_start, x_end, y_end))
    del draw

def elevation(tc):
    """
    Draw Elevation profile
    """
    smooth = 0.10

    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)

    y = int((im.size[1]-margin))
    y_range = 200

    # Read from file
    edata = []
    with open(tc['gps_file']) as f:
        for line in f:
            if line[0] == "#":
                continue
            l = line.strip().split(",")
            m = float(l[3])
            if first <= m <= last:
                if l[0] == "G":
                    if l[4] != "-":
                        edata.append({'mileage': float(l[3]), 'elevation': float(l[4])})
                    else:
                        edata.append({'mileage': float(l[3])})

    # Check for empty list
    if len(edata) == 0:
        return

    # Sort
    edata = sorted(edata, key=lambda k: k['mileage'], reverse=False)

    smooth_edata = list(edata)
    # smooth, looking at all measurements +/- 0.01
    for i in range(0, len(edata)):
        m = edata[i]['mileage']
        c = 1
        try:
            esum = edata[i]['elevation']
        except:
            esum = 0
        # work backwards
        j = i-1
        while j >= 0 and edata[j]['mileage'] >= m-smooth/2:
            try:
                esum += edata[j]['elevation']
                c += 1
            except:
                pass
            j -= 1
        # work forwards
        j = i + 1
        while j < len(edata) and edata[j]['mileage'] <= m+smooth/2:
            try:
                esum += edata[j]['elevation']
                c += 1
            except:
                pass
            j += 1
        # average
        smooth_edata[i] = {'mileage': m, 'elevation': esum / c}

    # find min and max
    emax = emin = smooth_edata[0]['elevation']
    for e in smooth_edata:
        t = e['elevation']
        if t < emin:
            emin = t
        elif t > emax:
            emax = t

    # baseline
    #draw.text((int(1.5*margin), im.size[1]-margin), "Base = %d" % emin)
    #draw.line((margin, im.size[1]-margin, im.size[0]-margin, im.size[1]-margin))

    # loop over the list
    min_display = max_display = False
    for j in range(1, len(smooth_edata)):
        x1 = mile_to_pixel(tc, smooth_edata[j-1]['mileage']-first)
        x2 = mile_to_pixel(tc, smooth_edata[j]['mileage']-first)
        y1 = y - (smooth_edata[j-1]['elevation'] - emin) * (y_range/emax)
        y2 = y - (smooth_edata[j]['elevation'] - emin) * (y_range/emax)
        draw.line((x1, y1, x2, y2))
        if smooth_edata[j]['elevation'] == emax and not max_display:
            txt = "%dft" % emax
            (x_size, y_size) = draw.textsize(txt)
            draw.text((int(x2-x_size/2), y2-y_size), txt)
            max_display = True
        elif smooth_edata[j]['elevation'] == emin and not min_display:
            txt = "%dft" % emin
            (x_size, y_size) = draw.textsize(txt)
            draw.text((int(x2-x_size/2), y2), txt)
            min_display = True

    del draw

def curvature(tc):
    """
    Draw Curvature
    """
    smooth = 0.06
    bearing_threshold = 2

    im = tc['image']
    margin = tc['margin']
    (first, last, pixel_per_mile) = tc['mileposts']
    draw = ImageDraw.Draw(im)

    y = int((im.size[1]-margin)*0.80)

    # Read from file
    cdata = []
    with open(tc['gps_file']) as f:
        for line in f:
            if line[0] == "#":
                continue
            l = line.strip().split(",")
            m = float(l[3])
            if first <= m <= last:
                if l[0] == "G":
                    cdata.append({'latitude': float(l[1]),
                                  'longitude': float(l[2]),
                                  'mileage': float(l[3]),
                                  'bearing': float(l[5])})

    # Check for empty list
    if len(cdata) == 0:
        return

    # Sort
    cdata = sorted(cdata, key=lambda k: k['mileage'], reverse=False)

    smooth_cdata = list(cdata)
    # smooth, looking at all measurements +/-
    for i in range(0, len(cdata)):
        m = cdata[i]['mileage']
        back = fore = cdata[i]
        try:
            back = cdata[i-1]
        except:
            pass
        try:
            fore = cdata[i+1]
        except:
            pass
        c = 1
        esum = cdata[i]['bearing']
        # work backwards
        j = i-1
        while j >= 0 and cdata[j]['mileage'] >= m-smooth/2:
            esum += cdata[j]['bearing']
            back = cdata[j]
            c += 1
            j -= 1
        # work forwards
        j = i + 1
        while j < len(cdata) and cdata[j]['mileage'] <= m+smooth/2:
            esum += cdata[j]['bearing']
            fore = cdata[j]
            c += 1
            j += 1
        # average
        d = geo.great_circle(back['latitude'], back['longitude'],
                             fore['latitude'], fore['longitude'])
        b = geo.bearing(back['latitude'], back['longitude'],
                        fore['latitude'], fore['longitude'])
        smooth_cdata[i] = {'mileage': m, 'bearing': b}
        print("%f %0.2fmiles @ %d" % (m, d, b))

        # copy bearing from second point
        smooth_cdata[0] = {
            'mileage': float(smooth_cdata[0]['mileage']),
            'bearing': float(smooth_cdata[1]['bearing'])}

    tangent_length = pixel_per_mile*0.02
    # loop over the list
    last_y = y
    last_x = mile_to_pixel(tc, smooth_cdata[0]['mileage']-first)
    for j in range(1, len(smooth_cdata)):
        x1 = mile_to_pixel(tc, smooth_cdata[j-1]['mileage']-first)
        x2 = mile_to_pixel(tc, smooth_cdata[j]['mileage']-first)
        bdiff = smooth_cdata[j]['bearing'] - smooth_cdata[j-1]['bearing']
        while bdiff > 180:
            bdiff -= 180
        while bdiff < -180:
            bdiff += 180

        if bdiff < 45 and abs(x2-last_x) > tangent_length:
            print("%0.2f miles @ %d" % ((x2-last_x)/pixel_per_mile, bdiff))
            if bdiff > bearing_threshold:
                # turning right
                y1 = y - min(10, bdiff)
            elif bdiff < -bearing_threshold:
                # turning left
                y1 = y + min(10, -bdiff)
            else:
                y1 = y
            if last_y != y1:
                draw.line((last_x, last_y, last_x, y1))
            draw.line((last_x, y1, x2, y1))
            last_y = y1
            last_x = x2

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
    ys = int((im.size[1]-margin)*0.34)

    scale = 5

    draw.text((margin, yx), "X")
    draw.text((margin, yy), "Y")
    draw.text((margin, yz), "Z")
    draw.text((margin, ys), "S")

    x_index = 5
    y_index = 6
    z_index = 7

    accel_threshold = 0

    # Read from file
    with open(tc['gps_file']) as f:
        for line in f:
            if line[0] == "#":
                continue
            l = line.strip().split(",")
            if l[0] == "A":
                for i in range(1, len(l)):
                    l[i] = float(l[i])
                if first <= l[3] <= last:
                    print(l)
                    x = mile_to_pixel(tc, l[3]-first)

                    # Speed
                    draw.point((x, ys-l[4]))

                    # Average X
                    if l[8] > accel_threshold:
                        draw.point((x, yx-scale*abs(l[x_index])))

                    # Average Y
                    if l[9] > accel_threshold:
                        draw.point((x, yy-scale*abs(l[y_index])))

                    # Average Z
                    if l[10] > accel_threshold:
                        draw.point((x, yz-scale*abs(l[z_index])))

                    #if l[8] > l[9] and l[8] > l[10]:
                    #    draw.point((x, yx+scale*l[x_index]))
                    #if l[9] > l[8] and l[9] > l[10]:
                    #    draw.point((x, yy+scale*l[y_index]))
                    #if l[10] > l[8] and l[10] > l[9]:
                    #    draw.point((x, yz+scale*l[z_index]))

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
    with open(tc['known_file']) as f:
        for line in f:
            if line[0] == "#":
                continue
            l = line.strip().split(",")
            m = float(l[3])
            if not (first <= m <= last):
                continue

            if l[0] != 'ST':
                continue

            start_x = mile_to_pixel(tc,float(l[3]) - first)
            end_x = mile_to_pixel(tc,float(l[5]) - first)
            y1 = y - pixel_per_mile * 0.01 * int(l[4])
            draw.line((start_x, y1, end_x, y1))

    del draw
