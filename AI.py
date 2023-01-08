import time
import pygame
import numpy as np
import threading
import CONSTANTS

class AI:
    def __init__(self,screen,GUI,color):

        self.bestMove = None
        self.GUI = GUI
        self.screen = screen

        #depth control
        self.currentDepth = 0
        self.maxDepth = 4

        #speed testing
        self.tested = 0
        self.t1 = 0

        #c info
        self.wtypes = {}
        self.btypes = {}
        self.initCInfo()

        #to restore board positions after move tests
        self.currentTiles = GUI.tiles.copy()
        self.currentWhitePieces = GUI.whitePieces.copy()
        self.currentBlackPieces = GUI.blackPieces.copy()
        self.currentGamestate = self.GUI.gamestate


        self.worstScore = -100000000
        self.bestMoveScore = self.worstScore

        #self and enemy pieces / color
        self.color = color
        self.peices=GUI.blackPieces
        self.enemyPieces = GUI.whitePieces
        if color=='white':
            self.pieces = GUI.whitePieces
            self.enemyPieces = GUI.blackPieces

    def initCInfo(self):
        self.wtypes["pawn"] = 1
        self.wtypes["rook"] = 2
        self.wtypes["knight"] = 3
        self.wtypes["bishop"] = 4
        self.wtypes["queen"] = 5
        self.wtypes["king"] = 6

        self.btypes["pawn"] = 11
        self.btypes["rook"] = 12
        self.btypes["knight"] = 13
        self.btypes["bishop"] = 14
        self.btypes["queen"] = 15
        self.btypes["king"] = 16


    def getCGamestate(self):
        pieceData = np.zeros((32, 6), dtype=np.int32)
        for i in range(32):
            piece = self.GUI.cPieces[i]

            alive = 0
            if piece.isAlive():
                alive = 1

            ptype = 0
            if i<=15:
                ptype = self.wtypes[piece.type]
            else:
                ptype = self.btypes[piece.type]
            data = [piece.x, piece.y, alive, piece.movesMade, ptype, i]
            pieceData[i] = np.array(data, dtype=np.int32)
        return pieceData


    def AIvAI(self):

        pieceData = self.getCGamestate()
        gameString = ""
        for i in range(32):
            for j in range(6):
                gameString += str(pieceData[i][j]) + " "
        f = open("./gamestate.txt", "w")
        f.write(gameString)
        f.close()


        while not self.GUI.forceQuit and self.GUI.gamestate.turn is not None:
            if self.GUI.analyzing:
                f2 = open("./turn.txt", "w")
                f2.write("1")
                f2.close()
                wait = True
                extraWait = True
                while wait:
                    if extraWait:
                        time.sleep(1.5)
                        extraWait = False
                    else:
                        time.sleep(.2)
                    wFile = open("./turn.txt", "r")
                    if wFile.read() == "0":
                        wait = False
                    wFile.close()
                # read C move from txt
                mFile = open("./move.txt", "r")
                res = mFile.read()
                mFile.close()
                arr = res.split()
                piece = self.GUI.cPieces[int(arr[0])]
                move = int(arr[1])
                if move == -1:
                    self.GUI.analyzing = False
                else:

                    if move > 900:
                        move = move - 900
                        print("******PROMOTION")
                        piece.type = "queen"
                        if piece.color == "white":
                            pieceImg = CONSTANTS.whitePieces['queen']
                            pieceImg = pygame.transform.scale(pieceImg, (piece.tileSize, piece.tileSize))
                            piece.image = pieceImg
                        else:
                            pieceImg = CONSTANTS.blackPieces['queen']
                            pieceImg = pygame.transform.scale(pieceImg, (piece.tileSize, piece.tileSize))
                            piece.image = pieceImg
                    y = move % 10
                    x = (move - y) // 10
                    print(piece.type)
                    print(move)
                    if x == piece.x and y == piece.y:
                        print("MAJOR ERROR")
                    else:
                        self.GUI.AIPieceRes = piece
                        self.GUI.AIMoveRes = (x, y)




    def cCheckMoves(self):
        #run infinitely as thread?
        while not self.GUI.forceQuit:
            if self.GUI.gamestate.turn==self.GUI.computer and self.GUI.analyzing:
                pieceData = self.getCGamestate()
                gameString = ""
                for i in range(32):
                    for j in range(6):
                        gameString+=str(pieceData[i][j])+" "
                f = open("./gamestate.txt", "w")
                f.write(gameString)
                f.close()
                f2 = open("./turn.txt","w")
                f2.write("1")
                f2.close()

                wait = True
                extrawait=True
                while wait:
                    if extrawait:
                        for i in range(1):
                            time.sleep(1)

                        extrawait=False
                    else:
                        time.sleep(.2)
                    tFile = open("./turn.txt", "r")
                    if tFile.read() == "0":
                        wait = False
                    tFile.close()

                #read C move from txt
                mFile = open("./move.txt","r")
                res = mFile.read()
                mFile.close()
                arr = res.split()
                piece = self.GUI.cPieces[int(arr[0])]
                move = int(arr[1])
                if move == -1:
                    self.GUI.analyzing = False
                    self.GUI.gamestate.changeTurn()
                    self.GUI.handleCheckmate()
                else:

                    if move >900:
                        move = move-900
                        print("******PROMOTION")
                        piece.type="queen"
                        if piece.color=="white":
                            pieceImg = CONSTANTS.whitePieces['queen']
                            pieceImg = pygame.transform.scale(pieceImg, (piece.tileSize, piece.tileSize))
                            piece.image = pieceImg
                        else:
                            pieceImg = CONSTANTS.blackPieces['queen']
                            pieceImg = pygame.transform.scale(pieceImg, (piece.tileSize, piece.tileSize))
                            piece.image = pieceImg
                    y = move % 10
                    x = (move - y) // 10
                    print(piece.type)
                    print(move)
                    if x==piece.x and y==piece.y:
                        print("MAJOR ERROR")
                    else:
                        self.GUI.AIPieceRes = piece
                        self.GUI.AIMoveRes = (x,y)
                        self.GUI.analyzing = False
                        self.GUI.gamestate.changeTurn()




    def checkMoves(self, color, depth, move=None):
        if self.tested == 0:
            self.GUI.speedTesting = True
            self.t1 = time.perf_counter()
        if color == 'white':
            nextColor = 'black'
        else:
            nextColor = 'white'
        #base case: return first move in highest rated sequence
        if depth==self.maxDepth:
            #reset board to actual position
            return move

        else:
            self.tested+=1
            if self.tested == 600:
                print(time.perf_counter() - self.t1)
                self.GUI.speedTesting=False
                for piece in self.GUI.whitePieces:
                    piece.draw(self.GUI.screen)
                for piece in self.GUI.blackPieces:
                    piece.draw(self.GUI.screen)

            firstMove = move

            #get dict of pieces for player of current move
            curPieces = self.GUI.whitePieces if color=='white' else self.GUI.blackPieces

            #for each piece, gets its moves, then for each move, make that move and recursively simulate a response from the opponent
            for piece in curPieces.copy():
                if piece.isAlive():
                    piece.getMoves()

                    for pmove in piece.moves:

                        #piece.move returns [original piece x, original piece y, piece taken by this move || None], store to undo move
                        res = piece.AIMove(pmove, self.screen)
                        if res!=False:
                            if not self.GUI.speedTesting:
                                #self.screen.blit(piece.image, (pmove[0]*piece.tileSize, pmove[1]*piece.tileSize))
                                pygame.display.flip()
                            #time.sleep(.3)
                            #recursively check deeper moves
                            self.checkMoves(nextColor,depth+1,move=firstMove)
                            #unmake move after recursion is complete
                            piece.returnMove((piece.x,piece.y), (res[0],res[1]), res[2], res[3],res[4], draw = not self.GUI.speedTesting)




    def analyzeMove(self):
        pass

