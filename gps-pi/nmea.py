#!/usr/bin/python3
"""
NMEA Utils
"""

def tpv_to_json(report):
    if report is None:
        return {"class": "TPV", "mode": 0}
    tpv = {
        'class': report['class'],
        'mode': report['mode'],
    }
    for field in ['device', 'status', 'time', 'altHAE', 'altMSL', 'alt',
            'climb', 'datum', 'depth', 'dgpsAge', 'dgpsSta',
            'epc', 'epd', 'eph', 'eps', 'ept', 'epx', 'epy', 'epv',
            'geoidSep', 'lat', 'leapseconds', 'lon', 'track', 'magtrack',
            'magvar', 'speed', 'ecefx', 'ecefy', 'ecefz', 'ecefpAcc',
            'ecefvx', 'ecefvy', 'ecefvz', 'exefvAcc', 'sep', 'relD',
            'relE', 'relN', 'velD', 'velE', 'velN', 'wanglem', 'wangler',
            'wanglet', 'wspeedr', 'wspeedt']:
        if field in report:
            tpv[field] = report[field]
    return tpv

def sky_to_json(report):
    if report is None:
        return {"class": "SKY", "satellites": []}
    sky = {
        'class': report['class'],
        'satellites': [],
    }
    for field in ['device', 'time', 'gdop', 'hdop', 'pdop', 'tdop', 'vdop',
            'xdop', 'ydop']:
        if field in report:
            sky[field] = report[field]
    for i in range(len(report['satellites'])):
        sat = report['satellites'][i]
        prn = {
            "PRN": sat['PRN'],
            "used": sat['used'],
        }
        for field in ['az', 'el', 'ss', 'gnssid', 'svid', 'sigid',
                'freqid', 'health']:
            if field in sat:
                prn[field] = sat[field]
        sky['satellites'].append(prn)
    return sky

def calc_used(sky):
    num_sat = len(sky['satellites'])
    num_used = 0
    for i in range(num_sat):
        if sky['satellites'][i]['used'] is True:
            num_used += 1
    return (num_used, num_sat)
