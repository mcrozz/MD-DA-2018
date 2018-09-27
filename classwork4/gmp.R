# Загрузите данные в датафрейм /data/gmp.dat 
data <- read.table("https://raw.githubusercontent.com/SergeyMirvoda/MD-DA-2018/master/data/gmp.dat", header = TRUE)
gmp <- data.frame(data)
gmp$pop <- gmp$gmp / gmp$pcgmp
y_st <- 6611

estimate.scaling.exponent <- function(a, y0=y_st, response=gmp$pcgmp,
                                        predictor = gmp$pop, maximum.iterations=100, deriv.step = 1/100,
                                        step.scale = 1e-12, stopping.deriv = 1/100) {
  mse <- function(a) { mean((response - y0*predictor^a)^2) }
  for (iteration in 1:maximum.iterations) {
    deriv <- (mse(a+deriv.step) - mse(a))/deriv.step
    a <- a - step.scale*deriv
    if (abs(deriv) <= stopping.deriv) { break() }
  }
  fit <- list(a=a,iterations=iteration,
              converged=(iteration < maximum.iterations))
  return(fit)
}

# Пример вызова с начальным занчением a
k <- estimate.scaling.exponent(0.15)

# С помошью полученного коэффициента постройте кривую (функция curve) зависимости
curve(y_st * x ^ estimate.scaling.exponent(0.15, y0 = y_st)$a,
      xlab = "Население",
      ylab = "ВВП / Человек",
      from = 1,
      to = 1000)

# Удалите точку из набора исходных данных случайным образом, как изменилось статистическая оценка коэффициента a?
set.seed(86548435, kind = "Knuth-TAOCP-2002")
gmp <- gmp[-c(sample.int(nrow(gmp), 1))]
k_changed <- estimate.scaling.exponent(0.15)

k$a - k_changed$a

# Запустите оценку несколько раз с разных стартовых точек. Как изменилось значение a?
k_1000 <- estimate.scaling.exponent(0.15, 1000)
k_2000 <- estimate.scaling.exponent(0.15, 2000)
k_3000 <- estimate.scaling.exponent(0.15, 3000)
k_10000 <- estimate.scaling.exponent(0.15, 10000)

# TODO: add graph
