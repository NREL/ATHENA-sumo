'''
This is a module to help run Sumo simulations using TraCI
'''
import os, sys
import numpy as np
import itertools
import random
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")
import traci

###
# SETUP
###
def sumoBinary():
    '''
    Uses the environment variable 'SUMO_HOME' to find the path to the
    Sumo binary. Returns the absolute path to the Sumo binary as a string.
    '''
    return os.path.join(os.environ['SUMO_HOME'], 'bin/sumo')

###
# Routes
###
tollPlazas = ["South_Plaza", "North_Plaza"] # Must match named edges in your network
exits = ["South_Exit", "North_Exit"]
curbsidePositions = [
    ["A_top_1","A_top_2","A_bot_1","A_bot_2"],
    ["B_top_1","B_top_2","B_top_3"],
    ["C_top_1","C_top_2","C_top_3","C_bot_1","C_bot_2","C_bot_3"],
    ["D_top_1","D_bot_1"],
    ["E_top_1","E_top_2","E_bot_1","E_bot_2"]]
flatListOfCurbs = [curb for sublist in curbsidePositions for curb in sublist]

def getRouteName(waypoints):
    '''
    Our convention in naming routes is <waypoint0>To<waypoint1>To<waypoint2> etc.
    '''
    return "To".join(waypoints)

def getCurbsideRoutes():
    '''
    Returns a list of tuples. Each tuple is a unique (start, curb, exit) representing
    a possible route someone may take into the airport, to a curb, and then exiting.
    '''
    return np.array(np.meshgrid(tollPlazas, flatListOfCurbs, exits)).T.reshape(-1,3)

def getPassThruRoutes():
    '''
    Returns a list of tuples. Each tuple is a unique (start, end) representing
    a possible route someone may take through the airport without stopping
    at a curb.
    '''
    return np.array(np.meshgrid(tollPlazas, exits)).T.reshape(-1,2)

def registerRoute(waypoints):
    '''
    Uses traci.simulation.findRoute to find a valid route between all of the
    waypoints (in order). Waypoints are just a list of strings, where each string
    corresponds to the name/id of an edge in the Sumo network file.
    Registers this route with traci.route.add using the route name from
    getRouteName(waypoints). This will allow you to add vehicles
    using this route name. Returns the registered route name as a string.
    '''
    routeName = getRouteName(waypoints)
    prev = waypoints[0]
    fullRoute = [waypoints[0]]
    for waypoint in waypoints[1:]:
        # Find a route from prev to this waypoint
        segment = traci.simulation.findRoute(prev, waypoint, vType="DEFAULT_VEHTYPE").edges
        fullRoute += segment[1:]
        prev = waypoint
    traci.route.add(routeName, fullRoute)
    return routeName

def registerRoutes():
    '''
    Registers all curbside and pass thru routes with traci.route.add.
    This doesn't add vehicles to the simulation, but will allow future
    vehicles to use curbside and pass thru routes. Routes are named with
    the following convention: <start>To<curb>To<end> for curbside routes,
    or <start>To<end> for pass thru routes. The names of all registered
    routes are returned as an array of strings.
    '''
    registeredRoutes = []
    for route in list(getCurbsideRoutes()) + list(getPassThruRoutes()):
        routeName = registerRoute(route)
        registeredRoutes.append(routeName)
    return registeredRoutes

def getCustomRoutes(count, fractionArrivingNorth, fractionLeavingNorth, fractionPassThru, fractionToCurbs):
    '''
    Will create a collection of <count> number of routes. Will use the <fraction*> parameters to choose routes across the
    specified distribution. Results are returned as a list of tuples. The first element of the tuple is the routeName.
    The second element of each tuple is a list of intermediate waypoints along the route, which can be used to set bus stops.
    '''
    # Should adjust to account for the fact that pass thru routes don't respect the fractionLeavingNorth thing?
    # Only send a fraction of the vehicles to a curb.
    curbRouteCount = int(count*(1-fractionPassThru))
    routeStarts = random.choices(
        population=tollPlazas,
        weights=[1-fractionArrivingNorth, fractionArrivingNorth],
        k=curbRouteCount)
    routeEnds = random.choices(
        population=exits,
        weights=[1-fractionLeavingNorth, fractionLeavingNorth],
        k=curbRouteCount)
    routeCurbs = random.choices(
        population=flatListOfCurbs,
        weights=fractionToCurbs,
        k=curbRouteCount)
    curbRoutes = np.stack((routeStarts, routeCurbs, routeEnds), axis=1)
    # I want the pass-thru routes to be north-to-south or vice versa, not north-to-north, etc
    passThruRoutes = random.choices(
        population=[["South_Plaza", "North_Exit"], ["North_Plaza", "South_Exit"]],
        weights=[1-fractionArrivingNorth, fractionArrivingNorth],
        k=int(count-curbRouteCount))
    #waypoints[1,-1]
    return [(getRouteName(waypoints), waypoints[1:-1]) for waypoints in itertools.chain(curbRoutes, passThruRoutes)]

###
# Polling
###
def pollVehicle(vehicleName):
    '''
    Uses traci to lookup the vehicle with name vehicleName, and returns
    an array with the vehicle's latitude, longitude, current speed, and the
    speed limit of the current edge.
    '''
    x, y = traci.vehicle.getPosition(vehicleName)
    lon, lat = traci.simulation.convertGeo(x, y)
    speed = traci.vehicle.getSpeed(vehicleName)
    laneID = traci.vehicle.getLaneID(vehicleName)
    maxSpeed = traci.lane.getMaxSpeed(laneID)
    return [lat,lon,speed,maxSpeed]
