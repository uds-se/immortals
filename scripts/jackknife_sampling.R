#!/usr/bin/env Rscript
require("data.table")
require("argparse")

parser = ArgumentParser()

parser$add_argument("-m", "--matrix", help="Input matrix")
args = parser$parse_args()

data = fread(args$matrix)
cat("Data size: ", dim(data), "\n")
print(data, nrows=3, topn=2)
data = data[,-1]

k = sum(data)
rs = rowSums(data)
print(rs)
counts = as.data.table(table(rs))
sprintf("# Samples: %d", k)
sprintf("# Mutants: %d", nrow(data))
print("Counts")
print(counts)

get_order <- function(df, order) {
    val = df[rs==order,N]
    if (length(val)==0){
        return(0)
    } else{
        return(val)
    }
}

f1=get_order(counts, 1)
f2=get_order(counts, 2)
f3=get_order(counts, 3)
f4=get_order(counts, 4)
sum_fk = sum(counts[rs!=0,N])
print("Estimations")
est1 = sum_fk + f1 * (  k - 1) /k
est2 = sum_fk + f1 * (2*k - 3) /k - f2 * (k - 2)^2           /(k*(k-1))
est3 = sum_fk + f1 * (3*k - 6) /k - f2 * (3*k^2 - 15*k + 19) /(k*(k-1)) + f3 * (k-3)^3                 /(k*(k-1)*(k-2))
est4 = sum_fk + f1 * (4*k - 10)/k - f2 * (6*k^2 - 36*k + 55) /(k*(k-1)) + f3 * (4*k^3-42*k^2+148*k-175)/(k*(k-1)*(k-2)) - f4 * (k-4)^4/(k*(k-1)*(k-2)*(k-3))
sprintf("Estimation O1: %f", est1)
sprintf("Estimation O2: %f", est2)
sprintf("Estimation O3: %f", est3)
sprintf("Estimation O4: %f", est4)
sprintf("Avg est 1&2: %f", (est1+est2)/2)