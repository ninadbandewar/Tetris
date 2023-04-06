import math, copy, random

from cmu_112_graphics import *

#################################################
# Helper functions
#################################################

def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

#################################################
# Tetris
#################################################

# Hard Code the Tetris Board Dimensions  
def gameDimensions():
    rows, cols, cellSize, margin = 15, 10, 20, 25
    return (rows, cols, cellSize, margin)

#################################################
# Some Helper Functions
#################################################

def createEmpty2DList(rows, cols, value):
    return [([value] * cols) for row in range(rows)] 

# Store the Possible Pieces and Colours
def piecesAndColours():
#From 
#https://www.cs.cmu.edu/~112/notes/notes-tetris/2_3_CreatingTheFallingPiece.html
#Seven "standard" pieces (tetrominoes)
    iPiece = [
            [  True,  True,  True,  True ]
        ]
    jPiece = [
            [  True, False, False ],
            [  True,  True,  True ]
        ]
    lPiece = [
            [ False, False,  True ],
            [  True,  True,  True ]
        ]
    oPiece = [
            [  True,  True ],
            [  True,  True ]
        ]
    sPiece = [
            [ False,  True,  True ],
            [  True,  True, False ]
        ]
    tPiece = [
            [ False,  True, False ],
            [  True,  True,  True ]
        ]
    zPiece = [
            [  True,  True, False ],
            [ False,  True,  True ]
        ]
    tetrisPieces = [iPiece, jPiece, lPiece, oPiece, sPiece, tPiece, zPiece]
    tetrisPieceColors = ["red", "yellow", "magenta", "pink", "cyan", 
                            "green","orange" ]
    return tetrisPieces, tetrisPieceColors

#################################################
# Model Functions
#################################################

def appStarted(app):
    app.rows, app.cols, app.cellSize, app.margin = gameDimensions()
    app.cellBoundary = app.cellSize // 5
    app.emptyColour = 'blue'
    app.board = createEmpty2DList(app.rows, app.cols, app.emptyColour)
    newFallingPiece(app)
    app.isGameOver = False
    app.score = 0
    # Sets the Game Speed
    app.timerDelay = 2000

