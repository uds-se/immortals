#!/usr/bin/env Rscript
require("data.table")
require("argparse")
require("wiqid")
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

print("Estimations")
print(closedCapMhJK(counts$N))