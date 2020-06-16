'''
This code contains all the nessecary moldules to run the master function. Documentation of each module
will be contained in each function.

'''

from __future__ import print_function
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment
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
import sys
from datetime import datetime

import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual
from ipywidgets import ToggleButtons
from tqdm import tqdm_notebook
import math
import warnings
import glob
warnings.filterwarnings('ignore')


def convertToDateTime(string):
    return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")

def convertDTtoDay(dt):
    return str(dt.year) + "-" + str(dt.month) + "-" + str(dt.day)

def pick_day(demand, date,level):
    """
    generates the exact day you select from the format YYYY-MM-DD
    """
    # assert date in set(demand['Date']), "Check to make sure Date is in Format YYYY-MM-DD no 0 padding (e.g. 2018-6-1)"
    # completed = set(selected['Date'])
    cta = ['A','B','C','D','E','pass','parking']
    demand['DateTime'] = demand['scheduled_fight_time'].apply(convertToDateTime)
    demand['Date'] = demand['DateTime'].apply(convertDTtoDay)
    demand['Total'] = demand[cta].sum(axis=1)

    day = demand.loc[(demand['Date'] == date)]
    day.set_index('time',inplace=True)
    file_name = date + "." + level + ".cars.csv"
    folder = "../Example_Files/Demand_CSV"
    day.to_csv(os.path.join(folder,file_name))
    return day


def scale_vehicles(df,years,growth=1.03):
    cta = ['A','B','C','D','E','pass','parking']
    scale = growth ** years
    scaled = df[cta].multiply(scale).round()
    scaled.index = df.index
    return scaled


def distributeParking(demand,columns):
    portionOfParking = []
    for i,parking in enumerate(tqdm_notebook(demand['parking'])):
        length = len(columns)
        rowParkingValue = parking/length

        portionOfParking.append(rowParkingValue)
    for col in columns:
        demand[col] = np.add(demand[col],portionOfParking)

    return demand

def create_depart_arrive(day_demand,
                         percent_of_arrivals=.5,
                         percent_of_departure=.5):
    assert percent_of_arrivals + percent_of_departure == 1,"Please ensure your arrivals and departures add to 1"
    cars = pd.DataFrame()

    columns = ['A','B','C','D','E']
    for col in columns:
        tmp_arrival = []
        tmp_departure = []
        for row in day_demand[col]:
            tmp_arrival.append(row * percent_of_arrivals)
            tmp_departure.append(row * percent_of_departure)

        cars['Arrive_' + col] = tmp_arrival
        cars['Depart_' + col] = tmp_departure

    cars['Time'] = day_demand.index
#     cars['parking'] = day_demand['parking']
    cars['pass_thru'] = np.array(day_demand['pass'])
    return cars

def cars_to_people(df,peoplePerCar=1.7,percentOfTransit=.005):
    columns = ['Arrive_A','Arrive_B','Arrive_C','Arrive_D','Arrive_E',
               'Depart_A','Depart_B','Depart_C','Depart_D','Depart_E']
    tmp_df = pd.DataFrame()
    for col in columns:
        tmp_people = []
        for row in df[col]:
            tmp_people.append((row * peoplePerCar/(1-percentOfTransit)))
        tmp_df[col + "_people"] = tmp_people
    depart_columns = []
    arrive_columns = []
    for col in tmp_df.columns:
        if col.startswith('Depart'):
            depart_columns.append(col)
        elif col.startswith('Arrive'):
            arrive_columns.append(col)
    tmp_df['Depart_total'] = tmp_df[depart_columns].sum(axis=1)
    tmp_df['Arrival_total'] = tmp_df[arrive_columns].sum(axis=1)

    tmp_df['pass_thru'] = df['pass_thru']
    tmp_df['Total'] = tmp_df[['Depart_total','Arrival_total']].sum(axis=1)
    return tmp_df

