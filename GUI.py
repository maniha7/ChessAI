import pygame
import tkinter as tk
import CONSTANTS
import random
import numpy as np
from tile import Tile
from Piece import Piece
from Gamestate import gamestate
from AI import AI
import threading

sysInfo = tk.Tk()

class GUI:
    def __init__(self):
        # init display settings
        pygame.init()
        pygame.display.set_caption("Chess")
        self.width = sysInfo.winfo_screenwidth()
        self.height = sysInfo.winfo_screenheight()
        self.screen = pygame.display.set_mode((self.width, self.height))

        #white/black orientation and who is who
        self.zeroPlayer = False
        self.zeroPlayerTurn = 0
        self.orientation = random.randint(1,1)
        self.player = 'white'
        self.computer = 'black'
        if not self.orientation:
            self.player = 'black'
            self.computer='white'

        self.AI = None
        self.AIThread = None
        self.threadRunning = False
        self.AIPieceRes = None
        self.AIMoveRes = None
        self.analyzing=False
        self.speedTesting = False
        self.kc = 0
        self.nkc = 0
        self.freeze = False

        self.gamestate = gamestate(self.orientation)

        self.tileSize = (self.height-1)//8
        self.tiles = {}
        self.initBoard()
        self.highlightedTile = None

        self.blackPieces = {}
        self.whitePieces = {}

        #sort-optimized pieceList for C
        self.cPieces = [None] * 32

        self.initPieces(self.orientation)

        #score
        self.computerScore = 0
        self.playerScore = 0

        self.forceQuit = False

        pygame.font.init()
        self.font = pygame.font.SysFont('sourcecodeproblack', 30)
        self.gamestate.getGUI(self)
        computerScoreText = self.font.render('Black: '+str(self.computerScore), True, (255, 255, 255))
        playerScoreText = self.font.render('White: ' + str(self.playerScore), True, (255, 255, 255))
        self.screen.blit(computerScoreText, (self.tileSize*8+40, 30))
        self.screen.blit(playerScoreText, (self.tileSize*8 + 40, self.height//2+30))
        self.screen.blit(self.gamestate.yTurnText, (self.tileSize * 8 + 40, self.height - 400))


    def resetGame(self):
        #reset current mid-move
        if self.highlightedTile!=None:
            self.highlightedTile.unhighlight((self.highlightedTile.x,self.highlightedTile.y))
            self.highlightedTile=None

        #reset graphics
        self.screen.fill((0,0,0))
        self.update()

        #reset orientation and players
        self.player = 'white'
        self.computer = 'black'
        if not self.orientation:
            self.player = 'black'
            self.computer = 'white'

        #reset gamestate
        self.gamestate = gamestate(self.orientation)


        #reset AI
        self.AI = None

        #reset board
        self.tiles = {}
        self.initBoard()
        self.highlightedTile = None

        #reset pieces
        self.blackPieces = {}
        self.whitePieces = {}
        self.cPieces = [None] * 32
        self.initPieces(self.orientation)

        #reset AI files
        f = open("./move.txt", "w")
        f.write("")
        f.close()
        f2 = open("./turn.txt", "w")
        f2.write("0")
        f2.close()

        self.gamestate.getGUI(self)
        #reset score text (maintain scores though)
        computerScoreText = self.font.render('Black: ' + str(self.computerScore), True, (255, 255, 255))
        playerScoreText = self.font.render('White: ' + str(self.playerScore), True, (255, 255, 255))
        self.screen.blit(computerScoreText, (self.tileSize * 8 + 40, 30))
        self.screen.blit(playerScoreText, (self.tileSize * 8 + 40, self.height // 2 + 30))
        self.screen.blit(self.gamestate.yTurnText, (self.tileSize * 8 + 40, self.height - 400))


    def zeroPlayerHandleCheckmate(self, winner):
        if winner=="white":
            self.playerScore+=1
        else:
            self.computerScore+=1
        self.gamestate.turn = None
        self.zeroPlayerTurn = -1

        # overwrite old score text by replacing with backgroundcolor
        pygame.draw.rect(self.screen, (0, 0, 0), (self.tileSize * 8, 0, self.width - self.tileSize * 8, self.height))

        #draw checkmate text & update score
        checkMateText = self.font.render('Checkmate! Press r to play again.', True, (255, 255, 255))
        computerScoreText = self.font.render('Black: ' + str(self.computerScore), True, (255, 255, 255))
        playerScoreText = self.font.render('White: ' + str(self.playerScore), True, (255, 255, 255))
        self.screen.blit(checkMateText, (self.tileSize * 8 + 40, self.height - 100))
        self.screen.blit(computerScoreText, (self.tileSize * 8 + 40, 30))
        self.screen.blit(playerScoreText, (self.tileSize * 8 + 40, self.height // 2 + 30))


    def handleCheckmate(self):
        #inc score and end all turns
        if self.gamestate.turn==self.player:
            self.playerScore+=1
        else:
            self.computerScore+=1
        self.gamestate.turn = None

        # overwrite old score text by replacing with backgroundcolor
        pygame.draw.rect(self.screen, (0, 0, 0), (self.tileSize * 8, 0, self.width - self.tileSize * 8, self.height))
        self.update()

        #draw checkmate text & update score
        checkMateText = self.font.render('Checkmate! Press r to play again.', True, (255, 255, 255))
        computerScoreText = self.font.render('Black: ' + str(self.computerScore), True, (255, 255, 255))
        playerScoreText = self.font.render('White: ' + str(self.playerScore), True, (255, 255, 255))
        self.screen.blit(checkMateText, (self.tileSize * 8 + 40, self.height - 100))
        self.screen.blit(computerScoreText, (self.tileSize * 8 + 40, 30))
        self.screen.blit(playerScoreText, (self.tileSize * 8 + 40, self.height // 2 + 30))

    #generate omnipiece for controlled tile testing
    def makeOmni(self,x,y, color):
        return Piece(x, y, 'omni', self.orientation, color, None)


    def highlight(self,pos, allowMove = True):
        p1 = pos[0]//self.tileSize
        p2 = pos[1]//self.tileSize
        if(not allowMove):
            p1 = pos[0]
            p2 = pos[1]
        if p1<8 and p2<8 and p1>-1 and p2>-2:
            if self.highlightedTile!=None:
                self.highlightedTile.unhighlight((p1,p2), allowMove=allowMove)
                self.highlightedTile=None

            tile = self.tiles[(p1,p2)]

            highlighted = tile.highlight()
            if highlighted:
                self.highlightedTile = tile


    # blank pixel setup
    def initBoard(self):
        for x in range(8):
            for y in range(8):
                color=(173, 119, 47)
                if (x%2==0 and y%2==0) or (x%2!=0 and y%2!=0):
                    color=(214, 182, 139)
                tile = Tile(x, y, self.screen)
                tile.draw(color)
                self.tiles[(x,y)]=tile

    #inits pieces. Orientation = true has white on bottom, false has black on bottom.
    def initPieces(self, orientation):
        blackBackRank = 0
        whiteBackRank = 7
        blackPawnRank = 1
        whitePawnRank = 6
        blackQueen = 3
        blackKing = 4
        whiteQueen = 3
        whiteKing = 4

        if not orientation:
            blackBackRank = whiteBackRank
            whiteBackRank = 0
            blackPawnRank = whitePawnRank
            whitePawnRank = 1
            blackQueen = 4
            blackKing = 3
            whiteQueen = 4
            whiteKing = 3

        #init black pawns
        for x in range(8):
            square = self.tiles[(x,blackPawnRank)]
            pieceImg = CONSTANTS.blackPieces['pawn']
            pieceImg = pygame.transform.scale(pieceImg,(self.tileSize,self.tileSize))
            self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
            piece = Piece(x, blackPawnRank, 'pawn',not orientation, 'black', pieceImg)
            self.cPieces[16+x] = piece
            self.blackPieces[piece]=piece
            self.tiles[x, blackPawnRank].getPiece(piece)

        #init black rooks
        pieceImg = CONSTANTS.blackPieces['rook']
        pieceImg = pygame.transform.scale(pieceImg, (self.tileSize, self.tileSize))
        square = self.tiles[(0,blackBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        square = self.tiles[(7, blackBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        #L
        piece = Piece(0, blackBackRank, 'rook',not orientation, 'black', pieceImg)
        self.cPieces[24] = piece
        self.blackPieces[piece] = piece
        self.tiles[0, blackBackRank].getPiece(piece)
        #R
        piece = Piece(7, blackBackRank, 'rook',not orientation, 'black', pieceImg)
        self.cPieces[31] = piece
        self.blackPieces[piece] = piece
        self.tiles[7, blackBackRank].getPiece(piece)

        #init black Knights
        pieceImg = CONSTANTS.blackPieces['knight']
        pieceImg = pygame.transform.scale(pieceImg, (self.tileSize, self.tileSize))
        square = self.tiles[(1, blackBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        square = self.tiles[(6, blackBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        #L
        piece = Piece(1, blackBackRank, 'knight',not orientation, 'black', pieceImg)
        self.cPieces[25] = piece
        self.blackPieces[piece] = piece
        self.tiles[1, blackBackRank].getPiece(piece)
        #R
        piece = Piece(6, blackBackRank, 'knight',not orientation, 'black', pieceImg)
        self.cPieces[30] = piece
        self.blackPieces[piece] = piece
        self.tiles[6, blackBackRank].getPiece(piece)

        # init black Bishops
        pieceImg = CONSTANTS.blackPieces['bishop']
        pieceImg = pygame.transform.scale(pieceImg, (self.tileSize, self.tileSize))
        square = self.tiles[(2, blackBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        square = self.tiles[(5, blackBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        #L
        piece = Piece(2, blackBackRank, 'bishop',not orientation, 'black', pieceImg)
        self.cPieces[26] = piece
        self.blackPieces[piece] = piece
        self.tiles[2, blackBackRank].getPiece(piece)
        #R
        piece = Piece(5, blackBackRank, 'bishop',not orientation, 'black', pieceImg)
        self.cPieces[29] = piece
        self.blackPieces[piece] = piece
        self.tiles[5, blackBackRank].getPiece(piece)

        # init black Queen
        pieceImg = CONSTANTS.blackPieces['queen']
        pieceImg = pygame.transform.scale(pieceImg, (self.tileSize, self.tileSize))
        square = self.tiles[(blackQueen, blackBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        piece = Piece(blackQueen, blackBackRank, 'queen',not orientation, 'black', pieceImg)
        self.cPieces[27] = piece
        self.blackPieces[piece] = piece
        self.tiles[blackQueen, blackBackRank].getPiece(piece)

        # init black King
        pieceImg = CONSTANTS.blackPieces['king']
        pieceImg = pygame.transform.scale(pieceImg, (self.tileSize, self.tileSize))
        square = self.tiles[(blackKing, blackBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        piece = Piece(blackKing, blackBackRank, 'king',not orientation, 'black', pieceImg)
        self.cPieces[28] = piece
        self.blackPieces[piece] = piece
        self.tiles[blackKing, blackBackRank].getPiece(piece)

        #WHITE PIECES

        # init white pawns
        for x in range(8):
            square = self.tiles[(x, whitePawnRank)]
            pieceImg = CONSTANTS.whitePieces['pawn']
            pieceImg = pygame.transform.scale(pieceImg, (self.tileSize, self.tileSize))
            self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
            piece = Piece(x, whitePawnRank, 'pawn', orientation, 'white', pieceImg)
            self.whitePieces[piece] = piece
            self.tiles[x,whitePawnRank].getPiece(piece)
            self.cPieces[8+x]=piece

        # init white rooks
        pieceImg = CONSTANTS.whitePieces['rook']
        pieceImg = pygame.transform.scale(pieceImg, (self.tileSize, self.tileSize))
        square = self.tiles[(0, whiteBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        square = self.tiles[(7, whiteBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        #L
        piece = Piece(0, whiteBackRank, 'rook', orientation, 'white', pieceImg)
        self.cPieces[0] = piece
        self.whitePieces[piece] = piece
        self.tiles[0, whiteBackRank].getPiece(piece)
        #R
        piece = Piece(7, whiteBackRank, 'rook', orientation, 'white', pieceImg)
        self.cPieces[7] = piece
        self.whitePieces[piece] = piece
        self.tiles[7, whiteBackRank].getPiece(piece)


        # init white Knights
        pieceImg = CONSTANTS.whitePieces['knight']
        pieceImg = pygame.transform.scale(pieceImg, (self.tileSize, self.tileSize))
        square = self.tiles[(1, whiteBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        square = self.tiles[(6, whiteBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        #L
        piece = Piece(1, whiteBackRank, 'knight', orientation, 'white', pieceImg)
        self.cPieces[1] = piece
        self.whitePieces[piece] = piece
        self.tiles[1, whiteBackRank].getPiece(piece)
        #R
        piece = Piece(6, whiteBackRank, 'knight', orientation, 'white', pieceImg)
        self.cPieces[6] = piece
        self.whitePieces[piece] = piece
        self.tiles[6, whiteBackRank].getPiece(piece)

        # init white Bishops
        pieceImg = CONSTANTS.whitePieces['bishop']
        pieceImg = pygame.transform.scale(pieceImg, (self.tileSize, self.tileSize))
        square = self.tiles[(2, whiteBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        square = self.tiles[(5, whiteBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        #L
        piece = Piece(2, whiteBackRank, 'bishop', orientation, 'white', pieceImg)
        self.cPieces[2] = piece
        self.whitePieces[piece] = piece
        self.tiles[2, whiteBackRank].getPiece(piece)
        #R
        piece = Piece(5, whiteBackRank, 'bishop', orientation, 'white', pieceImg)
        self.cPieces[5] = piece
        self.whitePieces[piece] = piece
        self.tiles[5, whiteBackRank].getPiece(piece)

        # init white Queen
        pieceImg = CONSTANTS.whitePieces['queen']
        pieceImg = pygame.transform.scale(pieceImg, (self.tileSize, self.tileSize))
        square = self.tiles[(whiteQueen, whiteBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        piece = Piece(whiteQueen, whiteBackRank, 'queen', orientation, 'white', pieceImg)
        self.cPieces[3] = piece
        self.whitePieces[piece] = piece
        self.tiles[whiteQueen, whiteBackRank].getPiece(piece)

        # init white King
        pieceImg = CONSTANTS.whitePieces['king']
        pieceImg = pygame.transform.scale(pieceImg, (self.tileSize, self.tileSize))
        square = self.tiles[(whiteKing, whiteBackRank)]
        self.screen.blit(pieceImg,(square.scaledX,square.scaledY))
        piece = Piece(whiteKing, whiteBackRank, 'king', orientation, 'white', pieceImg)
        self.cPieces[4] = piece
        self.whitePieces[piece] = piece
        self.tiles[whiteKing, whiteBackRank].getPiece(piece)



    # return current keyboard/mouse input
    def getEvent(self):
        return pygame.event.get()

    # update display
    def update(self):
        if self.gamestate.turn==self.computer and not self.analyzing and not self.zeroPlayer:
            self.analyzing = True
            #init AI on first turn
            if self.AI is None:
                self.AI = AI(self.screen,self,self.computer)
                self.AIThread = threading.Thread(target=self.AI.cCheckMoves, args=())
            if not self.threadRunning:
                self.threadRunning = True
                self.AIThread.start()
        #new input from C AI: do move in python
        elif self.AIPieceRes is not None and self.AIMoveRes is not None:
            self.AIPieceRes.AIMove(self.AIMoveRes, self.screen)
            if not self.zeroPlayer or (self.zeroPlayer and self.zeroPlayerTurn!=-1):
                self.AIPieceRes.getMoves()
            self.AIPieceRes = None
            self.AIMoveRes = None
            if self.AIPieceRes == -1:
                self.analyzing = False

            if self.zeroPlayer and self.zeroPlayerTurn!=-1:
                self.zeroPlayerTurn = 1 - self.zeroPlayerTurn
                self.gamestate.zeroPlayerChangeTurn()



        #pygame update handling
        pygame.display.flip()
        for event in self.getEvent():
            # Close button control
            if event.type == pygame.QUIT:
                self.forceQuit = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.forceQuit = True
                if event.key == pygame.K_SPACE and self.zeroPlayer==True and self.threadRunning:
                    self.analyzing = not self.analyzing

                if event.key == pygame.K_a and self.gamestate.turnsTaken==0 and self.AI is None:

                    self.AI = AI(self.screen, self, self.computer)
                    self.AIThread = threading.Thread(target=self.AI.AIvAI, args=())
                    if not self.threadRunning:

                        self.analyzing = True
                        self.zeroPlayer = True
                        self.zeroPlayerTurn = 0
                        self.gamestate.zeroPlayerChangeTurn()
                        self.threadRunning = True
                        self.AIThread.start()
                if event.key == pygame.K_r:
                    self.resetGame()
                    for tile in self.tiles:
                        self.tiles[tile].getGUI(self)
                    for piece in self.blackPieces:
                        piece.getGUI(self)
                    for piece in self.whitePieces:
                        piece.getGUI(self)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                self.highlight((pos[0], pos[1]))