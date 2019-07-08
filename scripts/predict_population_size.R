#!/usr/bin/env Rscript
library(data.table)
library("argparse")
library("wiqid")
library("jsonlite")
#not used
get_order <- function(df, order) {
    if (is.null(dim(df))) {# we have vector of frequences, not a table
        return(df[order])
    }
    val = df[rs == order, N]
    if (length(val) == 0) {
        return(0)
    } else {
        return(val)
    }
}

seN <- function(N, f, a, k){
    varN = sum(a[, k] ^ 2 * f) - N[k]
    return(sqrt(varN))
}

varNS <- function(N, f, a, S, k){
    b = a[, k + 1] - a[, k]
    v = S / (S - 1) * (sum(b ^ 2 * f) - (N[k + 1] - N[k]) ^ 2 / S)
    return(v)
}

Tk <- function(N, f, a, S, k){
    return((N[k + 1] - N[k]) / (varNS(N, f, a, S, k) ^ (1 / 2)))
}

p_value <- function(t){
    return(2 * pnorm(- t))
}

bootstrap <- function(data){
    n = ncol(data)
    # k = nrow(data)
    idx = sample(n, size = n, replace = TRUE)
    S0 = length(which(rowSums(data) > 0))
    B = data[, .SD, .SDcols = idx]
    Y = rowSums(B)
    Bs = sum((1 - Y / n) ^ n)
    Bn = S0 + Bs
    # return(list(Bn, B))
    return(Bn)
}

bootstrap_estimate <- function(data, counts, t=1000){
    data = data[rowSums(data) > 0] # get only caught mutants
    bres = replicate(t, bootstrap(data), simplify = TRUE)
    bn = mean(bres)
    varbn = 1 / (t - 1) * sum((bres - bn) ^ 2)
    se = sqrt(varbn)
    return(list(N = bn, lowCI = bn - 1.96 * se, uppCI = bn + 1.96 * se))
}

get_custom_jackknife_estimate <- function(data, counts){
    k = length(counts)
    #f = sapply(c(1 : k), function(x)get_order(counts, x))
    f = counts
    S = sum(counts)
    a = matrix(1, k, 5)
    N = c(0, 0, 0, 0)
    T = c(0, 0, 0)
    p = c(0, 0, 0)
    a[1, 1] = 1 + (k - 1) / k
    a[1, 2] = 1 + (2 * k - 3) / k
    a[2, 2] = 1 - (k - 2) ^ 2 / (k * (k - 1))
    a[1, 3] = 1 + (3 * k - 6) / k
    a[2, 3] = 1 - (3 * k ^ 2 - 15 * k + 19) / (k * (k - 1))
    a[3, 3] = 1 + (k - 3) ^ 3 / (k * (k - 1) * (k - 2))
    a[1, 4] = 1 + (4 * k - 10) / k
    a[2, 4] = 1 - (6 * k ^ 2 - 36 * k + 55) / (k * (k - 1))
    a[3, 4] = 1 + (4 * k ^ 3 - 42 * k ^ 2 + 148 * k - 175) / (k * (k - 1) * (k - 2))
    a[4, 4] = 1 - (k - 4) ^ 4 / (k * (k - 1) * (k - 2) * (k - 3))
    a[1, 5] = 1 + (5 * k - 15) / k
    a[2, 5] = 1 - (10 * k ^ 2 - 70 * k + 125) / (k * (k - 1))
    a[3, 5] = 1 + (10 * k ^ 3 - 120 * k ^ 2 + 485 * k - 660) / (k * (k - 1) * (k - 2))
    a[4, 5] = 1 - ((k - 4) ^ 5 - (k - 5) ^ 5) / (k * (k - 1) * (k - 2) * (k - 3))
    a[5, 5] = 1 + (k - 5) ^ 5 / (k * (k - 1) * (k - 2) * (k - 3) * (k - 4))
    N = sapply(c(1 : 5), function(x) S + sum(f * (a[, x] - 1)))
    T = sapply(c(1 : 4), function(x)Tk(N, f, a, S, x))
    p = sapply(c(1 : 4), function(x)p_value(T[x]))
    # print(N)
    se = sapply(c(1 : 5), function(k)seN(N, f, a, k))
    null_hyp = as.data.table(cbind(T, p))
    null_hyp = rbind(null_hyp, list(NaN, NaN))
    optimal = rep('', 5)
    opt_index = which(null_hyp$p > 0.05)[1]
    optimal[opt_index] = '*'
    if (is.na(opt_index)) {
        opt_index = 5
    }
    # print(null_hyp)
    Nse = cbind(optimal, N, se, lowCI = N - se * 1.96, uppCI = N + se * 1.96, null_hyp)
    lowCI = N - se * 1.96
    uppCI = N + se * 1.96
    # print(Nse)
    return (list(N = N[opt_index], se = se[opt_index], lowCI = lowCI[opt_index], uppCI = uppCI[opt_index]))
}

