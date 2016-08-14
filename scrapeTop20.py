import mechanize,csv,re

#TODO: get top 20 in 2015 from all-athletics.com

codes = ['10229630','10229605','10229631','10229501','10229502','10229607','10229609','10229610']
events = ['Men%im' % i for i in [100,200,400,800,1500,3000,5000,10000]]
codes += ['10229617','10229618']
events += ['MenLong_jump','MenTriple_jump']
codes += ['10229619','10229621','10229620']
events += ['MenShot_put','MenHammer','MenDiscus']

codes += ['10229509','10229510','10229511','10229512','10229513','10229519','10229514','10229521']
events += ['Women%im' % i for i in [100,200,400,800,1500,3000,5000,10000]]
codes += ['10229528','10229529']
events += ['WomenLong_jump','WomenTriple_jump']
codes += ['10229530','10229532','10229531']
events += ['WomenShot_put','WomenHammer','WomenDiscus']

br = mechanize.Browser()

avbestscores = []
for c in range(len(codes)):
    if 'Women' in events[c]:
        response = br.open('http://www.all-athletics.com/en-us/top-lists?event=%s&year=2015&gender=F&bro=0' % codes[c])
    else:
        response = br.open('http://www.all-athletics.com/en-us/top-lists?event=%s&year=2015&bro=0' % codes[c])
    response = response.readlines()

    for line in response:
        if 'fragment top-list' in line:
            break

    count, avScore = 0, 0
    for result in line.split('"f1-result-column">')[2:]:
        if events[c][-1] == 'm':
            time = result.split('<')[0]
            time = time.replace('h','')
            if time.find(':') != -1:
                minsecs,fracs = time.split('.')
                mins,secs = minsecs.split(':')
                time = str(60*int(mins)+int(secs))+'.'+fracs
            time = float(time)
            avScore += time
        elif 'jump' in events[c] or 'put' in events[c] or \
            'Hammer' in events[c] or 'Discus' in events[c]:
            time = result.split('<')[0]
            time = float(time)
            avScore += time

        count += 1
    avScore /= count
    print events[c],avScore
    avbestscores.append(avScore)

#requires 100m to be first in list
Mrefspeed = 100./avbestscores[0]
Wrefspeed = 100./avbestscores[len(codes)/2]
with open('top20ConvFactors.csv','w') as csvfile:
    mywriter = csv.writer(csvfile)
    for i in range(len(codes)/2):
        if events[i][-1] == 'm':
            speed = int(events[i].replace('Men','').replace('Women','')[:-1]) / avbestscores[i]
        elif 'jump' in events[i] or 'put' in events[i] or \
            'Hammer' in events[i] or 'Discus' in events[i]:
            speed = avbestscores[i]
        print events[i],speed
        mywriter.writerow((events[i],Mrefspeed/speed))

        if events[i][-1] == 'm':
            speed = int(events[i+len(codes)/2].replace('Men','').replace('Women','')[:-1]) / avbestscores[i+len(codes)/2]
        elif 'jump' in events[i] or 'put' in events[i] or \
            'Hammer' in events[i] or 'Discus' in events[i]:
            speed = avbestscores[i+len(codes)/2]
        print events[i+len(codes)/2],speed
        mywriter.writerow((events[i+len(codes)/2],Wrefspeed/speed))
