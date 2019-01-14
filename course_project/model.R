library(optparse)
library(dplyr)
option_list <- list(
    make_option(c('--genre'), action='store', default=NA, type='character', help='Genre')
)
opt = parse_args(OptionParser(option_list=option_list))

setwd('..') # for script

load('riaa.Rda')

generate.model <- function (timeseries) {
  model <- Arima(timeseries, seasonal=c(1,1,0), include.drift=T)
  return(model)
}

test.model <- function (timeseries) {
  ts.start <- start(timeseries)
  ts.end <- end(timeseries)
  ts.middle <- round(((ts.end[1] - ts.start[1]) * 0.6) + ts.start[1])
  model.train <- window(timeseries,
                        start=c(ts.start[1], ts.start[2]),
                        end=c(ts.middle[1], 12))
  model.test <- window(timeseries,
                       start=c(ts.middle[1]+1, 1),
                       end=c(ts.end[1], ts.end[2]))
  
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
  print(levels(time.range$Genre))

} else {
  library(spatstat)
  library(forecast)
  library(lubridate)

  ts.range <- filter(time.range, Genre == opt$genre)
  ts.range.start = ts.range$Start[1]
  ts.range.end = ts.range$End[1]
  ts.lag <- ts.range$Lag[1]
  remove('ts.range')
  
  table %>%
    filter(Genre == opt$genre) %>%
    filter(Release.date > ts.range.start) %>%
    filter(Release.date < ts.range.end) %>%
    select(c(Certified.Units, Release.date)) %>%
    group_by(Release.date=floor_date(Release.date, "month")) %>%
    summarise(Certified.Units=sum(Certified.Units)) %>%
    mutate(Certified.Units=log(Certified.Units)) %>%
    filter(Certified.Units > 13 & Certified.Units < 18) %>%
    arrange(Release.date) %>%
    select(c(Certified.Units)) %>%
    ts(.,
       start=c(year(ts.range.start), month(ts.range.start)),
       end=c(year(ts.range.end), month(ts.range.end)),
       frequency=12) -> timeseries
  
  model <- generate.model(timeseries)
  
  print('!&hasqr') # lag should be equals df from checkresiduals
  print(Box.test(model$residuals, lag=ts.lag, type='Ljung-Box', fitdf=0)$statistic)
  
  print('!&ljung')
  print(checkresiduals(model, plot=F))
  
  model.forecast <- forecast(model, h=24)
  prediction.sales <- model.forecast$upper[,2][1:12]
  
  pks <- which(diff(sign(diff(prediction.sales, na.pad=F)), na.pad=F) < 0) + 2
  peaks <- pks[prediction.sales[pks - 1] - prediction.sales[pks] > 0] - 1
  dates <- round(peaks / 12 * 365)
  
  print('!&dates')
  print(dates)
  
  test.model(timeseries)
}
