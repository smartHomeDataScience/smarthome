from bokeh.charts import Donut
from bokeh.layouts import widgetbox, row, layout
from bokeh.models.widgets import TextInput, Slider, PreText
from bokeh.plotting import figure, output_file, curdoc

from pymongo import MongoClient
import pandas as pd


class WebPage:
    def __init__(self):
        self.db = MongoClient('mongodb://localhost/SmartHome', 27017).SmartHome
        output_file("index.html")

    def control(self):
        pid = TextInput(value='0', title="pid")
        # pid2 = TextInput(value='0', title="pid")
        slider = Slider(start=0, end=1800, value=1, step=1, title="Time")
        annotationText = PreText(text='Annotation: ')
        locationText = PreText(text='Location: ')

        controls1 = widgetbox([pid, slider, annotationText, locationText], width=300)
        controls2 = widgetbox([], width=300)

        p = layout([
            [controls1, self.firstMap(), self.groundMap()],
            [controls2, self.annotationDistribution(0), self.locationDistribution(0)]
        ])
        def updatePid(a,b,value):
            try:
                value = int(value)
                p.children[1].children[1:3] = [self.annotationDistribution(value), self.locationDistribution(value)]
            except:
                pass

        def updateTime(a,b,value):
            try:
                location = self.db.timeBasedLocation.find({'t': int(value), 'pid': int(pid.value)})
                annotation = self.db.timeBasedAnnotations.find({'t': int(value), 'pid': int(pid.value)})

                locationText.text = 'Location: %s' % location[0]['name']
                annotationText.text = 'Annotation: %s' % annotation[0]['name']
            except:
                locationText.text = 'Location: Unknown'
                annotationText.text = 'Annotation: Unknown'


        pid.on_change('value', updatePid)
        slider.on_change('value',updateTime)
        # toggle = Toggle(label="Refresh", button_type="success")

        curdoc().add_root(p)
        # curdoc().add_root(p2)



    def annotationDistribution(self, pid=None):
        if pid is None:
            cursor = self.db.annotations.find({})
        else:
            cursor = self.db.annotations.find({'pid':pid})

        annotation = [0.0] * 20
        for i in cursor:
            annotation[int(i['index'])] += float(i['end']) - float(i['start'])

        data = pd.Series(annotation)
        p = Donut(data)
        return p


    def locationDistribution(self, pid=None):

        if pid is None:
            cursor = self.db.location.find({})
        else:
            cursor = self.db.location.find({'pid':pid})

        location = [0.0] * 9
        for i in cursor:
            location[int(i['index'])] += float(i['end']) - float(i['start'])

        data = pd.Series(location)
        p = Donut(data)
        return p

    def firstMap(self):
        x = [2.85, 4.65, 4.65, 0, 0, 2.85, 2.85]
        y = [0, 0, 10.45, 10.45, 3.2, 3.2, 0]

        bath_x = [2.85, 4.65, 4.65, 2.85, 2.85]
        bath_y = [0, 0, 3.2, 3.2, 0]

        bedroom1_x = [0, 3.4, 3.4, 0, 0]
        bedroom1_y = [3.2, 3.2, 6.8, 6.8, 3.2]

        bedroom2_x = [0, 3.8, 3.8, 0, 0]
        bedroom2_y = [6.8, 6.8, 10.45, 10.45, 6.8]

        landing_x = [3.4, 4.65, 4.65, 3.8, 3.8, 3.4, 3.4]
        landing_y = [3.2, 3.2, 8.2, 8.2, 6.8, 6.8, 3.2]

        wc_x = [3.8, 4.65, 4.65, 3.8, 3.8]
        wc_y = [8.2, 8.2, 10.45, 10.45, 8.2]

        p = figure(plot_width=400, plot_height=400)
        p.patches([x, bath_x, bedroom1_x, bedroom2_x, landing_x, wc_x],
                  [y, bath_y, bedroom1_y, bedroom2_y, landing_y, wc_y],
                  fill_color=['transparent','transparent','transparent','transparent','transparent','transparent'],
                  line_width=1)
        return p

    def groundMap(self):
        x = [1.65, 4.65, 4.65, 0, 0, 1.65, 1.65]
        y = [0, 0, 10.45, 10.45, 3.15, 3.15, 0]

        kitchen_x = [1.65, 4.65, 4.65, 1.65, 1.65]
        kitchen_y = [0, 0, 3.15, 3.15, 0]

        bedRoom_x = [0, 2.9, 2.9, 0, 0]
        bedRoom_y = [3.15, 3.15, 6.75, 6.75, 3.15]

        hall_x = [4.41, 4.65, 4.65, 4.41, 4.41]
        hall_y = [6.75, 6.75, 10.45, 10.45, 6.75]

        lounch_x = [0, 4.41, 4.41, 0, 0]
        lounch_y = [6.75, 6.75, 10.45, 10.45, 6.75]

        p = figure(plot_width=400, plot_height=400)
        p.patches([x, kitchen_x, bedRoom_x, hall_x, lounch_x],
                  [y, kitchen_y, bedRoom_y, hall_y, lounch_y],
                  fill_color=['transparent', 'transparent', 'transparent', 'transparent', 'transparent', 'transparent'],
                  line_width=2)
        return p
w = WebPage()
w.control()