table <- read.csv2('data/billboard.csv', header=TRUE, sep=';')

# Converting columns
table$Date <- as.Date(table$Date, '%Y-%m-%d')

summary(table)

plot(table[table$Position == 1, ]$Title ~ table[table$Position == 1, ]$Date)
