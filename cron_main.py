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
    segments = ['Ermatingen', 'Wartburg']
    time_strava = {'Ermatingen':'week',
                   'Wartburg':'year'}

elif dt.datetime.now() < dt.datetime(2021, 4, 25, 23, 59):
    segments = ['Berlingen', 'Wartburg']
    time_strava = {'Berlingen':'week',
                   'Wartburg':'year'}
    
elif dt.datetime.now() < dt.datetime(2021, 5, 2, 23, 59):
    segments = ['Steckborn', 'Wartburg']
    time_strava = {'Steckborn':'week',
                   'Wartburg':'year'}
    
elif dt.datetime.now() < dt.datetime(2021, 5, 9, 23, 59):
    segments = ['Liebenfels', 'Wartburg']
    time_strava = {'Liebenfels':'week',
                   'Wartburg':'year'}
    
else:
    segments = []
    time_strava = 'week'  

pull = leaderboard_pull(keys['user'], keys['pwd'], keys['spreadsheet'], time_strava = time_strava, segments = segments)
pull.update_board() 