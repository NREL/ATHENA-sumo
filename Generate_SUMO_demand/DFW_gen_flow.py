########################
# Author: Joseph Severino
# Organization: NREL
# Project: ATHENA
########################

'''
    The following code serves to clean and format the operational model
    data that predictes the volume every half hour so that it can be used to
    create the demand files for SUMO to run a simulation. It also creates the
    additional file for SUMO so that the each vehicle knows the locations for
    stopping on the network.
'''

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from lxml import etree
from copy import copy
import os
import inspect
from xml.dom import minidom
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def month(string):
    string = string.lower()
    months = ['january','febuary','march','april','may','june','july','august','september','october','november','december']
    monthNumber = months.index(string) + 1
    return monthNumber


def day(string):
    string = string.lower()
    days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
    dayNumber = days.index(string) + 1
    return dayNumber

def addDayOfWeek(demand):
    dw = []
    for i, row in enumerate(demand['scheduled_fight_time']):
        today = datetime_object = datetime.strptime(row, '%Y-%m-%d %H:%M:%S')
        dow = today.weekday()
        dw.append(dow)
    demand['day_of_week'] = dw #adding a column day of week


def extractDate(demand):
    date = []
    for i, row in enumerate(demand['scheduled_fight_time']):
        date.append(row.split()[0])
    demand['date'] = date # adding a date without timestamp column to aggregate over

def formatDate(df):
    t =[]
    for i in df.index:
        time = (datetime.strptime(i,"%Y-%m-%d"))
        time = time.strftime("%Y-%m-%d")
    df['date'] = time
    df.index = df['date']

def buildTopBottomMedianDays(demand):
    day_df = demand.groupby('date').sum()
    sorted_top10 = day_df.sort_values(['total_pass']).tail(10)
    sorted_bot10 = day_df.sort_values(['total_pass']).head(10)
    sort_all = day_df.sort_values(['total_pass'])
    length = round(day_df.shape[0]/2)
    median_days = day_df.sort_values(['total_pass'])[(length-5):(length+5)]
    return sorted_top10, sorted_bot10, median_days, sort_all

def avg_day_month(demand,d,m):
    d = day(d)
    m = month(m)
    agg = demand.loc[(demand['month'] == m) & (demand['day_of_week'] == d)]
    agg = agg.groupby('time').mean()
    return agg

def top_day_month(demand,d,m,p):
    d = day(d)
    m = month(m)
    agg = demand.loc[(demand['month'] == m) & (demand['day_of_week'] == d)]
    agg = agg.groupby('time').quantile(q=p)
    return agg

def pick_day(demand, date):
    day = demand.loc[(demand['date'] == date)]
    day.set_index('time',inplace=True)
    return day, date

def plot_vol_by_type(df):
    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.figure(figsize=(15,6))

    sns.set_style("whitegrid")
    cols = ['parking','pass','A','B','C','D','E']


    for c in cols:
        plt.plot(df.index,df[c],label=c)

    plt.xticks(rotation=45)
    plt.title("SUMO Input - 6/11/2018")
    plt.legend(loc='upper right')
    plt.xlabel("Time")
    plt.ylabel("Volume Count")
    plt.grid(True)
    plt.show()

def plot_tot_vs_term(df):
    import matplotlib.pyplot as plt
    import seaborn as sns



    plt.figure(figsize=(15,4))

    sns.set_style("whitegrid")
    plt.plot(df.index,df['total_pass'],label="Total Volume")
    plt.plot(df.index,df['terminal_tot'],label="Terminal Volume")
    plt.plot(df.index,df['pass'],label="Pass Through Traffic")
#     plt.axvspan(df.index[32],df.index[36], alpha=0.5, color='#d8d8d8',label="Observed Time in SUMO")


    plt.xticks(rotation=45)
    plt.title("Volume vs. Time  ")
    plt.legend(loc='upper right')
    plt.show()

def plot_pie_all(day):
    plt.figure(figsize=(20,8))

    labels = ['A','B','C','D','E','Pass Through','Parking']
    inter_labels = ['A','B','C','D','E','pass','parking']

    broad = [day['terminal_tot'].sum(axis=0),day['pass'].sum(axis=0),day['parking'].sum(axis=0)]
    broad_label = ['Terminal','Pass Through','Parking']
    explode_broad = np.zeros(3)
    explode_broad[np.argmax(broad,axis=0)] = .1
    explode_broad[np.argmin(broad,axis=0)] = .1

    sizes = []
    colors = ['#8c510a','#d8b365','#f6e8c3','#f5f5f5','#c7eae5','#5ab4ac','#01665e']
    for i in inter_labels:
        sizes.append(day[i].sum(axis=0))

    explode = np.zeros(len(sizes))  # only "explode" the 2nd slice (i.e. 'Hogs')
    explode[np.argmax(sizes,axis = 0)] = .1
    explode[np.argmin(sizes,axis = 0)] = .1
    plt.subplot(1, 2, 1)
    plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90, colors=colors)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.subplot(1, 2, 2)
    plt.pie(broad, explode=explode_broad, labels=broad_label, autopct='%1.1f%%',
            shadow=True, startangle=90, colors=colors)
    plt.show()

