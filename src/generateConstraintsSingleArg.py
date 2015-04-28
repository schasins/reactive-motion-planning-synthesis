initial = (0,0)
target = (3,3)
dimensions = (5,6)

def coordsToPoint(x,y):
	return y*dimensions[1]+x

def generateConstraints(allowedSteps):
	f = open('constraints.sl','w')
	f.write('(set-logic LIA)\n')

	width = str(dimensions[0])

	helperFunctions = """
		(define-fun interpret-move (( currPoint Int ) ( move Int )) Int
			(ite (= move 1) (- currPoint 1) 
											(ite (= move 2) (+ currPoint 1) 
																			(ite (= move 3) (- currPoint """+width+""") 
																											(ite (= move 4) (+ currPoint """+width+""") currPoint))))
		)
		\n
		"""

	getYCoordHelperFunction ="(define-fun get-y ((currPoint Int)) Int \n"
	for i in range(dimensions[1]-1):
		getYCoordHelperFunction+="(ite (< currPoint "+str(dimensions[0]*(i+1))+") "+str(i)+" "
	getYCoordHelperFunction+=str(dimensions[1]-1)
	for i in range(dimensions[1]-1):
		getYCoordHelperFunction+=")"
	getYCoordHelperFunction+=")\n"

	getXCoordHelperFunction ="""
		(define-fun get-x ((currPoint Int)) Int
			(- currPoint (get-y currPoint)))
		"""

	helperFunctions+=getYCoordHelperFunction+getXCoordHelperFunction+"\n\n"

	grammar = """
		(synth-fun move ((currPoint Int)) Int
			((Start Int (
				(interpret-move currPoint MoveId)
				(ite StartBool Start Start)))
  (MoveId Int (
				0 ;no move
				1 ;left
				2 ;right
				3 ;down
				4 ;up
  	))
	(CondInt Int (
		(get-y currPoint) ;y coord
		(get-x currPoint) ;x coord
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

	grammar2 = """
		(synth-fun all-moves ((startPoint Int)) Int
			((Start Int (
				(move Start)
				startPoint))))\n\n"""

	f.write(helperFunctions)
	f.write(grammar)
	#f.write(grammar2)
	
	
	currProg = str(coordsToPoint(initial[0],initial[1]))
	for i in range(allowedSteps):
		currProg = "(move "+currProg+")"

	f.write("(constraint (= "+currProg+" "+str(coordsToPoint(target[0],target[1]))+"))\n")
	
	#f.write("(constraint (= (all-moves "+str(coordsToPoint(initial[0],initial[1]))+") "+str(coordsToPoint(target[0],target[1]))+"))")

	f.write("\n(check-synth)")
	f.close()

