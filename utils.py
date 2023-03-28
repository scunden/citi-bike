import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math

def upload_data():
    stations=pd.read_csv('data/citibike-stations.csv')
    trips = pd.read_csv('data/citibike-trips-sample.csv')
    
    trips['starttime'] = pd.to_datetime(trips['starttime'])
    trips['stoptime'] = pd.to_datetime(trips['stoptime'])
    # trips['birth_year'] = pd.to_datetime(trips['birth_year'])

    trips['year'] = trips['starttime'].dt.year
    trips['month'] = trips['starttime'].dt.month
    trips['day'] = trips['starttime'].dt.day
    trips['date'] = trips['starttime'].dt.date

    trips['calc_duration']=(trips['stoptime']-trips['starttime']).astype('timedelta64[s]')
    trips['duration_diff'] = abs(trips['calc_duration']-trips['tripduration'])
    
    trips["age"] = 2023-trips["birth_year"]

    trips['h_distance'] = trips.apply(lambda x: h_distance((x.start_station_latitude, x.start_station_longitude),
                                                             (x.end_station_latitude, x.end_station_longitude)), axis=1)
    return trips, stations

def h_distance(origin, destination):
    """
    Calculate the Haversine distance.

    Parameters
    ----------
    origin : tuple of float
        (lat, long)
    destination : tuple of float
        (lat, long)

    Returns
    -------
    distance_in_km : float

    Examples
    --------
    >>> origin = (48.1372, 11.5756)  # Munich
    >>> destination = (52.5186, 13.4083)  # Berlin
    >>> round(distance(origin, destination), 1)
    504.2
    """
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d/1.6

def box_plot(df, axhs, title, savename):
    fig, axes = plt.subplots(1,2,figsize=(8,5))

    sns.boxplot(y=df['tripduration'], ax=axes[0])
    if axhs:
        for axh in axhs:
            axes[0].axhline(axh[0], linestyle='--', label=axh[1], color=axh[2])
        axes[0].legend()
        
    axes[0].set_title("Overall")
    axes[0].set_ylabel("Trips Duration (s)")

    sns.boxplot(data=df, y="tripduration", x="year", ax=axes[1])
    if axhs:
        for axh in axhs:
            axes[1].axhline(axh[0], linestyle='--', label=axh[1], color=axh[2])
        axes[1].legend()
        
    axes[1].set_ylabel("")
    axes[1].set_yticklabels([])
    axes[1].set_title("By Year")

    

    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig("images/{}.png".format(savename))