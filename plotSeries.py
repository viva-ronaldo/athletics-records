import numpy as np
import datetime,csv
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.stats import pearsonr
import pandas as pd
from sklearn import linear_model

men100mtimes = [10.6,10.4,10.3,10.2,10.1,10.0,9.95,
                9.93,9.92,9.90,9.86,9.85,9.84,9.79,
                9.77,9.74,9.72,9.69,9.58]
men100myears = [1912,1921,1930,1936,1956,1960,1968,
                1983,1988,1991,1992,1994,1996,1999,
                2005,2007,(2008,4),(2008,7),2009]
men100mdates = []
for year in men100myears:
    men100mdates.append(datetime.date(year,6,1) if \
        type(year) == type(1) else datetime.date(year[0],year[1],1))

women100mtimes = [12.8,12.4,12.2,12.0,11.9,11.8,
                  11.7,11.6,11.5,11.4,11.3,11.2,
                  11.1,11.08,11.07,11.04,11.01,10.88,
                  10.81,10.79,10.76,10.49]
women100myears = [1922,1926,(1928,4),(1928,7),1932,1933,
                  1934,1937,1948,1952,1955,1961,
                  1965,1968,1972,(1976,4),(1976,7),1977,
                  (1983,4),(1983,7),1984,1988]
women100mdates = []
for year in women100myears:
    women100mdates.append(datetime.date(year,6,1) if \
        type(year) == type(1) else datetime.date(year[0],year[1],1))

men100minterp = interp1d([men100mdates[i].toordinal() \
    for i in range(len(men100mdates))], men100mtimes,
    bounds_error=False, fill_value=men100mtimes[-1])
women100minterp = interp1d([women100mdates[i].toordinal() \
    for i in range(len(women100mdates))], women100mtimes,
    bounds_error=False, fill_value=women100mtimes[-1])

smoothtimes = range(men100mdates[0].toordinal(),datetime.date.today().toordinal())

# plt.plot(smoothtimes,men100minterp(smoothtimes),'k')
# plt.plot(smoothtimes,women100minterp(smoothtimes),'Violet')
# plt.plot(men100mdates,men100mtimes,'ko')
# plt.plot(women100mdates,women100mtimes,'o',color='Violet')
# plt.show()

# plt.plot([datetime.date.fromordinal(smoothtimes[i]) for i in range(len(smoothtimes))],
#     men100minterp(smoothtimes)/women100minterp(smoothtimes),
#     lw=2)
# plt.title('100m women record speed as fraction of men record')
# plt.ylabel('Performance fraction')
# plt.xlim([women100mdates[1],datetime.date.today()])
# plt.ylim([0.75,1.02])
# plt.plot([women100mdates[1],datetime.date.today()],[1,1],'k:')
# plt.show()

#---- Predict next new record?
events = ['Men100m','Women100m','Men200m','Women200m','Men400m','Women400m']

for e in events:
    times, athletes, dates = [], [], []
    with open('data/%sProgress.csv' % e,'r') as csvfile:
        myreader = csv.reader(csvfile)
        for row in myreader:
            if len(times) == 0 or float(row[0]) != times[-1]:
                times.append(float(row[0]))
                athletes.append(row[1])
                m,d,y = row[2].split(' ')
                dates.append(datetime.date(int(y),{'January':1,'February':2,'March':3,
                    'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,
                    'October':10,'November':11,'December':12}[m],int(d[:-1])))

    distance = int(e.replace('Men','').replace('Women','')[:-1])
    speeds = [distance/times[i] for i in range(len(times))]
    prevdrops = [times[i-1]-times[i] 
        for i in range(1,len(times)-1)]
    prevImproves = [100*(speeds[i]-speeds[i-1])/speeds[i-1] 
        for i in range(1,len(speeds)-1)]
    intervals = [(dates[i]-dates[i-1]).days 
        for i in range(2,len(dates))]
    #print 'Corr between prev drop and interval to next record = ',\
    #    pearsonr(prevdrops,intervals)[0]

    if e == events[0]:
        allRecords = pd.DataFrame(index=dates[2:],
            data=np.dstack([times[2:],speeds[2:],prevdrops,prevImproves,intervals])[0],
            columns=['time','speed','prevDrop','prevImprove','daysSincePrev'])
        allRecords['event'] = [e.replace('Men','M').replace('Women','W')]*len(intervals)
    else:
        allRecords = allRecords.append(pd.DataFrame(index=dates[2:],
            data=np.dstack([times[2:],speeds[2:],prevdrops,prevImproves,intervals])[0],

            columns=['time','speed','prevDrop','prevImprove','daysSincePrev']))
        allRecords.iloc[-len(intervals):,list(allRecords.columns).index('event')] = \
            [e.replace('Men','M').replace('Women','W')]*len(intervals)

intervalRegr = linear_model.LinearRegression(fit_intercept=False)

intervalRegr.fit(np.asmatrix(list(allRecords['prevImprove'])).transpose(),
    np.asmatrix(list(allRecords['daysSincePrev'])).transpose())

for e in allRecords['event'].unique():
    subset = allRecords[allRecords['event'] == e]
    lastImprove = 100*(list(subset['speed'])[-1]-list(subset['speed'])[-2])/list(subset['speed'])[-2]

    print 'Predicted date for next %s record (following %.2f%% improvement): %s' % \
        (e,lastImprove,(subset.index[-1]+datetime.timedelta(days=int(intervalRegr.predict(lastImprove)))))

allRecords.to_csv('recordsTable.csv')

#---- Better to model on curve rather than look at previous single improvement
#Take male and female separately for now

#TODO: normalise speeds across different distances by using top 20 in each in 2015

#TODO: fit all male speeds to one curve

#most recent record hopefully lies above the curve, so predict when curve 
#  catches up