get_sample_coverage_estimate <- function(data, counts){
    k = length(counts)
    # f = sapply(c(1 : k), function(x)get_order(counts, x))
    f = counts
    # r = sum(counts[, N]) # sum of unique samples found
    r = sum(counts) # sum of unique samples found
    sm = sum(f * c(1 : k))
    smi = sum(f * c(1 : k) * c(0 : (k - 1)))
    C = 1 - f[1] / (sm)
    gamma2 = max(0, r / C * smi / ((k - 1) * sm ^ 2) * k - 1)
    Nsc = r / C + f[1] * gamma2 / C
    H = array(, k)
    if (0 <= 1 - r / (C * (k - 1) * sm ^ 2) * k * smi) {
        H[1] = gamma2 / C + ((gamma2 * f[1] + r) * sm - f[1] ^ 2 * gamma2 - r * f[1]) / (C ^ 2 * sm ^ 2)
    }else{
        H[1] = - f[1] * r * (2 * C * sm - sm + f[1]) / (C ^ 3 * (k - 1) * sm ^ 4) * k * smi +
            gamma2 / C + ((gamma2 * f[1] + r) * sm - f[1] ^ 2 * gamma2 - r * f[1]) / (C ^ 2 * sm ^ 2)
    }
    for (j in c(2 : k)) {
        if (0 <= 1 - r / (C * (k - 1) * sm ^ 2) * k * smi) {
            H[j] = f[1] / (C ^ 2 * sm ^ 2) * j * (gamma2 * f[1] + r)
        }else {
            H[j] = - f[1] * r * j / (C^2*sm^2) -f[1]^2*gamma2*j/(C^2*sm^2)+ f[1]/C*k/(k-1)*r*(j^2/C/sm^2- j/(C*sm^2) - 2*j*smi/(C*sm^3) - j*f[1]/(C^2*sm^4)*smi)
        }
    }
    cov = matrix(, nrow = k, ncol = k)
    for (i in c(1 : k)) {
        for (j in c(1 : k)) {
            if (i == j) {
                cov[i, i] = f[i] * (1 - f[i] / Nsc)
            }else {
                cov[i, j] = - f[i] * f[j] / Nsc
            }
        }
    }
    varNsc = 0
    for (i in c(1 : k)) {
        for (j in c(1 : k)) {
            varNsc = varNsc + H[i] * H[j] * cov[i, j]
        }
    }
    se = sqrt(varNsc)
    # Nse = as.data.table(cbind(Nsc, se, lowCI = Nsc - se * 1.96, uppCI = Nsc + se * 1.96))
    lowCI = Nsc - se * 1.96
    uppCI = Nsc + se * 1.96
    return (list(N = Nsc, se = se, lowCI = lowCI, uppCI = uppCI))
}

# this is the Chao2 estimator
get_f1f2_estimate <- function(data, counts){

    k = 2 # we need only first two frequencies
    # f = sapply(c(1 : k), function(x)get_order(counts, x))
    f = counts
    # r = sum(counts[, N])
    r = sum(counts)
    if (f[2] == 0) {
        # print("WARN: f2 in f1f2 estimator is zero, se will be undefined")
        N12 = r + f[1] * (f[1] - 1) / 2
        se = 0
    }else {
        N12 = r + f[1] ^ 2 / (2 * f[2])
        varN12 = f[2] * (1 / 4 * (f[1] / f[2]) ^ 4 +
            (f[1] / f[2]) ^ 3 +
            1 / 2 * (f[1] / f[2]) ^ 2)
        se = sqrt(varN12)
    }
    # Nse = as.data.table(cbind(N12, se, lowCI = N12 - se * 1.96, uppCI = N12 + se * 1.96))
    lowCI = N12 - se * 1.96
    uppCI = N12 + se * 1.96
    return (list(N = N12, se = se, lowCI = lowCI, uppCI = uppCI))
}

load_data <- function(f_name){
    matrix = fread(f_name)
    cat("Data size: ", dim(matrix), "\n")
    if (max(matrix) > 1) { # remove index column
        matrix = matrix[, - 1]
    }
    rs = rowSums(matrix)
    n.cought = length(rs[rs > 0])
    print(sprintf("Cought: %d", n.cought))
    return(matrix)
}

