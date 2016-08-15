import numpy as np
import datetime,csv
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.stats import pearsonr
import pandas as pd
from sklearn import linear_model
from sklearn.metrics import precision_score,recall_score,average_precision_score,brier_score_loss

#---- Predict next new record?
events = ['Men100m','Women100m','Men200m','Women200m','Men400m','Women400m',
          'Men800m','Women800m','Men1500m','Women1500m','Men5000m','Women5000m',
          'Men10000m','Women10000m',
          'Men110mHurdles','Men400mHurdles','Women100mHurdles','Women400mHurdles',
          'MenLong_jump','MenTriple_jump','WomenLong_jump','WomenTriple_jump',
          'MenHammer','MenShot_put','MenDiscus','WomenHammer','WomenShot_put','WomenDiscus']

currentRecords, currentRecordSpeeds = [], []
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
                    'April':4,'May':5,'Jun':6,'June':6,'July':7,'August':8,'September':9,
                    'October':10,'November':11,'December':12}[m],int(d[:-1])))
        currentRecords.append(times[-1])

    if e[-1] == 'm':
        distance = int(e.replace('Men','').replace('Women','')[:-1])
        speeds = [distance/times[i] for i in range(len(times))]
    elif 'Hurdles' in e:
        distance = int(e.replace('Men','').replace('Women','').replace('Hurdles','')[:-1])
        speeds = [distance/times[i] for i in range(len(times))]
    elif 'jump' in e or 'Hammer' in e or 'Discus' in e or 'Shot' in e:
        speeds = times

    prevdrops = [times[i-1]-times[i] 
        for i in range(1,len(times)-1)]
    prevImproves = [100*(speeds[i]-speeds[i-1])/speeds[i-1] 
        for i in range(1,len(speeds)-1)]
    intervals = [(dates[i]-dates[i-1]).days 
        for i in range(2,len(dates))]

    if e[-1] == 'm' or 'Hurdles' in e:
        currentRecordSpeeds.append(distance/currentRecords[-1])
    elif 'jump' in e or 'Hammer' in e or 'Discus' in e or 'Shot' in e:
        currentRecordSpeeds.append(currentRecords[-1])

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

#for e in allRecords['event'].unique():
#    subset = allRecords[allRecords['event'] == e]
#    lastImprove = 100*(list(subset['speed'])[-1]-list(subset['speed'])[-2])/list(subset['speed'])[-2]
#
#    print 'Predicted date for next %s record (following %.2f%% improvement): %s' % \
#        (e,lastImprove,(subset.index[-1]+datetime.timedelta(days=int(intervalRegr.predict(lastImprove)))))

#---- Better to model on curve rather than look at previous single improvement
#Take male and female separately for now
#M:F speed ratio is ~1.11. Leave out/correct for W 5000m, 

#normalise speeds across different distances by using top 20 in each in 2015
allRecords['normSpeed'] = allRecords['speed']
with open('data/top20ConvFactors.csv','r') as csvfile:
    myreader = csv.reader(csvfile)
    for row in myreader:
        event = row[0].replace('Men','M').replace('Women','W')
        allRecords.loc[allRecords.event==event,'normSpeed'] /= float(row[1])
        #if event == 'M100m':
        #    Mspeed = float(row[1])
        #elif event == 'W100m':
        #    Wspeed = float(row[1])
        #    WtoMconv = Wspeed/Mspeed
        #if 'W' in event:
        #    allRecords.loc[allRecords.event==event,'normSpeed'] /= WtoMconv

#Use only men records to get good curve which avoids problems of women
#  events starting later. 
allRecords['MF'] = 'M'
allRecords.loc[[allRecords.event[i][0]=='W' for \
    i in range(len(allRecords))],'MF'] = 'W'
allRecords['dateDays'] = [list(allRecords.index)[i].toordinal() for i in range(len(allRecords.normSpeed))]