def convert_num_2_terminal(num):
    term_dict = {0:"A",1:"B",2:"C",3:"D",4:"E"}
    return term_dict[num]

def model_to_sumo(this_folder,df,date,policy = True,obey=.5):
    if policy:
        pamt = str(obey*100)
        file_name = 'trip_Policy_' + pamt + "_"+ date+ ".xml"
        print("you chose to impliment the policy!")
    else:
        file_name = 'trip_' + date +  ".xml"
        print('No policy was selected')
    cols = ['parking','pass','A','B','C','D','E']
    pickUpDropOff = [0,0,0,0,0]
    routes_custom = Element('routes')
    routes_custom.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    routes_custom.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/routes_file.xsd')
    # Additing vehicle type definition for truck and trailer
    park_south = ['park_south_term_1','park_south_term_2','park_south_term_3','park_south_term_4']
    park_north = ['park_north_emp_1',
              'park_north_emp_2','park_north_emp_3','park_north_emp_4','park_north_emp_5',
              'park_north_emp_6']
    terminal_dict = {
        "A":['A_top_1','A_top_2','A_top_3','A_bot_1'], #,'A_bot_2','A_bot_3'],
        "B":['B_top_1','B_top_2','B_top_3','B_bot_1'],#,'B_bot_2','B_bot_3'],
        "C":['C_top_1','C_top_2','C_top_3','C_bot_1'],#,'C_bot_2','C_bot_3'],
        "D":['D_depart_1','D_depart_2','D_arrive_1','D_arrive_2','D_service'],
        "E":['E_top_1','E_top_2','E_top_3','E_bot_1','E_bot_2','E_bot_3'],
        "parking":['park_south_term_1','park_south_term_2','park_south_term_3','park_south_term_4',
                  'park_south_emp_1','park_south_emp_2','park_south_emp_3','park_north_emp_1',
                  'park_north_emp_2','park_north_emp_3','park_north_emp_4','park_north_emp_5',
                  'park_north_emp_6'],
        "pass":"pass_through"
    }
    stop_dict = {
         "A":['A_top_1','A_top_2','A_top_3','A_bot_1'],#,'A_bot_2','A_bot_3'],
        "B":['B_top_1','B_top_2','B_top_3','B_bot_1'],#,'B_bot_2','B_bot_3'],
        "C":['C_top_1','C_top_2','C_top_3','C_bot_1'],#,'C_bot_2','C_bot_3'],
        "D":['D_depart_1','D_depart_2','D_arrive_1','D_arrive_2','D_service'],
        "E":['E_top_1','E_top_2','E_top_3','E_bot_1','E_bot_2','E_bot_3'],
    }
    NorthStart = ['North_Plaza','North_1','North_2']
    SouthStart = ['South_Plaza','South_1','South_2']
    dwell_time = [20,30,40,60,65,70,80,90,100,120,130,140,120,140,150,170,190,200,240,210]
    scaler = 0
    hhr = 60*30
    counter = 0
    for t, time in enumerate(df.index):
        interval = [scaler,(scaler+hhr)]
        scaler+=hhr

        for c in cols:
            vol = int(df.iloc[t][c])
            sample_t = np.around(np.random.uniform(interval[0],interval[1],vol))
            #print(c,terminal_dict[c],vol)
            for s in sample_t:
                counter +=1
                if c == "parking" or c == "pass":
                    boolean = 1
                else:
                    boolean = 0
                if c == "pass":


                    if random.uniform(0, 1) > .45:
                        #coming from the North
                        start = random.choice(NorthStart)
                        if random.uniform(0,1) >.2:
                            #80% of the time they leave the opposite they came
                            end = "South_Exit"
                        else:
                            end = "North_Exit"
                    else:
                        #coming form the South
                        start = random.choice(SouthStart)
                        if random.uniform(0,1) > .2:
                            end = "North_Exit"
                        else:
                            end = "South_Exit"
                elif c == "parking":
                    if random.uniform(0, 1) > .45:
                        #coming from the North
                        start = random.choice(NorthStart)

                    else:
                        #coming form the South
                        start = random.choice(SouthStart)
                    end = random.choice(terminal_dict[c])

                else:


                    if random.uniform(0, 1) > .45:
                        #coming from the North
                        start = random.choice(NorthStart)
                        if random.uniform(0,1) >.2:
                            #80% of the time they leave the same they came
                            end = "North_Exit"
                        else:
                            end = "South_Exit"
                    else:
                        #coming from the South
                        start = random.choice(SouthStart)
                        if random.uniform(0,1) > .2:
                            end = "South_Exit"
                        else:
                            end = "North_Exit"
                    stop = random.choice(stop_dict[c])
                    stop2 = random.choice(stop_dict[c])
                    stop3 = random.choice(stop_dict[c])
                    if policy == True:

                        min_indexN = np.argmin(pickUpDropOff)
                        max_indexN = np.argmax(pickUpDropOff)
                        min_index = convert_num_2_terminal(min_indexN)
                        max_index = convert_num_2_terminal(max_indexN)
                        if c == max_index:
                            if random.uniform(0,1) < obey:
                                if start == "North_Plaza":
                                    if random.uniform(0,1) > .95:
                                        stop = random.choice(park_north)

                                    else:
                                        stop = random.choice(stop_dict[min_index])

                                else:
                                    if random.uniform(0,1) > .95:
                                        stop = random.choice(park_south)
                                    else:
                                        stop = random.choice(stop_dict[min_index])





                if c == "parking":
                    #print("yellow")
                    color = "0,0,255" #Blue as above in plot
                elif c == "pass":
                    color = "249, 179, 49" # orange
                elif c == "A":
                    color = "16, 135, 40" # green
                    pickUpDropOff[0]+=1
                elif c == "B":
                    color = "216, 2, 16" # red
                    pickUpDropOff[1]+=1
                elif c == "C":
                    color = "124, 85, 135" # purple
                    pickUpDropOff[2]+=1
                elif c == "D":
                    color = "119, 100, 25" # brown
                    pickUpDropOff[3]+=1
                else:
                    color = "255, 130, 171" # pink
                    pickUpDropOff[4]+=1
                r = 1000*round(np.random.uniform(0,1),4)
                trip = Element('trip')
                trip.set('id', (str(counter)+c))
                trip.set('type', 'passenger')
                trip.set('color', color)
                trip.set('depart',str(s))
                trip.set('from',start)
                trip.set('to',end)
                trip.set('departSpeed', "max")
                trip.set('departPos', "last")


                routes_custom.append(trip)
                duration = str(random.choice(dwell_time))
                if boolean == 0:
                    ET.SubElement(trip, "stop",busStop=stop,duration=duration,parking='true')

    routes_custom[:] = sorted(routes_custom, key=lambda child: (child.tag,float(child.get('depart'))))




    print("Saving to xml: ", file_name)
    configfile = os.path.join(this_folder, file_name)
    with open(configfile, 'wb') as f:
        f.write(minidom.parseString(ET.tostring(routes_custom)).toprettyxml(encoding="utf-8"))

