library(optparse)
option_list <- list(
    make_option(c("--genre"), action="store", default=NA, type='character', help="Genre")
)
opt = parse_args(OptionParser(option_list=option_list))

load('../riaa.Rda')

table <- table[table$Genre==opt$genre,]

print(table[1,])