def create_sumo_demand_passenger_curbside(people,
                                          level,
                                          Date,
                                          percentOfPassenger=.309,
                                          peopleToCars=1.7,
                                          stops= {
        "A":['A_top_1','A_top_2','A_top_3','A_bot_1','A_bot_2','A_bot_3'],
        "B":['B_top_1','B_top_2','B_top_3','B_bot_1','B_bot_2','B_bot_3'],
        "C":['C_top_1','C_top_2','C_top_3','C_bot_1','C_bot_2','C_bot_3'],
        "D":['D_depart_1','D_depart_2','D_arrive_1','D_arrive_2','D_service'],
        "E":['E_top_1','E_top_2','E_top_3','E_bot_1','E_bot_2','E_bot_3'],

        },
                                         end_weight = [.2,.8],
                                         start_weights = [.225,.225,.275,.275],
                                         stop_duration = np.random.exponential(20,10000) + np.random.normal(60,5,10000),
                                         ):

    end_weight_south = end_weight[::-1]

    columns = ['Arrive_A_people','Arrive_B_people','Arrive_C_people','Arrive_D_people',
               'Arrive_E_people','Depart_A_people','Depart_B_people',
               'Depart_C_people','Depart_D_people','Depart_E_people']
    starts = ['South_1', 'South_Plaza', 'North_Plaza', 'North_1']
    ends = ['South_Exit', 'North_Exit']
    routes = Element('routes')
    routes.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    routes.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/routes_file.xsd')
    people['seconds'] = np.array(people.index) * 30 * 60
    count = 1

    for column in columns:
        column_string = column.split('_')
        terminal = column_string[1]
        for t,numberOfPeople in enumerate(people[column]):
            numberOfVehicles = round((numberOfPeople/peopleToCars) * percentOfPassenger)
            for i in range(numberOfVehicles):
                time = people['seconds'][t] + round(np.random.uniform(0,1800))
                start = np.random.choice(starts,p=start_weights )
                stop = np.random.choice(stops[terminal])
                if start[0] == "S":
                    p = end_weight_south
                else:
                    p = end_weight
                end = np.random.choice(ends,p=p)
                trip = Element('trip')
                trip.set('id', column + '_passenger_' + str(count))
                trip.set('type', 'passenger')
                trip.set('color', "#bb0000")
                trip.set('depart',str(time))
                trip.set('from',start)
                trip.set('to',end)
                trip.set('departSpeed', "max")
                trip.set('departLane', "best")

                count+=1
                routes.append(trip)
                duration = str(np.random.choice(stop_duration))

                ET.SubElement(trip,"stop",busStop=stop,duration=duration,parking='true')

    routes[:] = sorted(routes, key=lambda child: (child.tag,float(child.get('depart'))))

    file_name = Date + "." + level+ ".passenger.curb.xml"
    folder = "../Example_Files/TempDemandXML"
    print("Saving to xml: ", file_name)

    with open(os.path.join(folder,file_name), 'wb') as f:
        f.write(minidom.parseString(ET.tostring(routes)).toprettyxml(encoding="utf-8"))

def create_sumo_demand_passthru(people,Date,level):

    starts = ['South_1', 'South_Plaza', 'North_Plaza', 'North_1']
    ends = ['South_Exit', 'North_Exit']
    start_weights = [.225,.225,.275,.275]
    routes = Element('routes')
    routes.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    routes.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/routes_file.xsd')
    people['seconds'] = np.array(people.index) * 30 * 60
    count = 1


    for t,numberOfCars in enumerate(people['pass_thru']):

        for i in range(int(numberOfCars)):
            time = people['seconds'][t] + round(np.random.uniform(0,1800))
            start = np.random.choice(starts,p=start_weights)
            if start[0] == 'S':
                end = np.random.choice(ends,p=[.1,.9])
            else:
                end = np.random.choice(ends,p=[.9,.1])

            trip = Element('trip')
            trip.set('id','pass_' + str(count))
            trip.set('type', 'passenger')
            trip.set('color', "#bb0000")
            trip.set('depart',str(time))
            trip.set('from',start)
            trip.set('to',end)
            trip.set('departSpeed', "max")
            trip.set('departLane', "best")

            count+=1
            routes.append(trip)


    routes[:] = sorted(routes, key=lambda child: (child.tag,float(child.get('depart'))))

    file_name = Date + "." + level+ ".passthru.xml"
    folder = "../Example_Files/TempDemandXML"
    print("Saving to xml: ", file_name)

    with open(os.path.join(folder,file_name), 'wb') as f:
        f.write(minidom.parseString(ET.tostring(routes)).toprettyxml(encoding="utf-8"))

def create_sumo_demand_taxi_curbside(people,
                                          level,
                                          Date,
                                          percentOfTaxi=.027,
                                          peopleToCars=1.7,
                                          stops= {
        "A":['A_bot_1','A_bot_2','A_bot_3'],
        "B":['B_bot_1','B_bot_2','B_bot_3'],
        "C":['C_bot_1','C_bot_2','C_bot_3'],
        "D":['D_depart_1','D_depart_2','D_arrive_1','D_arrive_2','D_service'],
        "E":['E_bot_1','E_bot_2','E_bot_3'],

        },
                                         end_weight = [.2,.8],
                                         start_weights = [.225,.225,.275,.275],
                                         stop_duration = np.random.exponential(20,10000) + np.random.normal(60,5,10000),
                                         ):

    end_weight_south = end_weight[::-1]

    columns = ['Arrive_A_people','Arrive_B_people','Arrive_C_people','Arrive_D_people',
               'Arrive_E_people','Depart_A_people','Depart_B_people',
               'Depart_C_people','Depart_D_people','Depart_E_people']
    starts = ['South_1', 'South_Plaza', 'North_Plaza', 'North_1']
    ends = ['South_Exit', 'North_Exit']
    routes = Element('routes')
    routes.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    routes.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/routes_file.xsd')
    people['seconds'] = np.array(people.index) * 30 * 60
    count = 1

    for column in columns:
        column_string = column.split('_')
        terminal = column_string[1]
        for t,numberOfPeople in enumerate(people[column]):
            numberOfVehicles = round((numberOfPeople/peopleToCars) * percentOfTaxi)
            for i in range(numberOfVehicles):
                time = people['seconds'][t] + round(np.random.uniform(0,1800))
                start = np.random.choice(starts,p=start_weights )
                stop = np.random.choice(stops[terminal])
                if start[0] == "S":
                    p = end_weight_south
                else:
                    p = end_weight
                end = np.random.choice(ends,p=p)
                trip = Element('trip')
                trip.set('id', column + '_Taxi_' + str(count))
                trip.set('type', 'passenger')
                trip.set('color', "#bb0000")
                trip.set('depart',str(time))
                trip.set('from',start)
                trip.set('to',end)
                trip.set('departSpeed', "max")
                trip.set('departLane', "best")

                count+=1
                routes.append(trip)
                duration = str(np.random.choice(stop_duration))

                ET.SubElement(trip,"stop",busStop=stop,duration=duration,parking='true')

    routes[:] = sorted(routes, key=lambda child: (child.tag,float(child.get('depart'))))

    file_name = Date + "." + level+ ".taxi.curb.xml"
    folder = "../Example_Files/TempDemandXML"
    print("Saving to xml: ", file_name)

    with open(os.path.join(folder,file_name), 'wb') as f:
        f.write(minidom.parseString(ET.tostring(routes)).toprettyxml(encoding="utf-8"))