allRecordsMen = allRecords[allRecords['MF']=='M']
allRecordsWomen = allRecords[allRecords['MF']=='W']

recordsMenToFit = allRecordsMen[~allRecordsMen.event.isin(['MHammer','MShot_put','MDiscus'])]
recCurveMen = np.polyfit(recordsMenToFit.dateDays,
                         recordsMenToFit.normSpeed,
                         2)
recordsWomenToFit = allRecordsWomen[~allRecordsWomen.event.isin\
    (['WHammer','WShot_put','WDiscus','W400m','W800m'])]
recCurveWomen = np.polyfit(recordsWomenToFit.dateDays,
                           recordsWomenToFit.normSpeed,
                           2)
#recordsAllToFit = recordsMenToFit.append(recordsWomenToFit)
#recCurveAll,res,b,c,d = np.polyfit(recordsAllToFit.dateDays,recordsAllToFit.normSpeed,2,full=True)
recCurveMen = np.poly1d(recCurveMen)
recCurveWomen = np.poly1d(recCurveWomen)

print 'Normalised performance score today should be %.3f' % \
    recCurveMen(datetime.date.today().toordinal())

#plot scatter with fit line to inspect
plt.plot(recordsMenToFit['dateDays'],recordsMenToFit['normSpeed'],'bx',label='M')
plt.plot(range(700000,737000,3000),
    [recCurveMen(d) for d in range(700000,737000,3000)],'g')
plt.plot(recordsWomenToFit['dateDays'],recordsWomenToFit['normSpeed'],'rx',label='W')
plt.plot(range(700000,737000,3000),
    [recCurveWomen(d) for d in range(700000,737000,3000)],'Brown')
#plt.plot(range(720000,737000,2000),
#    [recCurveAll(d) for d in range(720000,737000,2000)],'k')
plt.legend(loc='lower right')
plt.title('Excluding throws and W400m, W800m')
plt.show()

#most recent record hopefully lies above the curve, so predict when curve 
#  catches up, using interpolation. 
#  May be better to make curve from top 5/10/20 per year but only have these from 2000.
curveMenNow = recCurveMen(datetime.date.today().toordinal())
for speed in currentRecordSpeeds:
    findRecord = allRecords[allRecords.speed==speed]
    if (findRecord.MF == 'M')[0]:
        print '%s record speed %.3f, curve now at %.3f' % \
            (findRecord.event[0],findRecord.normSpeed,curveMenNow)
#All records below curve but seems to say 200m is hardest and 
#  400m,1500m closest to curve
#for row in allRecordsMen.iterrows():
#    if row[0] > datetime.date(1995,1,1):
#        print row[1].event,row[0],row[1].time,row[1].normSpeed-recCurveMen(row[1].dateDays)

#TODO: make table of all years, position of current record relative to line,
#  target 'new record?' T or F. Maybe also 'record last year?' as feature.
#  Some interpolation needed to get position relative to line in all years.
years, diffs, newrecs, events, lengths, recents = [], [], [], [], [], []
for event in np.unique(allRecords.event):
    eventOnly = allRecords[allRecords.event==event]
    for year in range(1990,2017):
        toDateOnly = eventOnly[eventOnly.index < datetime.date(year,1,1)]
        if toDateOnly.shape[0] > 0:
            currentRecord = toDateOnly.tail(1).normSpeed[0]
            lengthStood = (datetime.date(year,1,1)-toDateOnly.tail(1).index[0]).days
            lengths.append(lengthStood)
            if lengthStood < 2*365:
                recents.append(1)
            else:
                recents.append(0)
            newRecordThisYear = len(eventOnly[[list(eventOnly.index)[i].year==year for i in range(len(eventOnly.index))]])
            if newRecordThisYear:
                newrecs.append(1)
            else:
                newrecs.append(0)
            years.append(year)
            events.append(event)
            diffs.append(currentRecord-recCurveMen(datetime.date(year,1,1).toordinal()))
