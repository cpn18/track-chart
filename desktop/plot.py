"""
Library to plot multiple datasets

Scroll down to unit_test() function
"""
import os
from PIL import Image, ImageDraw, ImageOps, ImageFont
import pirail

BLACK = (0,0,0)

class Plot():
    def __init__(self, params):
        self.width = int(params.get('width', 1024))
        self.height = int(params.get('height', 768))
        self.margin = int(params.get('margin',5))
        self.xaxis = params.get('xaxis', 'mileage')
        if self.xaxis == "time":
            self.start = pirail.parse_time(params.get('start'))
            self.end = pirail.parse_time(params.get('end'))
        else:
            self.start = round(float(params.get('start', 0)), 2)
            self.end = round(float(params.get('end', 100)), 2)
        self.type = params.get('type', 'scatter')
        self.title = params.get('title', 'My PiRail Data')

        self.image = Image.new("RGB", (self.width, self.height), "white")

        font = params.get('font', 'dejavu-sans-fonts/DejaVuSans.ttf')
        if font[0] != "/":
            font = os.path.join("/usr/share/fonts/", font)

        size = int(params.get('fontsize', 10))

        self.font = [
            ImageFont.truetype(font, size=size),
            ImageFont.truetype(font, size=size+2),
            ImageFont.truetype(font, size=size+4),
        ]

    def add_title(self):
        draw = ImageDraw.Draw(self.image)

        # Add Title
        text = self.title
        (x_size, y_size) = draw.textsize(text, self.font[2])
        draw.text(((self.width - x_size)/2, self.height-y_size-self.margin), text, fill=BLACK, font=self.font[2])

        if self.xaxis == "mileage":
            # Add Start Mileage
            text = "%0.2f" % self.start
        else:
            text = self.start.isoformat()
        (x_size, y_size) = draw.textsize(text, self.font[1])
        draw.text((self.margin, self.margin), text, fill=BLACK, font=self.font[1])

        if self.xaxis == "mileage":
            # Add End Mileage
            text = "%0.2f" % self.end
        else:
            text = self.end.isoformat()
        (x_size, y_size) = draw.textsize(text, self.font[1])
        draw.text((self.width - x_size - self.margin, self.margin), text, fill=BLACK, font=self.font[1])

        del draw

    def real_axis_to_x(self, value):
         x = (value - self.start) * (self.width - 2 * self.margin) / (self.end - self.start)
         return x + self.margin

    def add_plot(self, params):
        title = params.get('title', True)
        scale = float(params.get('scale', 1.0))

        key = params['key']
        data = []
        for _line_no, obj in pirail.read(params['filename']):
            try:
                if self.xaxis == "time":
                    midpoint = pirail.parse_time(obj[self.xaxis])
                else:
                    midpoint = obj[self.xaxis]
                if self.start <= midpoint <= self.end:
                    x = self.real_axis_to_x(midpoint)
                    data.append({"x": x, "y": obj[key]})
            except KeyError:
                pass

        # Sort By X
        data = sorted(data, key=lambda k: k['x'], reverse=False)

        baseline = int(params['y'] + params['height'] / 2.0)

        draw = ImageDraw.Draw(self.image)
        if len(data) > 0:
            last_x = data[0]['x']
            last_y = baseline - data[0]['y']
            for point in data:
                this_x = point['x']
                this_y = baseline - point['y']
                if self.type == "scatter":
                    draw.point((this_x, this_y), fill=params['fill'])
                elif self.type == "line":
                    draw.line((last_x, last_y, this_x, this_y), fill=params['fill'])
                elif self.type == "bar":
                    draw.line((this_x, baseline, this_x, this_y), fill=params['fill'])

                last_x = this_x
                last_y = this_y

        # Add filename
        if title is False:
            pass
        else:
            if title is True:
                text = "%s/%s" % (os.path.basename(os.path.dirname(params['filename'])), key)
            else:
                text = params['title']
            (_x_size, y_size) = draw.textsize(text, self.font[0])
            draw.text((self.margin, params['y']), text, fill=params['fill'], font=self.font[0])

        del draw

    def save(self, filename=None):
        if filename is None:
            filename = "images/output_%0.2f_%0.2f.png" % (self.start, self.end)
        self.image.save(filename)
        return filename

def unit_test():
    myplot = Plot({
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
