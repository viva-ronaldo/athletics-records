import mechanize,re,csv

event = 'Triple_jump'

athleteColNumber = 3 #??

months = {'01':'January','02':'February','03':'March',
    '04':'April','05':'May','06':'June','07':'July','08':'August',
    '09':'September','10':'October','11':'November','12':'December'}

br = mechanize.Browser()
response = br.open("https://en.wikipedia.org/wiki/%s_world_record_progression" % event)
response = response.readlines()

ready, havetime, toskip = 0, 0, 0
for mf in ['M','W']:
    records = []
    startText = {'M':'id="Men','W':'id="Women'}[mf]
    IAAFcond = 0
    
    for line in response:
        if startText in line:
            ready = 1
            rowcount = 0
        if ready:
            if event == 'Triple_jump' and mf == 'W':
                if 'Official IAAF progression from 1990' in line:
                    IAAFcond = 1
                    print 'found starter'
                    print line
            else:
                IAAFcond = 1

        if ready and IAAFcond:
            if '</table>' in line and len(records) > 0:
                ready = 0

            #print line, rowcount
            if rowcount == 1:
                if '<td align' in line:
                    print line
                    if toskip > 0:
                        print 'prev dist'
                        newDist = records[-1][0]
                    else:
                        newDist = re.search('([0-9]{1,2}\.[0-9]{1,2})',line).groups()
                        newDist = float(newDist[0])
                        print newDist

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
                records.append([newDist,athlete,newDate])
            elif havetime and rowcount >= 3 and re.search('\d{2} \w* \d{4}',line):
                newDate = re.search('(\d{2} \w* \d{4})',line).groups()[0]
                dateParts = newDate.split(' ')
                newDate = '%s %s, %s' % (dateParts[1],dateParts[0],dateParts[2])
                print newDate
                records.append([newDist,athlete,newDate])

            if '<tr' in line:
                rowcount = 0
                havetime = 0

                if toskip > 0:
                    toskip -= 1
                #if toskipAthlete > 0:
                #    toskipAthlete -= 1

            rowcount += 1

    with open('data/%s%sProgress.csv' % \
        ({'M':'Men','W':'Women'}[mf],event),'w') as csvfile:
        mywriter = csv.writer(csvfile)
        for row in records:
            mywriter.writerow(row)
