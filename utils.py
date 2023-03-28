import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math

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
    if not axhs:
        for axh in axhs:
            axes[0].axhline(axh[0], linestyle='--', label=axh[1], color=axh[2])
    axes[0].set_title("Overall")
    axes[0].set_ylabel("Trips Duration (s)")
    axes[0].legend()

    sns.boxplot(data=df, y="tripduration", x="year", ax=axes[1])
    if not axhs:
        for axh in axhs:
            axes[1].axhline(axh[0], linestyle='--', label=axh[1], color=axh[2])
    axes[1].set_ylabel("")
    axes[1].set_yticklabels([])
    axes[1].set_title("By Year")

    axes[1].legend()

    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig("images/{}.png".format(savename))