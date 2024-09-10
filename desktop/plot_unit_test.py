"""
Unit Test for Library to plot multiple datasets

"""
import plot

def unit_test():
    myplot = plot.Plot({
        "width": 1024*4,
        "height": 768*4,
        "xaxis": "mileage",
        "start": 0.0,
        "end": 1.5,
        #"xaxis": "time",
        #"start": "2024-06-01T11:32:05.000000Z",
        #"end": "2024-06-01T11:40:17.000000Z",
        "type": "bar",
#        "font": "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
#        "fontsize": 12,
        "title": "Seashore Trolley Museum",
    })

    myplot.add_title()

    y = 50
    height = 100

    #myplot.add_plot({
    #    "filename": "/run/media/jminer/8808-4BCF/PIRAIL/20240428/stm1.json",
    #    "key": "gyro_x",
    #    "fill": (0, 0, 0),
    #    "y": y,
    #    "height": height,
    #})

    #y += height

    #myplot.add_plot({
    #    "filename": "/run/media/jminer/8808-4BCF/PIRAIL/20240428/stm2.json",
    #    "key": "gyro_x",
    #    "fill": (0, 0, 0),
    #    "y": y,
    #    "height": height,
    #})

    #y += height

    #myplot.add_plot({
    #    "filename": "/run/media/jminer/FreeAgent Drive/PIRAIL/20240601/20240601_stm_with_mileage_sort_by_time.json",
    #    "key": "gyro_x",
    #    "fill": (255, 0, 0),
    #    "y": y,
    #    "height": height,
    #})
    #myplot.add_plot({
    #    "filename": "/run/media/jminer/FreeAgent Drive/PIRAIL/20240601/20240601_stm_with_mileage_sort_by_time.json",
    #    "key": "num_used",
    #    "fill": (0, 0, 255),
    #    "y": y,
    #    "height": height,
    #    "title": False,
    #})
    y += height

    myplot.add_plot({
        "filename": "/run/media/jminer/FreeAgent Drive/PIRAIL/20240601/20240601_stm_with_mileage_sort_by_time.json",
        "key": "acc_z",
        "fill": (255, 0, 0),
        "y": y,
        "height": height,
    })

    y += height

    myplot.add_plot({
        "filename": "/run/media/jminer/FreeAgent Drive/PIRAIL/20240601/20240601_stm_with_mileage_sort_by_time.json",
        "key": "pitch",
        "scale": 20,
        "fill": (255, 0, 0),
        "y": y,
        "height": height,
    })
    y += height

    myplot.add_plot({
        "filename": "../data/stm_20240908_with_mileage_sort_by_time.json",
        "key": "acc_z",
        "scale": 20,
        "fill": (0, 255, 0),
        "y": y,
        "height": height,
    })
    y += height

    myplot.add_plot({
        "filename": "../data/stm_20240908_with_mileage_sort_by_time.json",
        "key": "pitch",
        "scale": 20,
        "fill": (0, 255, 0),
        "y": y,
        "height": height,
    })

    filename = myplot.save("images/out.png")
    print("Saved to %s" % filename)

if __name__ == "__main__":
    unit_test()
