import random
import sys

sys.path.append("..")  # so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *
from operator import itemgetter, attrgetter
from random import shuffle


##
# AIPlayer
# Description: The responsbility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# will be implemented by students in Dr. Nuxoll's AI course.
#
# Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):
    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "Give me an A+")

        self.enemyFood = []
        self.ourFood = []

        self.weHaveNotDoneThisBefore = True

    ##
    # getPlacement
    #
    # Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    # Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    # Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:  # stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    ##
    # getMove
    # Description: Gets the next move from the Player.
    #
    # Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: The Move to be made
    ##
    def getMove(self, currentState):
        # get food lists
        if self.weHaveNotDoneThisBefore:
            foods = getConstrList(currentState, None, (FOOD,))
            for food in foods:
                if food.coords[1] > 3:
                    self.enemyFood.append(food)
                else:
                    self.ourFood.append(food)
            self.weHaveNotDoneThisBefore = False

        return (self.moveSearch(3, 0, self.initNode(None, currentState, True, None))['move'])

    ##
    # getAttack
    # Description: Gets the attack to be made from the Player
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        # Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    # getUtility
    # Description: Creates a utility value in the range 0-1 with the given state
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    ##
    def getUtility(self, currentState):
        # If our agent has won, return a utility of 1.0
        if self.hasWon(currentState, self.playerId):
            return 1.0
        # If our agent has lost, return a utility of 0
        elif self.hasWon(currentState, (self.playerId + 1) % 2):
            return 0.0
        # Getting our inventory and our enemy's inventory
        for inv in currentState.inventories:
            if inv.player == self.playerId:
                ourInv = inv
            else:
                enemyInv = inv



        utilities = []

        # The code below creates a utility value based on the amount of food our agent has in their inventory
        # Weight 0.4
        utilities.append((float(ourInv.foodCount)/12.0, 0.4))

        # If our agent has less than three ants this is a bad utility, if our agent has 3 to 5 ants this is a good
        # utility, and if our agent over 5 ants this is a medium utility
        # Weight 0.2
        numAnts = len(ourInv.ants)
        if numAnts == 1:
            antUtil = 0.0
        if numAnts == 2:
            antUtil = .3
        if numAnts == 3:
            antUtil= .8
        if numAnts == 4 or numAnts == 5:
            antUtil = 1.0
        if numAnts > 5:
            antUtil = 0.5
        utilities.append((antUtil, 0.2))

        # The code below creates a utility value based on the number of ants the enemy has
        # If the enemy has more than 4 ants this is a bad utility and if the enemy has less it is a good utility
        # Weight 0.1
        enemyNumAnts = len(enemyInv.ants)
        if enemyNumAnts == 1 or enemyNumAnts == 0:
            enemyAntUtil = 1.0
        if enemyNumAnts == 2:
            enemyAntUtil = .9
        if enemyNumAnts == 3:
            enemyAntUtil= .5
        if enemyNumAnts == 4:
            enemyAntUtil = 0.2
        if enemyNumAnts > 4:
            enemyAntUtil = 0.0
        utilities.append((enemyAntUtil, 0.1))

        # Add utility for each food being carried by an ant worker
        # Does not depend on number of worker ants
        # Weight 0.2
        carryUtil = 0.0
        listOfWorkers = getAntList(currentState, self.playerId, (WORKER,))
        for worker in listOfWorkers:
            if worker.carrying:
                tunnelAndHill = \
                        [float(approxDist(worker.coords, getConstrList(currentState, self.playerId, (TUNNEL,))[0].coords )),
                        float(approxDist(worker.coords, getConstrList(currentState, self.playerId, (ANTHILL,))[0].coords ))]
                carryUtil += ( 0.9-(min(tunnelAndHill)) / 30.0)
            else:
                foodDistances = [float(approxDist(worker.coords, self.ourFood[0].coords )),
                                float(approxDist(worker.coords, self.ourFood[1].coords ))]
                carryUtil += ( 0.7-(min(foodDistances) / 30.0))
        carryUtil /= len(listOfWorkers)
        carryUtil = min(carryUtil, 1.0)
        utilities.append((carryUtil, 0.2))

        # Add utility for warriors
        # Wieght
        # warriorUtil = 0.0
        # listOfWarriors = getAntList(currentState, self.playerId, (DRONE, SOLDIER, R_SOLDIER))
        # for warrior in listOfWarriors


        # Add utility for Her Majesty's health
        # Subtract utility if she's standing on food, the hill, or the tunnel
        # Weight 0.1
        myBeautifulQueen = getAntList(currentState, self.playerId, (QUEEN,))[0]
        queenUtil = float(myBeautifulQueen.health)/8.0
        if (myBeautifulQueen.coords == getConstrList(currentState, self.playerId, (ANTHILL,))[0].coords) or \
                (myBeautifulQueen.coords == getConstrList(currentState, self.playerId, (TUNNEL,))[0].coords) or \
                (myBeautifulQueen.coords == self.ourFood[0].coords) or \
                (myBeautifulQueen.coords == self.ourFood[1].coords):
            queenUtil = 0
        utilities.append((queenUtil, 0.1))

        # Add utilities together with respective weights
        finalUtil = 0.0
        for util in utilities:
            finalUtil += util[0]*util[1]

        return finalUtil

    # #
    # initNode
    # Description: Create a new Node and return it
    #
    # Parameters:
    #   move - the move to create the next node
    #   currentState - a clone of the current state
    ##
    def initNode(self, move, currentState, isMaxNode, parentNode):
        if move is None:
            nextState = currentState
        else:
            nextState = getNextStateAdversarial(currentState, move)

        if isMaxNode:
            bound = 0
        else:
            bound = 1

        node = {'move': move, 'currState': currentState,'nextState': nextState, 'utility': self.getUtility(nextState), 'isMax': isMaxNode,
                     'bound': bound, 'parentNode': parentNode}
        return node


    # #
    # evalNode                                          DEPRECIATED
    # Description: Takes a dictionary of node and returns the average utility
    #
    # Parameters:
    #   nodes - a dictionary list of nodes to be evaluated
    ##
    def evalNode(self, nodes):
    	util = 0
    	for node in nodes:
    		util += node['utility']

    	return float(util) / float(len(nodes))


    ##
    # moveSearch                                <!-- RECURSIVE -->
    #
    # Description: Takes the game state, depth, and a node and expands the node
    # using the current state. It then picks the node with the best utility and then
    # repeats this process until the desired depth has been reached.
    #
    # Parameters:
    #   state - the current game state
    #   depth - the depth we are currently at
    #   currNode - the node we are expanding
    #
    # Return:
    #   list of the moves to reach the most desireable state, list[-2] is the 
    #   first move that can be taken
    ##
    def moveSearch(self, finalDepth, currDepth, currNode):
        if currDepth >= finalDepth or currDepth >= 5:
            currNode['utility'] = self.getUtility(currNode['nextState'])
            return currNode

        
        # get list of neighboring nodes
        nodes = []
        for move in listAllLegalMoves(currNode['nextState']):
            if move.moveType == END:
                nodes.append(self.initNode(move, currNode['nextState'], not currNode['isMax'], currNode))
            else:
                nodes.append(self.initNode(move, currNode['nextState'], currNode['isMax'], currNode))

