from bokeh.charts import Donut, Bar
from bokeh.layouts import widgetbox, row, layout, column
from bokeh.models.widgets import TextInput, Slider, PreText, Select
from bokeh.plotting import figure, output_file, curdoc

from pymongo import MongoClient
import pandas as pd


class WebPage:
    def __init__(self):
        self.db = MongoClient('mongodb://localhost/SmartHome', 27017).SmartHome
        output_file("index.html")

    def control(self):
        personId = Select(value='all', title="Person ID", options=['all', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        room = Select(title="Room", value="all", options=["all", "bath", "bed1", "bed2", "hall", "kitchen",
                                                            "living", "stairs", "study", "toilet"])
        slider = Slider(start=0, end=1800, value=1, step=1, title="Time")
        annotationText = PreText(text='Annotation: ')
        locationText = PreText(text='Location: ')

        controls = widgetbox([personId, room, slider, annotationText, locationText], width=300)

        stackBar = self.annotationStackBar('all')
        p = layout([
            [controls,
             layout(
                 [[self.firstMap(),self.groundMap()],
                 [self.annotationDistribution('all'), self.locationDistribution('all')],
                 [self.annotationBar('all', 'all')], [stackBar[0]],[stackBar[1]]]
             )]
        ])

        def update(_, __, ___):
            try:
                pid = personId.value
                roomValue = room.value

                sb = self.annotationStackBar(pid)
                p.children[0].children[1] = layout(
                    [[self.firstMap(), self.groundMap()],
                     [self.annotationDistribution(pid), self.locationDistribution(pid)],
                     [self.annotationBar(pid, roomValue)], [sb[0]],
                     [sb[1]]
                     ])
            except:
                pass

        def updateTime(_, __, value):
            try:
                location = self.db.timeBasedLocation.find({'t': int(value), 'pid': int(pid.value)})
                annotation = self.db.timeBasedAnnotations.find({'t': int(value), 'pid': int(pid.value)})

                locationText.text = 'Location: %s' % location[0]['name']
                annotationText.text = 'Annotation: %s' % annotation[0]['name']
            except:
                locationText.text = 'Location: Unknown'
                annotationText.text = 'Annotation: Unknown'

        personId.on_change('value', update)
        room.on_change('value', update)
        slider.on_change('value', updateTime)

        # toggle = Toggle(label="Refresh", button_type="success")

        curdoc().add_root(p)
        # curdoc().add_root(p2)

    def annotationBar(self, pid, room):
        annotation = {
            "a_ascend": 0, "a_descend": 0, "a_jump": 0, "a_loadwalk": 0, "a_walk": 0,
            "p_bent": 0, "p_kneel": 0, "p_lie": 0, "p_sit": 0, "p_squat": 0, "p_stand": 0,
            "t_bend": 0, "t_kneel_stand": 0, "t_lie_sit": 0, "t_sit_lie": 0, "t_sit_stand": 0,
            "t_stand_kneel": 0, "t_stand_sit": 0, "t_straighten": 0, "t_turn": 0, "other": 0
        }
        query = {'annotationsName': {'$exists': True}}
        if pid!='all':
            query['pid'] = int(pid)
        if room!='all':
            query['locationName']=room
        cursor = self.db.timeBased.find(query)
        for i in cursor:
            annotation[i['annotationsName']] += 1


        data = pd.Series(annotation)
        median=data.median()
        for i in data[data <= median]:
            data['other'] += i
        data = data[data > median]
        p = Bar(data, title='Time Spending on Annotations: person #%s, location:%s' % (pid, room))
        return p

    def annotationStackBar(self, pid):
        annotation = [
            "a_ascend", "a_descend", "a_jump", "a_loadwalk", "a_walk", "p_bent", "p_kneel", "p_lie",
            "p_sit", "p_squat", "p_stand", "t_bend","t_kneel_stand", "t_lie_sit", "t_sit_lie",
            "t_sit_stand", "t_stand_kneel", "t_stand_sit", "t_straighten", "t_turn"
        ]
        room = ["bath", "bed1", "bed2", "hall", "kitchen", "living", "stairs", "study", "toilet"]

        query = {'annotationsName': {'$exists': True}}

        th=100
        if pid != 'all':
            query['pid'] = int(pid)
            th=10
        l = []
        for i in room:
            query['locationName'] = i
            for j in annotation:
                query['annotationsName'] = j
                c = self.db.timeBased.count(query)
                l.append([c, i, j])

        data = pd.DataFrame(l, columns=['count', 'location', 'annotation'])
        data = data[data['count'] > th]
        p = Bar(data, values='count', stack='location', label='annotation',
                legend='top_right', title='Time Spending on Annotations: person #%s' % pid)
        p1 = Bar(data, values='count', stack='annotation', label='location',
                 legend='top_right', title='Time Spending on Location: person #%s' % pid)
        return p, p1

    def annotationDistribution(self, pid):
        annotation = {
            "a_ascend": 0,"a_descend": 0, "a_jump": 0, "a_loadwalk": 0, "a_walk": 0,
            "p_bent": 0, "p_kneel": 0, "p_lie": 0, "p_sit": 0, "p_squat": 0, "p_stand": 0,
            "t_bend": 0, "t_kneel_stand": 0, "t_lie_sit": 0, "t_sit_lie": 0, "t_sit_stand": 0,
            "t_stand_kneel": 0, "t_stand_sit": 0, "t_straighten": 0, "t_turn": 0,"other": 0
        }

        if pid == 'all':
            cursor = self.db.annotations.find({})
            title = 'Time Spending on annotations: All(seconds).'
            th = 300
        else:
            cursor = self.db.annotations.find({'pid': int(pid)})
            title = 'Time Spending on annotations: person #%s (seconds).' % pid
            th = 30

        for i in cursor:
            annotation[i['name']] += float(i['end']) - float(i['start'])
        data = pd.Series(annotation)
        for i in data[data<=th]:
            data['other'] += i
        data = data[data > th]
        p = Donut(data, title=title)
        return p

    def locationDistribution(self, pid):
        location={
            "bath": 0,
            "bed1": 0,
            "bed2": 0,
            "hall": 0,
            "kitchen": 0,
            "living": 0,
            "stairs": 0,
            "study": 0,
            "toilet": 0,
            "other": 0
        }
        if pid == 'all':
            cursor = self.db.location.find({})
            title = 'Time Spending in Locations: All(seconds).'
            th = 500
        else:
            cursor = self.db.location.find({'pid': int(pid)})
            title = 'Time Spending in Locations: person #%s (second).' % pid
            th = 50

        for i in cursor:
            location[i['name']] += float(i['end']) - float(i['start'])

        data = pd.Series(location)
        for i in data[data <= th]:
            data['other'] += i
        data = data[data > th]
        p = Donut(data, title=title)
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

        p = figure(plot_width=400, plot_height=400, title='First Floor')
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

        p = figure(plot_width=400, plot_height=400, title='Ground Floor')
        p.patches([x, kitchen_x, bedRoom_x, hall_x, lounch_x],
                  [y, kitchen_y, bedRoom_y, hall_y, lounch_y],
                  fill_color=['transparent', 'transparent', 'transparent', 'transparent', 'transparent', 'transparent'],
                  line_width=1)
        return p

w = WebPage()
w.control()