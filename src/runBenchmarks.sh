#!/bin/bash

function join { local IFS="$1"; shift; echo "$*"; }

ITERATIONS=5

for entry in `ls generatedBenchmarks`; do
	ARRAY=()

	for ((i=0; i<$ITERATIONS;i++)); do
	        PRETIME=$(date +%s%N)
	        eval ~/research/sygus-comp14/solvers/enumerative/esolver-synth-lib/bin/opt/esolver-synthlib -s 25  generatedBenchmarks/"$entry" > solutions/"$entry"
	        POSTTIME=$(date +%s%N)
	        ARRAY+=(`expr $POSTTIME - $PRETIME`)
	done
	
	JOINED=`join , "${ARRAY[@]}"`
	echo $entry,$JOINED
done
