from tile import Tile
import pygame
import tkinter as tk
import CONSTANTS

sysInfo = tk.Tk()


class Piece:
    def __init__(self, x, y, type, orientation, color, img):
        self.GUI = None
        self.tileSize = (sysInfo.winfo_screenheight() - 1) // 8
        self.x=x
        self.y=y
        self.type=type
        self.image=img
        self.movesMade = 0
        #Orientation True = up, False = down
        self.orientation = orientation
        self.color=color


    #give pieces access to main gui
    def getGUI(self, GUI, omni=False):
        self.GUI=GUI
        self.moves = {}
        self.protects = {}
        self.attacks = {}
        if not omni:
            self.getMoves()

    def isAlive(self):
        if self.color=='white':
            if self in self.GUI.whitePieces:
                return True
            else:
                return False
        else:
            if self in self.GUI.blackPieces:
                return True
            else:
                return False


    #draw piece to tile it moved to
    def draw(self,screen):
        screen.blit(self.image, (self.x*self.tileSize, self.y*self.tileSize))


    #check if piece attacks certain tile
    def attacksTile(self, tile):

        #refresh moves if not king (King moves depend on this func so enters infinite loop if rechecks king moves)
        if self.type!='king':
            self.getMoves()
            if (tile.x, tile.y) in self.protects:
                return True
        #handle king distance from tile as alternative for checking if controlled
        elif abs(tile.x-self.x)<=1 and abs(tile.y-self.y)<=1:
            return True


        return False

    #return true if no moves are available
    def isCheckMate(self):
        if self.color=='white':
            for piece in self.GUI.blackPieces:
                piece.getMoves()
                if len(piece.moves) != 0:
                    return False
        else:
            for piece in self.GUI.whitePieces:
                piece.getMoves()
                if len(piece.moves) != 0:
                    return False
        return True

    #get moves per piece type
    def getMoves(self):
        self.moves = {}
        self.protects = {}
        self.attacks={}
        # pawn moves
        if self.type == 'pawn':
            self.getPawnMove()
        if self.type=='rook':
            self.getRookMove()
        if self.type=='knight':
            self.getKnightMove()
        if self.type=='bishop':
            self.getBishopMove()
        if self.type=='queen':
            self.getQueenMove()
        if self.type=='king':
            self.getKingMove()

        #locate and remove illegal moves (ones that put you in check basically)
        illegals = []
        for move in self.moves.copy():
            nkc = self.needKingCheck((move[0], move[1]))
            if nkc[0]:
                moveTile = self.GUI.tiles[move]
                if not self.isLegalMove(moveTile, checker=nkc[1]):
                    self.moves.pop(move)

                    if move in self.attacks:
                        self.attacks.pop(move)

                    if move in self.protects:
                        self.protects.pop(move)



    #move under the assumption that the computer can only pick from legal moves (skip double checking)
    def AIMove(self, pos, screen):
        checked = False
        curTile = self.GUI.tiles[(self.x, self.y)]
        moveTile = self.GUI.tiles[pos]
        self.movesMade +=1

        if moveTile.hasPiece:
            if self.color == 'white':
                self.GUI.blackPieces.pop(moveTile.piece)
            else:
                self.GUI.whitePieces.pop(moveTile.piece)
            moveTile.losePiece()

        self.x = pos[0]
        self.y = pos[1]
        curTile.losePiece()
        moveTile.getPiece(self)

        if self.type == 'king':
            if self.color == 'white':
                self.GUI.gamestate.whiteKingTile = (self.x, self.y)
            else:
                self.GUI.gamestate.blackKingTile = (self.x, self.y)
        self.getMoves()
        opKTile = self.GUI.gamestate.blackKingTile if self.color=="white" else self.GUI.gamestate.whiteKingTile
        opColor = "white" if self.color=="black" else "black"
        if opKTile in self.attacks:
            self.GUI.gamestate.checks[opColor] = True
            checked = True
        self.draw(screen)
        self.GUI.highlight(pos, allowMove=False)
        if self.isCheckMate():
            self.GUI.zeroPlayerHandleCheckmate(self.color)




    #move selected piece to selected tile (only if selected tile is in the piece's available moves)
    #return true if moved, false if move is illegal
    def move(self, pos, screen, AI=False, draw = True):
        taken = None
        cx = self.x
        cy = self.y

        if self.GUI.gamestate.checks[self.color]==False:
            if pos in self.moves:
                curTile = self.GUI.tiles[(self.x,self.y)]
                moveTile = self.GUI.tiles[pos]
                if pos in self.attacks:
                    taken = moveTile.piece
                    if self.color == 'white':
                        self.GUI.blackPieces.pop(moveTile.piece)
                    else:
                        self.GUI.whitePieces.pop(moveTile.piece)
                    moveTile.losePiece()
                moveTile.getPiece(self)
                curTile.losePiece()
                self.x=pos[0]
                self.y=pos[1]
                if self.type=='king':
                    if self.color=='white':
                        self.GUI.gamestate.whiteKingTile = (self.x,self.y)
                    else:
                        self.GUI.gamestate.blackKingTile = (self.x, self.y)
                if draw:
                    self.draw(screen)
                self.movesMade += 1
                if self.isCheckMate() and AI==False:
                    self.GUI.handleCheckmate()

                return [cx,cy,taken]
            return False

        #else in check
        else:
            #to test move then restore values if still in check
            selfTile = self.GUI.tiles[(self.x,self.y)]
            tempX = self.x
            tempY = self.y
            tempKingTile = self.GUI.gamestate.blackKingTile
            if self.color=='white':
                tempKingTile = self.GUI.gamestate.whiteKingTile


            if pos in self.moves:
                tile = self.GUI.tiles[pos]
                if tile.hasPiece:
                    if (self.type == 'pawn' and self.x != tile.x) or self.type != 'pawn':

                        if tile.piece.color != self.color and tile.piece.type != 'king':
                            tempPiece = tile.piece

                            #see if check is blocked
                            self.x = pos[0]
                            self.y = pos[1]

                            if self.color=='white':
                                self.GUI.blackPieces.pop(tile.piece)
                            else:
                                self.GUI.whitePieces.pop(tile.piece)

                            tile.getPiece(self)

                            if self.color=='white':
                                if self.type=='king':
                                    self.GUI.gamestate.whiteKingTile = (self.x, self.y)
                                if self.GUI.tiles[self.GUI.gamestate.whiteKingTile].isControlled(self.color):
                                    self.x=tempX
                                    self.y=tempY
                                    self.GUI.blackPieces[tempPiece]=tempPiece

                                    self.GUI.gamestate.whiteKingTile=tempKingTile
                                    tile.getPiece(tempPiece)
                                    return False
                                elif draw: tile.blankDraw()

                            else:
                                if self.type=='king':
                                    self.GUI.gamestate.blackKingTile = (self.x, self.y)
                                if self.GUI.tiles[self.GUI.gamestate.blackKingTile].isControlled(self.color):
                                    self.x=tempX
                                    self.y=tempY
                                    self.GUI.whitePieces[tempPiece] = tempPiece
                                    self.GUI.gamestate.blackKingTile = tempKingTile
                                    tile.getPiece(tempPiece)
                                    return False
                                elif draw: tile.blankDraw()
                        else:
                            return False
                    else:
                        return False
                else:
                    # see if check is blocked
                    self.x = pos[0]
                    self.y = pos[1]
                    tile.getPiece(self)

                    if self.color == 'white':
                        if self.type=='king':
                            self.GUI.gamestate.whiteKingTile = (self.x, self.y)
                        if self.GUI.tiles[self.GUI.gamestate.whiteKingTile].isControlled(self.color):
                            self.x = tempX
                            self.y = tempY
                            tile.losePiece()

                            return False

                    else:
                        if self.type == 'king':
                            self.GUI.gamestate.blackKingTile = (self.x, self.y)
                        if self.GUI.tiles[self.GUI.gamestate.blackKingTile].isControlled(self.color):
                            self.x = tempX
                            self.y = tempY
                            tile.losePiece()

                            return False

                self.x = pos[0]
                self.y = pos[1]
                selfTile.losePiece()
                if self.type=='king':
                    if self.color=='white':
                        self.GUI.gamestate.whiteKingTile=(self.x,self.y)
                    else:
                        self.GUI.gamestate.blackKingTile = (self.x, self.y)
                elif self.type=="pawn":
                    if self.color=="white" and self.y == 0:
                        self.type=="queen"
                        pieceImg = CONSTANTS.whitePieces['queen']
                        pieceImg = pygame.transform.scale(pieceImg, (self.tileSize, self.tileSize))
                        self.image = pieceImg
                    elif self.color=="black" and self.y==7:
                        self.type == "queen"
                        pieceImg = CONSTANTS.blackPieces['queen']
                        pieceImg = pygame.transform.scale(pieceImg, (self.tileSize, self.tileSize))
                        self.image = pieceImg
                if draw:
                    self.draw(screen)
                self.movesMade += 1
                tile.getPiece(self)


                self.protects = {}
                if self.color=='black':
                    if self.GUI.tiles[self.GUI.gamestate.whiteKingTile].isControlled('white'):
                        self.GUI.gamestate.checks['white']=True
                else:
                    if self.GUI.tiles[self.GUI.gamestate.blackKingTile].isControlled('black'):
                        self.GUI.gamestate.checks['black'] = True
                if self.isCheckMate():
                    self.GUI.handleCheckmate()
                return [cx,cy,taken]

        return False

    #go back to previous move
    def returnMove(self,curCoord,returnCoord, taken, checked, moves, draw=False):
        self.movesMade -=1
        self.moves = moves[0]
        self.attacks = moves[1]
        self.protects = moves[2]
        pTile = self.GUI.tiles[curCoord]
        pTile.losePiece(redraw=draw)
        if draw:
            pTile.draw(pTile.color)

        if taken!=None:
            pTile.getPiece(taken)
            if taken.color=="white":
                self.GUI.whitePieces[taken] = taken
            else:
                self.GUI.blackPieces[taken] = taken
            if draw:
                taken.draw(self.GUI.screen)


        self.x = returnCoord[0]
        self.y = returnCoord[1]
        self.GUI.tiles[returnCoord].getPiece(self)
        if draw:
            self.draw(self.GUI.screen)

        if self.type == "king":
            if self.color=='white':
                self.GUI.gamestate.whiteKingTile = returnCoord
            else:
                self.GUI.gamestate.blackKingTile = returnCoord

        #theoretically this works bc move list is set at each iteration start, correctly accounting for checks, so we are guaranteed to either exit check or end the game after this runs
        self.GUI.gamestate.checks[self.color] = False

        #undo checks if move put opponent in check
        opColor = "white" if self.color == "black" else "black"
        if checked:
            self.GUI.gamestate.checks[opColor] = False

    # TODO AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    #return false if move puts own side in check, is blocked, is currently in check, etc.
    def isLegalMove(self, tile, checker="all"):
        checkW = self.GUI.gamestate.checks['white']
        checkB = self.GUI.gamestate.checks['black']
        self.GUI.gamestate.checks[self.color] = False
        selfTile = self.GUI.tiles[(self.x, self.y)]
        tempPiece = None
        tempX = self.x
        tempY = self.y

        if tile.hasPiece:
            tempPiece = tile.piece
            if tile.piece.color == 'black':
                self.GUI.blackPieces.pop(tile.piece)
                tile.piece.protects = {}
            else:
                self.GUI.whitePieces.pop(tile.piece)
                tile.piece.protects = {}
            tile.losePiece(redraw=False)

        selfTile.losePiece(redraw=False)
        self.x = tile.x
        self.y = tile.y
        tile.getPiece(self)
        self.protects = {}

        if self.type == 'king':
            if self.color == 'white':
                self.GUI.gamestate.whiteKingTile = (self.x, self.y)
            else:
                self.GUI.gamestate.blackKingTile = (self.x, self.y)

        kTile = self.GUI.gamestate.whiteKingTile if self.color=='white' else self.GUI.gamestate.blackKingTile

        # see if you are in check
        if self.GUI.tiles[kTile].isControlled(self.color, checker=checker):
            self.GUI.gamestate.checks[self.color] = True

        # see if opponent was checked (potentially useful for scoring move)
        #opColor = "white" if self.color == "black" else "black"
        #opKTile = self.GUI.gamestate.whiteKingTile if self.color=="black" else self.GUI.gamestate.blackKingTile
        #if self.GUI.tiles[opKTile].isControlled(opColor):
        #    self.GUI.gamestate.checks[opColor] = True

        # return test taken/moved pieces
        tile.losePiece(redraw=False)
        selfTile.getPiece(self)

        self.x = tempX
        self.y = tempY

        if tempPiece != None:
            tile.getPiece(tempPiece)
            if tempPiece.color == 'black':
                self.GUI.blackPieces[tempPiece] = tempPiece
            else:
                self.GUI.whitePieces[tempPiece] = tempPiece
        if self.type == 'king':
            if self.color == 'black':
                self.GUI.gamestate.blackKingTile = (self.x, self.y)
            else:
                self.GUI.gamestate.whiteKingTile = (self.x, self.y)

        #illegal move if was put in check
        if self.GUI.gamestate.checks[self.color]:

            self.GUI.gamestate.checks['white'] = checkW
            self.GUI.gamestate.checks['black'] = checkB
            return False
        self.GUI.gamestate.checks['white'] = checkW
        self.GUI.gamestate.checks['black'] = checkB
        return True


    # see if there was a possibility this move could put us in check (so we can do deeper test later)
    def needKingCheck(self, move):
        if self.GUI.gamestate.checks[self.color]:
            return [True, "all"]

        mx = move[0]
        my = move[1]
        kTile = self.GUI.gamestate.whiteKingTile if self.color == 'white' else self.GUI.gamestate.blackKingTile
        kx = kTile[0]
        ky = kTile[1]
        if self.type=="king":
            return [True, "all"]
        if (self.y == ky and self.y != my) or (self.x == kx and self.x != mx):
            return [True, "rq"]
        # TODO this one could be improved somehow (find out when the diagonal remains the same and don't bother checking these)
        if self.x - kx != 0 and (self.y - ky) / (self.x - kx) == 1:
            return [True, "bq"]
        return [False, None]

    #get moves for a pawn
    def getPawnMove(self):
        if self.orientation and self.y - 1 >= 0:
            # check forward tiles
            moveTile = self.GUI.tiles[(self.x, self.y - 1)]
            if not moveTile.hasPiece:
                self.moves[(moveTile.x, moveTile.y)] = (moveTile.x, moveTile.y)
                if self.movesMade == 0:
                    moveTile = self.GUI.tiles[(self.x, self.y - 2)]
                    if not moveTile.hasPiece:
                        self.moves[(moveTile.x, moveTile.y)] = (moveTile.x, moveTile.y)

            # check left attack tile
            if self.x - 1 >= 0:
                attackTile = self.GUI.tiles[(self.x - 1, self.y - 1)]
                self.protects[(attackTile.x, attackTile.y)] = (attackTile.x, attackTile.y)
                if attackTile.hasPiece and attackTile.piece.color != self.color:
                    if attackTile.piece != 'king':
                        self.moves[(attackTile.x, attackTile.y)] = (attackTile.x, attackTile.y)
                    self.attacks[(attackTile.x, attackTile.y)] = (attackTile.x, attackTile.y)

            # check right attack tile
            if self.x + 1 < 8:
                attackTile2 = self.GUI.tiles[(self.x + 1, self.y - 1)]
                self.protects[(attackTile2.x, attackTile2.y)] = (attackTile2.x, attackTile2.y)
                if attackTile2.hasPiece and attackTile2.piece.color != self.color:
                    if attackTile2.piece != 'king':
                        self.moves[(attackTile2.x, attackTile2.y)] = (attackTile2.x, attackTile2.y)
                    self.attacks[(attackTile2.x, attackTile2.y)] = (attackTile2.x, attackTile2.y)

        # check for opposite side
        elif not self.orientation and self.y + 1 < 8:
            if self.GUI == None:
                self.moves[(self.x, self.y + 1)] = (self.x, self.y + 1)
                if self.movesMade == 0:
                    self.moves[(self.x, self.y + 2)] = (self.x, self.y + 2)
            else:
                # check forward tiles
                moveTile = self.GUI.tiles[(self.x, self.y + 1)]
                if not moveTile.hasPiece:
                    self.moves[(moveTile.x, moveTile.y)] = (moveTile.x, moveTile.y)
                    if self.movesMade == 0:
                        moveTile = self.GUI.tiles[(self.x, self.y + 2)]
                        if not moveTile.hasPiece:
                            self.moves[(moveTile.x, moveTile.y)] = (moveTile.x, moveTile.y)

                # check left attack tile
                if self.x - 1 >= 0:
                    attackTile = self.GUI.tiles[(self.x - 1, self.y + 1)]
                    self.protects[(attackTile.x, attackTile.y)] = (attackTile.x, attackTile.y)
                    if attackTile.hasPiece and attackTile.piece.color != self.color:
                        if attackTile.piece != 'king':
                            self.moves[(attackTile.x, attackTile.y)] = (attackTile.x, attackTile.y)
                        self.attacks[(attackTile.x, attackTile.y)] = (attackTile.x, attackTile.y)

                # check right attack tile
                if self.x + 1 < 8:
                    attackTile2 = self.GUI.tiles[(self.x + 1, self.y + 1)]
                    self.protects[(attackTile2.x, attackTile2.y)] = (attackTile2.x, attackTile2.y)
                    if attackTile2.hasPiece and attackTile2.piece.color != self.color:
                        if attackTile2.piece != 'king':
                            self.moves[(attackTile2.x, attackTile2.y)] = (attackTile2.x, attackTile2.y)
                        self.attacks[(attackTile2.x, attackTile2.y)] = (attackTile2.x, attackTile2.y)

    #get moves for a knight
    def getKnightMove(self):
        #left Up
        if self.y>0:
            if self.x>1:
                tile= self.GUI.tiles[(self.x - 2, self.y - 1)]
                self.knightHelper(tile)
        #right up
        if self.y>0:
            if self.x<6:
                tile= self.GUI.tiles[(self.x + 2, self.y - 1)]
                self.knightHelper(tile)

        # up left
        if self.y > 1:
            if self.x > 0:
                tile = self.GUI.tiles[(self.x - 1, self.y - 2)]
                self.knightHelper(tile)

        # up right
        if self.y > 1:
            if self.x < 7:
                tile = self.GUI.tiles[(self.x + 1, self.y - 2)]
                self.knightHelper(tile)

        # left down
        if self.y < 7:
            if self.x > 1:
                tile = self.GUI.tiles[(self.x - 2, self.y + 1)]
                self.knightHelper(tile)

        # right down
        if self.y < 7:
            if self.x < 6:
                tile = self.GUI.tiles[(self.x + 2, self.y + 1)]
                self.knightHelper(tile)

        # down left
        if self.y < 6:
            if self.x > 0:
                tile = self.GUI.tiles[(self.x - 1, self.y + 2)]
                self.knightHelper(tile)

        # down right
        if self.y < 6:
            if self.x < 7:
                tile = self.GUI.tiles[(self.x + 1, self.y + 2)]
                self.knightHelper(tile)

    def knightHelper(self, tile):
        self.protects[(tile.x, tile.y)] = (tile.x, tile.y)
        if not tile.hasPiece:
            self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
        elif tile.piece.color != self.color:
            if tile.piece.type != 'king':
                self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
            self.attacks[(tile.x, tile.y)] = (tile.x, tile.y)



    #get moves for a rook
    def getRookMove(self):
        #left
        blocked = False
        x=1
        while not blocked:
            if self.x-x<0:
                break
            tile = self.GUI.tiles[(self.x-x, self.y)]
            self.protects[(tile.x, tile.y)] = (tile.x, tile.y)
            if not tile.hasPiece:
                self.moves[(tile.x,tile.y)]=(tile.x,tile.y)
                x+=1
            else:
                if tile.piece.color != self.color:
                    if tile.piece.type != 'king':
                        self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                    self.attacks[(tile.x, tile.y)] = (tile.x, tile.y)
                blocked = True

        #up
        blocked = False
        y = 1
        while not blocked:
            if self.y-y<0:
                break
            tile = self.GUI.tiles[(self.x, self.y-y)]
            self.protects[(tile.x, tile.y)] = (tile.x, tile.y)
            if not tile.hasPiece:
                self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                y += 1

            else:
                if tile.piece.color != self.color:
                    if tile.piece.type != 'king':
                        self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                    self.attacks[(tile.x, tile.y)] = (tile.x, tile.y)
                blocked = True

        #right
        blocked = False
        x = 1
        while not blocked:
            if self.x+x>7:
                break
            tile = self.GUI.tiles[(self.x + x, self.y)]
            self.protects[(tile.x, tile.y)] = (tile.x, tile.y)
            if not tile.hasPiece:
                self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                x += 1
            else:
                if tile.piece.color != self.color:
                    if tile.piece.type != 'king':
                        self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                    self.attacks[(tile.x, tile.y)] = (tile.x, tile.y)
                blocked = True

        #down
        blocked = False
        y = 1
        while not blocked:
            if self.y+y>7:
                break
            tile = self.GUI.tiles[(self.x, self.y + y)]
            self.protects[(tile.x, tile.y)] = (tile.x, tile.y)
            if not tile.hasPiece:
                self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                y += 1
            else:
                if tile.piece.color!=self.color:
                    if tile.piece.type != 'king':
                        self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                    self.attacks[(tile.x, tile.y)] = (tile.x, tile.y)
                blocked = True

    #get moves for a bishop
    def getBishopMove(self):
        # up left
        blocked = False
        change = 1
        while not blocked:
            if self.x - change < 0 or self.y-change<0:
                break
            tile = self.GUI.tiles[(self.x - change, self.y-change)]
            self.protects[(tile.x, tile.y)] = (tile.x, tile.y)
            if not tile.hasPiece:
                self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                change+=1
            else:
                if tile.piece.color != self.color:
                    if tile.piece.type != 'king':
                        self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                    self.attacks[(tile.x, tile.y)] = (tile.x, tile.y)
                blocked = True

        # up right
        blocked = False
        change = 1
        while not blocked:
            if self.x + change > 7 or self.y - change < 0:
                break
            tile = self.GUI.tiles[(self.x + change, self.y - change)]
            self.protects[(tile.x, tile.y)] = (tile.x, tile.y)
            if not tile.hasPiece:
                self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                change += 1
            else:
                if tile.piece.color != self.color:
                    if tile.piece.type != 'king':
                        self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                    self.attacks[(tile.x, tile.y)] = (tile.x, tile.y)
                blocked = True


        # down left
        blocked = False
        change = 1
        while not blocked:
            if self.x - change < 0 or self.y + change > 7:
                break
            tile = self.GUI.tiles[(self.x - change, self.y + change)]
            self.protects[(tile.x, tile.y)] = (tile.x, tile.y)
            if not tile.hasPiece:
                self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                change += 1
            else:
                if tile.piece.color != self.color:
                    if tile.piece.type != 'king':
                        self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                    self.attacks[(tile.x, tile.y)] = (tile.x, tile.y)
                blocked = True


        # down right
        blocked = False
        change = 1
        while not blocked:
            if self.x + change > 7 or self.y + change > 7:
                break
            tile = self.GUI.tiles[(self.x + change, self.y + change)]
            self.protects[(tile.x, tile.y)] = (tile.x, tile.y)
            if not tile.hasPiece:
                self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                change += 1
            else:
                if tile.piece.color != self.color:
                    if tile.piece.type != 'king':
                        self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                    self.attacks[(tile.x, tile.y)] = (tile.x, tile.y)
                blocked = True

    #get moves for the queen
    def getQueenMove(self):
        self.getBishopMove()
        self.getRookMove()

    def getKingMove(self):
        leftAv = self.x-1>=0
        rightAv = self.x+1<8
        upAv = self.y-1>=0
        downAv = self.y+1<8
        #left
        if leftAv:
            tile = self.GUI.tiles[(self.x-1,self.y)]
            self.kingHelper(tile)
            #up left
            if upAv:
                tile = self.GUI.tiles[(self.x - 1, self.y-1)]
                self.kingHelper(tile)
            #down left
            if downAv:
                tile = self.GUI.tiles[(self.x - 1, self.y+1)]
                self.kingHelper(tile)

        #right
        if rightAv:
            tile = self.GUI.tiles[(self.x+1,self.y)]
            self.kingHelper(tile)
            #up left
            if upAv:
                tile = self.GUI.tiles[(self.x + 1, self.y-1)]
                self.kingHelper(tile)
            #down left
            if downAv:
                tile = self.GUI.tiles[(self.x + 1, self.y+1)]
                self.kingHelper(tile)
        #up
        if upAv:
            tile = self.GUI.tiles[(self.x,self.y-1)]
            self.kingHelper(tile)
        #down
        if downAv:
            tile = self.GUI.tiles[(self.x,self.y+1)]
            self.kingHelper(tile)


    def kingHelper(self, tile):
        if tile.hasPiece:
            if tile.piece.color != self.color and not tile.isControlled(self.color):
                self.moves[(tile.x, tile.y)] = (tile.x, tile.y)
                self.attacks[(tile.x, tile.y)] = (tile.x, tile.y)
        elif not tile.isControlled(self.color):
            self.moves[(tile.x, tile.y)] = (tile.x, tile.y)