def create_sumo_demand_TNC_curbside(people,
                                          level,
                                          Date,
                                          percentOfTNC=.255,
                                          peopleToCars=1.7,
                                          stops= {
        "A":['A_top_1','A_top_2','A_top_3','A_bot_1'],
        "B":['B_top_1','B_top_2','B_top_3','B_bot_1'],
        "C":['C_top_1','C_top_2','C_top_3','C_bot_1'],
        "D":['D_depart_1','D_depart_2','D_arrive_1','D_arrive_2'],
        "E":['E_top_1','E_top_2','E_top_3','E_bot_1'],

        },
                                         alt_stops = {
        "A":['A_top_1','A_top_2','A_top_3','A_bot_1','A_bot_2','A_bot_3'],
        "B":['B_top_1','B_top_2','B_top_3','B_bot_1','B_bot_2','B_bot_3'],
        "C":['C_top_1','C_top_2','C_top_3','C_bot_1','C_bot_2','C_bot_3'],
        "D":['D_depart_1','D_depart_2','D_arrive_1','D_arrive_2','D_service'],
        "E":['E_top_1','E_top_2','E_top_3','E_bot_1','E_bot_2','E_bot_3'],

        },
                                         ballpark = {
        'Arrive':['TNC_1','TNC_2','TNC_3']
        },
                                         policy=None,
                                         end_weight = [.2,.8],
                                         start_weights = [.225,.225,.275,.275],
                                         stop_duration = np.random.exponential(20,10000) + np.random.normal(60,5,10000),
                                         ):

    end_weight_south = end_weight[::-1]

    columns = ['Arrive_A_people','Arrive_B_people','Arrive_C_people','Arrive_D_people',
               'Arrive_E_people','Depart_A_people','Depart_B_people',
               'Depart_C_people','Depart_D_people','Depart_E_people']
    starts = ['South_1', 'South_Plaza', 'North_Plaza', 'North_1']
    ends = ['South_Exit', 'North_Exit']
    routes = Element('routes')
    routes.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    routes.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/routes_file.xsd')
    people['seconds'] = np.array(people.index) * 30 * 60
    count = 1

    for column in columns:
        column_string = column.split('_')
        terminal = column_string[1]
        for t,numberOfPeople in enumerate(people[column]):
            numberOfVehicles = round((numberOfPeople/peopleToCars) * percentOfTNC)
            for i in range(numberOfVehicles):
                time = people['seconds'][t] + round(np.random.uniform(0,1800))

                # make this basic from plaza to terminal

                start = np.random.choice(starts,p=start_weights )
                if start[0] == "S":
                    p = end_weight_south
                else:
                    p = end_weight
                end = np.random.choice(ends,p=p)
                stop = np.random.choice(stops[terminal])

                trip = Element('trip')
                trip.set('id', column + '_TNC_' + str(count))
                trip.set('type', 'passenger')
                trip.set('color', "#bb0000")
                trip.set('depart',str(time))
                trip.set('from',start)
                trip.set('to',end)
                trip.set('departSpeed', "max")
                trip.set('departLane', "best")

                count+=1
                routes.append(trip)
                duration = str(np.random.choice(stop_duration))

                ET.SubElement(trip,"stop",busStop=stop,duration=duration,parking='true')

    routes[:] = sorted(routes, key=lambda child: (child.tag,float(child.get('depart'))))

    file_name = Date + "." + level+ ".TNC.curb.xml"
    folder = "../Example_Files/TempDemandXML"
    print("Saving to xml: ", file_name)

    with open(os.path.join(folder,file_name), 'wb') as f:
        f.write(minidom.parseString(ET.tostring(routes)).toprettyxml(encoding="utf-8"))

