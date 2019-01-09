library(optparse)
library(dplyr)
option_list <- list(
    make_option(c('--genre'), action='store', default=NA, type='character', help='Genre')
)
opt = parse_args(OptionParser(option_list=option_list))

setwd('..') # for script
load('riaa.Rda')
table %>%
  filter(Genre != 'UNASSIGNED') %>%
  filter(Genre != ' None') -> table

table$Genre = factor(table$Genre)


generate.model <- function (timeseries) {
  model <- Arima(timeseries, seasonal=c(1,1,0), include.drift=T)
  return(model)
}

test.model <- function (timeseries) {
  model.train <- window(timeseries, start=2000, end=2015)
  model.test <- window(timeseries, start=2015+1/12, end=2018+11/12)
  
  model <- generate.model(model.train)
  
  acc <- accuracy(forecast(model, h=length(model.test)), model.test)
  print('!&ME')
  print(acc[,1])
  print('!&RMSE')
  print(acc[,2])
  print('!&MAE')
  print(acc[,3])
  print('!&MPE')
  print(acc[,4])
  print('!&MAPE')
  print(acc[,5])
  print('!&MASE')
  print(acc[,6])
  print('!&ACF1')
  print(acc[,7])
}



if (opt$genre == 'all') {
  print(levels(table$Genre))
} else {
  library(spatstat)
  library(forecast)
  library(lubridate)
  
  table %>%
    filter(Genre == opt$genre) %>%
    filter(Release.date > as.Date('2000-01-01')) %>%
    filter(Release.date < as.Date('2018-12-31')) %>%
    filter(!is.na(Certified.Units)) -> table
  
  timeseries <- ts(table$Certified.Units, start=2000, end=2018+11/12, frequency=12)
  
  model <- generate.model(timeseries)
  
  print('!&ljung')
  print(checkresiduals(model))
  
  model.forecast <- forecast(model, h=24)
  prediction.sales <- model.forecast$upper[,2][1:12]
  
  pks <- which(diff(sign(diff(prediction.sales, na.pad=F)), na.pad=F) < 0) + 2
  peaks <- pks[prediction.sales[pks - 1] - prediction.sales[pks] > 0] - 1
  dates <- round(peaks / 12 * 365)
  
  print('!&dates')
  print(dates)
  
  test.model(timeseries)
}