# Create a new piece and get the top left row and col
def newFallingPiece(app):
    app.tetrisPieces, app.tetrisPieceColours = piecesAndColours()
    randomIndexOne = random.randint(0, len(app.tetrisPieces) - 1)
    randomIndexTwo = random.randint(0, len(app.tetrisPieceColours) - 1)
    app.fallingPiece = app.tetrisPieces[randomIndexOne]
    app.fallingPieceColour = app.tetrisPieceColours[randomIndexTwo]
    app.fallingPieceRow = 0
    app.fallingPieceCol = (app.cols // 2) - (len(app.fallingPiece[0]) // 2)

# Remove Full rows, add new rows to top and update score accordingly
def removeFullRows(app):
    emptyRow = [app.emptyColour] * (app.cols)
    # In case multiple rows are completed at once
    fullRows = 0
    for row in range(len(app.board)):
        if app.emptyColour not in app.board[row]:
            app.board.pop(row)
            app.board.insert(0, emptyRow)
            fullRows += 1
    # More points for filling more rows at a time
    app.score += fullRows**2

def timerFired(app):
    if (not app.isGameOver):
        moveFallingPiece(app, +1, 0)
        if placeFallingPiece(app):
            newFallingPiece(app)
            # If the new Falling Piece is illegal, game is over
            if (not isFallingPieceLegal(app)):
                app.isGameOver = True

#################################################
# Controller Functions
################################################# 

def keyPressed(app, event):
    if (event.key == 'r'):
        appStarted(app)
    elif (not app.isGameOver): 
        if (event.key == 'Up'):
            rotateFallingPiece(app)
        elif (event.key == 'Left'):
            moveFallingPiece(app, 0, -1)
        elif (event.key == 'Right'):
            moveFallingPiece(app, 0, +1)
        elif (event.key == 'Down'):
            moveFallingPiece(app, +1, 0)
        elif (event.key == 'Space'):
            hardDrop(app)

# Check all cells of the piece to check its legality
def isFallingPieceLegal(app):
    for row in range(len(app.fallingPiece)):
        for col in range(len(app.fallingPiece[row])):
            if app.fallingPiece[row][col]:
                pieceRow = row + app.fallingPieceRow
                pieceCol = col + app.fallingPieceCol
                # Illegal if out of board or cell already occupied
                if ((pieceRow < 0) or (pieceCol < 0) or 
                    (pieceRow >= app.rows) or (pieceCol >= app.cols) or 
                    (app.board[pieceRow][pieceCol] != app.emptyColour)):
                    return False
    return True

# drow and dcol will be assigned according to the key pressed
def moveFallingPiece(app, drow, dcol):
    app.fallingPieceRow += drow
    app.fallingPieceCol += dcol
    if (not isFallingPieceLegal(app)):
        app.fallingPieceRow -= drow
        app.fallingPieceCol -= dcol
        return False
    return True

# Anti Clockwise Rotation
def rotateFallingPiece(app):
    tempPiece = app.fallingPiece
    tempRow, tempCol = app.fallingPieceRow, app.fallingPieceCol
    # The number of rows and cols are interchanged for new piece
    newPieceRows = len(app.fallingPiece[0])
    newPieceCols = len(app.fallingPiece)
    newPiece = createEmpty2DList(newPieceRows, newPieceCols, None)
    # Create the new Piece through rotation and assigning new values
    for row in range(newPieceRows):
        for col in range(newPieceCols):
            newPiece[row][col] = app.fallingPiece[col][newPieceRows - row - 1]
    app.fallingPiece = newPiece
    # Change the center row
    oldCenterRow = app.fallingPieceRow + (len(tempPiece) // 2)
    app.fallingPieceRow = oldCenterRow - len(newPiece) // 2
    # Change the center col
    oldCenterCol = app.fallingPieceCol + (len(tempPiece[0]) // 2)
    app.fallingPieceCol = oldCenterCol - len(newPiece[0]) // 2
    # If illegal, reset to original
    if (not isFallingPieceLegal(app)):
        app.fallingPiece = tempPiece
        app.fallingPieceRow, app.fallingPieceCol = tempRow, tempCol

def placeFallingPiece(app):
    # Place the piece only if cannot be moved further down
    if (not moveFallingPiece(app, +1, 0)):
        for row in range(len(app.fallingPiece)):
            for col in range(len(app.fallingPiece[row])):
                if app.fallingPiece[row][col]:
                    pieceRow = row + app.fallingPieceRow
                    pieceCol = col + app.fallingPieceCol
                    app.board[pieceRow][pieceCol] = app.fallingPieceColour
        # Remove full rows after every piece that is placed
        removeFullRows(app)
        return True
    return False

# Move the piece as far down as it can go when decides to hardDrop
def hardDrop(app):
    while moveFallingPiece(app, +1, 0):
        moveFallingPiece(app, +1, 0)

#################################################
# View Functions
#################################################

def redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = 'orange')
    drawBoard(app, canvas)
    drawFallingPiece(app, canvas)
    drawGameOver(app, canvas)
    drawScore(app, canvas)

# Iterate through number of cells and rows and draw each cell
def drawBoard(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app, canvas, row, col, app.board[row][col])

# Determine the start and end co-ordinates and draw the cell
# Takes in colour so can be updated for different functions
def drawCell(app, canvas, row, col, colour):
    startX = col * app.cellSize + app.margin 
    startY = row * app.cellSize + app.margin
    endX = (col + 1) * app.cellSize + app.margin 
    endY = (row + 1) * app.cellSize + app.margin
    canvas.create_rectangle(startX, startY, endX, endY, 
                    fill = colour, outline = 'black', 
                    width = app.cellBoundary)

# Draw the falling piece cell by cell
def drawFallingPiece(app, canvas):
    for row in range(len(app.fallingPiece)):
        for col in range(len(app.fallingPiece[row])):
            if app.fallingPiece[row][col]:
                pieceRow = row + app.fallingPieceRow
                pieceCol = col + app.fallingPieceCol
                drawCell(app, canvas, pieceRow, pieceCol, 
                            app.fallingPieceColour) 

# Display Game over when the game ends and provide further instructions
def drawGameOver(app, canvas):
    if app.isGameOver:
        canvas.create_rectangle(app.margin, app.height // 5, 
                            app.width - app.margin, app.height // 5 + 50,
                            fill = 'black')
        textHeight = (2 * app.height // 5 + 50) // 10
        canvas.create_text(app.width // 2, (2 * app.height // 5 + 50) // 2,
                            text = 'Game Over!', fill = 'yellow',
                            font = f'Helvetica {textHeight} bold')
        canvas.create_text(app.width // 2, app.height // 2 ,
                            text = "Press 'r' to restart ", fill = 'white',
                            font = f'Helvetica 15 bold')

# Update Score as the game goes on
def drawScore(app, canvas):
    textHeight = app.margin // 2
    canvas.create_text(app.width // 2, app.margin // 2,
                        text = f'Score : {app.score}', fill = 'black',
                        font = f'Helvetica {textHeight} bold')

# Use the dimensions to create the app
def playTetris():
    rows, cols, cellSize, margin = gameDimensions()
    width = cols * cellSize + 2 * margin
    height = rows * cellSize + 2 * margin
    runApp(width = width, height = height)

#################################################
# main
#################################################

def main():
    playTetris()

if __name__ == '__main__':
    main()
