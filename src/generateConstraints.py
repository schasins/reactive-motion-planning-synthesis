initial = (0,0)
target = (0,3)

def generateConstraints(allowedSteps):
    f = open('constraints.sl','w')
    f.write('(set-logic LIA)\n')
    grammar = """
(synth-fun move ((currX Int) (currY Int)) Int
 ((Start Int (
  1 ;left
  2 ;right
  3 ;down
  4 ;up
  (ite StartBool Start Start)))
 (CondInt Int (
  currX
  currY
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

    helperFunctions = """
(define-fun interpret-move-x (( x Int ) ( move Int )) Int
 (ite (= move 1) (- x 1) (ite (= move 2) (+ x 1) x))
)
(define-fun interpret-move-y (( y Int ) ( move Int )) Int
 (ite (= move 3) (- y 1) (ite (= move 4) (+ y 1) y))
) \n \n
"""

    f.write(grammar)
    f.write(helperFunctions)

    constr = "(constraint (let ((x Int "+str(initial[0])+") (y Int "+str(initial[1])+") (m Int (move "+str(initial[0])+" "+str(initial[1])+"))) "
    for i in range(allowedSteps-1):
        constr += "(let ((x Int (interpret-move-x x m)) (y Int (interpret-move-y y m))) (let ((m Int (move x y)))"
    constr += "(and (= (interpret-move-x x m) "+str(target[0])+") (= (interpret-move-y y m) "+str(target[1])+"))"
    for i in range(allowedSteps-1):
        constr += "))"
    constr += "))\n"
    f.write(constr)

    """
    counter = 0
    currentConstraint = "(let move Int (motion "+str(initial[0])+" "+str(initial[1])+"))"
    for i in range(allowedSteps-1):
        newConstraint = "(motion (interpret-move-x "+currentConstraint+") (interpret-move-y "+currentConstraint+"))"
        currentConstraint = newConstraint

    f.write("(constraint (= (interpret-move-x "+currentConstraint+") "+str(target[0])+"))\n")
    f.write("(constraint (= (interpret-move-y "+currentConstraint+") "+str(target[1])+"))\n")
   
    """
 
    f.write("\n(check-synth)")
    f.close()

generateConstraints(3)