# shuffle(nodes)
        if currNode['isMax']:
            nodes = sorted(nodes, key=itemgetter('utility'), reverse=True)[0:10]
        else:
            nodes = sorted(nodes, key=itemgetter('utility'), reverse=False)[0:10]

        for node in nodes:
            # if nodes.index(node) <= len(nodes)/10:
            #     node = self.moveSearch(finalDepth+1, currDepth+1, node)
            # else:
            node = self.moveSearch(finalDepth, currDepth+1, node)
            if currDepth != 0:
                if currNode['isMax'] and node['utility'] > currNode['bound']:
                    currNode['bound'] = node['utility']
                    if currNode['isMax'] is not currNode['parentNode']['isMax']:
                        if currNode['bound'] <= currNode['parentNode']['bound']:
                            currNode['bound'] = currNode['utility']
                            return currNode
                elif not currNode['isMax'] and node['utility'] < currNode['bound']:
                    currNode['bound'] = node['utility']
                    if currNode['isMax'] is not currNode['parentNode']['isMax']:
                        if currNode['bound'] >= currNode['parentNode']['bound']:
                            currNode['bound'] = currNode['utility']
                            return currNode

        if currNode['isMax']:
            maxUtil = -1
            for node in nodes:
                if node['utility'] > maxUtil:
                    maxUtil = node['utility']
                    favNode = node
            currNode['utility'] = maxUtil
        else:
            minUtil = 2
            for node in nodes:
                if node['utility'] < minUtil:
                    minUtil = node['utility']
                    favNode = node
            currNode['utility'] = minUtil

        if currDepth == 0:
            return favNode
        else:
            return currNode


        #     # recursively call this method, find path with best average utility
        #     pathUtil = -1
        #     for node in nodes:
        #     	pathToNode = self.moveSearch(node['nextState'], depth+1, node)
        #     	currUtil = self.evalNode(pathToNode)
        #     	if currUtil > pathUtil:
        #     		pathUtil = currUtil
        #     		favoriteMove = pathToNode

        # # return the best path of moves
        # favoriteMove.append(currNode)
        # return favoriteMove


    # Register a win
    def hasWon(self, currentState, playerId):
        opponentId = (playerId + 1) % 2

        if ((currentState.phase == PLAY_PHASE) and
                ((currentState.inventories[opponentId].getQueen() == None) or
                     (currentState.inventories[opponentId].getAnthill().captureHealth <= 0) or
                     (currentState.inventories[playerId].foodCount >= FOOD_GOAL) or
                     (currentState.inventories[opponentId].foodCount == 0 and
                              len(currentState.inventories[opponentId].ants) == 1))):
            return True
        else:
            return False








