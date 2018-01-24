#!/bin/bash

# Destription: testing cpu usage performance
# Example    : sh cpu_usage.sh 12
# Remark     : cat /proc/cpuinfo | grep "processor"|wc -l    #12==>Get the number of processor
# Date       : 2015-1-12
# update     : 2015-1-12

endless_loop()
{
 echo -ne "i=0;
 while true
 do
 i=i+100;
 i=100
 done" | /bin/bash &
}

if [ $# != 1 ] ; then
  echo "USAGE: $0 <CPUs>"
  exit 1;
fi
for i in `seq $1`
do
  endless_loop
  pid_array[$i]=$! ;
done

for i in "${pid_array[@]}"; do
  echo 'kill ' $i ';';
done