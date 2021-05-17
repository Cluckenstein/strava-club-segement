#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 21:38:47 2021

@author: maximilianreihn
"""


from worker import leaderboard_pull
import json
import datetime as dt


with open('secret_keys.json') as check:
  keys = json.load(check)
  
#possible segments 
'Ermatingen'
'Berlingen'
'Steckborn'
'Liebenfels'
'Wartburg'

#possible time filters 
'month'
'week'
'all'
'year'

if dt.datetime.now() < dt.datetime(2021, 4, 18, 23, 59):
    segments = ['Ermatingen', 'Berlingen', 'Steckborn', 'Liebenfels', 'Wartburg']
    time_strava = {'Berlingen':'week',
                    'Ermatingen':'week',
                    'Steckborn':'week',
                    'Liebenfels':'week',
                    'Wartburg':'week'}

elif dt.datetime.now() < dt.datetime(2021, 4, 25, 23, 59):
    segments = ['Ermatingen', 'Berlingen', 'Steckborn', 'Liebenfels', 'Wartburg']
    time_strava = {'Berlingen':'week',
                    'Ermatingen':'week',
                    'Steckborn':'week',
                    'Liebenfels':'week',
                    'Wartburg':'week'}
    
elif dt.datetime.now() < dt.datetime(2021, 5, 2, 23, 59):
    segments = ['Ermatingen', 'Berlingen', 'Steckborn', 'Liebenfels', 'Wartburg']
    time_strava = {'Berlingen':'week',
                    'Ermatingen':'week',
                    'Steckborn':'week',
                    'Liebenfels':'week',
                    'Wartburg':'week'}
    
elif dt.datetime.now() < dt.datetime(2021, 5, 9, 23, 59):
    segments = ['Ermatingen', 'Berlingen', 'Steckborn', 'Liebenfels', 'Wartburg']
    time_strava = {'Berlingen':'week',
                    'Ermatingen':'week',
                    'Steckborn':'week',
                    'Liebenfels':'week',
                    'Wartburg':'week'}
    
else:
    print('no segments to do ')
    segments = []
    time_strava = 'week'  


pull = leaderboard_pull(keys['user'], keys['pwd'], keys['spreadsheet'], time_strava = time_strava, segments = segments)
pull.update_board() 
print('success on scirpt')