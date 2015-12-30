dimensions = (10,10)
initial = (0,0)
target = (1,5)
motion_primitives = [[[0,0]],[[0,1]],[[1,0]],[[0,-1]],[[-1,0]]]
obstacles_initial = [(9,9),(8,9)]
obstacles_motion_primitives_list = [
        [[[0,1]],[[0,-1]]], #first obstacle
        [[[0,0]],[[0,1]],[[0,-1]]]  #second obstacle
]
maxSteps = 7

def coordsToPoint(x,y):
	return y*dimensions[0]+x

def andItems(ls):
	andstring = ""
	for i in range(len(ls)):
		andstring+="(and "+ls[i]+" "
	andstring+="true"+(")"*len(ls))
	return andstring

def generateCombinationFunction(funcName, l1, l2):
	string = "(define-fun "+funcName+" ("+" ".join(map((lambda x: "(p"+str(x)+" Int)"),range(l1+l2)))+") Bool"
	stepCombinations = [];
	for i in range(l1):
		for j in range(l2):
			stepCombinations.append("(not (= p"+str(i)+" p"+str(l1+j)+"))")
	string+="\n\t"+andItems(stepCombinations)+")\n\n"
	return string

combinationFunctions = {}
def generateNoOveralap(fun_name, motion_primitives, obstacle_motion_primitives):
	string = "(define-fun "+fun_name+" (( currPoint Int ) ( move Int) (obstacleCurrPoint Int) (obstacleMove Int)) Bool\n\t(= 1"
	for i in range(len(motion_primitives)):
		motion_primitive = motion_primitives[i]
		string+="\n\t(ite (= move "+str(i)+") "
		for j in range(len(obstacle_motion_primitives)):
			string+="\n\t\t(ite (= obstacleMove "+str(j)+") "
			obstacle_motion_primitive = obstacle_motion_primitives[j]
			combinationFunc = "no-overlap-one-move-combination-"+str(len(motion_primitive)+1)+"-"+str(len(obstacle_motion_primitive)+1) #plus one because must add initial position
			if combinationFunc not in combinationFunctions:
				combinationFunctions[combinationFunc] = generateCombinationFunction(combinationFunc,len(motion_primitive)+1, len(obstacle_motion_primitive)+1)
			string+="(ite ("+combinationFunc
			string+=" currPoint"
			for k in range(len(motion_primitive)):
				step = motion_primitive[k]
				string += " (+ (+ currPoint "+str(step[0])+") "+ str(step[1]*dimensions[0])+")"
			string+=" obstacleCurrPoint"
			for k in range(len(obstacle_motion_primitive)):
				step = obstacle_motion_primitive[k]
				string += " (+ (+ obstacleCurrPoint "+str(step[0])+") "+ str(step[1]*dimensions[0])+")"
			string+=") 1 0)"
		string+=" 0"+(")"*len(obstacle_motion_primitives)) #wasn't any of the moves we recognize, so should fail
	string+=" 0"+(")"*len(motion_primitives)) #wasn't any of the moves we recognize, so should fail
	return string+"))\n\n"

def generateNoOverlapsOneStep(numObstacles):
	#helper func
	string="(define-fun no-overlaps-one-step-helper ((currPoint Int) (move Int)"
	for i in range(numObstacles):
		string+= " (o"+str(i)+"-t Int) (o"+str(i)+"move Int)"
	string+=") Bool\n\t"
	noOverlaps=[]
	for i in range(numObstacles):
		noOverlaps.append("(no-overlaps-"+str(i)+" currPoint move o"+str(i)+"-t o"+str(i)+"move)")
	string+=andItems(noOverlaps)+")\n\n"

	#outer func
	string+="(define-fun no-overlaps-one-step ((currPoint Int) (move Int) "
	for i in range(numObstacles):
		string+=" (o"+str(i)+"-0 Int) (o"+str(i)+"-1 Int)"
	string+=") Bool\n\t(no-overlaps-one-step-helper currPoint move"
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

