#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 21:32:07 2021

@author: maximilianreihn
"""


import datetime
import time
import os.path
import pandas as pd 
pd.options.mode.chained_assignment = None 
import numpy as np
import json
import requests
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup




class leaderboard_pull(object):
    
    
    def __init__(self, user, pwd, spreadsheet, time_frame = datetime.datetime(2001, 1, 1), time_strava = 'month', segments = []): 
        self.user = user
        self.pwd = pwd
        self.time_frame = time_frame
        self.time_strava = time_strava
        self.boards = {}
        self.riders = {}
        self.spreadsheet = spreadsheet
        self.segments_id = {'Berlingen': '9518185',
                             'Ermatingen': '4373308',
                             'Wartburg': '13663639',
                             'Steckborn': '7850497',
                             'Liebenfels': '1651294'}
        
        #segments list of the segments to be updated
        
        self.segments = {k:self.segments_id[k] for k in segments}
            
            
        if type(time_strava) != str:
            self.diff_filters = True
            self.filters = {self.segments_id[k]: time_strava[k] for k in time_strava}
        else:
            self.diff_filters = False
        
        self.segment_range = {'9518185': {'m': 'M6:N46', 'w': 'K6:L46'}, #Berlingen
                              '4373308': {'m': 'G6:H46', 'w': 'E6:F46'}, #Ermatingen
                              '13663639': {'m': 'AE6:AF46', 'w': 'AC6:AD46'}, #Wartburg
                              '7850497': {'m': 'S6:T46', 'w': 'Q6:R46'}, #Steckborn
                              '1651294': {'m': 'Y6:Z46', 'w': 'W6:X46'},#Liebenfels
                              'gesamt': {'m': 'AK6:AL46', 'w': 'AI6:AJ46'} }
        
        self.manual_range = {'9518185': 'O6:P46', #Berlingen
                              '4373308': 'I6:J46', #Ermatingen
                              '13663639': 'AG6:AH46', #Wartburg
                              '7850497': 'U6:V46', #Steckborn
                              '1651294': 'AA6:AB46' }#Liebenfels
        
        
        
        

        # If modifying these scopes, delete the file token.json.
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
 
        self.google_service = build('sheets', 'v4', credentials=creds)
        
        
    def update_board(self):
        try:
            options = Options()
            options.headless = True
            
            driver = webdriver.Chrome(options=options, executable_path='/Users/maximilianreihn/Downloads/chromedriver')
            url = 'https://status.strava.com'     
            driver.get(url)
            html=driver.page_source
            
        except:
            html = 'Major Outage Major Outage'
            
        if html.count('Major Outage') > 1:
            print("strava timed out, no update on leaderboard")
        else:
            print('strava is responding normally')
            self.get_leaderboard()
            self.parse()
            self.get_riders()
    
            # self.segment_id = self.segments[ort]
            self.get_segment_time()
                
            self.make_json()
            self.make_leaderboard()

        
        
    def make_json(self):
        print('saving and checking best times')
        rider_times = {rider: self.riders[rider] for rider in self.riders}#if len(self.riders[rider].keys())>2}
        
        try:
            with open('best_times.json', 'r') as saver:
                data = json.load(saver)
                
            new_times = {}
            
            both = set(rider_times).intersection(set(data))
            
            only_new = set(rider_times) - set(data)
            only_old = set(data) - set(rider_times)
            
            for rider in list(only_new):
                new_times[rider] = rider_times[rider]
            for rider in list(only_old):
                new_times[rider] = data[rider]
                
                
                
            for rider in list(both):
                new_times[rider] = {'strava': rider_times[rider]['strava'], 'sex':rider_times[rider]['sex']}
                for segment in [self.segments_id[k] for k in self.segments_id]:
                    if segment in data[rider] and segment in rider_times[rider]:
                        
                        new_times[rider][segment] = min(data[rider][segment], rider_times[rider][segment])
                        
                    elif segment in data[rider]:
                        new_times[rider][segment] = data[rider][segment]
                    elif segment in rider_times[rider]:
                        new_times[rider][segment] = rider_times[rider][segment]
             
                
        except:
            new_times = rider_times.copy()
            
        self.riders = new_times.copy()
            
        with open('best_times.json', 'w') as saver:
            json.dump(new_times, saver)
        
        
        
        
    def make_leaderboard(self):
        print('creating leaderboard for sheet')


        for seg in self.segments:
            print('filling out ',seg)
            self.segment_id = self.segments_id[seg]
            
            female = {rider:self.riders[rider][self.segment_id] for rider in self.riders if self.riders[rider]['sex']=='w' and self.segment_id in self.riders[rider]}
            male = {rider:self.riders[rider][self.segment_id] for rider in self.riders if self.riders[rider]['sex']=='m' and self.segment_id in self.riders[rider]}
            
            sorted_f = sorted(female.items(), key=lambda x: x[1])
            sorted_m = sorted(male.items(), key=lambda x: x[1])
            
            fastest_f = min([female[k] for k in female])
            fastest_m = min([male[k] for k in male])

            values_f = []
            values_m = []
            
            for i in range(len(sorted_f)):
                time_points = self.make_time_string(sorted_f[i][1])
                time_points += ' (+'+ str(np.round( (sorted_f[i][1]/fastest_f - 1)* 100 , 1)) + '%)'         
                values_f.append([sorted_f[i][0], time_points])
                
            for i in range(len(sorted_m)):
                time_points = self.make_time_string(sorted_m[i][1])
                time_points += ' (+'+ str(np.round( (sorted_m[i][1]/fastest_m -1)*100, 1)) + '%)'
                values_m.append([sorted_m[i][0], time_points])
                
            #clean and fill then 
            for val in [[ [['']*2]*36, [['']*2]*36 ] , [values_f, values_m]]:
            
                request = self.google_service.spreadsheets().values().update(spreadsheetId=self.spreadsheet,
                                                                             range=self.segment_range[self.segment_id]['w'], 
                                                                             valueInputOption = 'RAW',
                                                                             body=dict(
                                                                                majorDimension='ROWS',
                                                                                values=val[0]))
                request.execute()
                
                request = self.google_service.spreadsheets().values().update(spreadsheetId=self.spreadsheet,
                                                                             range=self.segment_range[self.segment_id]['m'], 
                                                                             valueInputOption = 'RAW',
                                                                             body=dict(
                                                                                majorDimension='ROWS',
                                                                                values=val[1]))
                request.execute()
       

        quickest = {}
        for seg in self.segments_id:
            self.segment_id = self.segments_id[seg]
            
            female = {rider:self.riders[rider][self.segment_id] for rider in self.riders if self.riders[rider]['sex']=='w' and self.segment_id in self.riders[rider]}
            male = {rider:self.riders[rider][self.segment_id] for rider in self.riders if self.riders[rider]['sex']=='m' and self.segment_id in self.riders[rider]}
            
            sorted_f = sorted(female.items(), key=lambda x: x[1])
            sorted_m = sorted(male.items(), key=lambda x: x[1])
            
            quickest[self.segment_id] = {'w': min([female[k] for k in female]), 'm':min([male[k] for k in male])}
  
         
        gesamt_punkte_f = {}
        gesamt_punkte_m = {}
        for rider in self.riders:
            #warthburg: '13663639'
            
            if len(list(self.riders[rider].keys())) > 4:
                points = []
                
                for seg in self.segments_id:
                    if self.segments_id[seg] in self.riders[rider]:
                        points.append(np.round((self.riders[rider][self.segments_id[seg]]/ quickest[self.segments_id[seg]][self.riders[rider]['sex']] -1 )*100, 1 ))
                        
                best_3 = np.sort(points)[:3]
                gesamt = sum(best_3)
                
                if self.riders[rider]['sex'] == 'w':
                    gesamt_punkte_f[rider] = gesamt
                else:
                    gesamt_punkte_m[rider] = gesamt
                

        sorted_f = sorted(gesamt_punkte_f.items(), key=lambda x: x[1])
        sorted_m = sorted(gesamt_punkte_m.items(), key=lambda x: x[1])
        
        values_f = []
        values_m = []
        
        for i in range(len(sorted_f)):        
            values_f.append([sorted_f[i][0], sorted_f[i][1]])
            
        for i in range(len(sorted_m)):
            values_m.append([sorted_m[i][0], sorted_m[i][1]])
            
        #clean and fill then 
        for val in [[ [['']*2]*36, [['']*2]*36 ] , [values_f, values_m]]:
        
            request = self.google_service.spreadsheets().values().update(spreadsheetId=self.spreadsheet,
                                                                         range=self.segment_range['gesamt']['w'], 
                                                                         valueInputOption = 'RAW',
                                                                         body=dict(
                                                                            majorDimension='ROWS',
                                                                            values=val[0]))
            request.execute()
            
            request = self.google_service.spreadsheets().values().update(spreadsheetId=self.spreadsheet,
                                                                         range=self.segment_range['gesamt']['m'], 
                                                                         valueInputOption = 'RAW',
                                                                         body=dict(
                                                                            majorDimension='ROWS',
                                                                            values=val[1]))
            request.execute()
            
                
                
                
                
        request = self.google_service.spreadsheets().values().update(spreadsheetId=self.spreadsheet,
                                                                         range='O2:P2', 
                                                                         valueInputOption = 'RAW',
                                                                         body=dict(
                                                                            majorDimension='ROWS',
                                                                            values=[[str(datetime.datetime.now())[:-7]]]))
        request.execute()
    
        
        
    @staticmethod
    def make_time_string(seconds):
        first = int(np.floor(seconds/60))
        sec = int(seconds % 60)
        if first<10:
            first = '0'+str(first)
        else:
            first = str(first)
            
        if sec<10:
            sec = '0'+str(sec)
        else:
            sec = str(sec)
            
        return first + ':' + sec
        
    
    def get_segment_time(self):
        print('listing strava and manual times')
        for segment in self.segments:
            segment_id = self.segments_id[segment]
            
            
            #Strava Times
            for i in self.boards[segment_id].index:
                if self.boards[segment_id]['Name'][i] in self.riders and self.boards[segment_id]['Date'][i] >= self.time_frame:
                    if self.riders[self.boards[segment_id]['Name'][i]]['strava']:              
                        self.riders[self.boards[segment_id]['Name'][i]][segment_id] = self.boards[segment_id]['Time'][i]
                    
            #Manual times
            sheet = self.google_service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.spreadsheet,
                                        range=self.manual_range[segment_id]).execute()
            values = result.get('values', [])
            for rider in self.riders:
                if not self.riders[rider]['strava']:
                    try:
                        index = [k[0] for k in values].index(rider)
                        time_string = values[index][1]
                        time_ride = int(time_string[:time_string.index(':')])*60 + int(time_string[time_string.index(':')+1:])
                        self.riders[rider][segment_id] = int(time_ride)
                    except:
                        None
            
            
    def get_riders(self):
        print('getting riders')
        # The ID and range of a sample spreadsheet.
        range_riders = 'A6:D46'
        
        # Call the Sheets API
        sheet = self.google_service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.spreadsheet,
                                    range=range_riders).execute()
        
        values = result.get('values', [])
        for rider in values:
            if rider[0] != '':
                self.riders[rider[0]] = {'sex': self.get_sex(rider[1], rider[2]),
                                         'strava':rider[3]=='TRUE'}
                
               
    @staticmethod
    def get_sex(is_female, is_male):
        if is_female == "TRUE":
            return 'w'
        else:
            return 'm'
                
    
    
    def parse(self):
        print('parsing leaderboard')
        for segment in self.segments:

            if self.boards[self.segments[segment]]['Name'][0] != 'No results found':
                for i in self.boards[self.segments[segment]].index:
                    self.boards[self.segments[segment]]['Date'][i] = datetime.datetime.strptime(self.boards[self.segments[segment]]['Date'][i], '%b %d, %Y')
                    self.boards[self.segments[segment]]['Time'][i] = int(self.boards[self.segments[segment]]['Time'][i][:self.boards[self.segments[segment]]['Time'][i].index(':')]) *60\
                        + int(self.boards[self.segments[segment]]['Time'][i][self.boards[self.segments[segment]]['Time'][i].index(':')+1:])
                    
                    
        
    
    
    def get_leaderboard(self):       
        url = 'http://www.strava.com/login'
        
        options = Options()
        options.headless = True
        
        driver = webdriver.Chrome(options=options, executable_path='/Users/maximilianreihn/Downloads/chromedriver')
        
        driver.get(url)
        
        logbtn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='login-button']")))
        
        
        usr = driver.find_element_by_xpath("//*[@id='email']")
        passw = driver.find_element_by_xpath("//*[@id='password']")
        
        usr.send_keys(self.user)
        passw.send_keys(self.pwd)
        logbtn.click()
    
        time.sleep(2)
        
        for segment in self.segments:
            print('pulling ',segment)
            
            self.boards[self.segments[segment]] = {}
            if self.diff_filters:
                filter_all = self.time_strava[segment]

            else:
                filter_all = self.time_strava
                
            seg_url = 'https://www.strava.com/segments/'+str(self.segments[segment])
            driver.get(seg_url)

            asc_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='premium-enhanced']/ul/ul[1]/li[5]/a")))
            
    
            #ASC Filter //*[@id="premium-enhanced"]/ul/ul[1]/li[5]/a//*[@id="premium-enhanced"]/ul/ul[1]/li[5]/a
            asc_filter.click()
            time.sleep(3)
            
            time_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='segment-results']/div[2]/table/tbody/tr/td[3]/div/button")))
            time_filter.click()
            time.sleep(1)
            filters = {'week': "//*[@id='segment-results']/div[2]/table/tbody/tr/td[3]/div/ul/li[3]",
                       'month': "//*[@id='segment-results']/div[2]/table/tbody/tr/td[3]/div/ul/li[4]",
                       'all': "//*[@id='all-time']",
                       'year': "//*[@id='this-year']"}
            
            choosen_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, filters[filter_all])))

            choosen_filter.click()
            time.sleep(6)
            
            stop = 0
            board = pd.DataFrame()
            while not stop:
                
                html=driver.page_source
                soup=BeautifulSoup(html,'html.parser')
                div=soup.select_one('#results > table')
                table=pd.read_html(str(div))
            
                board = board.append(table[0], ignore_index=True)
            
                try:
                    next_page = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[@id='results']/nav/ul/li[4]/a")))
                    next_page.click()
                    time.sleep(3)
                except WebDriverException:
                    stop = 1
                    
            time.sleep(1)
            
            self.boards[self.segments[segment]] = board

        
        