import mechanize,re,csv

#mf = 'Men'
distance = 10000

athleteColNumber = 3 #??

months = {'01':'January','02':'February','03':'March',
    '04':'April','05':'May','06':'June','07':'July','08':'August',
    '09':'September','10':'October','11':'November','12':'December'}

br = mechanize.Browser()
if distance == 10000:
    response = br.open("https://en.wikipedia.org/wiki/10,000_metres_world_record_progression")
else:
    response = br.open("https://en.wikipedia.org/wiki/%i_metres_world_record_progression" % distance)
response = response.readlines()

ready, havetime, toskip = 0, 0, 0
for mf in ['M','W']:
    records = []
    startText = {'M':'id="Men','W':'id="Women'}[mf]
    postIAAF = 0
    
    for line in response:
        if startText in line:
            ready = 1
            rowcount = 0
        if ready:
            if distance in [1500,5000]:
                testword = 'IAAF era'
                if distance == 5000 and mf == 'W':
                    testword = 'IAAF world records'
            elif distance == 10000:
                testwrod = 'IAAF world records'
            elif distance == 800:
                testword = startText #(none needed)

            if testword in line:
                postIAAF = 1

        if ready and postIAAF:
            if '</table>' in line:
                ready = 0

            #qprint line
            if rowcount == 1:
                #print line
                #if '<i>' not in line and '<th>' not in line and \
                if '<td' in line:
                    #'wikitable' not in line and len(line) < 100:
                    if toskip > 0:
                        print 'prev time'
                        newTime = records[-1][0]
                    else:
                        newTime = re.search('(?:[td>b<]*)([0-9:.]{5,8})',line).groups()[0]
                        minsec, tenths = newTime.split('.')
                        mins,secs = minsec.split(':')
                        newTime = float(str(60*int(mins)+int(secs))+'.'+tenths)
                        print newTime

                    havetime = 1
                    if 'rowspan' in line:
                        toskip = int(re.search('rowspan="([1-9])"',line).groups()[0])

            if rowcount == athleteColNumber:# and toskip == 0 or rowcount == 4 and toskip > 0:

                if havetime:
                    #print line
                    if 'href' in line:
                        #athlete = re.search('.*>([A-Za-z \\\]*)</a></td>',line).groups()[0]
                        #athlete = re.search('.*>([\D]*)</a></td>',line).groups()[0]
                        athlete = 'NA'
                    else:
                        #athlete = re.search('.*>([A-Za-z ]*)</td>',line).groups()[0]
                        #athlete = re.search('.*>([\D]*)</td>',line).groups()[0]
                        athlete = 'NA'

            if havetime and rowcount >= 3 and re.search('\d{4}-\d{2}-\d{2}',line):
                newDate = re.search('(\d{4}-\d{2}-\d{2})',line).groups()[0]
                print newDate
                dateParts = newDate.split('-')
                newDate = '%s %s, %s' % (months[dateParts[1]],dateParts[2],dateParts[0])
                records.append([newTime,athlete,newDate])
            elif havetime and rowcount >= 3 and re.search('\d, \d{4}',line):
                newDate = re.search('(\w* \d+, \d{4})',line).groups()[0]
                print newDate
                records.append([newTime,athlete,newDate])

            if '<tr' in line:
                rowcount = 0
                havetime = 0

                if toskip > 0:
                    toskip -= 1
                if toskipAthlete > 0:
                    toskipAthlete -= 1

            rowcount += 1

    with open('data/%s%imProgress.csv' % \
        ({'M':'Men','W':'Women'}[mf],distance),'w') as csvfile:
        mywriter = csv.writer(csvfile)
        for row in records:
            mywriter.writerow(row)