def generateConstraints(filename, d, i, t, allowedSteps, mp, oi, ompl):
	global initial, dimensions, target, motion_primitives, obstacles_initial, obstacles_motion_primitives_list
	dimensions = d
	initial = i
	target = t
	motion_primitives = mp
	obstacles_initial = oi
	obstacles_motion_primitives_list = ompl

	f = open(filename,'w')
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

	moveCombinations = ("\n\n").join(combinationFunctions.values()) #combinationFunctions have been generated over the course of making the no overlaps code

	macros = getYCoordHelperFunction+getXCoordHelperFunction+robotMoves+obstacleMoves+obstacleAllowableMoves+obstacleGetMove+moveCombinations+obstacleNoOverlaps+obstaclesNoOverlapsOneStep+"\n\n"

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

	#f.write(solution)
	f.write(grammar)
	#f.write(grammar2)

	obstacles = []
	for i in range(len(obstacles_initial)):
		obstacles.append([str(coordsToPoint(obstacles_initial[i][0],obstacles_initial[i][1]))])
		for j in range(allowedSteps):
			obstacles[i].append("o"+str(i)+"-"+str(j+1))

	lets = ""
	for i in range(allowedSteps+1):
		lets +=" (let (("
		lets+="pos"+str(i)+" Int "
		if i == 0:
			lets+= str(coordsToPoint(initial[0],initial[1]))
		else:
			lets+= "(interpret-move pos"+str(i-1)+" mov"+str(i-1)+")"
		lets += "))"
		if i < allowedSteps:
			#only calculate the move if we have to
			lets+=" (let (("
			lets+="mov"+str(i)+" Int (move pos"+str(i)
			for j in range(len(obstacles)):
				lets+= " "+obstacles[j][i]
			lets+=")))"
	lets+="\n"

	letsEnd = ")"*(2*allowedSteps+1)

	correctProgConstraint = "(= pos"+str(allowedSteps)+" "+str(coordsToPoint(target[0],target[1]))+")"

	allowableObstacleMoves = []
	for i in range(len(obstacles)):
		obstaclePlaces = obstacles[i]
		for j in range(len(obstaclePlaces)-1):
			allowableObstacleMoves.append("(allowable-move-obstacle-"+str(i)+" "+obstaclePlaces[j]+" "+obstaclePlaces[j+1]+")")
	allowableObstacleMovesConstraint = andItems(allowableObstacleMoves)

	noOverlapItems = []
	for i in range(allowedSteps):
		string = "(no-overlaps-one-step pos"+str(i)+" mov"+str(i)
		for j in range(len(obstacles)):
			string+=" "+obstacles[j][i]+" "+obstacles[j][i+1]
		string+=")"
		noOverlapItems.append(string)
	noOverlapsConstraint = andItems(noOverlapItems)

	f.write("(constraint "+lets+" (or \n\t(and\n\t\t"+correctProgConstraint+"\n\t\t"+noOverlapsConstraint+")\n\t(not "+allowableObstacleMovesConstraint+"))"+letsEnd+")")
	
	#f.write("(constraint (= (all-moves "+str(coordsToPoint(initial[0],initial[1]))+") "+str(coordsToPoint(target[0],target[1]))+"))")

	f.write("\n\n(check-synth)")
	f.close()

def genBenchmarks():
	motion_primitives = [[[0,0]],[[0,1]],[[1,0]],[[0,-1]],[[-1,0]]]

	# Dimensions benchmarks
	initial = (1,0)
	target = (6,5)
	maxSteps = 10
	obstacles_initial = []
	obstacles_motion_primitives_list = []
	for i in range(10):
		obstacles_initial.append([0,i])
		obstacles_motion_primitives_list.append([[[0,1]],[[0,-1]]])
	for i in range(10, 110, 10):
		generateConstraints("generatedBenchmarks/dimensions_"+str(i)+"-"+str(i)+"_10-10-4.sl", [i,i], initial, target, maxSteps, motion_primitives, obstacles_initial, obstacles_motion_primitives_list)

	# Num obstacles benchmarks
	dimensions = [30,30]
	initial = (0,0)
	target = (5,5)
	maxSteps = 10
	obstacles_initial = []
	obstacles_motion_primitives_list = []
	for i in range(50):
		obstacles_initial.append([i, 19])
		obstacles_motion_primitives_list.append([[[0,1]],[[0,-1]]])
	for i in range(5, 55, 5):
		oi = obstacles_initial[:i]
		ompl = obstacles_motion_primitives_list[:i]
		generateConstraints("generatedBenchmarks/numobstacles_"+str(i)+"_30-10-"+str(i)+"-4.sl", dimensions, initial, target, maxSteps, motion_primitives, oi, ompl)

	# Num steps benchmarks
	dimensions = [30,30]
	initial = (1,1)
	obstacles_initial = []
	obstacles_motion_primitives_list = []
	for i in range(10):
		obstacles_initial.append([0, i])
		obstacles_motion_primitives_list.append([[[0,1]],[[0,-1]]])
	for i in range(5, 55, 5):
		maxSteps = i
		xDir = maxSteps/2
		yDir = maxSteps - xDir
		target = [1+xDir,1+yDir]
		generateConstraints("generatedBenchmarks/numsteps_"+str(i)+"_30-"+str(i)+"-10-4.sl", dimensions, initial, target, maxSteps, motion_primitives, obstacles_initial, obstacles_motion_primitives_list)

	# Depth benchmarks
	dimensions = [6,6]
	initials = [(0,0), (0,0), (1,0), (3,0)]
	targets = [(5,0), (4,0), (4,1), (3,2)]
	depths = [1, 4, 5, 6]
	obstacles_initial = [(0,1), (1,1), (2,1), (3,1)]
	obstacles_motion_primitives_list = []
	maxSteps = 5
	for i in range(len(obstacles_initial)):
		obstacles_motion_primitives_list.append([[[0,0]]])
	for i in range(len(initials)):
		initial = initials[i]
		target = targets[i]
		depth = str(depths[i])
		generateConstraints("generatedBenchmarks/zdepth_"+depth+"_6-5-4-"+depth+".sl", dimensions, initial, target, maxSteps, motion_primitives, obstacles_initial, obstacles_motion_primitives_list)


generateBenchmarks = True
if generateBenchmarks:
	genBenchmarks()
else:
	generateConstraints(maxSteps)
