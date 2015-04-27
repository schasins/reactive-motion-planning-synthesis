initial = (0,0)
target = (3,3)
dimensions = (5,6)

def generateConstraints(allowedSteps):
	f = open('constraints.sl','w')
	f.write('(set-logic LIA)\n')
	grammar = """
		(synth-fun move ((currX Int) (currY Int)) Int
			((Start Int (
				MoveId
				(ite StartBool Start Start)))
  (MoveId Int (
				0  ;no move
				1 ;left
				2 ;right
				3 ;down
				4 ;up
  	))
	(CondInt Int (
		currX
		currY
		(+ CondInt CondInt)
		(- CondInt CondInt)
		-1
		"""
	for i in range(max(dimensions)):
		grammar += str(i)+"\n"
	grammar += """
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
	
	body = "(let ((x0 Int "+str(initial[0])+") (y0 Int "+str(initial[1])+") (m0 Int (move "+str(initial[0])+" "+str(initial[1])+"))) "
	for i in range(allowedSteps-1):
		body += "(let ((x"+str(i+1)+" Int (interpret-move-x x"+str(i)+" m"+str(i)+")) (y"+str(i+1)+" Int (interpret-move-y y"+str(i)+" m"+str(i)+"))) (let ((m"+str(i+1)+" Int (move x"+str(i+1)+" y"+str(i+1)+")))"
	body += "(and (= (interpret-move-x x"+str(allowedSteps-1)+" m"+str(allowedSteps-1)+") "+str(target[0])+") (= (interpret-move-y y"+str(allowedSteps-1)+" m"+str(allowedSteps-1)+") "+str(target[1])+"))"
	for i in range(allowedSteps-1):
		body += "))"
	body += ")\n"
	f.write("(define-fun target-reached () Bool \n"+body+"\n) \n \n")
	f.write("(constraint (target-reached))")
	
	"""
	currentX = str(initial[0])
	currentY = str(initial[1])
	currentMove = "(move "+currentX+" "+currentY+")"
	for i in range(allowedSteps-1):
		currentX = "(interpret-move-x "+currentX+" "+currentMove+")"
		currentY = "(interpret-move-y "+currentY+" "+currentMove+")"
		currentMove = "(move "+currentX+" "+currentY+")"

		f.write("(constraint (= (interpret-move-x "+currentX+" "+currentMove+") "+str(target[0])+"))\n")
		f.write("(constraint (= (interpret-move-y "+currentY+" "+currentMove+") "+str(target[1])+"))\n")
	"""

	f.write("\n(check-synth)")
	f.close()

generateConstraints(7)
