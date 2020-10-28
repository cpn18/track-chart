import json
import sys
import gps_to_mileage

GPS = gps_to_mileage.Gps2Miles(sys.argv[2])

acclist = []
data = []
last_tpv = None
with open(sys.argv[1]) as f:
    for line in f:
        items = line.split()
        if items[-1] != "*":
            continue
        if items[1] == "TPV":
            tpv = json.loads(" ".join(items[2:-1]))
            if tpv['mode'] < 3:
                continue
            print(tpv)
            if last_tpv is not None:
                if len(acclist) > 0:
                    delta_lat = (tpv['lat'] - last_tpv['lat'])
                    delta_lon = (tpv['lon'] - last_tpv['lon'])
                    delta_alt = (tpv['alt'] - last_tpv['alt'])
                    for acc in acclist:
                        millsec = float("0." + acc['time'].split(".")[1].replace("Z", ""))
                        acc['lat'] = last_tpv['lat'] + millsec*delta_lat
                        acc['lon'] = last_tpv['lon'] + millsec*delta_lon
                        acc['alt'] = last_tpv['alt'] + millsec*delta_alt
                        acc['mileage'], acc['certainty'] = GPS.find_mileage(acc['lat'], acc['lon'])
                        data.append(acc)
            tpv['mileage'], tpv['certainty'] = GPS.find_mileage(tpv['lat'], tpv['lon'])
            data.append(tpv)
            last_tpv = tpv
            acclist = []
        elif items[1] == "ATT":
            att = json.loads(" ".join(items[2:-1]))
            acclist.append(att)

data = sorted(data, key=lambda k: k['mileage'], reverse=False)

new_data = []
accset = []
current = 0
start_mileage = round(data[0]['mileage'],2)
next_mileage = start_mileage + 0.001
while current < len(data):
    if round(data[current]['mileage'],2) < next_mileage:
        accset.append(data[current])
        current += 1
    else:
        acc_z = -9999
        for a in accset:
            if a['class'] != "ATT":
                continue
            print(a)
            if a['acc_z'] > acc_z:
                acc_z = a['acc_z']
        if acc_z != -9999:
            new_data.append({'class': "ATT", 'mileage': start_mileage, 'acc_z': acc_z, 'lat': data[current]['lat'], 'lon': data[current]['lon']})
        accset = []
        start_mileage = next_mileage
        next_mileage += 0.001

print(new_data)


with open("acc_by_mileage.csv", "w") as f:
    f.write("Mileage Latitude Longitude ACCz\n")
    for d in new_data:
        if d['class'] == "ATT":
            f.write("%0.2f %f %f %f\n" % (d['mileage'],d['lat'], d['lon'], d['acc_z']))
