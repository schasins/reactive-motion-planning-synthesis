dimensions = (5,6)

initial = (0,0)
target = (3,3)
motion_primitives = [[[0,0]],[[0,1]],[[1,0]],[[0,-1]],[[-1,0]]]

obstacles_initial = [(1,5),(2,5)]
obstacles_motion_primitives_list = [
	[[[0,0]],[[0,1]],[[0,-1]]], #first obstacle
	[[[0,0]],[[0,1]],[[0,-1]]]  #second obstacle
]

def coordsToPoint(x,y):
	return y*dimensions[0]+x

def andItems(ls):
	andstring = ""
	for i in range(len(ls)):
		andstring+="(and "+ls[i]+" "
	andstring+="true"+(")"*len(ls))
	return andstring

def generateNoOveralap(fun_name, motion_primitives, obstacle_motion_primitives):
	string = "(define-fun "+fun_name+" (( currPoint Int ) ( move Int) (obstacleCurrPoint Int) (obstacleMove Int)) Bool"
	for i in range(len(motion_primitives)):
		motion_primitive = motion_primitives[i]
		motion_primitive.append([0,0])
		string+="\n\t(ite (= move "+str(i)+") "
		for j in range(len(obstacle_motion_primitives)):
			string+="\n\t\t(ite (= obstacleMove "+str(j)+") "
			obstacle_motion_primitive = obstacle_motion_primitives[j]
			obstacle_motion_primitive.append([0,0])
			stepCombinations = [];
			for k in range(len(motion_primitive)):
				step = motion_primitive[k]
				for l in range(len(obstacle_motion_primitive)):
					ostep = obstacle_motion_primitive[l]
					stepCombinations.append("(!= (+ (+ currPoint "+str(step[0])+") "+ str(step[1]*dimensions[0])+") (+ (+ obstacleCurrPoint "+str(ostep[0])+") "+ str(ostep[1]*dimensions[0])+"))")
			string+=andItems(stepCombinations)
		string+=" false"+(")"*len(obstacle_motion_primitives)) #wasn't any of the moves we recognize, so should fail
	string+=" false"+(")"*len(motion_primitives)) #wasn't any of the moves we recognize, so should fail
	return string+")\n\n"

def generateNoOverlapsOneStep(numObstacles):
	#helper func
	string="(define-fun no-overlaps-one-step-helper ((currPoint Int) (move Int)"
	for i in range(numObstacles):
		string+= " (o"+str(i)+"-t Int) (o"+str(i)+"move Int)"
	string+=")\n\t"
	noOverlaps=[]
	for i in range(numObstacles):
		noOverlaps.append("(no-overlaps-"+str(i)+" currPoint move o"+str(i)+"-t o"+str(i)+"move)")
	string+=andItems(noOverlaps)+")\n\n"

	#outer func
	string+="(define-fun no-overlaps-one-step ((currPoint Int) "
	for i in range(numObstacles):
		string+=" o"+str(i)+"-0 o"+str(i)+"-1"
	string+=")\n\t(no-overlaps-one-step-helper currPoint (move currPoint"
	for i in range(numObstacles):
		string+=" o"+str(i)+"-0"
	string+=")"
	for i in range(numObstacles):
		string+=" o"+str(i)+"-0 (get-move-obstacle-"+str(i)+" o"+str(i)+"-0 o"+str(i)+"-1)"
	string+="))\n\n"
	return string

def generateInterpretMove(fun_name, motion_primitives):
	string = "(define-fun "+fun_name+" (( currPoint Int ) ( move Int)) Int"
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

def consolidateMotionPrimitives(motion_primitives):
	final_position_to_index = {}
	for i in range(len(motion_primitives)):
		motion_primitive = motion_primitives[i]
		final_position = motion_primitive[-1]
		final_position_str = str(final_position)
		if final_position_str in final_position_to_index:
			intermediate_steps = motion_primitive[0:-1]
			preexisting_primitive = motion_primitives[final_position_to_index[final_position_str]]
			for step in intermediate_steps:
				if step not in preexisting_primitive:
					preexisting_primitive.insert(0,step)

			motion_primitives[final_position_to_index[final_position_str]] = preexisting_primitive
		else:
			final_position_to_index[final_position_str] = i
	final_primitives = []
	for i in final_position_to_index.values():
		final_primitives.append(motion_primitives[i])
	return final_primitives

