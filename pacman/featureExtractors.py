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

def cordsToDistances(pos, coords, walls):
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    coords = map((lambda coord: (int(coord[0]), int(coord[1]))), coords)
    distances = {}
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find the coord at this location then exit
        if (int(pos_x), int(pos_y)) in coords:
            distances[(int(pos_x), int(pos_y))] = dist
            if len(distances) == len(coords):
                break
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))

    return [distances[coord] for coord in coords if coord in distances]

class SimpleExtractor(FeatureExtractor):
    """
    Returns simple features for a basic reflex Pacman:
    - whether food will be eaten
    - how far away the next food is
    - whether a ghost collision is imminent
    - whether a ghost is one step away
    """


    def getFeatures(self, state, action):
        
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()
        ghostStates = state.getGhostStates()

        capsules = state.getCapsules()
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


        flagEating = False

        def getTargetPoses(ghosts):
            targetPosses = []
            for ghost in ghosts:
                targetPosses.append(ghost.getPosition())
            return targetPosses
        

        if len(scaredGhosts) != 0:
            targetPoses = getTargetPoses(scaredGhosts)
            distToGhost = cordsToDistances((next_x, next_y), targetPoses, walls)
            if (distToGhost != None):
                flagEating = True
                features["closest-ghost"] = float(min(distToGhost)) / (walls.width * walls.height)
                features["eating-ghosts"] = 1.0
        
        
        capsulesDists = cordsToDistances((next_x, next_y), capsules, walls)
        flagCapsules = False
        if capsulesDists != [] and not flagEating:
            flagCapsules = True
            features["eating-capsules"] = 1.0
            features["closest-capsule"] = float(min(capsulesDists)) / (walls.width * walls.height)  
                
            

        # if there is no danger of ghosts then add the food feature
        if not features["#-of-ghosts-1-step-away"] and (food[next_x][next_y]):
            features["eats-food"] = 1.0

        if flagEating or flagCapsules:
            features["eats-food"] = 0.01

        dist = closestFood((next_x, next_y), food, walls)


        if dist is not None and not (flagEating or flagCapsules):
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)

        
        
            


        

        features.divideAll(10.0)
        
        # if features['eats-ghosts'] != 0.0:
        #     print('food: ', features["eats-food"])
        #     print('ghost: ', features["eats-ghosts"])
        return features
