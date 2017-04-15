# -*- coding: utf-8 -*-
import os
import csv
from pymongo import MongoClient
import math

ROOT_DIR = 'data/train'

class DataProcessor(object):

    def __init__(self,folderName):
        self.db = MongoClient('mongodb://localhost/SmartHome', 27017).SmartHome
        self.folderName=folderName

    def readData(self):
        dirs = [d[0] for d in os.walk(self.folderName)][1:]
        count=0
        for d in dirs:
            print('loading %s/location_0.csv...'%d)
            with open(d+'/location_0.csv', 'r') as f:
                reader = csv.DictReader(f)
                for item in reader:
                    for i in range(math.ceil(float(item['start'])),math.floor(float(item['end']))+1):
                        dict = {}
                        dict['t']=i
                        dict['pid']=count
                        dict['locationIndex']=item['index']
                        dict['locationName'] = item['name']
                        self.db.timeBased.insert_one(dict)
                print('done!\n')

            print('loading %s/annotations_0.csv...' % d)
            with open(d + '/annotations_0.csv', 'r') as f:
                reader = csv.DictReader(f)
                for item in reader:
                    for i in range(math.ceil(float(item['start'])), math.floor(float(item['end'])) + 1):
                        dict = {}
                        dict['t'] = i
                        dict['pid'] = count
                        dict['annotationsIndex'] = item['index']
                        dict['annotationsName'] = item['name']

                        # try:
                        a = self.db.timeBased.update(
                            {'t': i, 'pid': count},
                            {'$set':
                                {
                                    'annotationsIndex': item['index'],
                                    'annotationsName': item['name']
                                }
                             }
                        )
                        if a['n']<1:
                            self.db.timeBased.insert_one(dict)
            print('done!\n')
            count += 1
            # except:
            #     print('no such file: %s/location_0.csv...\n'%d)

DataProcessor(ROOT_DIR).readData()