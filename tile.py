import pygame
import tkinter as tk
import CONSTANTS


sysInfo = tk.Tk()

class Tile:
    def __init__(self,x,y,screen):
        self.tileSize = (sysInfo.winfo_screenheight() - 1) // 8
        self.screen=screen
        self.x=x
        self.y=y
        self.scaledX =x * self.tileSize
        self.scaledY =y * self.tileSize

        self.hasPiece = False
        self.piece = None

        self.color = None
        self.isHighlighted = False
        self.GUI = None

        #only updated / used by AI
        self.controlled = False


    #return true if square is attacked by enemy
    def isControlled(self, color, checker="all"):
        #piece that can move in any direction (basically queen+knight) to look for attacking pieces directly
        OMNIPIECE = self.GUI.makeOmni(self.x,self.y,color)
        OMNIPIECE.getGUI(self.GUI,omni=True)
        if checker=="rq":
            # Search for attacking rook/queen
            OMNIPIECE.attacks = {}
            OMNIPIECE.getRookMove()
            for attack in OMNIPIECE.attacks:
                attackerTile = self.GUI.tiles[attack]
                if attackerTile.piece.type == 'rook' or attackerTile.piece.type == 'queen':
                    return True
        elif checker=="bq":
            # else search for attacking bishop/queen
            OMNIPIECE.attacks = {}
            OMNIPIECE.getBishopMove()
            for attack in OMNIPIECE.attacks:
                attackerTile = self.GUI.tiles[attack]
                if attackerTile.piece.type == 'bishop' or attackerTile.piece.type == 'queen':
                    return True

        #check all possible checks
        elif checker=="all":
            #Search for attacking rook/queen
            OMNIPIECE.attacks = {}
            OMNIPIECE.getRookMove()
            for attack in OMNIPIECE.attacks:
                attackerTile = self.GUI.tiles[attack]
                if attackerTile.piece.type=='rook' or attackerTile.piece.type=='queen':
                    return True

            #else search for attacking bishop/queen
            OMNIPIECE.attacks={}
            OMNIPIECE.getBishopMove()
            for attack in OMNIPIECE.attacks:
                attackerTile = self.GUI.tiles[attack]
                if attackerTile.piece.type=='bishop' or attackerTile.piece.type=='queen':
                    return True

            #else search for attacking knight
            OMNIPIECE.attacks = {}
            OMNIPIECE.getKnightMove()
            for attack in OMNIPIECE.attacks:
                attackerTile = self.GUI.tiles[attack]
                if attackerTile.piece.type == 'knight':
                    return True

            #else search for attacking pawn..
            bot = 'white'
            if not self.GUI.orientation:
                bot='black'
            if color==bot:
                if self.x-1>=0 and self.y-1>=0:
                    tile = self.GUI.tiles[(self.x-1,self.y-1)]
                    if tile.hasPiece and tile.piece.color!=color and tile.piece.type=='pawn':
                        return True
                if self.x+1<8 and self.y-1>=0:
                    tile = self.GUI.tiles[(self.x+1,self.y-1)]
                    if tile.hasPiece and tile.piece.color!=color and tile.piece.type=='pawn':
                        return True
            else:
                if self.x-1>=0 and self.y+1<8:
                    tile = self.GUI.tiles[(self.x-1,self.y+1)]
                    if tile.hasPiece and tile.piece.color!=color and tile.piece.type=='pawn':
                        return True
                if self.x+1<8 and self.y+1<8:
                    tile = self.GUI.tiles[(self.x+1,self.y+1)]
                    if tile.hasPiece and tile.piece.color!=color and tile.piece.type=='pawn':
                        return True

            #else search for attacking king
            if color=='black':
                if abs(self.GUI.gamestate.whiteKingTile[0]-self.x)<=1 and abs(self.GUI.gamestate.whiteKingTile[1]-self.y)<=1:
                    return True
            else:
                if abs(self.GUI.gamestate.blackKingTile[0]-self.x)<=1 and abs(self.GUI.gamestate.blackKingTile[1]-self.y)<=1:
                    return True



    #get GUI
    def getGUI(self,GUI):
        self.GUI=GUI

    #draw tile to screen
    def draw(self,color):
        self.color = color
        pygame.draw.rect(self.screen, color,(self.scaledX, self.scaledY, self.tileSize, self.tileSize))

    #highlight tile (when clicked)
    def highlight(self):
        if self.hasPiece:
            hColor = self.color[0] + 40
            self.draw((hColor, self.color[1], self.color[2]))
            #redraw piece
            self.isHighlighted = True
            self.screen.blit(self.piece.image, (self.scaledX, self.scaledY))
            return True
        return False

    #unhighlight tile and move piece to tile if available move
    def unhighlight(self, newpos, allowMove=True):
        hColor = self.color[0] - 40
        self.draw((hColor, self.color[1], self.color[2]))
        self.isHighlighted = False

        #make sure it is correct turn before moving piece
        if self.GUI.gamestate.turn==self.piece.color and allowMove:

            #make sure piece is not moving to the same square
            if newpos!=(self.x,self.y):
                self.piece.getMoves()
                moved = self.piece.move(newpos,self.screen)
                if not moved:

                    self.screen.blit(self.piece.image, (self.scaledX, self.scaledY))
                else:
                    self.GUI.gamestate.changeTurn()
            #keep pieces drawn if move is cancelled
            else:
                self.screen.blit(self.piece.image, (self.scaledX, self.scaledY))
        else:
            self.screen.blit(self.piece.image, (self.scaledX, self.scaledY))

    #give this tile a piece
    def getPiece(self,piece):
        self.hasPiece=True
        self.piece=piece


    #remove this tiles association with the piece on it.
    def losePiece(self,redraw=True):
        if redraw==True:
            self.draw(self.color)
        self.hasPiece=False
        self.piece=None

    def blankDraw(self):
        self.draw(self.color)
