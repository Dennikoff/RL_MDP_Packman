# featureExtractors.py
# --------------------
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


"Feature extractors for Pacman game states"

from game import Directions, Actions
import util

class FeatureExtractor:
    def getFeatures(self, state, action):
        """
          Returns a dict from features to counts
          Usually, the count will just be 1.0 for
          indicator functions.
        """
        util.raiseNotDefined()

class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[(state,action)] = 1.0
        return feats

class CoordinateExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[state] = 1.0
        feats['x=%d' % state[0]] = 1.0
        feats['y=%d' % state[0]] = 1.0
        feats['action=%s' % action] = 1.0
        return feats

def closestFood(pos, food, walls):
    """
    closestFood -- this is similar to the function that we have
    worked on in the search project; here its all in one place
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a food at this location then exit
        if food[pos_x][pos_y]:
            return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no food found
    return None

class SimpleExtractor(FeatureExtractor):
    """
    Returns simple features for a basic reflex Pacman:
    - whether food will be eaten
    - how far away the next food is
    - whether a ghost collision is imminent
    - whether a ghost is one step away
    """


    def getFeatures(self, state, action):

        def areGhostsClose(ghostScared, ghostActive):
            return util.manhattanDistance(ghostScared.getPosition(), ghostActive.getPosition()) < 3

        def getClosestGhost(state, ghosts):
            minDist = None
            minGhost = None

            for ghost in ghosts:
                dist = util.manhattanDistance(state.getPacmanPosition(), ghost.getPosition())
                if dist < minDist or minDist == None:
                    minDist = dist
                    minGhost = ghost
            return minDist, minGhost
        
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()
        ghostStates = state.getGhostStates()

        scaredGhosts = []
        activeGhosts = []
        
        for ghost in ghostStates:
            if ghost.isScared():
                scaredGhosts.append(ghost)
            else:
                activeGhosts.append(ghost)

        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        features["eats-ghosts"] = 0.0

        # features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)
        sumVal = 0
        for g in ghostStates:
            if not g.isScared() and (next_x, next_y) in Actions.getLegalNeighbors(g.getPosition(), walls):
                sumVal += 1
        
        features["#-of-ghosts-1-step-away"] = sumVal 

        distanceToScaredGhost = -1
        distanceToActiveGhost = -1
        flagEating = False
        # count the number of ghosts 1-step away
        if len(scaredGhosts) != 0:
            distanceToScaredGhost, closestScaredGhost = getClosestGhost(state, scaredGhosts)
            if len(activeGhosts) != 0:
                distanceToActiveGhost, closestActiveGhost = getClosestGhost(state, activeGhosts)
            # print('scared: ', distanceToScaredGhost, '\n', "active: ", distanceToActiveGhost)

            if ((distanceToActiveGhost == -1) or (distanceToScaredGhost < distanceToActiveGhost) and not areGhostsClose(closestScaredGhost, closestActiveGhost)) and (distanceToScaredGhost < 6):
                print("EATING")
                flagEating = True
                features["count-of-scared-ghosts"] = len(scaredGhosts)
                features["closest-scared-x"], features["closest-scared-y"] = closestScaredGhost.getPosition()
                features["closest-scared-x"] -= x
                features["closest-scared-y"] -= y

                print(features["closest-scared-x"], features["closest-scared-y"])

                if features["closest-scared-x"] < 0.0:
                    features["closest-scared-x"] = abs(features["closest-scared-x"])
                    features["closest-scared-direction-x"] = 0.0
                else:
                    features["closest-scared-direction-x"] = 1.0
                
                if features["closest-scared-y"] < 0.0:
                    features["closest-scared-y"] = abs(features["closest-scared-y"])
                    features["closest-scared-direction-y"] = 0.0
                else:
                    features["closest-scared-direction-y"] = 1.0

                print(features["closest-scared-x"], features["closest-scared-direction-x"])
                print(features["closest-scared-y"], features["closest-scared-direction-y"])
                
            

        # if there is no danger of ghosts then add the food feature
        if not flagEating and not features["#-of-ghosts-1-step-away"] and (food[next_x][next_y] or features["closest-scared-x"] == next_x and features["closest-scared-y"] == next_y):
            features["eats-food"] = 1.0

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            if flagEating:
                features["closest-food"] = min(distanceToScaredGhost, float(dist)) / (walls.width * walls.height)
            else:
                features["closest-food"] = float(dist) / (walls.width * walls.height)
        
            


        

        features.divideAll(10.0)
        
        # if features['eats-ghosts'] != 0.0:
        #     print('food: ', features["eats-food"])
        #     print('ghost: ', features["eats-ghosts"])
        return features
