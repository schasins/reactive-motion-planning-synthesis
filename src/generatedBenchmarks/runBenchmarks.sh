#!/bin/bash

ITERATIONS=5

for entry in `ls`; do
	ARRAY=()

	for ((i=0; i<$ITERATIONS;i++)); do
	    for((j=0; j<2; j++)); do
	        PRETIME=$(date +%s%N)
	        ~/research/sygus-comp14/solvers/enumerative/esolver-synth-lib/bin/opt/esolver-synthlib $entry
	        POSTTIME=$(date +%s%N)
	        $(ARRAY)+= $POSTTIME-$PRETIME
	    done
	done

	echo $entry $ARRAY
done
