import mechanize,csv,re

#TODO: get top 20 in 2015 from all-athletics.com

codes = ['10229630','10229605','10229631','10229501','10229502','10229607','10229609','10229610']
events = ['Men%im' % i for i in [100,200,400,800,1500,3000,5000,10000]]
#codes += []
codes += ['10229509','10229510','10229511','10229512','10229513','10229519','10229514','10229521']
events += ['Women%im' % i for i in [100,200,400,800,1500,3000,5000,10000]]

br = mechanize.Browser()

avbesttimes = []
for c in range(len(codes)):
    if 'Women' in events[c]:
        response = br.open('http://www.all-athletics.com/en-us/top-lists?event=%s&year=2015&gender=F&bro=0' % codes[c])
    else:
        response = br.open('http://www.all-athletics.com/en-us/top-lists?event=%s&year=2015&bro=0' % codes[c])
    response = response.readlines()

    for line in response:
        if 'fragment top-list' in line:
            break

    count, avTime = 0, 0
    for result in line.split('"f1-result-column">')[2:]:
        time = result.split('<')[0]
        time = time.replace('h','')
        if time.find(':') != -1:
            minsecs,fracs = time.split('.')
            mins,secs = minsecs.split(':')
            time = str(60*int(mins)+int(secs))+'.'+fracs
        time = float(time)
        avTime += time
        count += 1
    avTime /= count
    print events[c],avTime
    avbesttimes.append(avTime)

Mrefspeed = 100./avbesttimes[0]
Wrefspeed = 100./avbesttimes[len(codes)/2]
with open('top20ConvFactors.csv','w') as csvfile:
    mywriter = csv.writer(csvfile)
    for i in range(len(codes)/2):
        speed = int(events[i].replace('Men','').replace('Women','')[:-1]) / avbesttimes[i]
        print events[i],speed
        mywriter.writerow((events[i],Mrefspeed/speed))
        speed = int(events[i+len(codes)/2].replace('Men','').replace('Women','')[:-1]) / avbesttimes[i+len(codes)/2]
        print events[i+len(codes)/2],speed
        mywriter.writerow((events[i+len(codes)/2],Wrefspeed/speed))
