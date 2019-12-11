# ==============================CS-199==================================
# FILE:          MyAI.py
#
# AUTHOR:     Justin Chung
#
# DESCRIPTION: This file contains the MyAI class. You will implement your
#           agent in this file. You will write the 'getAction' function,
#           the constructor, and any additional helper functions.
#
# NOTES:      - MyAI inherits from the abstract AI class in AI.py.
#
#           - DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
import random
import copy


class MyAI(AI):
    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        self.rowDimension = rowDimension
        self.colDimension = colDimension
        self.moveCount = 0
        self.totalMines = totalMines
        self.startX = startX
        self.startY = startY
        self.lastRowAction = startY
        self.lastColAction = startX
        self.tileInfo = [[-2 for col in range(self.colDimension)] for row in range(self.rowDimension)]
        self.flagNum = 0
        self.coveredTile = rowDimension * colDimension - totalMines
        self.exploreQueue = []
        self.bombQueue = []
        self.unexploredQueue = [(i, j) for i in range(self.rowDimension) for j in range(self.colDimension)]
        self.counter = 0
        self.currentMines = totalMines
        self.constraintSet = []
        self.constraintRowSize = 4
        self.constraintColSize = 4

    # add a tile into the explore queue if it has not been uncovered, flagged or already in the explore queue
    # if a tile is added to the explore queue, it is safe to explore the tile
    def addExploreQueue(self, row, col):
        if (row in range(self.rowDimension)) and (col in range(self.colDimension)):
            if (self.tileInfo[row][col] < -1) and ((row, col) not in self.exploreQueue):
                self.exploreQueue.append((row, col))

    def addBombQueue(self, row, col):
        if (row in range(self.rowDimension)) and (col in range(self.colDimension)):
            if (self.tileInfo[row][col] < -1) and ((row, col) not in self.bombQueue):
                self.bombQueue.append((row, col))

    def updateQueue(self, number):
        # when the number is zero, it's safe to explore all the neighbor nodes
        if number == 0:
            self.addExploreQueue(self.lastRowAction + 1, self.lastColAction + 1)
            self.addExploreQueue(self.lastRowAction + 1, self.lastColAction)
            self.addExploreQueue(self.lastRowAction + 1, self.lastColAction - 1)
            self.addExploreQueue(self.lastRowAction, self.lastColAction + 1)
            self.addExploreQueue(self.lastRowAction, self.lastColAction - 1)
            self.addExploreQueue(self.lastRowAction - 1, self.lastColAction + 1)
            self.addExploreQueue(self.lastRowAction - 1, self.lastColAction)
            self.addExploreQueue(self.lastRowAction - 1, self.lastColAction - 1)

    def checkNumberBomb(self, i, j):
        if (i in range(self.rowDimension)) and (j in range(self.colDimension)):
            if self.tileInfo[i][j] >= 0:
                return 0
            elif self.tileInfo[i][j] == -1:
                return -1
            elif self.tileInfo[i][j] == -2:
                return 1
        else:
            return 0

    def addConstraint(self, i, j, number):
        discovered_bomb = 0
        constraint_flag = 0
        constraint_li = []

        sur_tile = [[i-1, j-1], [i-1, j], [i-1, j+1], [i, j-1], [i, j+1], [i+1, j-1], [i+1, j], [i+1, j+1]]

        for loc in sur_tile:
            if self.checkNumberBomb(loc[0], loc[1]) == 1:
                constraint_li.append(loc)
                constraint_flag = 1
            if self.checkNumberBomb(loc[0], loc[1]) == -1:
                discovered_bomb += 1

        # add a constraint if there is covered tile around that number
        if constraint_flag == 1:
            constraint_li.append((number - discovered_bomb))
            self.constraintSet.append(constraint_li)

    def startConstraint(self):
        # choose the block with least covered tile to work with
        RowBlockCount = int(self.rowDimension/self.constraintRowSize)
        ColBlockCount = int(self.colDimension/self.constraintColSize)

        block_li = []

        for i in range(RowBlockCount):
            for j in range(ColBlockCount):
                sum = 0

                row_left_limit = self.constraintRowSize * i
                row_right_limit = self.constraintRowSize * (i + 1) - 1
                col_low_limit = self.constraintColSize * j
                col_up_limit = self.constraintColSize * (j + 1) - 1

                for tile in self.unexploredQueue:
                    if tile[0] >= row_left_limit and tile[0] <= row_right_limit and tile[1] >= col_low_limit and tile[1] <= col_up_limit:
                        sum += 1


                block_li.append([i,j,sum])

        block_li = sorted(block_li, key=lambda x:x[2])

        block_flag = 0
        current_block = 0
        for i in range(len(block_li)):
            if block_li[i][2] != 0 and block_li[i][2] != 16:
                block = [block_li[i][0], block_li[i][1]]
                current_block = i
                block_flag = 1
                break

        if block_flag == 0:
            block = [block_li[0][0], block_li[0][1]]
            current_block = 0


        while not self.constraintSet:
            if current_block == len(block_li):
                return -1
                break

            block = [block_li[current_block][0], block_li[current_block][1]]

            for i in range(self.constraintRowSize * block[0], self.constraintRowSize * (block[0] + 1)):
                for j in range(self.constraintColSize * block[1], self.constraintColSize*(block[1] + 1)):
                    if self.tileInfo[i][j] > 0:
                        self.addConstraint(i,j,self.tileInfo[i][j])

            current_block += 1

        return 0

    # when there is no deterministic move, solve a CSP
    def checkConstraint(self):
        # variable list
        var_li = []
        for constraint in self.constraintSet:
            for item in constraint:
                if type(item) == list:
                    if item not in var_li:
                        var_li.append(item)

        sol_li = []

        # construct solution list - populate all the possible solutions
        for i in range(len(var_li)):
            # initialize the solution
            if i == 0:
                sol_li.append([[var_li[i][0],var_li[i][1], 0]])
                sol_li.append([[var_li[i][0],var_li[i][1], 1]])

            else:
                sol_li_2 = []
                sol_li_2 = copy.deepcopy(sol_li)
                for sol in sol_li:
                    sol.append([var_li[i][0],var_li[i][1], 0])
                for sol in sol_li_2:
                    sol.append([var_li[i][0],var_li[i][1], 1])
                sol_li.extend(sol_li_2)
                sol_li_2 = []

        # for each of the solution, check whether they satisfy the constraint or not
        sol_check = []
        for i in range(len(sol_li)):
            check_flag = 0
            for constraint in self.constraintSet:
                cons_sum = 0
                for j in range(len(constraint) - 1):
                    for k in range(len(sol_li[i])):
                        if constraint[j][0] == sol_li[i][k][0] and constraint[j][1] == sol_li[i][k][1]:
                            if sol_li[i][k][2] == 1:
                                cons_sum += 1
                                break
                            else:
                                break
                if cons_sum != constraint[len(constraint) - 1]:
                    check_flag = 1
                    break
            sol_check.append([i, check_flag])


        # now sol_check has all the valid solutions for this condition, update sol_li and delete all the invalid solutions
        for i in range(len(sol_check) - 1, -1, -1):
            if sol_check[i][1] == 1:
                sol_li.pop(sol_check[i][0])

        # check if there is a tile that always stays 0 in all solutions, if there is, add that tile to the explore queue
        for tile in var_li:
            check_flag = 0
            for sol in sol_li:
                for i in range(len(sol)):
                    if tile[0] == sol[i][0] and tile[1] == sol[i][1]:
                        if sol[i][2] != 0:
                            check_flag = 1
                            break

            if check_flag == 0:
                self.addExploreQueue(tile[0],tile[1])


        # check if there is a tile taht always stays 1 in all solutions, if there is, add that tile to the bomb queue
        for tile in var_li:
            check_flag = 0
            for sol in sol_li:
                for i in range(len(sol)):
                    if tile[0] == sol[i][0] and tile[1] == sol[i][1]:
                        if sol[i][2] != 1:
                            check_flag = 1
                            break

            if check_flag == 0:
                self.addBombQueue(tile[0], tile[1])

        # if there is no tile that can be added to the explore queue or bomb queue, then calculate the probability of each tile not having bomb

        if (not self.exploreQueue) and (not self.bombQueue):
            prob_li = []
            for tile in var_li:
                sum = 0
                for sol in sol_li:
                    for i in range(len(sol)):
                        if tile[0] == sol[i][0] and tile[1] == sol[i][1]:
                            if sol[i][2] == 0:
                                sum += 1

                prob_li.append([tile[0], tile[1], sum])

            prob_li = sorted(prob_li, key = lambda x:x[2])
            prob_li.reverse()

            self.addExploreQueue(prob_li[0][0], prob_li[0][1])

        self.constraintSet = []

    # when the number is greater than zero, check the tile info
    def checkCondition(self, i, j, number):
        covered_sum = 0
        discovered_bomb = 0

        check_result_li = [self.checkNumberBomb(i - 1, j - 1), self.checkNumberBomb(i - 1, j),
                           self.checkNumberBomb(i - 1, j + 1), self.checkNumberBomb(i, j - 1),
                           self.checkNumberBomb(i, j + 1), self.checkNumberBomb(i + 1, j - 1),
                           self.checkNumberBomb(i + 1, j), self.checkNumberBomb(i + 1, j + 1)]

        for result in check_result_li:
            if result == -1:
                discovered_bomb += 1
            else:
                covered_sum += result

        # when all the bombs around this number have been discovered, all the unexplored tile are safe to be added to the explore queue
        if discovered_bomb == number:
            self.addExploreQueue(i - 1, j - 1)
            self.addExploreQueue(i - 1, j)
            self.addExploreQueue(i - 1, j + 1)
            self.addExploreQueue(i, j - 1)
            self.addExploreQueue(i, j + 1)
            self.addExploreQueue(i + 1, j - 1)
            self.addExploreQueue(i + 1, j)
            self.addExploreQueue(i + 1, j + 1)


        # when the number of covered tiles match the hint number, they can be determined as bomb tiles.

        elif (covered_sum + discovered_bomb) == number:
            self.addBombQueue(i - 1, j - 1)
            self.addBombQueue(i - 1, j)
            self.addBombQueue(i - 1, j + 1)
            self.addBombQueue(i, j - 1)
            self.addBombQueue(i, j + 1)
            self.addBombQueue(i + 1, j - 1)
            self.addBombQueue(i + 1, j)
            self.addBombQueue(i + 1, j + 1)


    def checkNumber(self):
        # check all the numbers on the edge, identify possible bombs and add new safe nodes to the queue
        for i in range(self.rowDimension):
            for j in range(self.colDimension):
                if self.tileInfo[i][j] > 0:
                    self.checkCondition(i, j, self.tileInfo[i][j])

    # used to finish the game - the game has to finish by uncovering all safe tiles and a bomb in the end. This function is to uncover a bomb
    def lastUncover(self):
        for i in range(self.rowDimension):
            for j in range(self.colDimension):
                if self.tileInfo[i][j] == -1:
                    coordX = j
                    coordY = i
                    action = AI.Action.UNCOVER
                    return coordX, coordY, action

    def getAction(self, number: int) -> "Action Object":
        # maintain the unexploredQueue (a node is considered unexplored before an action has been taken to it)

        index = self.unexploredQueue.index((self.lastRowAction, self.lastColAction))
        self.unexploredQueue.pop(index)

        self.counter += 1
        coordX = -10

        # print('iteration:', self.counter)
        # print('unexploredQueue', self.unexploredQueue)

        # after 10000 requests, leave the game
        if self.counter >= 10000:
            return Action(AI.Action.LEAVE)

        self.tileInfo[self.lastRowAction][self.lastColAction] = number

        # for row in self.tileInfo:
        #     print(row)

        if number >= 0:
            self.coveredTile -= 1

        # update the explore queue first when the hint number is 0
        if number == 0:
            self.updateQueue(number)

        # if there is still any node in the explore queue, explore the nodes first
        if self.exploreQueue:
            coordX = self.exploreQueue[0][1]
            coordY = self.exploreQueue[0][0]
            action = AI.Action.UNCOVER
            self.exploreQueue.pop(0)

        # if there is still any node in the bomb queue, flag the bomb nodes
        elif self.bombQueue:
            coordX = self.bombQueue[0][1]
            coordY = self.bombQueue[0][0]
            action = AI.Action.FLAG
            self.bombQueue.pop(0)


        # if there is no node at the explore queue or the bomb queue, do the following actions
        else:
            self.checkNumber()

            if self.exploreQueue:
                coordX = self.exploreQueue[0][1]
                coordY = self.exploreQueue[0][0]
                action = AI.Action.UNCOVER
                self.exploreQueue.pop(0)

            elif self.bombQueue:
                coordX = self.bombQueue[0][1]
                coordY = self.bombQueue[0][0]
                action = AI.Action.FLAG
                self.bombQueue.pop(0)

        # exit condition - discover all tiles and leave the game or flagged all the mines
        if self.coveredTile == 0 or self.currentMines == 0:
            if self.unexploredQueue:
                coordX = self.unexploredQueue[0][1]
                coordY = self.unexploredQueue[0][0]
                action = AI.Action.UNCOVER
            else:
                coordX, coordY, action = self.lastUncover()


        # cannot decide which is the next step, check the constraints and find the next step using probability
        if coordX == -10 or coordY == -10:

            constraint_flag = self.startConstraint()
            # if there is csp problem to solve
            if constraint_flag == 0:

                self.checkConstraint()

                if self.exploreQueue:
                    coordX = self.exploreQueue[0][1]
                    coordY = self.exploreQueue[0][0]
                    action = AI.Action.UNCOVER
                    self.exploreQueue.pop(0)

                elif self.bombQueue:
                    coordX = self.bombQueue[0][1]
                    coordY = self.bombQueue[0][0]
                    action = AI.Action.FLAG
                    self.bombQueue.pop(0)
            else:
                # take a random step
                index = random.randrange(0,len(self.unexploredQueue))
                coordX = self.unexploredQueue[index][1]
                coordY = self.unexploredQueue[index][0]
                action = AI.Action.UNCOVER

        self.lastRowAction = coordY
        self.lastColAction = coordX

        if action == AI.Action.FLAG:
            self.currentMines -= 1

        return Action(action, coordX, coordY)