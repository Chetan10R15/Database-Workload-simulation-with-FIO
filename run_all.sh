#!/bin/bash
cd ~/fio-lab
mkdir -p results
{ date; fio --version; uname -r; df -hT ~; nproc; free -h; } > results/environment.txt
for rep in 1 2 3; do
  for c in A B C D; do
    for qd in 1 8 32; do
      echo "rep $rep case $c qd $qd"
      IODEPTH=$qd fio case_$c.fio --output=results/case${c}_qd${qd}_run${rep}.json --output-format=json
      sleep 2
    done
  done
done
echo done
