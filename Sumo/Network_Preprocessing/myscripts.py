
from shapely.geometry import LineString
import numpy as np



def create_lat_lon(df,round=6):

    df_sm = df.head(1).bounds
    test = df_sm['minx'][0] == df_sm['maxx'][0]
    if test:
        #print('This is a node')
        x = np.array(df.centroid.x)
        y = np.array(df.centroid.y)
        lat_lon = np.column_stack((x,y)).tolist()
        col = []
        for i in lat_lon:
            array = np.around(np.array(i),decimals=round).tolist()
            col.append(array)
        df['lat_lon'] = col
        #df.drop(columns=['x','y'],inplace=True)
    else:
        print('this is a linestring')



    return df

def create_lat_lon_N(df,round=6):

    col = []


    for line in df.geometry:
        l = LineString(line)
        lis = list(l.coords)
        lis = np.around(np.array(lis),decimals=round).tolist()
        col.append(lis)
    df['lat_lon'] = col
    return df




def split_lat_lon_col(shp_line):
    lat_start = []
    lat_end = []
    lon_start = []
    lon_end = []

    drop_cols = ['lat_lon','lat_lo_EN','lat_lo_ST']

    for i in range(shp_line.shape[0]):
        lat_start.append(shp_line.lat_lo_ST[i][0])
        lat_end.append(shp_line.lat_lo_EN[i][0])
        lon_start.append(shp_line.lat_lo_ST[i][1])
        lon_end.append(shp_line.lat_lo_EN[i][1])

    shp_line['lat_start'] = lat_start
    shp_line['lat_end'] = lat_end
    shp_line['lon_start'] = lon_start
    shp_line['lon_end'] = lon_end

    shp_line.drop(drop_cols, axis=1,inplace=True)
    return shp_line



def merge_node_network(shp_node,shp_line):
    length = shp_line.shape[0]
    tenp = round(shp_line.shape[0]*.1,0)
    new_node = shp_node.copy()
    new_node['keepers'] = False
    included = list(new_node['keepers'])#setting all rows as throwaways
    node_cols = shp_node.columns.tolist()
    lists = [[] for n in node_cols]
    count = 0
    for i,col in enumerate(shp_line['lat_lon']):
        count+=1

        for j,col2 in enumerate(shp_node['lat_lon']):
            #print(shp_node.lat_lon[j],shp_line.lat_lon[i][0])
            if col2 == col[0]:
                # keep this node
                included[j] = True
                for k,l in enumerate(lists):
                    l.append(shp_node[node_cols[k]][j])
                break
        if count%tenp ==1:

            print(100*round(count/length,2), "% complete 1 out of 2")
    print()
    print("---------------------------------------------------")
    print()
    count = 0
    listEnd = [[] for n in node_cols]
    for i,col in enumerate(shp_line['lat_lon']):
        count+=1

        for j,col2 in enumerate(shp_node['lat_lon']):

            if col2 == col[-1]:
                included[j]=True

                for k,l in enumerate(listEnd):
                    l.append(shp_node[node_cols[k]][j])
                break

        if count%tenp ==1:
            print(100*round(count/length,2), "% complete 2 out of 2")

    start_cols = []
    end_cols = []
    for n in node_cols:
        start_cols.append(n[0:6]+"_ST")
        end_cols.append(n[0:6]+"_EN")

    for i,col in enumerate(start_cols):
        shp_line[col] = lists[i]

    for i,col in enumerate(end_cols):
        shp_line[col] = listEnd[i]
    new_node['keepers'] = included
    new_node = new_node.loc[new_node['keepers'] ==True]
    new_node.drop(columns=['keepers'],inplace=True)
    new_node.reset_index(drop=True, inplace=True)
    shp_line.drop(columns=['geomet_EN','geomet_ST'],inplace=True)

    lat = []
    lon = []
    for i, row in enumerate(new_node.lat_lon):
        lat.append(row[0])
        lon.append(row[1])

    new_node['lat'] = lat
    new_node['lon'] = lon

    new_node.drop('lat_lon', axis=1,inplace=True)

    print('MERGE COMPLETE!')
    return new_node, shp_line


def delete_centroids(df_line):
    '''
    df_line['ROAD_FLAG'] = 1100
    These values are extra edges that are not supposed to be in the network
    '''
    df_line = df_line[df_line['ROAD_FLAG'] != 1100]
    df_line.reset_index(drop=True, inplace=True)
    return df_line


def bounded_area(data,lon_min=32.8135,lon_max=32.9621,lat_min=-97.1017,lat_max =-96.9772):
    df = data.copy()
    in_region = []
    line = False
    for geom in df['lat_lon']:
        if len(geom) > 2:
            line = True
            break

    if line == False:
        #print("Nodes")
        for geom in df['lat_lon']:

            lat = geom[0]
            lon = geom[1]
            #print(lat_min <= lat and lat_max >= lat)
            if (lat_min <= lat and lat_max >= lat) and (lon_min <= lon and lon_max >= lon):
                in_region.append(True)
            else:
                in_region.append(False)
    else:
        #print("Lines")
        for geom in df['lat_lon']:

            lat = [geom[0][0],geom[-1][0]]
            lon = [geom[0][1],geom[-1][1]]
            #print(lat_min <= min(lat) and lat_max >= max(lat))
            if (lat_min <= min(lat) and lat_max >= max(lat)) and (lon_min <= min(lon) and lon_max >= max(lon)):
                in_region.append(True)
            else:
                in_region.append(False)
    df['keep'] = in_region
    df = df.loc[df['keep'] == True]
    df.drop(columns=['keep'],inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