#test
#print [[1, 0], [0, 1], [1, 1]] in consolidateMotionPrimitives([[[0,0]],[[0,1],[1,1]],[[1,0],[1,1]],[[0,-1]],[[-1,0]]])

def generateAllowableMoves(funName, interpretFunName, numMoves):
	string = "(define-fun "+funName+" (( start Int ) ( end Int)) Bool"
	for i in range(numMoves):
		string+="\n\t(or (= ("+interpretFunName+" start "+str(i)+") end)"
	string+=" false"
	for i in range(numMoves):
		string+=")"
	return string+")\n\n"

def generateGetObstacleMove(funName, interpretFunName, numMoves):
	string = "(define-fun "+funName+" (( start Int ) ( end Int)) Int"
	for i in range(numMoves):
		string+="\n\t(ite (= ("+interpretFunName+" start "+str(i)+") end) "+str(i)+" "
	string+=" -1"
	for i in range(numMoves):
		string+=")"
	return string+")\n\n"

def generateConstraints(allowedSteps):
	f = open('constraints.sl','w')
	f.write('(set-logic LIA)\n')

	width = str(dimensions[0])

	getYCoordHelperFunction ="\n\n(define-fun get-y ((currPoint Int)) Int \n"
	for i in range(dimensions[1]-1):
		getYCoordHelperFunction+="(ite (< currPoint "+str(dimensions[0]*(i+1))+") "+str(i)+" "
	getYCoordHelperFunction+=str(dimensions[1]-1)
	for i in range(dimensions[1]-1):
		getYCoordHelperFunction+=")"
	getYCoordHelperFunction+=")\n"

	getXCoordHelperFunction ="""
(define-fun get-x ((currPoint Int)) Int
	(- currPoint (* (get-y currPoint) """+width+""")))\n"""

	obstacleParams = ""
	obstacleArgs = ""
	for i in range(len(obstacles_initial)):
		obstacleParams+=" (o"+str(i)+" Int)"
		obstacleArgs+=" o"+str(i)
	synthWrapper = """
(define-fun move-wrapper ((currPoint Int)"""+obstacleParams+""") Int	
	(interpret-move currPoint (move currPoint """+obstacleArgs+""")))\n\n"""

	robotMoves = generateInterpretMove("interpret-move", motion_primitives)
	#first preprocess the moves so that all intermediate stages that lead to the same final position are consolidated
	#assumption is that the obstacle can be in any of those intermediate positions if gets to the given final position
	#that way we won't have to deal later with the fact that we mustn't intercept with either, once we've found one primitive
	#that matches the move, we don't have to look for others, don't have to handle two or more
	obstacleMoves = ""
	for i in range(len(obstacles_motion_primitives_list)):
		obstacles_motion_primitives_list[i] = consolidateMotionPrimitives(obstacles_motion_primitives_list[i])
		newMoves = generateInterpretMove("interpret-move-obstacle-"+(str(i)), obstacles_motion_primitives_list[i])
		obstacleMoves+=newMoves

	obstacleAllowableMoves = ""
	for i in range(len(obstacles_initial)):
		obstacleAllowableMoves += generateAllowableMoves("allowable-move-obstacle-"+str(i),"interpret-move-obstacle-"+(str(i)),len(obstacles_motion_primitives_list[i]))

	obstacleGetMove = ""
	for i in range(len(obstacles_initial)):
		obstacleGetMove += generateGetObstacleMove("get-move-obstacle-"+str(i),"interpret-move-obstacle-"+(str(i)),len(obstacles_motion_primitives_list[i]))

	obstacleNoOverlaps = ""
	for i in range(len(obstacles_initial)):
		obstacleNoOverlaps+= generateNoOveralap("no-overlaps-"+str(i), motion_primitives, obstacles_motion_primitives_list[i])

	obstaclesNoOverlapsOneStep = generateNoOverlapsOneStep(len(obstacles_initial))

	macros = getYCoordHelperFunction+getXCoordHelperFunction+synthWrapper+robotMoves+obstacleMoves+obstacleAllowableMoves+obstacleGetMove+obstacleNoOverlaps+obstaclesNoOverlapsOneStep+"\n\n"

	obstaclePositions = ""
	for i in range(len(obstacles_initial)):
		for j in range(allowedSteps):
			obstaclePositions+="(declare-var o"+str(i)+"-"+str(j+1)+" Int)\n"

	solution = """
	(define-fun soln ((currPoint Int)) Int
		(ite (<= (get-y currPoint) 2) (interpret-move currPoint 4) (ite (<= (get-x currPoint) 2) (interpret-move currPoint 2) (interpret-move currPoint 0))))
	"""

	obstacleUses = ""
	for i in range(len(obstacles_initial)):
		obstacleUses+="\n\t\t(get-y o"+str(i)+")\n\t\t(get-x o"+str(i)+")"

	grammar = """
(synth-fun move ((currPoint Int)"""+obstacleParams+""") Int
	((Start Int (
		MoveId
		(ite StartBool Start Start)))
    (MoveId Int ("""+("\n\t\t").join(map(str,range(len(motion_primitives))))+"""
  	))
	(CondInt Int (
		(get-y currPoint) ;y coord
		(get-x currPoint) ;x coord"""+obstacleUses+"""
		(+ CondInt CondInt)
		(- CondInt CondInt)
		-1
		"""+("\n\t\t").join(map(str,range(max(dimensions))))+"""
				))
	(StartBool Bool ((and StartBool StartBool)
		(or  StartBool StartBool)
		(not StartBool)
		(<=  CondInt CondInt)
		(=   CondInt CondInt)
		(>=  CondInt CondInt))))) \n \n """

	f.write(macros)
	f.write(obstaclePositions)

	f.write(solution)
	f.write(grammar)
	#f.write(grammar2)

	def getLocationInSteps(steps,obstacles):
		currProg = str(coordsToPoint(initial[0],initial[1]))
		for i in range(steps):
			currProg = "(move-wrapper "+currProg+" "+(" ").join(map(lambda x: x[i], obstacles))+")"
		return currProg
	
	obstacles = []
	for i in range(len(obstacles_initial)):
		obstacles.append([str(coordsToPoint(obstacles_initial[i][0],obstacles_initial[i][1]))])
		for j in range(allowedSteps):
			obstacles[i].append("o"+str(i)+"-"+str(j+1))

	finalLoc = getLocationInSteps(allowedSteps,obstacles)
	correctProgConstraint = "(= "+finalLoc+" "+str(coordsToPoint(target[0],target[1]))+")"

	allowableObstacleMoves = []
	for i in range(len(obstacles)):
		obstaclePlaces = obstacles[i]
		for j in range(len(obstaclePlaces)-1):
			allowableObstacleMoves.append("(allowable-move-obstacle-"+str(i)+" "+obstaclePlaces[j]+" "+obstaclePlaces[j+1]+")")
	allowableObstacleMovesConstraint = andItems(allowableObstacleMoves)

	noOverlapItems = []
	for i in range(allowedSteps):
		string = "(no-overlaps-one-step "+getLocationInSteps(i,obstacles)
		for j in range(len(obstacles)):
			string+=" "+obstacles[j][i]+" "+obstacles[j][i+1]
		string+=")"
		noOverlapItems.append(string)
	noOverlapsConstraint = andItems(noOverlapItems)

	f.write("(or \n\t(and\n\t\t"+correctProgConstraint+"\n\t\t"+noOverlapsConstraint+")\n\t(not "+allowableObstacleMovesConstraint+"))")
	
	#f.write("(constraint (= (all-moves "+str(coordsToPoint(initial[0],initial[1]))+") "+str(coordsToPoint(target[0],target[1]))+"))")

	f.write("\n(check-synth)")
	f.close()

generateConstraints(6)