def create_sumo_demand_parking(people,
                                      level,
                                      Date,
                                      percentOfParking=.25,
                                      peopleToCars=1.7,
                                      starts= {
                                        'parking' : ['park_south_term_1','park_south_term_2',
                                                 'park_south_term_3','park_south_term_4',
                                                 'park_south_emp_1','park_south_emp_2',
                                                 'park_south_emp_3','park_north_emp_1'],
                                        "A":['A_park_enter'] ,
                                        "B":['B_park_enter_1'] ,
                                        "C":['C_park_enter_1'] ,
                                        "D":['D_park'] ,
                                        "E":['E_park_enter'],

                                        },
                                     arrive = {
                                        'parking' : ['park_south_term_1','park_south_term_2',
                                                 'park_south_term_3','park_south_term_4',
                                                 'park_south_emp_1','park_south_emp_2',
                                                 'park_south_emp_3','park_north_emp_1'],
                                        "A":['A_park_exit'] ,
                                        "B":['B_park_exit'] ,
                                        "C":['C_park_exit_1'] ,
                                        "D":['D_park'] ,
                                        "E":['E_park_exit_1'],

                                        },
                                         end_weight = [.2,.8],
                                         start_weights = [.225,.225,.275,.275],
                                         stop_duration = np.random.exponential(20,10000) + np.random.normal(60,5,10000),
                                         ):

    start_depart = ['South_1', 'South_Plaza', 'North_Plaza', 'North_1']
    end_arrive = ['South_Exit', 'North_Exit']
    columns = ['Arrive_A_people','Arrive_B_people','Arrive_C_people','Arrive_D_people',
               'Arrive_E_people','Depart_A_people','Depart_B_people',
               'Depart_C_people','Depart_D_people','Depart_E_people']

    routes = Element('routes')
    routes.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    routes.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/routes_file.xsd')
    people['seconds'] = np.array(people.index) * 30 * 60
    count = 1
    buses = {}
    #intializing a dictionary
    for term in ['A','B','C','D','E']:
        for hr in range(24):
            for arrdp in ['Arrive','Depart']:
                buses[term+'_'+str(hr)+'_'+arrdp]=0

    for column in columns:
        column_string = column.split('_')
        terminal = column_string[1]
        for t,numberOfPeople in enumerate(people[column]):
            numberOfVehicles = round((numberOfPeople/peopleToCars) * percentOfParking)
            for i in range(numberOfVehicles):
                time = people['seconds'][t] + round(np.random.uniform(0,1800))
                if column_string[0] == 'Arrive':
                    begin = arrive[terminal] + arrive['parking']
                    start = np.random.choice(begin)
                    end = np.random.choice(end_arrive)
                    #add buses from terminal to parking

                else:
                    finish = starts[terminal] + starts['parking']
                    start = np.random.choice(start_depart,p=start_weights)
                    end = np.random.choice(finish)
                    #add buses from parking to terminal

                halfHour = round(time/3600)
                # try:
                #     buses[terminal + '_' + str(halfHour)] += 1
                # except:
                #     buses[terminal + '_' + str(halfHour)] = 1=
                try:
                    buses[terminal + '_' + str(int(halfHour))+'_'+column_string[0]] += peopleToCars
                except:
                    buses[terminal + '_' + str(int(halfHour))+'_'+column_string[0]] = peopleToCars
                trip = Element('trip')
                trip.set('id', column + '_parking_' + str(count))
                trip.set('type', 'passenger')
                trip.set('color', "#bb0000")
                trip.set('depart',str(time))
                trip.set('from',start)
                trip.set('to',end)
                trip.set('departSpeed', "max")
                trip.set('departLane', "best")

                count+=1
                routes.append(trip)
    #building dictionary for extra buses
    maxbuses={}
    for term in ['A','B','C','D','E']:
        for hr in range(24):
            maxbuses[term+'_'+str(hr)]=max(buses[term+'_'+str(hr)+'_Arrive'],buses[term+'_'+str(hr)+'_Depart'])

    routes[:] = sorted(routes, key=lambda child: (child.tag,float(child.get('depart'))))

    file_name = Date + "." + level+ ".parking.xml"
    folder = "../Example_Files/TempDemandXML"
    print("Saving to xml: ", file_name)

    with open(os.path.join(folder,file_name), 'wb') as f:
        f.write(minidom.parseString(ET.tostring(routes)).toprettyxml(encoding="utf-8"))

    return maxbuses

def add_buses_for_people(buses,
                         Date,
                         level,
                         capacity=50,
                         starts = {
                                "A":['A_bot_1','A_bot_2','A_bot_3'],
                                "B":['B_bot_1','B_bot_2','B_bot_3'],
                                "C":['C_bot_1','C_bot_2','C_bot_3'],
                                "D":['D_depart_1','D_service'],
                                "E":['E_bot_1','E_bot_2','E_bot_3']},
                         stops = ['park_south_term_1','park_south_emp_3',
                                  'park_north_emp_1'],
                         stop_duration=np.random.exponential(20,10000) + np.random.normal(60,5,10000)
                        ):
    routes = Element('routes')
    routes.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    routes.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/routes_file.xsd')
    count = 0
    for key in buses:
        key_string = key.split('_')
        terminal = key_string[0]
        hour = key_string[1]
        hr = float(hour) * 3600
        passengers = buses[key]
        number_of_buses = int(np.ceil(passengers/capacity)) - 4
        if number_of_buses > 0:

            for i in range(number_of_buses):
                time = hr + round(np.random.uniform(0,3600))
                start = np.random.choice(starts[terminal])
                end = start
                trip = Element('trip')
                trip.set('id', terminal + '_' + str(count))
                trip.set('type', 'bus')
                trip.set('color', "#bb0000")
                trip.set('depart',str(time))
                trip.set('from',start)
                trip.set('to',end)
                trip.set('departSpeed', "max")
                trip.set('departLane', "best")

                count+=1
                routes.append(trip)

                count+=1
                for stop in stops:
                    duration = str(round(np.random.choice(stop_duration)))
                    ET.SubElement(trip,"stop",busStop=stop,duration=duration,parking='true')



    routes[:] = sorted(routes, key=lambda child: (child.tag,float(child.get('depart'))))

    file_name = Date + "." + level+ ".MoreBuses.xml"
    folder = "../Example_Files/TempDemandXML"
    print("Saving to xml: ", file_name)

    with open(os.path.join(folder,file_name), 'wb') as f:
        f.write(minidom.parseString(ET.tostring(routes)).toprettyxml(encoding="utf-8"))

