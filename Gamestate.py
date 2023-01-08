class gamestate:

    def __init__(self, orientation):
        self.GUI = None

        self.orientation = orientation
        self.turn='white'
        self.turnsTaken = 0

        self.checkmated = False

        self.checks = {}
        self.checks['white']=False
        self.checks['black']=False

        self.whiteKingTile = (4,7)
        self.blackKingTile = (4,0)
        if not orientation:
            self.whiteKingTile = (3, 0)
            self.blackKingTile = (3, 7)
        self.turnText = None
        self.yTurnText = None
        self.ycTurnText = None


    def getGUI(self,gui):
        self.GUI=gui
        self.turnText = self.GUI.font.render('Thinking...', True, (235, 10, 10))
        self.ycTurnText = self.GUI.font.render('Thinking...', True, (235, 10, 10))
        self.yTurnText = self.GUI.font.render('Your turn', True, (30, 190, 40))


    def zeroPlayerChangeTurn(self):
        if self.GUI.zeroPlayerTurn == 0:
            self.GUI.screen.fill((0, 0, 0), (self.GUI.tileSize * 8 + 40, 120, 500, 100))
            self.GUI.screen.fill((0, 0, 0), (self.GUI.tileSize * 8 + 40, self.GUI.height - 400, 500, 100))
            self.GUI.screen.blit(self.ycTurnText, (self.GUI.tileSize * 8 + 40, self.GUI.height -400))

        else:
            self.GUI.screen.fill((0, 0, 0), (self.GUI.tileSize * 8 + 40, self.GUI.height -400, 500, 100))
            self.GUI.screen.blit(self.turnText, (self.GUI.tileSize * 8 + 40, 120))


    def changeTurn(self):
        if self.turn=='white':
            self.turn='black'
            self.GUI.screen.fill((0, 0, 0), (self.GUI.tileSize * 8 + 40, self.GUI.height -400, 500, 100))
            self.GUI.screen.blit(self.turnText, (self.GUI.tileSize * 8 + 40, 120))

        elif self.turn==None:
            self.turn=None
        else:
            self.turn='white'
            self.GUI.screen.fill((0,0,0), (self.GUI.tileSize * 8 + 40, 120, 500,100))
            self.GUI.screen.blit(self.yTurnText, (self.GUI.tileSize * 8 + 40, self.GUI.height -400))



    def getPositionRating(self,color):
        tilesControlled = {}
        if color=='white':
            for piece in self.GUI.whitePieces:
                piece.getMoves()
                #add controlled squares of each move to dict so no unecessary copies
                tilesControlled.update(piece.protects)