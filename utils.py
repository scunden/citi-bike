import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
import itertools
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm


def generate_holidays(df, window=1):
    holidays = pd.read_csv('data/us_holidays.csv')
    holidays['Date'] = pd.to_datetime(holidays['Date'])
    holidays = holidays.rename({'Date':'ds', 'Holiday':'holiday'}, axis = 1)
    holidays = holidays.loc[(holidays.ds > df.index.min()) & (holidays.ds <= df.index.max())]
    # holidays = holidays.set_index(['ds'])
    holidays['lower_window']=0
    holidays['upper_window']=window
    return holidays[['ds','holiday', 'lower_window', 'upper_window']]

def train_test_split(df, test_perc, weekly=False):
    test_period = int(df.shape[0]*test_perc)
    train = df.iloc[:-test_period]
    if weekly:
        test = df.iloc[-test_period:-1]
    else:
        test = df.iloc[-test_period:]

    return train, test, test_period

def adf_test(dates):
    t_stat, p_value, _, _, critical_values, _  = adfuller(dates.values, autolag='AIC')
    t_critical_value = critical_values["1%"]
    
    if t_stat < t_critical_value:
        # Means series is stationary
        print("Series is Stationary | P Value: {}".format(p_value))
        return (0,1)
    else: 
        print("Series is not Stationary | P Value: {}".format(p_value))
        return (1,2)

def iterate_parameters(train, test, freq=12, alpha=0.3, run_adf_test=True, verbose=False, pq_range=3):
    
    param_tracker = pd.DataFrame(columns = ["param","param_seasonal","aic","mape"])
    pred_tracker = pd.DataFrame()
    lower_tracker = pd.DataFrame()
    upper_tracker = pd.DataFrame()
    
    # if run_adf_test:
    #     d_lower, d_upper = adf_test(train)
    # else:
    #     d_lower, d_upper = (0,2)
        
    p = q = range(0,pq_range)
    d = 1

    # Generate all different combinations of p, q and q triplets
    pdq = list(itertools.product(p, [d], q))

    # Generate all different combinations of seasonal p, q and q triplets
    seasonal_pdq = [(x[0], x[1], x[2], freq) for x in list(itertools.product(p, [d], q))]

    for param in pdq:
        for param_seasonal in seasonal_pdq:
            # for trend in ['n','c','t','ct']:
                
            results = sm.tsa.statespace.SARIMAX(train,
                                            order=param,
                                            seasonal_order=param_seasonal,
                                            enforce_stationarity=False,
                                            enforce_invertibility=False,
                                            # trend=trend
                                            ).fit(disp=0)
            if verbose:
                print("Param: {}|ParamSeasonal: {} | AIC: {}".format(param, param_seasonal, results.aic))
            pred = results.get_prediction(
                start=test.index[0],
                end=test.index[len(test)-1], 
                dynamic=False)

            pred_ci = pred.conf_int(alpha=alpha)

            pred_tracker = pd.concat([pred_tracker,
                                        pred.predicted_mean.rename("{}{}".format(param,param_seasonal))],
                                        axis=1)

            lower_tracker = pd.concat([lower_tracker,
                                        pred_ci["lower y"].rename("{}{}".format(param,param_seasonal))],
                                        axis=1)

            upper_tracker = pd.concat([upper_tracker,
                                        pred_ci["upper y"].rename("{}{}".format(param,param_seasonal))],
                                        axis=1)

            param_tracker.loc[len(param_tracker)] = [param, 
                                                        param_seasonal, 
                                                        # trend,
                                                        results.aic, 
                                                        mape(test, pred.predicted_mean)
                                                    ]
                
    return param_tracker, pred_tracker, lower_tracker, upper_tracker

def mape(y_true, y_pred): 
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true))


def filter_outliers(df, perc, age_t):
    df = df[df.h_distance < df.h_distance.max()]
    df = df[df.tripduration < np.percentile(df.tripduration,perc)]
    df = df.loc[df.age<=age_t]
    return df
    
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