#Adding new function for adding RAC add_buses_for_people
def add_buses_for_RAC(people,level,Date,percentOfRAC,
                         capacity=43*0.7,
                         stops = {
                                "A":['A_bot_3','A_bot_2'],
                                "B":['B_bot_3','B_bot_2'],
                                "C":['C_bot_3','C_bot_2'],
                                "D":['D_arrive_1','D_depart_2'],
                                "E":['E_bot_3','E_bot_2','E_bot_1']},
                         stop_duration=np.random.exponential(20,10000) + np.random.normal(60,5,10000)):

    columns = ['Arrive_A_people','Arrive_B_people','Arrive_C_people','Arrive_D_people',
               'Arrive_E_people','Depart_A_people','Depart_B_people',
               'Depart_C_people','Depart_D_people','Depart_E_people']
    people['seconds'] = np.array(people.index) * 30 * 60
    count = 1
    buses = {}
    for term in ['A','B','C','D','E']:
        for hr in range(24):
            for arrdp in ['Arrive','Depart']:
                buses[term+'_'+str(hr)+'_'+arrdp]=0
    for column in columns:
        column_string = column.split('_')
        terminal = column_string[1]
        for t,numberOfPeople in enumerate(people[column]):
            numberOfPeopleFromRAC = round(numberOfPeople * percentOfRAC)
            for i in range(numberOfPeopleFromRAC):
                time = people['seconds'][t] + round(np.random.uniform(0,1800))
                hr = round(time/3600)
                try:
                    buses[terminal + '_' + str(int(hr))+'_'+column_string[0]] += 1
                except:
                    buses[terminal + '_' + str(int(hr))+'_'+column_string[0]] = 1
                count+=1
    maxbuses={}
    for term in ['A','B','C','D','E']:
        for hr in range(24):
            maxbuses[term+'_'+str(hr)]=max(buses[term+'_'+str(hr)+'_Arrive'],buses[term+'_'+str(hr)+'_Depart'])

    routes = Element('routes')
    routes.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    routes.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/routes_file.xsd')
    count = 0
    for key in maxbuses:
        key_string = key.split('_')
        terminal = key_string[0]
        hour = key_string[1]
        hr = float(hour) * 3600
        passengers = maxbuses[key]
        number_of_buses = int(np.ceil(passengers/capacity))
        if number_of_buses > 0:
            for i in range(number_of_buses):
                time = max(0, round(hr + 3600/number_of_buses*i + np.random.uniform(-60,60)))
               # time = hr + round(np.random.uniform(0,3600))
                start = 'RAC_pick'
                end = 'RAC_drop'
                trip = Element('trip')
                trip.set('id', 'RAC_'+terminal + '_' + str(count))
                trip.set('type', 'bus')
                trip.set('color', "#bb0000")
                trip.set('depart',str(time))
                trip.set('from',start)
                trip.set('to',end)
                trip.set('departSpeed', "max")
                trip.set('departLane', "best")
                count+=1
                routes.append(trip)
                for stop in stops[terminal]:
                    duration = str(round(np.random.choice(stop_duration)))
                    ET.SubElement(trip,"stop",busStop=stop,duration=duration,parking='true')
    routes[:] = sorted(routes, key=lambda child: (child.tag,float(child.get('depart'))))
    file_name = Date + "." + level+ ".RAC_bus.xml"
    folder = "../Example_Files/TempDemandXML"
    print("Saving to xml: ", file_name)
    with open(os.path.join(folder,file_name), 'wb') as f:
        f.write(minidom.parseString(ET.tostring(routes)).toprettyxml(encoding="utf-8"))