def create_additional_file(this_folder,stop_dict,date):
    additional = Element('additional')
    additional.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    additional.set('xsi:noNamespaceSchemaLocation', "http://sumo.dlr.de/xsd/additional_file.xsd")
    # Additing vehicle type definition for truck and trailer

    vtype = Element('vType')
    vtype.set('id', 'truck')
    vtype.set('vClass', 'truck')
    additional.append(vtype)
    vtype1 = Element('vType')
    vtype1.set('id', 'trailer')
    vtype1.set('vClass', 'trailer')
    additional.append(vtype1)
    vtype2 = Element('vType')
    vtype2.set('id', 'passenger')
    vtype2.set('vClass', 'passenger')
    additional.append(vtype2)
    vtype3 = Element('vType')
    vtype3.set('id', 'bus')
    vtype3.set('vClass', 'bus')
    additional.append(vtype3)
    for s in stop_dict.keys():


        for ind in stop_dict[s]:

            lane = ind + "_0"

            busStop = Element('busStop')
            busStop.set('id', ind)
            busStop.set('lane', lane)
            busStop.set('friendlyPos','1')
            busStop.set('lines','1')
            busStop.set('startPos','0')
            busStop.set('endPos','-1')


            additional.append(busStop)
    file_name = 'additional_' + date + ".xml"
    print("Saving to xml: ", file_name)
    configfile = os.path.join(this_folder, file_name)
    with open(configfile, 'wb') as f:
        f.write(minidom.parseString(ET.tostring(additional)).toprettyxml(encoding="utf-8"))



if __name__=="__main__":
    print("python modules")
