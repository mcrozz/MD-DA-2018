# Append libraries that will be used for model generation on server side

packages <- c('curl', 'dplyr', 'optparse', 'spatstat', 'forecast', 'lubridate')

install.packages(packages, repos='https://cran.rstudio.com')