def create_sumo_demand_limo_curbside(people,
                                          level,
                                          Date,
                                          percentOfLimo=.01,
                                          peopleToCars=1.7,
                                          stops= {
        "A":['A_bot_1','A_bot_2','A_bot_3'],
        "B":['B_bot_1','B_bot_2','B_bot_3'],
        "C":['C_bot_1','C_bot_2','C_bot_3'],
        "D":['D_depart_1','D_service'],
        "E":['E_bot_1','E_bot_2','E_bot_3'],

        },
                                         end_weight = [.2,.8],
                                         start_weights = [.225,.225,.275,.275],
                                         stop_duration = np.random.exponential(20,10000) + np.random.normal(60,5,10000)
                                         ):

    end_weight_south = end_weight[::-1]

    columns = ['Arrive_A_people','Arrive_B_people','Arrive_C_people','Arrive_D_people',
               'Arrive_E_people','Depart_A_people','Depart_B_people',
               'Depart_C_people','Depart_D_people','Depart_E_people']
    starts = ['South_1', 'South_Plaza', 'North_Plaza', 'North_1']
    ends = ['South_Exit', 'North_Exit']
    routes = Element('routes')
    routes.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    routes.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/routes_file.xsd')
    people['seconds'] = np.array(people.index) * 30 * 60
    count = 1

    for column in columns:
        column_string = column.split('_')
        terminal = column_string[1]
        for t,numberOfPeople in enumerate(people[column]):
            numberOfVehicles = round((numberOfPeople/peopleToCars) * percentOfLimo)
            for i in range(numberOfVehicles):
                time = people['seconds'][t] + round(np.random.uniform(0,1800))
                start = np.random.choice(starts,p=start_weights )
                stop = np.random.choice(stops[terminal])
                if start[0] == "S":
                    p = end_weight_south
                else:
                    p = end_weight
                end = np.random.choice(ends,p=p)
                trip = Element('trip')
                trip.set('id', column + '_Limo_' + str(count))
                trip.set('type', 'passenger')
                trip.set('color', "#bb0000")
                trip.set('depart',str(time))
                trip.set('from',start)
                trip.set('to',end)
                trip.set('departSpeed', "max")
                trip.set('departLane', "best")

                count+=1
                routes.append(trip)
                duration = str(np.random.choice(stop_duration))

                ET.SubElement(trip,"stop",busStop=stop,duration=duration,parking='true')

    routes[:] = sorted(routes, key=lambda child: (child.tag,float(child.get('depart'))))

    file_name = Date + "." + level+ ".limo.curb.xml"
    folder = "../Example_Files/TempDemandXML"
    print("Saving to xml: ", file_name)

    with open(os.path.join(folder,file_name), 'wb') as f:
        f.write(minidom.parseString(ET.tostring(routes)).toprettyxml(encoding="utf-8"))

def combineTrips(fileOutput,
                 trips="../Example_Files/TempDemandXML/*.xml",
                 folderOutput = "../Example_Files/TempInputTrips"
                ):
    xroutes = Element('routes')
    xroutes.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    xroutes.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/routes_file.xsd')
    trip_list = []
    listOfFiles = glob.glob(trips)
    print(len(trips))
    for files in listOfFiles:
        print("Combining: ",files)
        print(80*"=")
        path_file = os.path.join(files)
        root_tree = ET.parse(path_file).getroot()
        trip_list.extend(root_tree)
    trip_list[:] = sorted(trip_list, key=lambda child: (child.tag,float(child.get('depart'))))

    xroutes.extend(trip_list)


    print("Saving to xml: ", fileOutput)
    configfile = os.path.join(folderOutput,fileOutput)
    with open(configfile, 'wb') as f:
        f.write(minidom.parseString(ET.tostring(xroutes)).toprettyxml(encoding="utf-8"))

