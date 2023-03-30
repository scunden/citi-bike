# Getting Started

First, create a virtual environment using the `requirements.txt` file, using the command `conda create --name <env> --file requirements.txt`

To generate all the plots and images used in the summary reports, simply run the jupyter notebooks after the virtual environment has been created. All plots and images will be generated in the `images` directory

# Executive Summary

In this section, I will give a brief overview of the major takeaways from each section. This section is only intended to summarize the overall results, and more details can be found within the respective sections.

## 1. Detection of potential outliers and anomalies for Citibike usage

I found that ultimately, there were two main source of anomalies. There were some smaller discrepancies in `trip distance`, but the main one was in the `tripduration` and `birth_year` variables, where I observed a lot of extremely high outliers. Let's start with `tripduration`.

### Trip Duration

![trips-duration-outliers](./images/box-plot-all.png)

As you can see, a lot of these outliers far exceed the **24hour usage limit** that Citi Bike has, which means that these data points are either completely **incorrect**, or there was a **mis calculation** in how their duration was measured. Additional analyses revealed that those were indeed incorrect datapoints or extreme usage case.

To observe a more representative distribution of the data, I then chose to retain only up to the **95th percentile** of trip duration, losing only a small percentage of data points. The resulting distribution is shown below.

![trips-duration-outliers](./images/box-plot-95th.png)

---

### Age

We observed a similar pattern for age, whereby some records had extremely high ages in comparison to the median. However, all of those high cases were contained within "Subscriber" users, as shown below:

![trips-duration-outliers](./images/age_box_plot_unfiltered.png)

Given that the extreme cases were concentrated in one class, my assumption was that most of these data points must have been some data collection system. It is also entirely possible that some of these older customers are legitimate, especially since we see the average age being slightly higher for subscribers, but ages greater than 80 seem unreasonable.

So I have fileterd the dataset to only retain records of age 80 and below. This removed less than 0.3% of the data points available, but gave me more confidence in the dataset. The final disribution are shown below.

![trips-duration-outliers](./images/age_box_plot_filtered.png)

## 2. Citibike usage forecast

Here, I set out to predict the citi bikes usage, by focusing on the aggregated number of trips by day. But first, I identified the major components of our series, shown below:

![trips-duration-outliers](./images/daily_decomposition.png)

We can see that our data has a clear trend, but that it is very recent. The first few years of the data are fairly flat. We also observe two seasonality patterns, one at a yearly level where we see warmer months attract more trips, and one at the weekly level where weekdays are usually much busies than the weekend. 

We can also see that holidays generally have a negative impact on the number of trips. Other than Columbus day and Easter, on most holidays, the bike usage decreases.

Now, I used those results to help guide a grid search over a large parameter space to find the best performing algorithm. The best performing algorithm was found to have  daily MAPE score of ~26%, and is shown predicting usage for 2017 below:

![trips-duration-outliers](./images/2017_daily_forecast.png)


## 3. Insights into bike stations based on the data