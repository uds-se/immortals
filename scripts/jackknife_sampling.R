#!/usr/bin/env Rscript
require("data.table")
require("argparse")
require("wiqid")

get_order <- function(df, order) {
    if(is.null(dim(df))){# we have vector of frequences, not a table
        return(df[order])
    }
    val = df[rs==order,N]
    if (length(val)==0){
        return(0)
    } else{
        return(val)
    }
}

# deprecated
reduce_matrix<-function(matrix, n_groups){
    c_names = names(matrix)
    if (n_groups==1){
        dt = sign(as.data.table(matrix[,rowSums(.SD)]))
    }else{
        idx = split(sample(c_names),cut(1:length(c_names), n_groups))
        dt = sign(as.data.table(lapply(idx, function(x) matrix[,rowSums(.SD), .SDcols=x])))
    }
    return(dt)
}

seN<-function(N, f, a, k){
    varN=sum(a[,k]^2*f)-N[k]
    return(sqrt(varN))
}

varNS<-function(N, f, a, S, k){
    b = a[,k+1]-a[,k]
    v = S/(S-1)*(sum(b^2*f)-(N[k+1]-N[k])^2/S)
    return(v)
}

Tk<-function(N, f, a, S, k){
    return((N[k+1]-N[k])/(varNS(N,f,a,S,k)^(1/2)))
}

p_value<-function(t){
    return(2*pnorm(-t))
}

get_custom_jackknife_estimate<-function(counts){
    k=nrow(counts)
    f = sapply(c(1:k), function(x)get_order(counts, x))
    S = sum(counts[rs!=0,N])
    a = matrix(1, k, 5)
    N = c(0,0,0,0)
    T = c(0,0,0)
    p = c(0,0,0)
    a[1,1] = 1 + (k - 1)/k
    a[1,2] = 1 + (2*k-3)/k
    a[2,2] = 1 - (k-2)^2/(k*(k-1))
    a[1,3] = 1 + (3*k-6)/k
    a[2,3] = 1 - (3*k^2-15*k + 19)/(k*(k-1))
    a[3,3] = 1 + (k-3)^3/(k*(k-1)*(k-2))
    a[1,4] = 1 + (4*k-10)/k
    a[2,4] = 1 - (6*k^2-36*k + 55)/(k*(k-1))
    a[3,4] = 1 + (4*k^3-42*k^2+148*k-175)/(k*(k-1)*(k-2))
    a[4,4] = 1 - (k-4)^4/(k*(k-1)*(k-2)*(k-3))
    a[1,5] = 1 + (5*k-15)/k
    a[2,5] = 1 - (10*k^2-70*k+125)/(k*(k-1))
    a[3,5] = 1 + (10*k^3-120*k^2+485*k-660)/(k*(k-1)*(k-2))
    a[4,5] = 1 - ((k-4)^5-(k-5)^5)/(k*(k-1)*(k-2)*(k-3))
    a[5,5] = 1 + (k-5)^5/(k*(k-1)*(k-2)*(k-3)*(k-4))
    N = sapply(c(1:5), function(x) S + sum(f*(a[,x]-1)))
    T = sapply(c(1:4),function(x)Tk(N,f,a,S,x))
    p = sapply(c(1:4),function(x)p_value(T[x]))
    # print(N)
    se=sapply(c(1:5), function(k)seN(N,f,a,k))
    null_hyp = as.data.table(cbind(T,p))
    null_hyp = rbind(null_hyp,list(NaN,NaN))
    optimal = rep('',5)
    opt_index=which(null_hyp$p > 0.05)[1]
    optimal[opt_index]='*'
    # print(null_hyp)
    Nse=cbind(optimal,N,se, lowCI=N-se*1.96,uppCI=N+se*1.96,null_hyp)
    print(Nse)
    return (Nse)
}

get_nonzero_f<-function(f, idx){

}

