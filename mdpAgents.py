# -*- coding: utf-8 -*-
# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)

    def createMapOfAllPaths(self, state):
        #use layout info about walls etc. to add valid states (states pacman can visit) to dict
        # get the corners of the layout map
        corners = api.corners(state)
        # pathways, +1 to accommodate for edge walls
        width = corners[3][0] + 1
        height = corners[3][1] + 1
        coordsList = []
        wallsList = api.walls(state)

        # add all coordinates of the map to coordslist
        for x in range(0, width):
            for y in range(0, height):
                coordsList.append((x,y))

        # remove the coordinates of any walls from the list, leaving us with just the accessible paths
        for wall in wallsList:
            if wall in coordsList:
                coordsList.remove(wall)
        
        # final map of accessible pathways
        pathMap = coordsList

        return pathMap

    def rewardMap(self, state, allStates):
    	#create a dictionary of the initial values of each state
    	rewardValues = {}
    	pacman = api.whereAmI(state)

        # loop through all states to assign reward values
        for i in allStates:
            ghostList = api.ghosts(state)
            ghostNeighbours = []
            ghostNextNeighbours = []

            # give ghosts' neighbour states a reward to keep pacman away more easily
            for ghost in ghostList:
                ghostNeighbours.append([(ghost[0],ghost[1]+1),
                                    (ghost[0]+1,ghost[1]),
                                    (ghost[0],ghost[1]-1),
                                    (ghost[0]-1,ghost[1])])
            # neighbours of neighbours for added safety
            for neighbours in ghostNeighbours:
                for neighbour in neighbours:
                    ghostNextNeighbours.append([(neighbour[0],neighbour[1]+1),
                                        (neighbour[0]+1,neighbour[1]),
                                        (neighbour[0],neighbour[1]-1),
                                        (neighbour[0]-1,neighbour[1])])

            allGhostneighbours = ghostNeighbours + ghostNextNeighbours

            # ghost is checked first, as it is to be avoided more than food is needed to be gained
            for neighbour in allGhostneighbours:
                # ghosts and ghost neighbours
                if i in neighbour or i in ghostList:
                    rewardValues[i] = -100
                # food
                elif i in api.food(state):
                    rewardValues[i] = 10                 
            	# pacman current position
                elif i == pacman:
            	   rewardValues[i] = -1
                # capsules
                elif i in api.capsules(state):
                    rewardValues[i] = 250                 
                # empty
                else:
            		rewardValues[i] = -0.04                

        return rewardValues
 
    def getProbabilities(self, state, intendedAction):
        nextState = [0, 0, 0, 0]

        if intendedAction == 0: # north
            nextState[0] = 0.8
            nextState[1] = 0
            nextState[2] = 0.1
            nextState[3] = 0.1
        elif intendedAction == 1: # south
            nextState[0] = 0
            nextState[1] = 0.8
            nextState[2] = 0.1
            nextState[3] = 0.1
        elif intendedAction == 2: # west
            nextState[0] = 0.1
            nextState[1] = 0.1
            nextState[2] = 0.8
            nextState[3] = 0
        elif intendedAction == 3: # east
            nextState[0] = 0.1
            nextState[1] = 0.1
            nextState[2] = 0
            nextState[3] = 0.8
        else:
            return

        return nextState # list of probabilities of neighbour states, for a given action

    def policyIteration(self, state, currentState, allStates):
        discount = 0.66 # gamma value for discounting bellman equation
        policy = {} # to be north, south, west or east per state
        previousPolicy = {}
        pacman = api.whereAmI(state)
        actions = [0, 1, 2, 3] # actions, north south west east
        actionSum = [0, 0, 0, 0]
        reward = self.rewardMap(state, allStates)
        pathMap = self.createMapOfAllPaths(state)
        utility = {}
        optimal = False 

        #set initial utilities & initial, arbitrary policy
        for s in allStates:
            utility[s] = 0
            policy[s] = random.choice(actions)       

        while not optimal:

            previousPolicy = policy.copy() # copy by reference not val. policy is what will update in 'improvement' stage

            # Policy evaluation
            for s in allStates:

                x = s[0] 
                y = s[1]

                sPrime = [(x,y+1), (x,y-1), (x-1,y), (x+1,y)]

                # change illegal moves to just the current position
                for i in range(len(sPrime)):
                    if sPrime[i] not in pathMap:
                        sPrime[i] = (x, y)

                # get probabilities based on the state's current policy
                policyProbabilityOf = self.getProbabilities(state, policy[s]) 
                previousPolicyUtility = utility.copy()

                policySum = (policyProbabilityOf[0] * previousPolicyUtility[sPrime[0]]) + \
                        (policyProbabilityOf[1] * previousPolicyUtility[sPrime[1]]) + \
                        (policyProbabilityOf[2] * previousPolicyUtility[sPrime[2]]) + \
                        (policyProbabilityOf[3] * previousPolicyUtility[sPrime[3]])

                utility[s] = reward[s] + discount * policySum

            # Policy improvement
            for s in allStates:
                ##getting sPrimes for each state again
                x = s[0] 
                y = s[1]
                sPrime = [(x,y+1), (x, y-1), (x-1,y), (x+1, y)] #north south west east

                # set illegal neighbours to Pacman's current position
                for i in range(4):
                    if sPrime[i] not in pathMap:
                        sPrime[i] = (x, y)

                for a in actions:
                    # get probabilities based on just action
                    actionProbabilityOf = self.getProbabilities(state, a) 

                    actionSum[a] = (actionProbabilityOf[0] * utility[sPrime[0]]) + \
                                 (actionProbabilityOf[1] * utility[sPrime[1]]) + \
                                 (actionProbabilityOf[2] * utility[sPrime[2]]) + \
                                 (actionProbabilityOf[3] * utility[sPrime[3]])

                policy[s] = actionSum.index(max(actionSum)) # update the policy
            
            # if policy hasn't changed, is optimal
            if policy == previousPolicy:
                optimal = True
        
        return policy


    def modifiedPolicyIteration(self, state, currentState, allStates):
        discount = 0.66
        policy = {} # to be north, south, west or east per state
        previousPolicy = {}
        pacman = api.whereAmI(state)
        actions = [0, 1, 2, 3] # actions, north south west east
        actionSum = [0, 0, 0, 0]
        reward = self.rewardMap(state, allStates)
        pathMap = self.createMapOfAllPaths(state)
        utility = {}   
        optimal = False

        #set initial utilities & initial, arbitrary policy
        for s in allStates:
            utility[s] = 0
            policy[s] = random.choice(actions)

        while not optimal:
            previousPolicy = policy.copy() # policy is what will update in 'improvement' stage

            for s in allStates:
                x = s[0] 
                y = s[1]

                sPrime = [(x,y+1), (x,y-1), (x-1,y), (x+1,y)]

                # change illegal moves to just the current position
                for i in range(len(sPrime)):
                    if sPrime[i] not in pathMap:
                        sPrime[i] = (x, y)

                for i in range(5):
                    # get probabilities based on the state's current policy
                    policyProbabilityOf = self.getProbabilities(state, policy[s])
                    previousPolicyUtility = utility.copy()
  
                    policySum = (policyProbabilityOf[0] * previousPolicyUtility[sPrime[0]]) + \
                            (policyProbabilityOf[1] * previousPolicyUtility[sPrime[1]]) + \
                            (policyProbabilityOf[2] * previousPolicyUtility[sPrime[2]]) + \
                            (policyProbabilityOf[3] * previousPolicyUtility[sPrime[3]])

                    utility[s] = reward[s] + discount * policySum

            for s in allStates:          

                ##getting sPrimes for each state again
                x = s[0] 
                y = s[1]
                sPrime = [(x,y+1), (x, y-1), (x-1,y), (x+1, y)] #north east west south

                # set illegal neighbours to Pacman's current position
                for i in range(4):
                    if sPrime[i] not in pathMap:
                        sPrime[i] = (x, y)

                for a in actions:
                    # get probabilities based on just action
                    actionProbabilityOf = self.getProbabilities(state, a) 

                    actionSum[a] = (actionProbabilityOf[0] * utility[sPrime[0]]) + \
                                 (actionProbabilityOf[1] * utility[sPrime[1]]) + \
                                 (actionProbabilityOf[2] * utility[sPrime[2]]) + \
                                 (actionProbabilityOf[3] * utility[sPrime[3]])

                policy[s] = actionSum.index(max(actionSum)) # update the policy

            if policy == previousPolicy:
                optimal = True
        
        return policy

    def valueIteration(self, state, currentState, allStates): # pathmap is passed as allStates
        discount = 0.66
        actions = [0, 1, 2, 3] # north, south, west, east; respectively
        maxFunc = [0.0, 0.0, 0.0, 0.0]
        utility = {} # list of utilities, this is what is updated with each Bellman iteration
        previousUtility = {}
        reward = self.rewardMap(state, allStates)

        pathMap = self.createMapOfAllPaths(state)

        # Setting initial utility to 0
        for s in allStates:
            utility[s] = 0

        converged = False         
        
        while not converged:
            for i in utility: 
                previousUtility[i] = utility[i]
            
            for s in allStates:
                x = s[0] 
                y = s[1]

                sPrime = [(x,y+1), (x, y-1), (x-1,y), (x+1, y)] #north east west south

                # change ones not possible to just the current pos
                for i in range(4):
                    if sPrime[i] not in pathMap:
                        sPrime[i] = (x, y)

                for a in actions:
                    # get probabilities based on just action
                    probability = self.getProbabilities(state, a) # list of probabilities

                    maxFunc[a] = (probability[0] * previousUtility[sPrime[0]]) + \
                                 (probability[1] * previousUtility[sPrime[1]]) + \
                                 (probability[2] * previousUtility[sPrime[2]]) + \
                                 (probability[3] * previousUtility[sPrime[3]])

                utility[s] = reward[s] + (discount * max(maxFunc))

                differenceThreshold = 0.05 # threshold for ending iteration early

                for i in utility:
                    # if the difference between all utilities is smaller than the threshold, consider them converged
                    if abs(previousUtility[i] - utility[i]) < differenceThreshold:
                        converged = True
                    else:
                        # continue iterating until converged
                        converged = False
                        break

        return utility

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    def getAction(self, state):
        pacman = api.whereAmI(state)
        pathMap = self.createMapOfAllPaths(state)

        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        ###CODE TO EXECUTE NORMAL POLI ITER STRATEGY
        optimalPolicy = self.policyIteration(state, pacman, pathMap)

        move = [api.makeMove(Directions.NORTH, legal), api.makeMove(Directions.SOUTH, legal), api.makeMove(Directions.WEST, legal), api.makeMove(Directions.EAST, legal)]

        return move[optimalPolicy[pacman]] # move in the direction of the best action for pacman's current state position

        # NOTE: any code below this line has been left intentionally (in case of assessment of two other strategies)

        ###CODE TO EXECUTE VALUE ITERATION STRATEGY###
        # utility = self.valueIteration(state, pacman, pathMap)
        # actions = [0, 1, 2, 3] # north, south, west, east; respectively
        # maxFunc = [0.0, 0.0, 0.0, 0.0]
        #
        # x = pacman[0]
        # y = pacman[1] 
        # neighbours = [(x,y+1), (x, y-1), (x-1,y), (x+1, y)]
        #
        # for i in range(4):
        #     if neighbours[i] not in pathMap:
        #         neighbours[i] = (x, y)
        #
        # for a in actions:
        #     actionProbabilityOf = self.getProbabilities(state, a) 
        #
        #     maxFunc[a] = (actionProbabilityOf[0] * utility[neighbours[0]]) + \
        #                  (actionProbabilityOf[1] * utility[neighbours[1]]) + \
        #                  (actionProbabilityOf[2] * utility[neighbours[2]]) + \
        #                  (actionProbabilityOf[3] * utility[neighbours[3]])
        #
        # actionIndexOfMaximisedUtility = maxFunc.index(max(maxFunc))
        #
        # move = [api.makeMove(Directions.NORTH, legal), api.makeMove(Directions.SOUTH, legal), api.makeMove(Directions.WEST, legal), api.makeMove(Directions.EAST, legal)]
        #
        # return move[actionIndexOfMaximisedUtility]
        ##############################################

        ###CODE TO EXECUTE MODIPOLI STRATEGY###
        # optimalPolicy = self.modifiedPolicyIteration(state, pacman, pathMap)
        #
        # move = [api.makeMove(Directions.NORTH, legal), api.makeMove(Directions.SOUTH, legal), api.makeMove(Directions.WEST, legal), api.makeMove(Directions.EAST, legal)]
        #
        # return move[optimalPolicy[pacman]] # move in the direction of the best action for pacman's current state position
        #######################################