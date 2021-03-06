library(ggplot2)

records <- read.csv('recordsTable.csv',header=TRUE)
records$MF <- substring(records$event,1,1)

#for (distance in unique(substr(records$event,2,10))) {
#    menMax <- max(records[grepl(paste0('M',distance),records$event),]$speed)
#    womenMax <- max(records[grepl(paste0('W',distance),records$event),]$speed)
#    cat(distance,': ',menMax/womenMax,'\n')
#}

records$etype <- 'run'
records[records$event %in% c('MHammer','MShot_put','MDiscus',
    'WHammer','WShot_put','WDiscus'),]$etype <- 'throw'
records[records$event %in% c('MLong_jump','MTriple_jump',
    'WLong_jump','WTriple_jump'),]$etype <- 'jump'


maleRecords <- records[grepl('M',records$event),]
maleRecords$distance <- as.integer(substr(maleRecords$event,2,nchar(as.character(maleRecords$event))-1))

mine <- ggplot(records) + geom_point(aes(dateDays,normSpeed,colour=etype,shape=MF))
mine

#For women looks like 800,1500,400 (and 200,100) maybe got too good too fast, 
#  and/or 5000 was late to start
#1500 and 10000 have been brought back to schedule recently?
#Actually curve fit may be OK as times in 80s sit above line. Recent
#  1500 and 10000 times important to anchor curve. Or could use top 20s
#  to normalise M v F.

#Men's throwing seems to follow different path: length almost doubling
#  from start to 80s, whereas running speed doesn't see similar improvement.