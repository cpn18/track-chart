import geo

def great_circle(last, now):
    """ Great Circle Calculation """
    try:
        return geo.great_circle(
            last['lat'],
            last['lon'],
            now['lat'],
            now['lon']
        )
    except KeyError:
        return 0

def update_odometer(odometer, odir, last_pos, obj):
    """ Update Odometer """
    if 'speed' in obj:
        if 'eps' in obj and obj['speed'] < obj['eps']:
            # Skip it... we might not be moving
            pass
        else:
            odometer += odir * great_circle(last_pos, obj)
            last_pos = obj
    return (odometer, last_pos)
