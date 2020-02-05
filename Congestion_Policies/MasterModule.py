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
sys.path.insert(0, os.path.abspath('../Generate_SUMO_demand/'))
import DFW_gen_flow as gf
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
        rowParkingValue = np.around(parking/length)
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
            tmp_arrival.append(math.floor(row * percent_of_arrivals))
            tmp_departure.append(math.ceil(row * percent_of_departure))

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
            tmp_people.append(round((row * peoplePerCar/(1-percentOfTransit))))
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
                try:
                    buses[terminal + '_' + str(halfHour)] += 1
                except:
                    buses[terminal + '_' + str(halfHour)] = 1
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


    routes[:] = sorted(routes, key=lambda child: (child.tag,float(child.get('depart'))))

    file_name = Date + "." + level+ ".parking.xml"
    folder = "../Example_Files/TempDemandXML"
    print("Saving to xml: ", file_name)

    with open(os.path.join(folder,file_name), 'wb') as f:
        f.write(minidom.parseString(ET.tostring(routes)).toprettyxml(encoding="utf-8"))

    return buses

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
                trip.set('id', column + '_' + str(count))
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