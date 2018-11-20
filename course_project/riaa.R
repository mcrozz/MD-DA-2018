table <- read.csv2('data/riaa.csv', header=TRUE, sep=';')

# Converting columns
table$Certification.date <- as.Date(table$Certification.date, '%B %d, %Y')
table$Release.date <- as.Date(table$Release.date, '%B %d, %Y')

value <- regexpr("(\\d+|\\d+\\.\\d+)", table$Certified.Units)
value <- regmatches(table$Certified.Units, value)
table$Certified.Units <- as.double(value) * 1e6

summary(table)

plot(table$Release.date ~ table$Certification.date)
