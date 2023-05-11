#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import requests
import re
import datetime
import holidays
import json
import pandas as pd
import copy
import openpyxl
from sqlalchemy import create_engine
import schedule
import time


# In[12]:


def scrape_and_paste():

    #Parse
    html_text = requests.get('https://alpuente.mx/matamoros/').text
    soup = BeautifulSoup(html_text, 'lxml')
    containers = soup.find_all("ul", {"class": "list-group no-border text-left"})
    h2s = soup.find_all('h2')

    #Nombre de Puentes y que tipo
    puentes_list = ['Tomates Std', 'Tomates Ready', 'Tomates Express',
                    'Indios Std', 'Indios Ready', 'Indios Express',
                    'Nuevo Std', 'Nuevo Ready', 'Nuevo Express',
                    'Viejo Std', 'Viejo Ready', 'Viejo Express']
    puente_nombre_ = pd.DataFrame(puentes_list, columns=['puente_nombre_'])
                    
    puentes_short = ['Tomates', 'Indios', 'Nuevo', 'Viejo']
    puente_nombre_short_ = pd.DataFrame(puentes_short, columns=['puente_nombre__'])
    

    #Convert minutes or hours, etc to minutes
    def time_to_minutes(time_str):
        time_list = time_str.split()
        minutes = 0
        for i in range(len(time_list)):
            if time_list[i] == "hr" or time_list[i] == "hrs" or time_list[i] == "h":
                minutes += int(time_list[i-1]) * 60
            elif time_list[i] == "min" or time_list[i] == "mins":
                minutes += int(time_list[i-1])
        return minutes

        # If we didn't match any pattern, return None
        return None

    #Get the wait time
    tiempos_generales = []

    tiempo_list = []
    for container in containers:
        group_items = container.find_all("li", {"class": "list-group-item"})
        for item in group_items:
            text_muted = item.find("span", {"class": "text-muted"})
            if text_muted:
                if "cerrado" in text_muted.text:
                    tiempo_list.append(None)
                else:
                    pull_right = item.find("span", {"class": "pull-right"})
                    if pull_right:
                        tiempo_en_minutos = time_to_minutes(pull_right.text)
                        tiempo_list.append(tiempo_en_minutos)
    wait_time_minutes_ = pd.DataFrame(tiempo_list, columns=['wait_time_minutes_'])

    #Tiempo for short
    tiempo_list_short=[]
    for i in range(1,5):
        tiempo_list_short.append(h2s[i].text)
    
    wait_time_minutes_short = []
    for i in tiempo_list_short:
        wait_time_minutes_short.append(time_to_minutes(i))
    
    wait_time_minutes_short_ = pd.DataFrame(wait_time_minutes_short, columns=['wait_time_minutes__'])
    
    #Get Lanes Open

    lines_open_list = []
    for container in containers:
        group_items = container.find_all("li", {"class": "list-group-item"})
        for item in group_items:
            text_muted = item.find("span", {"class": "text-muted"})
            if text_muted:
                if "cerrado" in text_muted.text:
                    lines_open_list.append('0')
                else:
                    lines_open_list.append(text_muted.text.split(' ')[0][0])
    lanes_open_ = pd.DataFrame(lines_open_list, columns=['lanes_open_'])
    
    #get day of week
    
    weekday = []
    weekday_short = []
    for i in range(len(tiempo_list)):
        weekday.append(datetime.date.today().weekday())
    for i in range(len(tiempo_list_short)):
        weekday_short.append(datetime.date.today().weekday())
        
    weekday_ = pd.DataFrame(weekday, columns=['day_of_week_'])
    weekday_short_ = pd.DataFrame(weekday_short, columns=['day_of_week__'])

    # get date to the minute

    now = datetime.datetime.now()

    dates_list = []
    dates_list_short = []
    for i in range(len(tiempo_list)):
        dates_list.append(now)
        
    for i in range(len(tiempo_list_short)):
        dates_list_short.append(now)
        
    date_ = pd.DataFrame(dates_list, columns=['date_'])
    date_short_ = pd.DataFrame(dates_list_short, columns=['date__'])


    # If it is a holidays then it returns True else False
    us_holidays = holidays.US()
    mx_holidays = holidays.MX()
    today = now.today()
    holiday_list = []
    holiday_list_short = []
    if (today in us_holidays) or (today in mx_holidays):
        holiday =  1
    else:
        holiday = 0
    for i in range(len(tiempo_list)):
        holiday_list.append(holiday)
    for i in range(len(tiempo_list_short)):
        holiday_list_short.append(holiday)
    holiday_ = pd.DataFrame(holiday_list, columns=['holiday_'])
    holiday_short_ = pd.DataFrame(holiday_list_short, columns=['holiday__'])

    #Tell if its weekend or weekday

    day = datetime.datetime.today().weekday()

    weekend_list = []
    weekend_list_short = []
    if day > 5:

        weekend = 1
    else:
        weekend = 0
    for i in range(len(tiempo_list)):
        weekend_list.append(weekend)
    for i in range(len(tiempo_list_short)):
        weekend_list_short.append(weekend)
    weekend_ = pd.DataFrame(weekend_list, columns=['weekend_'])
    weekend_short_ = pd.DataFrame(weekend_list_short, columns=['weekend__'])
    
    #Which Day of the Week
    day_of_week = datetime.datetime.today().weekday()

    day_of_week_list = []
    day_of_week_list_short = []
    for i in range(len(tiempo_list)):
        day_of_week_list.append(day_of_week)
    for i in range(len(tiempo_list_short)):
        day_of_week_list_short.append(day_of_week)
    day_of_week_ = pd.DataFrame(day_of_week_list, columns=['day_of_week_'])
    day_of_week_short_ = pd.DataFrame(day_of_week_list_short, columns=['day_of_week__'])
    

    #Mark if its a week with a holiday

    week_with_holiday = []
    holiday_week_list = []
    holiday_week_list_short = []
    for i in range(-3,4,1):
        holiday_check = []
        date1 = datetime.datetime.now()
        end_date = date1 + datetime.timedelta(days=i)
        if (end_date in us_holidays) or (end_date in mx_holidays):
            holiday =  1
        else:
            holiday = 0
        holiday_check.append(holiday)

    if 1 in holiday_check:
        week_with_holiday.append(1)
    else:
        week_with_holiday.append(0)
    for i in range(len(tiempo_list)):
        holiday_week_list.append(weekend)
    for i in range(len(tiempo_list_short)):
        holiday_week_list_short.append(weekend)
    holiday_week_ = pd.DataFrame(holiday_week_list, columns=['holiday_week_'])
    holiday_week_short_ = pd.DataFrame(holiday_week_list_short, columns=['holiday_week__'])


    #Connnect to the DB
    engine = create_engine('mysql+mysqlconnector://root:password@localhost:3306/puentes')

    #Append to a new dataframe
    combined_data = pd.DataFrame()
    combined_data_short = pd.DataFrame()
    combined_data = pd.concat([date_,weekday_, weekend_, holiday_, holiday_week_,
                               lanes_open_, wait_time_minutes_, puente_nombre_], axis=1)
    combined_data_short = pd.concat([date_short_,weekday_short_, weekend_short_, holiday_short_, holiday_week_short_,
                               wait_time_minutes_short_, puente_nombre_short_], axis=1)

    #Write to MySQL
    combined_data.to_sql('puentes_all', con=engine, if_exists='append', index=False)
    combined_data_short.to_sql('puentes_short', con=engine, if_exists='append', index=False)
    pass


# In[14]:


scrape_and_paste()


# In[5]:


datetime.date.today().weekday()


# In[ ]:




