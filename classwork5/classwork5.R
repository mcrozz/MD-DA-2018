# Модифицируйте код из предыдущей лекции (функцию estimate.scaling.exponent), чтобы он возвращал список a и y0
data <- read.table("https://raw.githubusercontent.com/SergeyMirvoda/MD-DA-2018/master/data/gmp.dat", header = TRUE)
gmp <- data.frame(data)
gmp$pop <- gmp$gmp / gmp$pcgmp
y_st <- 6611

estimate.scaling.exponent <- function(a, y0=6611, response=gmp$pcgmp,
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
  
  result.a <- a
  result.y0 <- y0
  return(result)
}

k <- estimate.scaling.exponent(0.15)

# Напишите рекурсивные функции факториала и фибоначчи


# Улучшите функцию из примера к лекции 4.1 (код в файле 4.1.R)
predict.plm <- function(obj, dt) {
  # Проверим, есть ли нужные нам компоненты в объекте
  if ( !("a" %in% names(obj)) && !("y0" %in% names(obj)) ) return(NA)
  
  stopifnot("a" %in% names(obj), "y0" %in% names(obj))
  a <- obj$a
  y0 <- obj$y0
  # Проверка входных данных
  stopifnot(is.numeric(a),length(a)==1)
  stopifnot(is.numeric(y0),length(y0)==1)
  stopifnot(is.numeric(dt))
  return(y0*dt^a) # Вычислим и выйдем
}

predict.plm(k, 1)
