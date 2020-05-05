"""
Tic Tac Toe Player
"""

import math
import random
import copy
#import runner

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if empty(board) or count(board,X) == count(board,O):
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    raise NotImplementedError
    """
    x = set()
    for i in range(3):
        for j in range(3):
            if board[i][j]==EMPTY:
                x.add((i,j))
    return x
    

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    raise NotImplementedError"""
    
    i,j = action[0],action[1]
    sign = player(board)
    #print(actions(board))
    if action in actions(board):
        board1 = copy.deepcopy(board)
        board1[i][j] = sign

    #elif len(actions(board))==0:
        
    else:
        
        raise "Not Valid Action"
    return board1

def winner(board):
    """
    Returns the winner of the game, if there is one.
    raise NotImplementedError"""
    players = [X,O]
    winner = None
    for p in players:
        if row_win(board,p) or col_win(board,p) or diag_win1(board,p) or diag_win2(board,p):
            winner = p
    return winner


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    raise NotImplementedError"""
    i = False
    w = winner(board)
    e = actions(board)
    if w is not None or len(e)==0:
        i = True
    return i

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    raise NotImplementedError"""
    #while terminal(board):
    if winner(board)==X:
        return 1
    elif winner(board)==O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    raise NotImplementedError"""
    moves =len(actions(board))
    best_move = (-1,-1)
    if terminal(board):
        return None

    elif player(board)==X:
        if len(actions(board)) == 9:
            return random.sample(actions(board),1)[0]
        else:
            res = []
            best_val = -2
            for i in actions(board):
                value = min_value(result(board,i),moves)[0]
                if value > best_val:
                    best_val = value
                    best_move = i
            return best_move
        
        

    elif player(board)==O:
        best_val = 2
        for i in actions(board):
            value = max_value(result(board,i),moves)[0]
            if value < best_val:
                best_val = value
                best_move = i
        return best_move

def max_value(board,moves):
    if terminal(board):
        return utility(board),moves
    else:
        i = -2
        moves += 1
        for j in actions(board):
            i = max(i,(min_value(result(board,j),moves)[0]))
             
            if i ==1:
                break
        return i,moves
                
def min_value(board,moves):
    if terminal(board):
        return utility(board),moves
    else:
        i = 2
        moves += 1
        for j in actions(board):
            i = min(i,(max_value(result(board,j),moves)[0]))
            if i == -1:    
                break
        return i,moves


def count(board,sign):
    count = 0
    for i in range(3):
        count += board[i].count(sign)
    return count

def empty(board):
    if count(board,O) + count(board,X) == 0:
        return True
    else:
        return False 
                
                 
def row_win(board,sign):

# Row wins
    for i in range(len(board)):
        win = True
        for j in range(len(board)):
            if board[j][i] != sign:
                win = False
                continue
        if win==True:
            return win
    return win

def col_win(board,sign):
#col wins
    for i in range(len(board)):
        win = True
        for j in range(len(board)):
            if board[i][j] != sign:
                win = False
                continue
        if win == True:
            return win
    return win

def diag_win1(board,sign):
#diagonal wins
    win = True
    for i in range(len(board)):
        if board[i][i]!=sign:
            win=False
    return win
def diag_win2(board, sign):
    win =True
    for i in range(len(board)):
        if board[i][len(board)-1-i]!= sign:
            win = False
    return win
