# install.packages(c('tidyverse', 'gapminder', 'dplyr', 'nycflights13'))
library(gapminder)
library(dplyr)

library(magrittr)
library(nycflights13)

#Функция фильтр
filter(gapminder, lifeExp < 29)
filter(gapminder, country == "Afghanistan", year > 1981)
filter(gapminder, continent %in% c("Asia", "Africa"))

#Тоже самое для векторов
gapminder[gapminder$lifeExp < 29, ]
subset(gapminder, country == "Rwanda")

head(gapminder)
gapminder %>% head(3)

head(select(gapminder, year, lifeExp),4)

#Ниже то же самое, но с пайпом
gapminder %>%
  select(year, lifeExp) %>%
  head(4)

gapminder %>%
  filter(country == "Cambodia") %>%
  select(year, lifeExp)

#Ниже то же самое
gapminder[gapminder$country == "Cambodia", c("year", "lifeExp")]

#Для демонстрации следующих функций загрузим другой датасет
msleep <- read.csv("https://raw.githubusercontent.com/genomicsclass/dagdata/master/inst/extdata/msleep_ggplot2.csv")
head(msleep)

#Упорядочить по одной колонке
msleep %>% arrange(order) %>% head

#По нескольким
msleep %>% 
  select(name, order, sleep_total) %>%
  arrange(order, sleep_total) %>% 
  head

#Отфильтруем и отсортируем по убыванию
msleep %>% 
  select(name, order, sleep_total) %>%
  arrange(order, sleep_total) %>% 
  filter(sleep_total >= 16)

#Добавление колонок
msleep %>%
  select(name, sleep_rem, sleep_total) %>% 
  mutate(rem_proportion = sleep_rem / sleep_total) %>%
  head

#Получение итогов
msleep %>% 
  summarise(avg_sleep = mean(sleep_total), 
            min_sleep = min(sleep_total),
            max_sleep = max(sleep_total),
            total = n())

msleep %>% 
  group_by(order) %>%
  summarise(avg_sleep = mean(sleep_total), 
            min_sleep = min(sleep_total), 
            max_sleep = max(sleep_total),
            total = n())


# http://rpubs.com/tjmahr/dplyr_2015


tbl_df(flights)

glimpse(flights)

flights %>%
  filter(dest == "MSN")

flights %>%
  filter(dest == "MSN", month == 1, day <= 7)

flights %>%
  arrange(origin, year, month, day)

flights %>%
  filter(dest == "MSN") %>%
  arrange(desc(dep_delay))

flights %>%
  select(origin, year, month, day)

flights %>%
  select(origin, year:day, starts_with("dep"))

flights %>%
  select(-dest, -starts_with("arr"),
         -ends_with("time"))

flights %>%
  rename(y = year, m = month, d = day)

flights %>%
  mutate(
    gain = arr_delay - dep_delay,
    speed = (distance / air_time) * 60,
    gain_per_hour = gain / (air_time / 60)) %>%
  select(gain:gain_per_hour)

aggregate(dep_delay ~ month, flights, mean,
          subset = flights$dest == "MSN")

msn_by_month <- flights %>%
  filter(dest == "MSN") %>%
  group_by(month)
flights

msn_by_month %>%
  summarise(
    flights = n(),
    avg_delay = mean(dep_delay, na.rm = TRUE),
    n_planes = n_distinct(tailnum))

flights %>%
  group_by(dest, month) %>%
  tally

msn_by_month %>% ungroup

per_day <- flights %>%
  group_by(dest, year, month, day) %>%
  summarise(flights = n())
per_day

per_month <- per_day %>%
  summarise(flights = sum(flights))
per_month

per_year <- per_month %>%
  summarise(flights = sum(flights))
per_year

flights %>%
  group_by(dest, month) %>%
  mutate(timely = row_number(dep_delay),
         late = row_number(desc(dep_delay))) %>%
  select(dep_delay, timely:late)

mean_center <- function(xs) {
  xs - mean(xs, na.rm = TRUE)
}
flights %>%
  group_by(dest, month) %>%
  mutate(c_delay = mean_center(dep_delay)) %>%
  select(dep_delay, c_delay)
