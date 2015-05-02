initial = (0,0)
target = (3,3)
dimensions = (5,6)
motion_primitives = [[[0,0]],[[0,1]],[[1,0]],[[0,-1]],[[-1,0]]]

def coordsToPoint(x,y):
	return y*dimensions[0]+x

def generateInterpretMove(motion_primitives):
	string = "(define-fun interpret-move (( currPoint Int ) ( move Int)) Int"
	return string+generateInterpretMoveHelper(motion_primitives,0)+")\n\n"

def generateInterpretMoveHelper(motion_primitives,i):
	if (len(motion_primitives) < 1):
		#we've run out of new motion primitives!
		return "\ncurrPoint"

	final_position = motion_primitives[0][-1]

	if (final_position[0] != 0 and final_position[1] != 0):
		string = ("\n(ite (= move "+str(i)+") \
                   (ite (or \
                      (or (< (+ (get-x currPoint) "+str(final_position[0])+") 0) (>= (+ (get-x currPoint) "+str(final_position[0])+") "+str(dimensions[0])+")) \
                      (or (< (+ (get-y currPoint) "+str(final_position[1])+") 0) (>= (+ (get-y currPoint) "+str(final_position[1])+") "+str(dimensions[1])+"))) \
                          currPoint ( + ( + (currPoint "+str(final_position[0])+" "+str(final_position[1]*dimensions[0])+")))) ")

	elif (final_position[0] != 0):
		string = "\n(ite (= move "+str(i)+") \
                   (ite (or (< (+ (get-x currPoint) "+str(final_position[0])+") 0) (>= (+ (get-x currPoint) "+str(final_position[0])+") "+str(dimensions[0])+")) \
                      currPoint (+ currPoint  "+str(final_position[0])+")) "

	elif (final_position[1] != 0):
		string = "\n(ite (= move "+str(i)+") \
                   (ite (or (< (+ (get-y currPoint) "+str(final_position[1])+") 0) (>= (+ (get-y currPoint) "+str(final_position[1])+") "+str(dimensions[1])+")) \
                      currPoint (+ currPoint  "+str(final_position[1]*dimensions[0])+")) "

	else:
		#both 0
		string = "\n(ite (= move "+str(i)+") currPoint "

        return string+generateInterpretMoveHelper(motion_primitives[1:],i+1)+")"

def generateConstraints(allowedSteps):
	f = open('constraints.sl','w')
	f.write('(set-logic LIA)\n')

	width = str(dimensions[0])

	helperFunction = generateInterpretMove(motion_primitives)

	getYCoordHelperFunction ="(define-fun get-y ((currPoint Int)) Int \n"
	for i in range(dimensions[1]-1):
		getYCoordHelperFunction+="(ite (< currPoint "+str(dimensions[0]*(i+1))+") "+str(i)+" "
	getYCoordHelperFunction+=str(dimensions[1]-1)
	for i in range(dimensions[1]-1):
		getYCoordHelperFunction+=")"
	getYCoordHelperFunction+=")\n"

	getXCoordHelperFunction ="""
		(define-fun get-x ((currPoint Int)) Int
			(- currPoint (* (get-y currPoint) """+width+""")))
		"""

        macros = getYCoordHelperFunction+getXCoordHelperFunction+helperFunction+"\n\n"

	solution = """
	(define-fun soln ((currPoint Int)) Int
		(ite (<= (get-y currPoint) 2) (interpret-move currPoint 4) (ite (<= (get-x currPoint) 2) (interpret-move currPoint 2) (interpret-move currPoint 0))))
	"""

	grammar = """
		(synth-fun move ((currPoint Int)) Int
			((Start Int (
				(interpret-move currPoint MoveId)
				(ite StartBool Start Start)))
  (MoveId Int ("""+("\n").join(map(str,range(len(motion_primitives))))+"""
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

	f.write(macros)

	f.write(solution)
	f.write(grammar)
	#f.write(grammar2)
	
	
	currProg = str(coordsToPoint(initial[0],initial[1]))
	for i in range(allowedSteps):
		currProg = "(move "+currProg+")"

	f.write("(constraint (= "+currProg+" "+str(coordsToPoint(target[0],target[1]))+"))\n")
	
	#f.write("(constraint (= (all-moves "+str(coordsToPoint(initial[0],initial[1]))+") "+str(coordsToPoint(target[0],target[1]))+"))")

	f.write("\n(check-synth)")
	f.close()

generateConstraints(6)
