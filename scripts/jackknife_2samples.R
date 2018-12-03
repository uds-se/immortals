#!/usr/bin/env Rscript
require("data.table")
require("argparse")

parser = ArgumentParser()

parser$add_argument("-f", "--matrix_fuzz", help="Input matrix for fuzzing testsuit")
parser$add_argument("-d", "--matrix_dev", help="Input matrix for manual testsuit")
args = parser$parse_args()

data_fuzz = fread(args$matrix_fuzz)
data_dev = fread(args$matrix_dev)
cat("Fuzz data size: ", dim(data_fuzz), "\n")
cat("Dev data size: ", dim(data_dev), "\n")
data_fuzz = data_fuzz[,-1]
data_dev = data_dev[,-1]
rsf = rowSums(data_fuzz)
rsd = rowSums(data_dev)
data = as.data.table(cbind(sign(rsf), sign(rsd)))
print(data)

k = ncol(data)
rs = rowSums(data)
print(rs)
counts = as.data.table(table(rs))
sprintf("# Samples: %d", k)
sprintf("# Mutants: %d", nrow(data))
print("Counts")
print(counts)

# get_estimator <- function(k, n) {
# 	series = seq(1, k, 1)
# 	s = 1/choose(n, k)*sum()
# }

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
sprintf("capture frequences: 1-%d 2-%d 3-%d 4-%d", f1, f2, f3, f4)
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