process_folder <- function(d_name, est, out_dir){
    for (f_name in list.files(d_name, full.names = T)) {
        res = calculate_estimators(f_name, est)
        js = toJSON(res, pretty = TRUE)
        print(js)
        if (! is.null(out_dir)) {
            out_dir = file.path(out_dir, basename(f_name) + '.json')
            write(js, out_dir)
        }
    }
}

# deprecated
get_population_estimate <- function(data){
    k = ncol(data)
    n_mutants = nrow(data)
    rs = rowSums(data)
    counts = as.data.table(table(rs))[- 1]  # remove f0
    setnames(counts, c("rs", "N"))
    print("Frequencies:")
    print(counts[N > 0])
    print(sprintf("# of Samples: %d", k))
    print(sprintf("True # of Mutants: %d", n_mutants))
    est_wiqid = closedCapMhJK(counts$N)
    # Burnham, K. P. and Overton, W. S. (1978). Estimation of the size of a
    # closed population when capture probabilities vary among animals
    print("Jackknife Estimation (wiqid)")
    print(est_wiqid$real[1, 1 : 3])
    est_custom = get_custom_jackknife_estimate(counts)
    print("Jackknife Estimation (custom)")
    print(est_custom$N)
    est_f1f2 = get_f1f2_estimate(counts)
    print("F1F2 Estimation (Chao Estimator)")
    print(est_f1f2)
    est_sample = get_sample_coverage_estimate(counts)
    print("Sample coverage Estimation")
    print(est_sample)
    get_lowerbound(counts)
    get_upperbound(counts, n_mutants)
    return (list(n_mutants, est_wiqid, est_custom, est_f1f2, est_sample))
}

get_upperbound <- function(data, counts, alpha=0.05){
    # Estimating the Richness of a Population When the Maximum Number of Classes
    # Is Fixed: A Nonparametric Solution to an Archaeological Problem
    # 2012
    n_mutants = nrow(data)
    U = n_mutants
    f = sapply(c(1 : 2), function(x)get_order(counts, x))
    s_obs = sum(counts)
    if (f[2] == 0) {
        s_hat = s_obs + f[1] * (f[1] - 1) / 2
        var_s = 0
    }else {
        s_hat = s_obs + f[1] ^ 2 / (2 * f[2])
        var_s = f[2] * ((f[1] / f[2]) ^ 2 / 0.5 +
            (f[1] / f[2]) ^ 3 +
            (f[1] / f[2]) ^ 4 / 0.25)
    }
    mu_y = log(s_hat - s_obs)
    sigma2 = log(1 + var_s / (s_hat - s_obs) ^ 2)
    sigma = sqrt(sigma2)
    p = pnorm((log(U - s_obs) - mu_y) / sigma)
    z_p_alpha = qnorm(p * alpha / 2)
    z_p_1alpha = qnorm(p * (1 - alpha / 2))
    # print(sprintf("a: %f 1-a: %f", z_p_alpha, z_p_1alpha))
    s_lower = s_obs + (s_hat - s_obs) * exp(sigma * z_p_alpha)
    s_upper = s_obs + (s_hat - s_obs) * exp(sigma * z_p_1alpha)
    # print(sprintf("Estimate from the upperbound formula (U=%f)", U))
    # print(sprintf("Est: %f, LowCI: %f UppCI: %f", s_hat, s_lower, s_upper))
    return(list(N = s_hat, se = - 1, lowCI = s_lower, uppCI = s_upper))
}

get_lowerbound <- function(data, counts) {
    # chao1987estimating.pdf Estimating the Population Size for Capture-Recapture Data with Unequal Catchability
    # An Improved Nonparametric Lower Bound of Species Richness via a Modified Good–Turing Frequency Formula 2014
    S_obs <- sum(counts)
    n <- S_obs
    f1 <- counts[1]
    f2 <- counts[2]
    f3 <- counts[3]
    f4 <- counts[4]
    var_Schao1 <- f2 * (1 / 4 * ((n - 1) / n) ^ 2 * (f1 / f2) ^ 4 +
        ((n - 1) / n) ^ 2 * (f1 / f2) ^ 3 +
        1 / 2 * (n - 1) / n * (f1 / f2) ^ 2)
    var_Schao1 <- f2 * (0.25 * (f1 / f2) ^ 4 +
        (f1 / f2) ^ 3 +
        0.5 * (f1 / f2) ^ 2) # chao1987estimating.pdf
    #S_chao1 <- S_obs + (n-1)/n*f1^2/2/f2
    S_chao1 <- S_obs + f1 ^ 2 / 2 / f2 # chao1987estimating.pdf
    # set 1.96 to 1.64 to switch to a one sided 95\% confidence interval, and skip the upper
    R <- exp(1.96 * (1 + var_Schao1 / (S_chao1 - S_obs) ^ 2) ^ 0.5)
    #R <- exp(1.96*(log(1+var_Schao1/(S_chao1 - S_obs)^2))^0.5) #<- from reviewer
    S_lower <- S_obs + (S_chao1 - S_obs) / R
    S_upper <- S_obs + (S_chao1 - S_obs) * R

    #print("Estimate of killable mutants from the lowerbound formula")
    #print(sprintf("Est: %s, LowCI(important): %f UppI: %f", S_chao1, S_lower, S_upper))
    return(list(N = S_chao1, se = - 1, lowCI = S_lower, uppCI = S_upper))
}