get_sample_coverage_estimate<-function(counts){
    k = nrow(counts)
    f = sapply(c(1:k), function(x)get_order(counts, x))
    r = sum(counts[,N]) # sum of unique samples found
    sm = sum(f*c(1:k))
    smi = sum(f*c(1:k)*c(0:(k-1)))
    C = 1 - f[1]/(sm)
    gamma2 = max(0, r/C*smi/((k-1)*sm^2)*k-1)
    Nsc = r/C + f[1]*gamma2/C
    H = array(,k)
    for (j in c(1:k)){
        if (0 <= 1-r*smi/(C*(k-1)*sm^2)*k){
            H[1] = gamma2 / C + ((gamma2 * f[1] + r) * sm - f[1] ^ 2 * gamma2 - r * f[1]) / (C ^ 2 * sm ^ 2)
            H[j] = f[1] * j * (gamma2 * f[1] + r) / (C ^ 2 * sm ^ 2)
        }else{
            H[1] = - f[1] * r * (2 * C * sm - sm + f[1]) / (C ^ 3 * (k - 1) * sm ^ 4) * k * smi +
                gamma2 / C + ((gamma2 * f[1] + r) * sm - f[1] ^ 2 * gamma2 - r * f[1]) / (C ^ 2 * sm ^ 2)
            H[j] = (- f[1] * r * j * (sm * ((j - 1) * sm - 2 * smi) * C - smi * f[1]) * k / (C ^ 3 * (k - 1) * sm ^ 4)) + f[1] * j * (gamma2 * f[1] + r) / (C ^ 2 * sm ^ 2)
        }
    }
    cov = matrix(, nrow = k, ncol = k)
    for (i in c(1:k)){
        for (j in c(1:k)){
            if (i==j){
                cov[i,i]=f[i]*(1-f[i]/Nsc)

            }else{
                cov[i,j]=-f[i]*f[j]/Nsc
            }
        }
    }
    varNsc=0
    for (i in c(1:k)){
        for (j in c(1:k)){
            varNsc=varNsc+H[i]*H[j]*cov[i,j]
        }
    }
    se = sqrt(varNsc)
    Nse = as.data.table(cbind(Nsc,se, lowCI=Nsc-se*1.96,uppCI=Nsc+se*1.96))
    return (Nse)
}

get_f1f2_estimate<-function(counts){
    k = nrow(counts)
    k = 2 # we need only first two frequencies
    f = sapply(c(1:k), function(x)get_order(counts, x))
    r = sum(counts[,N])
    if (f[2]==0){
        print("WARN: f2 in f1f2 estimator is zero, se will be undefined")
        N12 = r+f[1]*(f[1]-1)/2
        se = 0
    }else{
        N12 = r+f[1]^2/(2*f[2])
        varN12 = f[2]*(1/4*(f[1]/f[2])^4+(f[1]/f[2])^3+1/2*(f[1]/f[2])^2)
        se = sqrt(varN12)
    }
    Nse = as.data.table(cbind(N12,se, lowCI=N12-se*1.96,uppCI=N12+se*1.96))
    return (Nse)
}

process_file<-function(f_name, reduction=1){
    matrix = fread(f_name)
    print(sprintf("Processing %s", basename(f_name)))
    cat("Data size: ", dim(matrix), "\n")
    if (max(matrix) > 1){ # remove index column
        matrix = matrix[,-1]
    }
    # data_ids=sample(ncol(matrix), size=subsample_size)
    m_size = ncol(matrix)
    n_groups = m_size / reduction
    dt = reduce_matrix(matrix, n_groups)
    return(dt)
 }

process_folder<-function(d_name){
    res = data.table(
            file_name = character(),
            real_mutants_count = integer(),
            wiqid_estimation = numeric(),
            custom_estimation = character()
        )
    for(f_name in list.files(d_name, full.names=T)){
        dt = process_file(f_name)
        est_tuple = get_jackknife_estimate(dt)
        lb = get_lowerbound(dt)
        num_mutants = est_tuple[[1]]
        est_wiqid = est_tuple[[2]]
        est_custom = est_tuple[[3]]
        est_f1f2 = est_tuple[[4]]
        est_sample = est_tuple[[5]]
        est_custom_value = est_custom[optimal=='*',.(N,se)]
        ci = paste(est_custom[optimal=='*',.(lowCI,uppCI)], collapse=', ')
        if (nrow(est_custom_value)==0){
            est_custom_value = est_custom[5,.(N,se)]
            ci = paste(est_custom[5,.(lowCI,uppCI)], collapse=', ')
        }
        est_custom_string = do.call(sprintf, c(list('%f ± %f, (%s)'), est_custom_value, ci))
        #sprintf('%f ± %f, %s', est_custom_value, ci)
        est_wiqid_count = do.call(sprintf, c(list('%f, (%f, %f)'), est_wiqid$real))
        est_f1f2_string = do.call(sprintf, c(list('%f ± %f, (%f, %f)'), est_f1f2[1,.(N12, se, lowCI, uppCI)]))
        est_sample_string = do.call(sprintf, c(list('%f ± %f, (%f, %f)'), est_sample[1,.(Nsc, se, lowCI, uppCI)]))
        res=rbind(res, list(basename(f_name), num_mutants, est_wiqid_count, est_custom_string, est_f1f2_string, est_sample_string))
    }
    return (res)
}

