records <- read.csv('recordsTable.csv',header=TRUE)

for (distance in unique(substr(mine$event,2,10))) {
    menMax <- max(records[grepl(paste0('M',distance),records$event),]$speed)
    womenMax <- max(records[grepl(paste0('W',distance),records$event),]$speed)
    cat(distance,': ',menMax/womenMax,'\n')
}

maleRecords <- records[grepl('M',records$event),]
maleRecords$distance <- as.integer(substr(maleRecords$event,2,nchar(as.character(maleRecords$event))-1))

#fit curve to speed v distance
#lin reg only has R2=0.52