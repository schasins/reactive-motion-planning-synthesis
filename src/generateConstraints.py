initial = 0
target = 6

def generateConstraints(allowedSteps):
    f = open('constraints.sl','w')
    f.write('(set-logic LIA)\n')
    grammar = """
(synth-fun motion ((currX Int)) Int
 ((Start Int (currX ; no move
  (+ currX 1) ;right
  (- currX 1) ;left
  (ite StartBool Start Start)))
 (CondInt Int (Start
  (+ CondInt CondInt)
  (- CondInt CondInt)
  1
  -1
  ))
 (StartBool Bool ((and StartBool StartBool)
  (or  StartBool StartBool)
  (not StartBool)
  (<=  CondInt CondInt)
  (=   CondInt CondInt)
  (>=  CondInt CondInt))))) \n \n """

    f.write(grammar)
    f.write("(constraint (= ")
    for i in range(allowedSteps):
        f.write("(motion ")
    f.write(str(initial))
    for i in range(allowedSteps):
        f.write(")")
    f.write(" "+str(target)+"))\n")
    
    f.write("\n(check-synth)")
    f.close()

generateConstraints(6)
