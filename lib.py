from config import *
from datetime import datetime
import math as math

def load_data(path):
    """
    Load cabs data from file
    """
    files = [f for f in gl.glob(path + '**/*.txt')]
    cabs_data = pd.DataFrame()
    for f in files:
        cab_name = f.split('_')[1].split('.')[0]
        cab_data = pd.read_table(f, header=None, delimiter=" ")
        cab_data['name'] = cab_name
        cabs_data = pd.concat([cabs_data, cab_data], ignore_index=True)

    cabs_data.columns = ['latitude', 'longitude', 'occupancy', 'timestamp', 'cab_name']
    return cabs_data;
	
def data_formatting_time(cabs_data):
    """
    Convert timestamp to datetime object and extract
    """
    time = []
    for v in cabs_data['timestamp'].values:
        time.append(datetime.fromtimestamp(v).strftime('%Y-%m-%d %H:%M:%S'))
    cabs_data['time'] = pd.to_datetime(time)
    # Extract hour and day of the week
    cabs_data['hour'] = cabs_data['time'].apply(lambda x: x.hour)
    cabs_data['day'] = cabs_data['time'].apply(lambda x: x.dayofweek)
    cabs_data['minute'] = cabs_data['time'].apply(lambda x: x.minute)
    cabs_data['dayofmonth'] = cabs_data['time'].apply(lambda x: x.day)
    return cabs_data;

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 3956 # Radius of earth in kilometers. Use 3956 for miles. Use 6371 for km.
    return c * r;

def data_formatting_labels(cabs_data):
    """
    Add pick up and drop off labels to locations.
    Compute distance in miles between consecutive (in time) cabs locations.
    """
    # Sort according to cab_names and timestamps
    cabs_data = cabs_data.sort_values(by=['cab_name', 'timestamp'], ascending=[True, True])

    # Retrieve pick up and drop off entries
    occ = cabs_data['occupancy'][0]
    cab = cabs_data['cab_name'][0]
    pick_up = []
    drop_off = []
    miles = []
    prow = None
    for row in cabs_data.itertuples():
        if row.cab_name != cab:
            miles.append(0)
            cab = row.cab_name
            occ = row.occupancy
            if occ == 1:
                pick_up.append(1)
            else:
                pick_up.append(0)
            drop_off.append(0)
        else:
            miles.append(haversine(row.longitude, row.latitude, prow.longitude, prow.latitude))
            if row.occupancy != occ:
                # pick up
                if row.occupancy > occ:
                    pick_up.append(1)
                    drop_off.append(0)
                # drop off
                if row.occupancy < occ:
                    pick_up.append(0)
                    drop_off.append(1)
                occ = row.occupancy
            else:
                pick_up.append(0)
                drop_off.append(0)
        prow = row

    cabs_data['pick_up'] = pick_up
    cabs_data['drop_off'] = drop_off
    cabs_data['miles'] = miles
    return cabs_data;
	
def format_data(cabs_data):
    """
    Data formatting wrapper
    """
    print("Formatting time related fields...")
    cabs_data = data_formatting_time(cabs_data)
    print("...adding pick up and drop off location flags and miles...")
    cabs_data = data_formatting_labels(cabs_data)
    print("...done!")
    return cabs_data;
