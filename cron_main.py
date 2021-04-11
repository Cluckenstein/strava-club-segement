#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 21:38:47 2021

@author: maximilianreihn
"""


from worker import leaderboard_pull
import json


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

segments = ['Berlingen']
time_strava = 'week'

pull = leaderboard_pull(keys['user'], keys['pwd'], keys['spreadsheet'], time_strava = 'month', segments = segments)
pull.update_board() 