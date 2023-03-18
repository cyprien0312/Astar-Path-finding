# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part A: Single Player Infexion
from collections import defaultdict
from queue import PriorityQueue
import math

def apply_ansi(str, bold=True, color=None):
    """
    Wraps a string with ANSI control codes to enable basic terminal-based
    formatting on that string. Note: Not all terminals will be compatible!

    Arguments:

    str -- String to apply ANSI control codes to
    bold -- True if you want the text to be rendered bold
    color -- Colour of the text. Currently only red/"r" and blue/"b" are
        supported, but this can easily be extended if desired...

    """
    bold_code = "\033[1m" if bold else ""
    color_code = ""
    if color == "r":
        color_code = "\033[31m"
    if color == "b":
        color_code = "\033[34m"
    return f"{bold_code}{color_code}{str}\033[0m"

def render_board(board: dict[tuple, tuple], ansi=False) -> str:
    """
    Visualise the Infexion hex board via a multiline ASCII string.
    The layout corresponds to the axial coordinate system as described in the
    game specification document.
    
    Example:

        >>> board = {
        ...     (5, 6): ("r", 2),
        ...     (1, 0): ("b", 2),
        ...     (1, 1): ("b", 1),
        ...     (3, 2): ("b", 1),
        ...     (1, 3): ("b", 3),
        ... }
        >>> print_board(board, ansi=False)

                                ..     
                            ..      ..     
                        ..      ..      ..     
                    ..      ..      ..      ..     
                ..      ..      ..      ..      ..     
            b2      ..      b1      ..      ..      ..     
        ..      b1      ..      ..      ..      ..      ..     
            ..      ..      ..      ..      ..      r2     
                ..      b3      ..      ..      ..     
                    ..      ..      ..      ..     
                        ..      ..      ..     
                            ..      ..     
                                ..     
    """
    dim = 7
    output = ""
    for row in range(dim * 2 - 1):
        output += "    " * abs((dim - 1) - row)
        for col in range(dim - abs(row - (dim - 1))):
            # Map row, col to r, q
            r = max((dim - 1) - row, 0) + col
            q = max(row - (dim - 1), 0) + col
            if (r, q) in board:
                color, power = board[(r, q)]
                text = f"{color}{power}".center(4)
                if ansi:
                    output += apply_ansi(text, color=color, bold=False)
                else:
                    output += text
            else:
                output += " .. "
            output += "    "
        output += "\n"
    return output

def correctCoordinates(coordinates: tuple):
    """
    this function is being used to correct the corrdinates
    for example: (7, 7) -> (0, 0)
    """
    r = coordinates[0]
    q = coordinates[1]
    if r < 0:
        r = 7 - abs(r) % 7
    else:
        r = r % 7
    if q < 0:
        q = 7 - abs(q) % 7
    else:
        q = q % 7
    return (r, q)
    
def spread(board: dict[tuple, tuple], token: tuple, direction: tuple):
    """
    spread function. The input is the board status, tokens coordinates
    that about to move, and move direction
    """
    color = board[token][0]
    power = board[token][1]
    curr_tok = token
    
    while power > 0 :
        curr_tok = correctCoordinates((curr_tok[0] + direction[0], curr_tok[1] + direction[1]))
        addToken(board,curr_tok,color)
        power -= 1

    # delete the token being spreaded
    del board[token]
    

def addToken(board: dict[tuple, tuple], token: tuple, color: str):
    """
    Add a token to the board, increment its power if it's already present,
    and remove it if its power reaches 7.
    """
    if token in board:
        current_power = board[token][1] + 1
        if current_power < 7:
            board[token] = (color, current_power)
        else:
            del board[token]
    else:
        board[token] = (color, 1)

def distance(p1, p2):
    """
    eulidean distance of two points
    """
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def findClosestTwoTokens(redTokens, blueTokens):
    """
    this function find the closest blue token and red token
    """
    minDistance = 1000
    for redToken in redTokens:
        for blueToken in blueTokens:
            tokDistance = distance(redToken, blueToken)
            if tokDistance < minDistance:
                minDistance = tokDistance
                closestPair = (redToken, blueToken)
    return closestPair

def findAllNeighbours(token):
    """
    this funciton find all six neigoubours
    """    
    directions = [(0,1), (-1,1), (-1,0), (0,-1), (1,-1), (1,0)]
    neighbours = []
    for direction in directions:
        neighbour = (token[0] + direction[0], token[1] + direction[1])
        neighbours.append(correctCoordinates(neighbour))
    return neighbours
    
def divideTokens(board: dict[tuple, tuple]):
    """
    divide blue tokens and red tokens
    """
    redTokens = []
    blueTokens = []

    # divide tokens by color
    for token in board.keys():
        color = board[token][0]
        if color == 'r':
            redTokens.append(token)
        else:
            blueTokens.append(token)

    return (redTokens, blueTokens)

def aStarSearch(board: dict[tuple, tuple], heuristic):
    # group redTokens and blueTokens
    dividedTokens = divideTokens(board)
    redTokens = dividedTokens[0]
    blueTokens = dividedTokens[1]

    # find closest two tokens
    closestPair = findClosestTwoTokens(redTokens, blueTokens)
    startToken = closestPair[0]
    endToken = closestPair[1] 

    neighbours = findAllNeighbours(startToken)

    priorityQ = PriorityQueue()
    priorityQ.put(startToken, 0)
    cameFrom = defaultdict(tuple)
    cost = defaultdict(float)

    while not priorityQ.empty():
        currentToken = priorityQ.get()

        if currentToken == endToken:
            break

        neighbours = findAllNeighbours(currentToken)

        for neighbour in neighbours:
            newCost = cost[currentToken] + 1
            if neighbour not in cost or newCost < cost[neighbour]:
                cost[neighbour] = newCost
                priority = newCost + heuristic(endToken, neighbour)
                priorityQ.put(neighbour, priority)
                cameFrom[neighbour] = currentToken

    path = [endToken]
    while path[-1] != startToken:
        path.append(cameFrom[path[-1]])
    path.reverse()
    return path