get_jackknife_estimate<-function(data){
    k = ncol(data)
    n_mutants = nrow(data)
    rs = rowSums(data)
    counts = as.data.table(table(factor(rs, levels=1:k)))
    setnames(counts, c("rs","N"))
    print("Frequencies:")
    print(counts)
    print(sprintf("# of Samples: %d", k))
    print(sprintf("True # of Mutants: %d", n_mutants))
    est_wiqid = closedCapMhJK(counts$N)
    print("Jackknife Estimation (wiqid)")
    print(est_wiqid$real)
    est_custom = get_custom_jackknife_estimate(counts)
    print("Jackknife Estimation (custom)")
    print(est_custom$N)
    est_f1f2 = get_f1f2_estimate(counts)
    print("F1F2 Estimation")
    print(est_f1f2)
    est_sample = get_sample_coverage_estimate(counts)
    print("Sample coverage Estimation")
    print(est_sample)
    return (list(n_mutants, est_wiqid, est_custom, est_f1f2, est_sample))
}

get_upperbound <- function(data, U=0, alpha=0.05){
    k = ncol(data)
    n_mutants = nrow(data)
    if (U==0){
        U=n_mutants
    }
    rs = rowSums(data)
    counts = as.data.table(table(factor(rs, levels=1:k)))
    setnames(counts, c("rs","N"))
    f = sapply(c(1:2), function(x)get_order(counts, x))
    s_obs = sum(counts[,N])
    if (f[2]==0){
        print("Unsupported f2==0")
        return()
    }
    s_hat = s_obs + f[1]^2/(2*f[2])
    var_s = f[2]*((f[1]/f[2])^2/0.5+(f[1]/f[2])^3+(f[1]/f[2])^4/0.25)
    mu_y = log(s_hat - s_obs)
    sigma2 = log(1 + var_s/(s_hat-s_obs)^2)
    sigma = sqrt(sigma2)
    p = pnorm((log(U-s_obs)-mu_y)/sigma)
    z_p_alpha = qnorm(p*alpha/2)
    z_p_1alpha = qnorm(p*(1-alpha/2))
    # print(sprintf("a: %f 1-a: %f", z_p_alpha, z_p_1alpha))
    s_lower = s_obs + (s_hat-s_obs)*exp(sigma*z_p_alpha)
    s_upper = s_obs + (s_hat-s_obs)*exp(sigma*z_p_1alpha)
    print(sprintf("Estimate from the upperbound formula (U=%f)", U))
    print(sprintf("Est: %f, LowCI: %f UppCI: %f", s_hat, s_lower, s_upper))
}

get_lowerbound <- function(data) {
  # An Improved Nonparametric Lower Bound of Species Richness via a Modified Good–Turing Frequency Formula 2014
  k = ncol(data)
  n_mutants = nrow(data)
  rs = rowSums(data)
  counts = as.data.table(table(factor(rs, levels=1:k)))
  setnames(counts, c("rs","N"))
  S_obs <- sum(counts$N)
  n <- S_obs
  f1 <- counts$N[1]
  f2 <- counts$N[2]
  f3 <- counts$N[3]
  f4 <- counts$N[4]
  var_Schao1 <- f2*(1/4 * ((n-1)/n)^2 * (f1/f2)^4 + ((n-1)/n)^2 * (f1/f2)^3 + 1/2 * (n-1)/n * (f1/f2)^2)
  S_chao1 <- S_obs + (n-1)/n*f1^2/2/f2
  R <- exp(1.96*(1+var_Schao1/(S_chao1 - S_obs)^2)^0.5)
  S_lower <- S_obs + (S_chao1 - S_obs)/R
  S_upper <- S_obs + (S_chao1 - S_obs)*R

  print("Estimate from the lowerbound formula")
  print(sprintf("LowCI(important): %f UppCI: %f", S_lower, S_upper))
}

parser = ArgumentParser()
parser$add_argument("-m", "--matrix", help="Input matrix file")
parser$add_argument("-d", "--dir", help="Input dir")
parser$add_argument("-u", help="Upper bound", type="integer",default=0)
parser$add_argument("-o", "--output", help="Filename for the resulting comparison table")
parser$add_argument("-n", "--reduction", help="Matrix reduction rate", default=1, type="integer")

args = parser$parse_args()
if (!is.null(args$matrix)){
    dt=process_file(args$matrix, args$reduction)
    est=get_jackknife_estimate(dt)
    lb=get_lowerbound(dt)
    U=args$u
    ub=get_upperbound(dt, U)
}else if(!is.null(args$dir)){
    wdir = getwd()
    output = if (!is.null(args$output)) args$output else file.path(wdir, 'estimation_results.csv')
    res = process_folder(args$dir)
    fwrite(res,file=output,sep="\t")
}else{
    print("test dataset")
    cc=as.data.table(cbind(seq(1,18),c(43,16,8,6,0,2,1,rep(0,11))))
    print(cc)
    names(cc)<-c("rs","N")
    print("jack_knife_estimate:")
    est=get_custom_jackknife_estimate(cc)
    print("sample_coverage_estimate:")
    sce=get_sample_coverage_estimate(cc)
    print(sce)
    print("f1f2_estimate:")
    f1f2=get_f1f2_estimate(cc)
    print(f1f2)
}
# TODO
# make bootstrap on top


