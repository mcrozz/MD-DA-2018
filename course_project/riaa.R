library(dplyr)

table <- read.csv2('data/riaa.csv', header=TRUE, sep=';')
time.range <- read.csv2('data/riaa-genre-timespans.csv', header=TRUE, sep=';')

# Converting columns
table$Certification.date <- as.Date(table$Certification.date, '%B %d, %Y')
table$Release.date <- as.Date(table$Release.date, '%B %d, %Y')
time.range$Start <- as.Date(time.range$Start)
time.range$End <- as.Date(time.range$End)

value <- regexpr('(\\d+|\\d+\\.\\d+)', table$Certified.Units)
value <- regmatches(table$Certified.Units, value)
table$Certified.Units <- as.double(value) * 1e6
remove('value')

# Filtering dataset from garbage
table %>%
  filter(Genre != 'UNASSIGNED') %>%
  filter(Genre != ' None') %>%
  filter(!is.na(Genre)) %>%
  filter(!is.na(Release.date)) %>%
  filter(!is.na(Certified.Units)) -> table

table$Genre = factor(table$Genre)

summary(table)

save(table, time.range, file='riaa.Rda')
