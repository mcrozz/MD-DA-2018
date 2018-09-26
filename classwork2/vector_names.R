# Урал (Домашние матчи)
ural_home <- c(2, 0, 1, 0)

# Выездные
ural_away <- c(0, 0, 1, 1)

# Напечатайте на консоль оба вектора
ural_home
ural_away

# Назначим имена элеметом вектора (Команды Гости)
names(ural_home) <- c("Ufa", "CSKA", "Arsenal", "Anzhi")

# Проделайте то же самое для вектора ural_away назначив имена команд гостей (away_names)
away_names <- c("Rostov", "Amkar", "Rubin", "Orenburg")
names(ural_away) <- away_names

# Напечатайте на консоль оба вектора, заметьте разницу
ural_home
ural_away

# Посчитайте статистикку домашних и выездных матчей
## Количество голов
sum(ural_home)
sum(ural_away)
## Среднее количество голов
mean(ural_home)
mean(ural_away)

# Сравните векторы ural_home и ural_away и сделайте вывод
if ( identical(ural_home, ural_home) ) "identical" else "not same"
