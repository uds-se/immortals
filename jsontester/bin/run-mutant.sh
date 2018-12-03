
testsuite=$1
mutant=$2
mutant_path=`dirname $mutant`
export PYTHONPATH=$mutant_path:libs

python3 $testsuite --verbose
