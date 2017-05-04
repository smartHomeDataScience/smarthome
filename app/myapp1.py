from bokeh.charts import Donut, Bar
from bokeh.layouts import widgetbox, row, layout, column
from bokeh.models.widgets import TextInput, Slider, PreText, Select
from bokeh.models import ColumnDataSource, ranges, LabelSet
from bokeh.plotting import figure, output_file, curdoc
from bokeh.models import LinearAxis, Range1d
from pymongo import MongoClient
import pandas as pd
import numpy as np


class WebPage:
    def __init__(self):
        self.map={
            'bath': (1,3.8,1,1),
            'bed1': (1,1,5,2),
            'bed2': (1,1,8.3,3),
            'hall': (0,3.1,8.2,3),
            'kitchen': (0,2.2,1.2,1),
            'living': (0,1,8.3,4),
            'stairs': (1,3.4,5.3,4),
            'study': (0,1.5,5,2),
            'toilet': (1,3.1,9,5)
        }


        self.db = MongoClient('mongodb://localhost/SmartHome', 27017).SmartHome
        self.read_data()
        # # ---------- annotation bar ----------
        x, y, c = self.annotation_bar('all', 'all')
        self.barSource = ColumnDataSource(dict(x=x, y=y, c=c))
        self.bar = figure(plot_width=1200, plot_height=320, x_range=self.barSource.data["x"])
        self.bar.vbar(source=self.barSource, x='x', top='y', bottom=0, width=0.5,color='c')
        # ---------- annotation bar ----------

        # ---------- stack1 bar ----------
        b, t, x, r, c, l = self.annotation_stack_bar('all')
        self.stack1Source = ColumnDataSource(dict(x=x, t=t, b=b, c=c, l=l))
        self.stack1 = figure(plot_width=1200, plot_height=320, x_range=r)
        self.stack1.vbar(source=self.stack1Source, x='x', top='t', bottom='b', width=0.5, color='c', legend='l')
        # ---------- stack1 bar ----------

        # ---------- ground map ----------
        x, y, c = self.groundMap()
        self.groundSource = ColumnDataSource(dict(x=x, y=y, c=c, t=[''], px=[0], py=[0]))
        self.ground = figure(plot_width=400, plot_height=400, title='Ground Floor')
        self.ground.patches(source=self.groundSource, xs='x', ys='y', fill_color='c', line_width=1)
        self.ground.text(source=self.groundSource, x='px', y='py', text='t')#, text_font_style="bold", text_font_size="15pt", **text_props)
        # ---------- ground map ----------

        # ---------- first map ----------
        x, y, c = self.firstMap()
        self.firstSource = ColumnDataSource(dict(x=x, y=y, c=c, t=[''], px=[0], py=[0]))
        self.first = figure(plot_width=400, plot_height=400, title='First Floor')
        self.first.patches(source=self.firstSource, xs='x', ys='y', fill_color='c', line_width=1)
        self.first.text(source=self.firstSource, x='px', y='py', text='t')
        # ---------- first map ----------

        # ---------- gantt chart ----------
        t, b, s, e = self.gantt_chart('all')
        self.ganttSource = ColumnDataSource(dict(t=t, b=b, s=s, e=e, lx=[0,0],ly=[0,10]))
        self.gantt = figure(plot_width=1200, plot_height=320, title='Gantt Chart')
        self.gantt.quad(source=self.ganttSource, top='t', bottom='b', left='s', right='e', color="#B3DE69")
        self.gantt.line(source=self.ganttSource, x='lx', y='ly', line_width=1)
        # ---------- gantt chart ----------


    def control(self):
        personId = Select(value='all', title="Person ID",
                          options=['all', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        room = Select(title="Room", value="all",
                      options=["all", "bath", "bed1", "bed2", "hall", "kitchen","living", "stairs", "study", "toilet"])
        slider = Slider(start=0, end=1900, value=0, step=3, title="Time")
        annotationText = PreText(text='Annotation: ')
        locationText = PreText(text='Location: ')

        controls = widgetbox([personId, room, slider, annotationText, locationText], width=400)

        stackBar = self.annotation_stack_bar('all')
        p = layout([
            [controls, self.first, self.ground],
            [self.gantt],
            [self.bar],
            [self.stack1]
        ])

        def update(_, __, ___):
            try:
                pid = personId.value
                roomValue = room.value

                x, y, c = self.annotation_bar(pid, roomValue)
                self.barSource.data = dict(x=x, y=y, c=c)

                b, t, x, r, c, l = self.annotation_stack_bar(pid)
                self.stack1Source.data = dict(x=x, t=t, b=b, c=c, l=l)

                t, b, s, e = self.gantt_chart(pid)
                self.ganttSource.data = dict(t=t, b=b, s=s, e=e, lx=[0, 0], ly=[0, 10])

            except:
                pass

        def updateTime(_, __, value):
            try:
                if personId.value == 'all':
                    pValue = 0
                else:
                    pValue = int(personId.value)

                t, b, s, e = self.gantt_chart(pValue)
                self.ganttSource.data = dict(t=t, b=b, s=s, e=e, lx=[int(value), int(value)], ly=[0, 10])

                location = self.db.timeBased.find({'t': int(value), 'pid': pValue})[0]['locationName']
                annotation = self.db.timeBased.find({'t': int(value), 'pid': pValue})[0]['annotationsName']
                locationText.text = 'Location: %s' % location
                annotationText.text = 'Annotation: %s' % annotation

                floor = self.map[location][0]
                pos = self.map[location][3]
                px = self.map[location][1]
                py = self.map[location][2]
                t = '%s: %s' % (location, annotation)

                x1, y1, c1 = self.groundMap()
                x2, y2, c2 = self.firstMap()

                if floor==0:
                    c1[pos] = 'BlueViolet'
                    c2=['transparent']*6
                    self.groundSource.data = dict(x=x1, y=y1, c=c1, t=[t], px=[px], py=[py])
                    self.firstSource.data = dict(x=x2, y=y2, c=c2, t=[''], px=[0], py=[0])
                else:
                    c2[pos] = 'BlueViolet'
                    c1 = ['transparent'] * 5
                    self.groundSource.data = dict(x=x1, y=y1, c=c1, t=[''], px=[0], py=[0])
                    self.firstSource.data = dict(x=x2, y=y2, c=c2, t=[t], px=[px], py=[py])

            except:
                locationText.text = 'Location: Unknown'
                annotationText.text = 'Annotation: Unknown'

        personId.on_change('value', update)
        room.on_change('value', update)
        slider.on_change('value', updateTime)
        curdoc().add_root(p)

    def read_data(self):
        self.timeBasedDf = pd.DataFrame(list(self.db.timeBased.find({})))
        self.locationDf = pd.DataFrame(list(self.db.location.find({})))
        # self.accelerationDf = pd.DataFrame(list(self.db.acceleration.find({})))

    def annotation_bar(self, pid, room):
        df = self.timeBasedDf
        if room != 'all':
            df = df[df['locationName'] == room]
        if pid != 'all':
            df = df[df['pid'] == int(pid)]

        data = pd.value_counts(df['annotationsName'].values)
        x = list(data.index)
        y = list(data)
        c = ["#%02x%02x%02x" % (r, g, 150) for r, g in zip(list(range(0, 200, 10)), list(range(190, -1, -10)))]
        return x, y, c

    def annotation_stack_bar(self, pid):
        df = self.timeBasedDf
        if pid != 'all':
            df = df[df['pid'] == int(pid)]
        data = df.groupby(["annotationsName", "locationName"]).size().reset_index(name="count")
        annotations = data['annotationsName'].unique()

        b, t, x, c, l = [], [], [], [], []

        colors = ['Fuchsia', 'Blue', 'Aqua', 'Lime', 'Yellow', 'Red', 'HotPink', 'LightCoral', 'Turquoise']
        locations = ['bath', 'bed1', 'bed2', 'hall', 'kitchen', 'living', 'stairs', 'study', 'toilet']
        color_dic = {}
        for i in range(9):
            color_dic[locations[i]] = colors[i]

        for i in annotations:
            curr = data[data['annotationsName'] == i]
            locations = curr['locationName'].unique()
            bottom = 0
            for j in locations:
                count = int(curr[curr['locationName'] == j]['count'])
                top = bottom + count
                b.append(bottom)
                t.append(top)
                x.append(i)
                c.append(color_dic[j])
                l.append(j)
                bottom = top
        return b, t, x, list(annotations), c, l

    def annotation_pie(self, pid):
        df = self.timeBasedDf
        if pid != 'all':
            df = df[df['pid'] == int(pid)]
        data = pd.value_counts(df['annotationsName'].values)
        p = Donut(data, title='Time Spending on annotations')
        return p

    def location_pie(self, pid):
        df = self.timeBasedDf
        if pid != 'all':
            df = df[df['pid'] == int(pid)]
        data = pd.value_counts(df['locationName'].values)

        p = Donut(data, title='Time Spending for locations')
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

        return [x, bath_x, bedroom1_x, bedroom2_x, landing_x, wc_x], \
               [y, bath_y, bedroom1_y, bedroom2_y, landing_y, wc_y], ['transparent'] * 6

    def groundMap(self):
        x = [1.65, 4.65, 4.65, 0, 0, 1.65, 1.65]
        y = [0, 0, 10.45, 10.45, 3.15, 3.15, 0]

        kitchen_x = [1.65, 4.65, 4.65, 1.65, 1.65]
        kitchen_y = [0, 0, 3.15, 3.15, 0]

        bedRoom_x = [0, 2.9, 2.9, 0, 0]
        bedRoom_y = [3.15, 3.15, 6.75, 6.75, 3.15]

        hall_x = [3.65, 4.65, 4.65, 3.65, 3.65]
        hall_y = [6.75, 6.75, 10.45, 10.45, 6.75]

        lounch_x = [0, 3.65, 3.65, 0, 0]
        lounch_y = [6.75, 6.75, 10.45, 10.45, 6.75]

        return [x, kitchen_x, bedRoom_x, hall_x, lounch_x], \
               [y, kitchen_y, bedRoom_y, hall_y, lounch_y], ['transparent'] * 5

    def gantt_chart(self, pid):
        df = self.locationDf
        if pid == 'all':
            pid = 0

        df = df[df['pid'] == int(pid)]
        s = list(df['start'])
        e = list(df['end'])
        b = list(df['index'])
        t = [b[i] + 0.5 for i in range(len(s))]
        return t, b, s, e

    # def acceleration_bar(self,pid):
    #     df = self.accelerationDf

w = WebPage()
# w.gantt_chart('all')
w.control()
# w.read_data()