# -*- coding: utf-8 -*-
import os
import csv
from pymongo import MongoClient

ROOT_DIR = 'data/train'

class DataProcessor(object):

    def __init__(self,folderName):
        self.db = MongoClient('mongodb://localhost/SmartHome', 27017).SmartHome
        self.folderName=folderName

    def readData(self):
        dirs = [d[0] for d in os.walk(self.folderName)][1:]
        count=0
        for d in dirs:
            # try:
            #     print('loading %s/acceleration.csv...'%d)
            #     with open(d+'/acceleration.csv', 'r') as f:
            #         reader = csv.DictReader(f)
            #         for item in reader:
            #             for k,v in item.items():
            #                 try:
            #                     item[k]=float(v)
            #                 except:
            #                     pass
            #             self.db.acceleration.insert_one(item)
            #     print('done!\n')
            # except:
            #     print('no such file: %s/acceleration.csv...\n'%d)

            # try:
            #     print('loading %s/annotations_0.csv...'%d)
            #     with open(d+'/annotations_0.csv', 'r') as f:
            #         reader = csv.DictReader(f)
            #         for item in reader:
            #             for k, v in item.items():
            #                 try:
            #                     item[k] = float(v)
            #                 except:
            #                     pass
            #             item['pid'] = count
            #             self.db.annotations.insert_one(item)
            #
            #     print('done!\n')
            # except:
            #     print('no such file: %s/annotations_0.csv...\n'%d)


            # try:
            #     print('loading %s/annotations_1.csv...'%d)
            #     with open(d+'/annotations_1.csv', 'r') as f:
            #         reader = csv.DictReader(f)
            #         for item in reader:
            #             for k,v in item.items():
            #                 try:
            #                     item[k]=float(v)
            #                 except:
            #                     pass
            #             self.db.annotations.insert_one(item)
            #     print('done!\n')
            # except:
            #     print('no such file: %s/annotations_1.csv...\n'%d)

            try:
                print('loading %s/location_0.csv...'%d)
                with open(d+'/location_0.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    for item in reader:
                        for k,v in item.items():
                            try:
                                item[k]=float(v)
                            except:
                                pass
                        item['pid'] = count
                        self.db.location.insert_one(item)
                print('done!\n')
            except:
                print('no such file: %s/location_0.csv...\n'%d)

            # try:
            #     print('loading %s/location_1.csv...'%d)
            #     with open(d+'/location_1.csv', 'r') as f:
            #         reader = csv.DictReader(f)
            #         for item in reader:
            #             for k,v in item.items():
            #                 try:
            #                     item[k]=float(v)
            #                 except:
            #                     pass
            #             self.db.location.insert_one(item)
            #     print('done!\n')
            # except:
            #     print('no such file: %s/location_1.csv...\n'%d)
            #
            # try:
            #     print('loading %s/pir.csv...'%d)
            #     with open(d+'/pir.csv', 'r') as f:
            #         reader = csv.DictReader(f)
            #         for item in reader:
            #             for k,v in item.items():
            #                 try:
            #                     item[k]=float(v)
            #                 except:
            #                     pass
            #             self.db.pir.insert_one(item)
            #     print('done!\n')
            # except:
            #     print('no such file: %s/pir.csv...\n'%d)
            #
            # try:
            #     print('loading %s/video_hallway.csv...'%d)
            #     with open(d+'/video_hallway.csv', 'r') as f:
            #         reader = csv.DictReader(f)
            #         for item in reader:
            #             for k,v in item.items():
            #                 try:
            #                     item[k]=float(v)
            #                 except:
            #                     pass
            #             self.db.video_hallway.insert_one(item)
            #     print('done!\n')
            # except:
            #     print('no such file: %s/video_hallway.csv...\n'%d)
            #
            # try:
            #     print('loading %s/video_kitchen.csv...'%d)
            #     with open(d+'/video_kitchen.csv', 'r') as f:
            #         reader = csv.DictReader(f)
            #         for item in reader:
            #             for k,v in item.items():
            #                 try:
            #                     item[k]=float(v)
            #                 except:
            #                     pass
            #             self.db.video_kitchen.insert_one(item)
            #     print('done!\n')
            # except:
            #     print('no such file: %s/video_kitchen.csv...\n'%d)
            #
            # try:
            #     print('loading %s/video_living_room.csv...'%d)
            #     with open(d+'/video_living_room.csv', 'r') as f:
            #         reader = csv.DictReader(f)
            #         for item in reader:
            #             for k,v in item.items():
            #                 try:
            #                     item[k]=float(v)
            #                 except:
            #                     pass
            #             self.db.video_living_room.insert_one(item)
            #     print('done!\n')
            # except:
            #     print('no such file: %s/video_living_room.csv...\n'%d)
            count += 1

DataProcessor(ROOT_DIR).readData()