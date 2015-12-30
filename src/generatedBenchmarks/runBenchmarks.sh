for entry in `ls .`; do
	echo $entry
    for i in {1..5}; do
    ~/research/sygus-comp14/solvers/enumerative/esolver-synth-lib/bin/opt/esolver-synthlib -s 15 $entry
    done
done
