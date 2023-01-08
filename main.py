from GUI import GUI
import pygame
import subprocess

def startProgram():
    SW_HIDE = 0
    SW_MINIMIZE = 6
    info = subprocess.STARTUPINFO()
    info.dwFlags = subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = SW_MINIMIZE
    subprocess.Popen('test.exe', startupinfo=info)



running = True
GUI = GUI()
for tile in GUI.tiles:
    GUI.tiles[tile].getGUI(GUI)
for piece in GUI.blackPieces:
    piece.getGUI(GUI)
for piece in GUI.whitePieces:
    piece.getGUI(GUI)

f = open("./move.txt","w")
f.write("")
f.close()
f2 = open("./turn.txt","w")
f2.write("0")
f2.close()
#startProgram()



GUI.update()
while running:
    GUI.update()
    if GUI.forceQuit:
        running = False
        pygame.quit()