def create_sumo_demand_TNC_curbside_base(people,
                                          level,
                                          Date,
                                          staging = .9,
                                          percentOfTNC=.255,
                                          peopleToCars=.309,
                                          stops= {
        "A":['A_top_1','A_top_2','A_top_3','A_bot_1'],
        "B":['B_top_1','B_top_2','B_top_3','B_bot_1'],
        "C":['C_top_1','C_top_2','C_top_3','C_bot_1'],
        "D":['D_depart_1','D_depart_2','D_arrive_1','D_arrive_2'],
        "E":['E_top_1','E_top_2','E_top_3','E_bot_1'],

        },
                                         alt_stops = {
        "A":['A_top_1','A_top_2','A_top_3','A_bot_1','A_bot_2','A_bot_3'],
        "B":['B_top_1','B_top_2','B_top_3','B_bot_1','B_bot_2','B_bot_3'],
        "C":['C_top_1','C_top_2','C_top_3','C_bot_1','C_bot_2','C_bot_3'],
        "D":['D_depart_1','D_depart_2','D_arrive_1','D_arrive_2','D_service'],
        "E":['E_top_1','E_top_2','E_top_3','E_bot_1','E_bot_2','E_bot_3'],

        },
                                         ballpark = {
        'Arrive':['TNC_1','TNC_2','TNC_3']
        },
                                        missed_stop = {
       'A_top_1':['A_top_2','A_top_3','A_bot_1','A_bot_2','A_bot_3'],
       'A_top_2':['A_bot_3','A_bot_1','A_bot_2','A_bot_3'],
       'A_top_3':['A_bot_1','A_bot_2','A_bot_3'],
       'A_bot_1':['A_top_1','A_top_2','A_top_3','A_bot_2','A_bot_3'],
       'B_top_1':['B_top_2','B_top_3','B_bot_1'],
       'B_top_2':['B_top_3','B_bot_1','B_bot_2'],
       'B_top_3':['B_bot_1','B_bot_2','B_bot_3'],
       'B_bot_1':['B_top_1','B_top_2','B_top_3','B_bot_2'],
       'C_top_1':['C_top_2','C_top_3','C_bot_1'],
       'C_top_2':['C_top_3','C_bot_1','C_bot_2'],
       'C_top_3':['C_bot_1','C_bot_2','C_bot_3'],
       'C_bot_1':['C_top_1','C_top_2','C_top_3'],
       'D_depart_1':['D_depart_2','D_arrive_1','D_arrive_2'],
       'D_depart_2':['D_arrive_1','D_arrive_2'],
       'D_arrive_1':['D_arrive_2','D_depart_2','D_depart_1'],
       'D_arrive_2':['D_depart_2','D_arrive_1','D_depart_1'],
       'E_top_1':['E_top_2','E_top_3','E_bot_1'],
       'E_top_2':['E_top_3','E_bot_1','E_bot_2'],
       'E_top_3':['E_bot_1','E_bot_2','E_bot_3'],
       'E_bot_1':['E_top_1','E_top_2','E_top_3']
        },
                                         policy=None,
                                         end_weight = [.2,.8],
                                         start_weights = [.225,.225,.275,.275],
                                         stop_duration_drop_off = np.random.exponential(20,10000) + np.random.normal(60,5,10000),
                                         stop_duration_pick_up = np.random.exponential(20,10000) + np.random.normal(60,5,10000),
                                         mid_stop_duration = np.random.normal(60,5,10000),
                                         ):

    end_weight_south = end_weight[::-1]

    columns = ['Arrive_A_people','Arrive_B_people','Arrive_C_people','Arrive_D_people',
               'Arrive_E_people','Depart_A_people','Depart_B_people',
               'Depart_C_people','Depart_D_people','Depart_E_people']
    starts = ['South_1', 'South_Plaza', 'North_Plaza', 'North_1']
    ends = ['South_Exit', 'North_Exit']
    routes = Element('routes')
    routes.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    routes.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/routes_file.xsd')
    people['seconds'] = np.array(people.index) * 30 * 60
    count = 1

    # TNC vehicles pre-staging (vehicles go to the staging area waiting for high-demand)
    arrive_num = (people['Arrive_A_people'] + people['Arrive_B_people'] + \
    people['Arrive_C_people'] + people['Arrive_D_people'] + people['Arrive_E_people'])
    depart_num = (people['Depart_A_people'] + people['Depart_B_people'] + \
    people['Depart_C_people'] + people['Depart_D_people'])
    # every one of the departure TNC will go to the staging area for a pick up.. may need to change
    TNC_prestaging = arrive_num - depart_num
    # go to staging area half an hour before curb time
    TNC_prestaging = TNC_prestaging[1:48]
    TNC_prestaging.index = np.arange(47)
    # when there are more departure than arrival, no pre-staging needed
    TNC_prestaging[TNC_prestaging<0] = 0
    TNC_prestaging = round(TNC_prestaging/peopleToCars)
    # generate trips
    TNC_prestaging_seconds = np.array(TNC_prestaging.index) * 30 * 60
    for t,numTNC in enumerate(TNC_prestaging.astype('int')):
         for i in range(numTNC):
            time = TNC_prestaging_seconds[t] + round(np.random.uniform(0,1800))
            start = np.random.choice(starts,p=start_weights )
            end = np.random.choice(ballpark['Arrive'])
            stop = end

            trip = Element('trip')
            trip.set('id', 'pre_statging' + '_TNC_' + str(count))
            trip.set('type', 'passenger')
            trip.set('color', "#bb0000")
            trip.set('depart',str(time))
            trip.set('from',start)
            trip.set('to',end)
            trip.set('departSpeed', "max")
            trip.set('departLane', "best")

            count+=1
            routes.append(trip)
            ET.SubElement(trip,"stop",busStop=stop,duration='0',parking='true')

    for column in columns:
        column_string = column.split('_')
        category = column_string[0] # arrival or departure
        terminal = column_string[1]

        ## pick up
        if(category == 'Arrive'):
            for t,numberOfPeople in enumerate(people[column]):
                numberOfVehicles = round((numberOfPeople/peopleToCars) * percentOfTNC)
                numberOfVehicles_from_outside = round(numberOfVehicles * 0)
                numberOfVehicles_from_staging = round(numberOfVehicles * 1)
                # here to specify a proportion that experience difficulty finding passengers

                for i in range(numberOfVehicles_from_outside):
                    time = people['seconds'][t] + round(np.random.uniform(0,1800))
                    start = np.random.choice(starts,p=start_weights )
                    if start[0] == "S":
                        p = end_weight_south
                    else:
                        p = end_weight
                    end = np.random.choice(ends,p=p)
                    stop = np.random.choice(stops[terminal])

                    trip = Element('trip')
                    trip.set('id', column + '_TNC_' + str(count))
                    trip.set('type', 'passenger')
                    trip.set('color', "#bb0000")
                    trip.set('depart',str(time))
                    trip.set('from',start)
                    trip.set('to',end)
                    trip.set('departSpeed', "max")
                    trip.set('departLane', "best")

                    count+=1
                    routes.append(trip)
                    duration = str(np.random.choice(stop_duration_pick_up))
                    mid_duration = str(np.random.choice(mid_stop_duration))
                    if np.random.uniform(100) < 5:
                        second_stop = np.random.choice(missed_stop[stop])
                        ET.SubElement(trip,"stop",busStop=stop,duration=mid_duration)
                        ET.SubElement(trip,"stop",busStop=second_stop,duration=duration,parking='true')

                    else:
                        ET.SubElement(trip,"stop",busStop=stop,duration=duration,parking='true')

                for i in range(numberOfVehicles_from_staging):
                    time = people['seconds'][t] + round(np.random.uniform(0,1800))
                    start = np.random.choice(ballpark['Arrive'])
                    end = np.random.choice(ends,p=end_weight)
                    stop = np.random.choice(stops[terminal])

                    trip = Element('trip')
                    trip.set('id', column + '_TNC_' + str(count))
                    trip.set('type', 'passenger')
                    trip.set('color', "#bb0000")
                    trip.set('depart',str(time))
                    trip.set('from',start)
                    trip.set('to',end)
                    trip.set('departSpeed', "max")
                    trip.set('departLane', "best")

                    count+=1
                    routes.append(trip)
                    duration = str(np.random.choice(stop_duration_pick_up))
                    mid_duration = str(np.random.choice(mid_stop_duration))
                    if np.random.uniform(100) < 5:
                        second_stop = np.random.choice(missed_stop[stop])
                        ET.SubElement(trip,"stop",busStop=stop,duration=mid_duration)
                        ET.SubElement(trip,"stop",busStop=second_stop,duration=duration,parking='true')

                    else:
                        ET.SubElement(trip,"stop",busStop=stop,duration=duration,parking='true')

        ## dropp-off
        non_staging = 1 - staging 
        else:
            for t,numberOfPeople in enumerate(people[column]):
                numberOfVehicles = round((numberOfPeople/peopleToCars) * percentOfTNC)
                numberOfVehicles_to_outside = round(numberOfVehicles * non_staging)
                numberOfVehicles_to_staging = round(numberOfVehicles * staging)

                for i in range(numberOfVehicles_to_outside):
                    time = people['seconds'][t] + round(np.random.uniform(0,1800))
                    start = np.random.choice(starts,p=start_weights )
                    if start[0] == "S":
                        p = end_weight_south
                    else:
                        p = end_weight
                    end = np.random.choice(ends,p=p)
                    stop = np.random.choice(stops[terminal])

                    trip = Element('trip')
                    trip.set('id', column + '_TNC_' + str(count))
                    trip.set('type', 'passenger')
                    trip.set('color', "#bb0000")
                    trip.set('depart',str(time))
                    trip.set('from',start)
                    trip.set('to',end)
                    trip.set('departSpeed', "max")
                    trip.set('departLane', "best")

                    count+=1
                    routes.append(trip)
                    duration = str(np.random.choice(stop_duration_drop_off))
                    ET.SubElement(trip,"stop",busStop=stop,duration=duration,parking='true')

                for i in range(numberOfVehicles_to_staging):
                    time = people['seconds'][t] + round(np.random.uniform(0,1800))
                    start = np.random.choice(starts,p=start_weights )
                    end = np.random.choice(ballpark['Arrive'])
                    stop = np.random.choice(stops[terminal])

                    trip = Element('trip')
                    trip.set('id', column + '_TNC_' + str(count))
                    trip.set('type', 'passenger')
                    trip.set('color', "#bb0000")
                    trip.set('depart',str(time))
                    trip.set('from',start)
                    trip.set('to',end)
                    trip.set('departSpeed', "max")
                    trip.set('departLane', "best")

                    count+=1
                    routes.append(trip)
                    duration = str(np.random.choice(stop_duration_drop_off))
                    ET.SubElement(trip,"stop",busStop=stop,duration=duration,parking='true')


    routes[:] = sorted(routes, key=lambda child: (child.tag,float(child.get('depart'))))

    file_name = Date + "." + level+ ".TNC.curb.xml"
    folder = "../Example_Files/TempDemandXML"
    print("Saving to xml: ", file_name)

    with open(os.path.join(folder,file_name), 'wb') as f:
        f.write(minidom.parseString(ET.tostring(routes)).toprettyxml(encoding="utf-8"))


