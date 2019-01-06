library("spatstat")
library("forecast")
library("lubridate")
#table <- read.csv2('data/riaa.csv', header=TRUE, sep=';')

# Converting columns
#table$Certification.date <- as.Date(table$Certification.date, '%B %d, %Y')
#table$Release.date <- as.Date(table$Release.date, '%B %d, %Y')

#value <- regexpr("(\\d+|\\d+\\.\\d+)", table$Certified.Units)
#value <- regmatches(table$Certified.Units, value)
#table$Certified.Units <- as.double(value) * 1e6

#summary(table)

#plot(table$Release.date ~ table$Certification.date)

load('riaa.Rda')

genre<-table[table$Genre=="ROCK",]
genre$Award<-c(1,2,3)[genre$Award]
y=ts(genre$Certified.Units, start=c(2012, yday("2012-01-01")),end=c(2018, yday("2018-01-01")), frequency=365)
y.stlf<-stlf(y,h=365)
plot(y.stlf)
Q<-ppp(x=genre$Release.date, y=genre$Award)
Q <- ppp(genre)
ppm(Q ~ 1)
fit<-arima(y, order=c(1,0,12))
plot(forecast(fit, 365))
accuracy(fit)
