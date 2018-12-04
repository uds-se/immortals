#!/usr/bin/env Rscript
require("data.table")
require("argparse")
require("wiqid")

get_order <- function(df, order) {
    val = df[rs==order,N]
    if (length(val)==0){
        return(0)
    } else{
        return(val)
    }
}

get_custom_estimate<-function(counts){
    k=nrow(counts)
    f1=get_order(counts, 1)
    f2=get_order(counts, 2)
    f3=get_order(counts, 3)
    f4=get_order(counts, 4)
    sum_fk = sum(counts[rs!=0,N])
    est1 = sum_fk + f1 * (k - 1)   /k
    est2 = sum_fk + f1 * (2*k - 3) /k - f2 * (k - 2)^2          /(k*(k-1))
    est3 = sum_fk + f1 * (3*k - 6) /k - f2 * (3*k^2 - 15*k + 19)/(k*(k-1)) + f3 * (k-3)^3                 /(k*(k-1)*(k-2))
    est4 = sum_fk + f1 * (4*k - 10)/k - f2 * (6*k^2 - 36*k + 55)/(k*(k-1)) + f3 * (4*k^3-42*k^2+148*k-175)/(k*(k-1)*(k-2)) - f4 * (k-4)^4/(k*(k-1)*(k-2)*(k-3))
    return (list(est1,est2,est3,est4))
}

process_file<-function(f_name){
    matrix = fread(f_name)
    sprintf("Processing %s", basename(f_name))
    cat("Data size: ", dim(matrix), "\n")
    # print(data, nrows=3, topn=2)
    if (max(matrix) > 1){ # remove index column
        matrix = matrix[,-1]
    }
    return (get_estimate(matrix))
}

process_folder<-function(d_name){
    res = data.table(
            file_name = character(),
            real_mutants_count = integer(),
            wiqid_estimation = numeric(),
            custom_estimation = character()
        )
    for(f_name in list.files(d_name, full.names=T)){
        est_tuple = process_file(f_name)
        num_mutants = est_tuple[[1]]
        est_wiqid = est_tuple[[2]]
        est_custom = est_tuple[[3]]
        est_custom_string = paste(est_custom, collapse=', ')
        est_wiqid_count = est_wiqid$real[1,1]
        res=rbind(res, list(basename(f_name), num_mutants, est_wiqid_count, est_custom_string))
    }
    return (res)
}

get_estimate<-function(data){
    k = ncol(data)
    n_mutants = nrow(data)
    rs = rowSums(data)
    counts = as.data.table(table(factor(rs, levels=0:k)))
    setnames(counts, c("rs","N"))
    print("Frequencies:")
    print(counts)
    sprintf("# of Samples: %d", k)
    sprintf("True # of Mutants: %d", n_mutants)

    print("Estimation (wiqid)")
    est_wiqid = closedCapMhJK(counts$N)
    est_custom = get_custom_estimate(counts)
    print(est_wiqid$real)
    print("Estimation (custom)")
    print(est_custom)
    return (list(n_mutants, est_wiqid, est_custom))
}

parser = ArgumentParser()
parser$add_argument("-m", "--matrix", help="Input matrix file")
parser$add_argument("-d", "--dir", help="Input dir")
parser$add_argument("-o", "--output", help="Filename for the resulting comparison table")

args = parser$parse_args()
if (!is.null(args$matrix)){
    est=process_file(args$matrix)
}else if(!is.null(args$dir)){
    wdir = getwd()
    output = if (!is.null(args$output)) args$output else file.path(wdir, 'estimation_results.csv')
    print(output)
    #res = process_folder(args$dir)
    #fwrite(res,file=output,sep=";")
}else{
    stop("invalid arguments")
}
