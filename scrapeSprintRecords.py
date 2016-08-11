import mechanize,re,csv

mf = 'Men'
distance = 400

if mf == 'Women' and distance in [100,200]:
    athleteColNumber = 3
elif distance >= 400:
    athleteColNumber = 2
else:
    athleteColNumber = 4

br = mechanize.Browser()
response = br.open("https://en.wikipedia.org/wiki/%s's_%i_metres_world_record_progression" \
    % (mf,distance))
response = response.readlines()


ready, havetime, toskip, toskipAthlete = 0, 0, 0, 0
records = []
for line in response:
    if 'mw-headline' in line and \
        ('from 1977' in line or 'from 1975' in line or 'post-1977' in line or 'post-1976' in line):
        ready = 1
        rowcount = 0

    if ready:
        if '</table>' in line:
            ready = 0

        #print line
        if rowcount == 1:
            #print line
            if '<i>' not in line and '<th>' not in line and len(line) < 100:
                if toskip > 0:
                    print 'prev time'
                    newTime = records[-1][0]
                else:
                    newTime = float(re.search('<td.*>([\.\d]*) ?A?</td>',line).groups()[0])
                    print newTime

                havetime = 1
                if 'rowspan' in line:
                    toskip = int(re.search('rowspan="([1-9])"',line).groups()[0])
        
        if rowcount == athleteColNumber:# and toskip == 0 or rowcount == 4 and toskip > 0:
            
            if havetime:
                print line
                if toskipAthlete == 0:
                    if 'href' in line:
                        #athlete = re.search('.*>([A-Za-z \\\]*)</a></td>',line).groups()[0]
                        athlete = re.search('.*>([\D]*)</a></td>',line).groups()[0]
                    else:
                        #athlete = re.search('.*>([A-Za-z ]*)</td>',line).groups()[0]
                        athlete = re.search('.*>([\D]*)</td>',line).groups()[0]
                else:
                    #print 'prev athlete'
                    athlete = records[-1][1]

                if 'rowspan' in line:
                    toskipAthlete = int(re.search('rowspan="([1-9])"',line).groups()[0])
                    #print 'athlete covers %i rows' % toskipAthlete

        if havetime and rowcount > 4 and re.search('\d, \d{4}',line):
            newDate = re.search('(\w* \d+, \d{4})',line).groups()[0]
            print newDate
            records.append([newTime,athlete,newDate])
        elif havetime and rowcount > 4 and re.search('\d+ \w* \d{4}',line):
            newDate = re.search('(\d+ \w* \d{4})',line).groups()[0]
            dateParts = newDate.split(' ')
            newDate = '%s %s, %s' % (dateParts[1],dateParts[0],dateParts[2])
            records.append([newTime,athlete,newDate])

        if '<tr' in line:
            rowcount = 0
            havetime = 0
            
            if toskip > 0:
                toskip -= 1
            if toskipAthlete > 0:
                toskipAthlete -= 1

        rowcount += 1
        
with open('data/%s%imProgress.csv' % (mf,distance),'w') as csvfile:
    mywriter = csv.writer(csvfile)
    for row in records:
        mywriter.writerow(row)