test <- function(){
    print("test dataset")
    cc = as.data.table(cbind(seq(1, 18), c(43, 16, 8, 6, 0, 2, 1, rep(0, 11))))
    print(cc)
    names(cc) <- c("rs", "N")
    print("jack_knife_estimate:")
    est = get_custom_jackknife_estimate(cc)
    print("sample_coverage_estimate:")
    sce = get_sample_coverage_estimate(cc)
    print(sce)
    print("f1f2_estimate:")
    f1f2 = get_f1f2_estimate(cc)
    print(f1f2)
}

get_jack_wiqid <- function(data, counts){
    est_wiqid = closedCapMhJK(counts)
    N = est_wiqid$real[1, 1]
    lowCI = est_wiqid$real[1, 2]
    uppCI = est_wiqid$real[1, 3]
    print(est_wiqid$real)
    return(list(N = N, lowCI = lowCI, uppCI = uppCI)) # N, low, upp
}

get_counts <- function(data){
    # data - matrix of 0/1
    # return vector of counts including not-found mutants i.e. f[0]
    n = ncol(data)
    counts = as.data.frame(table(factor(rowSums(data), levels = c(0 : n))))
    return(counts$Freq)
}

calculate_estimators <- function(input_file_name, estimators){
    input_file_name = normalizePath(input_file_name)
    print(sprintf("Processing %s", basename(input_file_name)))
    data = load_data(input_file_name)
    samples = ncol(data)
    n_mutants = nrow(data)
    counts_with0 = get_counts(data)
    counts = counts_with0[- 1]
    n.cougth = sum(counts)
    est_results = data.frame(matrix(ncol = 3, nrow = 0))
    colnames(est_results) <- c("estimator", "value", "ci")
    for (est in estimators) {
        value = do.call(est_map[[est]], list(data, counts))
        res = list(estimator = est, value = value$N, ci = sprintf("(%f, %f)", value$lowCI, value$uppCI))
        est_results = rbind(est_results, res, stringsAsFactors = FALSE)
    }
    results = list(dataset = unbox(input_file_name), n.mutants = unbox(n_mutants), n.samples = unbox(samples), n.cougth = unbox(n.cougth), estimators = est_results)
    return(results)
}

est_map = list(chao_lower = 'get_lowerbound', bootstrap = 'bootstrap_estimate', sample_coverage = 'get_sample_coverage_estimate',
chao_upperbound = 'get_upperbound', chao2_our = 'get_f1f2_estimate', jack_wiqid = 'get_jack_wiqid', jack_our = 'get_custom_jackknife_estimate')
estimators = names(est_map)

parser = ArgumentParser()
parser$add_argument("-m", "--matrix", help = "Input matrix file")
parser$add_argument("-d", "--dir", help = "Input dir")
parser$add_argument("-u", help = "Upper bound", type = "integer", default = 0)
parser$add_argument("-o", "--output", help = "Filename for the resulting comparison table")
parser$add_argument("-e", "--estimator", choices = estimators, nargs = '+', help = "Specify list of estimators to calculate")
parser$add_argument("-a", "--all", action = 'store_true', help = "Use all estimators")

args = parser$parse_args()
if (is.null(args$estimator) && ! args$all) {
    print("Estimators not specified")
    stop(0)
}
est = if (args$all)estimators else args$estimator
if (! is.null(args$dir)) {
    process_folder(args$dir, est, args$output)
}else if (! is.null(args$matrix)) {
    res = calculate_estimators(args$matrix, est)
    js = toJSON(res, pretty = TRUE)
    print(js)
    if (! is.null(args$output)) {
        write(js, args$output)
    }
}else {
    parser$print_help()
}
# test()
#     wdir = getwd()
#     output = if (! is.null(args$output))args$output else file.path(wdir, 'estimation_results.csv')
#     res = process_folder(args$dir)
#     fwrite(res, file = output, sep = "\t")
# }else {
#     dt = process_file(args$matrix)
#     calculate_estimators(dt, args$estimator)
#     # test()
# }