def get_unique_stops(trip_file):
    '''
    This function takes a relative or explicit path to your trip file and returns only the unique stop location
    names to be used to geneerate your additional file.
    '''
    unique_stops = set()
    tree = etree.parse(trip_file)
    root = tree.getroot()
    for trip in root.findall('trip'):
        stops = trip.findall('stop')
        if stops != None:
            for stop in stops:
                unique_stops.add(stop.attrib['busStop'])
    return unique_stops

def build_additional_file(unique_stops):
    '''
    Takes in unique stop IDs and builds out everything you'll need for your additional file and guarantees
    all stop IDs are generated. Adds both vehicle types and their respective parameters along with vehicle stops.
    '''
    additional = Element('additional')
    vTypes = ['truck','trailer','bus','passenger']
    sigma = .13
    for veh in vTypes:

        vType = Element('vType')
        vType.set('id', veh)
        vType.set('vClass', veh)
        vType.set('sigma', str(sigma))
        if veh == 'passenger':
            vType.set('accel',str(10))
            vType.set('decel',str(10))
            vType.set('length',str(7))
        additional.append(vType)

    for stop in unique_stops:
        lane = stop + "_0"
        busStop = Element('busStop')
        busStop.set('endPos', "-1")
        busStop.set('friendlyPos', "1")
        busStop.set('id', stop)
        busStop.set('lane', lane)
        busStop.set('lines', str(1))
        busStop.set('startPos', str(0))
        additional.append(busStop)
    Date = str(datetime.today()).split()[0]
    file_name = Date + ".additional.xml"
    folder = "../Example_Files/SUMO_Input_Files"

    with open(os.path.join(folder,file_name), 'wb') as f:
        f.write(minidom.parseString(ET.tostring(additional)).toprettyxml(encoding="utf-8"))
    print("your file named: ", file_name, " is located in: ",folder)

def main_additional_build(trip_file):
    unique_stops = get_unique_stops(trip_file)
    build_additional_file(unique_stops)