#TODO a cutoff of record in previous 1 or 2 years may be better than lengthStood

#print 'Average curve diff in years with new record set = %.3f' % np.mean(diffsRecYears)
#print 'Average curve diff in years with no new record set = %.3f' % np.mean(diffsNoRecYears)
#For men it's -0.04 vs -0.01, so records are more likely

recYears = pd.DataFrame(data=np.dstack([years,events,diffs,lengths,recents,newrecs])[0],
    columns=['year','event','curveDiff','lengthStood','setRecently','newRecord'])
recYears.year = recYears.year.astype('int')
recYears.curveDiff = recYears.curveDiff.astype('float')
recYears.newRecord = recYears.newRecord.astype('int')
recYears.setRecently = recYears.setRecently.astype('int')
recYears.lengthStood = recYears.lengthStood.astype('int')

#Av age of record in years with new record is 1721 days, non-rec years 3341
histbins = recYears.sort_values('lengthStood').lengthStood.values[[0,80,160,240,320,-1]]

#Olympic years seem slightly better for records
recYears['Oyear'] = [0]*recYears.shape[0]
recYears.loc[recYears.year % 4 == 0,'Oyear'] = 1


#TODO add age of record as predictor - fit is too sensitive to this at present
print '\nCorr(newRecord,curveDiff) = %.2f' % pearsonr(recYears.newRecord,recYears.curveDiff)[0]
print 'Corr(newRecord,lengthStood) = %.2f' % pearsonr(recYears.newRecord,recYears.lengthStood)[0]
#train model 
mylogreg = linear_model.LogisticRegression(C=50)  #higher penalty fits tighter
mylogreg.fit(np.asmatrix([recYears.curveDiff,
                          recYears.setRecently,
                          recYears.Oyear]).transpose(),
             newrecs)
diffsTrain = [[recYears.curveDiff.values[i],
               recYears.setRecently.values[i],
               recYears.Oyear.values[i]] for i in range(recYears.shape[0])]
predsTrain = mylogreg.predict_proba(diffsTrain)
#Precision etc not so relevant because I'm not trying to predict records
#  in a given year. It is enough to say which are coming sooner than others.
#  So use probabilistic predictions
print '\nBrier = %.3f' % (brier_score_loss(newrecs,[predsTrain[i][1] for i in range(len(newrecs))]))
#Using constant prob of ~0.11 gives 0.093

#predictions for 2016
recYears2016 = recYears[recYears.year==2016]
diffs2016 = [[recYears2016.curveDiff.values[i],
              recYears2016.setRecently.values[i],
              recYears2016.Oyear.values[i]] for i in range(recYears2016.shape[0])]
#diffs2016 = [[recYears[recYears.year==2016].curveDiff[i],
#              recYears[recYears.year==2016].lengthStood[i]] \
#    for i in range(sum(recYears.year==2016))]    
preds2016 = mylogreg.predict_proba(diffs2016)
preds2016table = pd.DataFrame(columns=['event','chance'])
#print '\nChance of records in 2016:'
for e in range(len(diffs2016)):
    #print '%s (%s%.3f, %i days): %.1f%%' % (np.unique(allRecords.event)[e],
    #    '+' if diffs2016[e][0] > 0 else '-',
    #    diffs2016[e][0] if diffs2016[e][0] > 0 else -1*diffs2016[e][0],
    #    recYears2016.lengthStood.values[e],
    #    100*preds2016[e][1])
    preds2016table = preds2016table.append(pd.Series({'event':np.unique(allRecords.event)[e],
        'chance':round(100*preds2016[e][1],1)}), ignore_index=True)

print '\nMost likely records in 2016:'
print preds2016table.sort_values('chance',ascending=False).head(8)
print '\nLeast likely:'
print preds2016table.sort_values('chance',ascending=True).head(8)

#TODO: can run through different years and get prob of record by 2026

allRecords.to_csv('recordsTable.csv')