# #### UNIT TESTS ####

# # Create a GameState and populate it with inventories and a board
# board = [[Location((col, row)) for row in xrange(0,BOARD_LENGTH)] for col in xrange(0,BOARD_LENGTH)]
# p1Inventory = Inventory(PLAYER_ONE, [Ant((3,4), WORKER, PLAYER_ONE), Ant((4,2), QUEEN, PLAYER_ONE)]
#                 , [Building((0,0), ANTHILL, PLAYER_ONE), Building((2,1), TUNNEL, PLAYER_ONE)], 0)
# p2Inventory = Inventory(PLAYER_TWO, [Ant((2,6), WORKER, PLAYER_TWO), Ant((2,8), QUEEN, PLAYER_TWO)]
#                 , [Building((5,7), ANTHILL, PLAYER_TWO), Building((4,1), TUNNEL, PLAYER_TWO)], 0)
# neutralInventory = Inventory(NEUTRAL, [], [], 0)
# state = GameState(board, [p1Inventory, p2Inventory, neutralInventory], PLAY_PHASE, PLAYER_ONE)

# # Create a player object to call the methods
# player = AIPlayer(PLAYER_ONE)


# # Test that getUtility() returns a float in the bounds
# x = player.getUtility(state)

# if not (x <=1 and x >= 0):
#     print "The method getUtility() has returned an out of bounds value."


# # Test that initNode() returns a node structure
# nodes = []
# for move in listAllLegalMoves(state):
#     node = player.initNode(move, state)
#     nodes.append(node)
#     if not isinstance(node['move'], Move):
#         print "Move not found in Node structure"
#     if not isinstance(node['nextState'], GameState):
#         print "State not found in Node structure"
#     if not isinstance(node['utility'], float):
#         print "Utility not found in Node structure"


# # Test that evalNode() returns a float in bounds
# y = player.evalNode(nodes)

# if not (y <=1 and y >= 0):
#     print "The method evalNode() has returned an out of bounds value."


# # Test that moveSearch() returns a list of Nodes, last one is None
# nodes = player.moveSearch(state, 0, None)

# for node in nodes:
#     if node is nodes[-1]: 
#         continue

#     if not isinstance(node['move'], Move):
#         print "Move not found in Node structure"
#     if not isinstance(node['nextState'], GameState):
#         print "State not found in Node structure"
#     if not isinstance(node['utility'], float):
#         print "Utility not found in Node structure" 