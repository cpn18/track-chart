#!/usr/bin/python3
"""
Wait for GPS Fix and Set System Time
"""
import os
import sys
import gps

def set_date(gps_date):
    """ Set the system clock """
    sys_date = "%s%s%s%s%s.%s" % (
        gps_date[5:7],
        gps_date[8:10],
        gps_date[11:13],
        gps_date[14:16],
        gps_date[0:4],
        gps_date[17:19])
    command = "date --utc %s > /dev/null" %  sys_date
    os.system(command)

def wait_for_timesync():
    """ Wait for Time Sync """

    # Listen on port 2947 (gpsd) of localhost
    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

    done = False
    while not done:
        try:
            report = session.next()
            if report['class'] != 'TPV':
                continue
            if hasattr(report, 'mode') and report.mode == 1:
                # can't trust a mode=1 time
                continue
            if hasattr(report, 'time'):
                print(report.time)
                set_date(report.time)
                done = True
        except Exception as ex:
            print(ex)
            sys.exit(1)

if __name__ == "__main__":
    # Make sure we have a time sync
    wait_for_timesync()

sys.exit(0)
