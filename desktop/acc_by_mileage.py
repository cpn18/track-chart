"""
Find the Peak ACC_Z by Mileage
"""
import sys
import json
import pirail

GRAVITY = 9.80665 # m/s2

DIRECTION = -1 # either 1 or -1

def acc_z_by_mileage(filename, step=0.001, digits=3):
    """
    Find Peak Z by Mileage
    """
    # Find Starting Mileage
    accset = []
    start_mileage = None
    with open("acc_by_mileage.json", "w") as output_file:
        for _line_no, obj in pirail.read(filename, classes=['ATT']):

            # Skip entry without a mileage
            if not 'mileage' in obj:
                continue

            # First time through set the start mileage
            if start_mileage is None:
                start_mileage = round(obj['mileage'],digits)
                next_mileage = start_mileage + step * DIRECTION
                print(start_mileage, next_mileage)
                continue

            # Append the data
            if DIRECTION == -1 and round(obj['mileage'],digits) > next_mileage:
                accset.append(obj)
                continue
            elif DIRECTION == 1 and round(obj['mileage'],digits) < next_mileage:
                accset.append(obj)
                continue

            print(len(accset))
            # Find the highest magnitude acceleration
            acc_z = None
            for accdata in accset:
                if acc_z is None or abs(accdata['acc_z']-GRAVITY) > abs(acc_z-GRAVITY):
                    acc_z = accdata['acc_z']

            # Write out the data
            if acc_z is not None:
                output_file.write(json.dumps({
                    'class': "ATT",
                    'mileage': round(start_mileage, digits),
                    'acc_z': acc_z,
                    'lat': obj['lat'],
                    'lon': obj['lon']
                }))
                output_file.write("\n")

            # Reset
            accset = []
            start_mileage = next_mileage
            next_mileage += step * DIRECTION
            print(start_mileage, next_mileage)

if __name__ == "__main__":
    acc_z_by_mileage(sys.argv[-1])
