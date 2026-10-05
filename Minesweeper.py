import tkinter as tk
from tkinter import ttk, messagebox

from random import *

#CONSTANTS
NumColour = {0: "#B3B6B7",
             1: "#00A419",
             2: "#22C8B9",
             3: "#0077FE",
             4: "#0023A4",
             5: "#7829BF",
             6: "#DC20EC",
             7: "#FEC800",
             8: "#FE0800"}
RevealMode = 0
FlagMode = 1

TileUnknown = 0
TileFlagged = 1
TileUncovered = 2

UI_font = ('Menlo',12)

MinGridSize = 5
MaxGridSizeX = 30
MaxGridSizeY = 25

#CLASSES
class Board:
    def __init__(self,x,y,count):
        self.SizeX = x
        self.SizeY = y
        self.FlagCount = count
        self.MineCount = count
        self.Remaining = x * y
        self.Tiles = []

        for i in range(y):
            self.Tiles.append([])
            for j in range(x):
                self.Tiles[i].append(Tile(j,i,self))



        window.grid_columnconfigure(2, minsize=25)
        window.grid_columnconfigure(x+3, minsize=25)


        label = tk.Label(window,text="Row: ",font = UI_font)
        label.grid(sticky = tk.W, row = 0, column = 0)
        label = tk.Label(window,text="Col: ",font = UI_font)
        label.grid(sticky = tk.W, row = 1, column = 0)
        label = tk.Label(window,text="Mines: ",font = UI_font)
        label.grid(sticky = tk.W, row = 2, column = 0)

        self.ny = tk.IntVar();
        self.YValue = ttk.Spinbox(window, from_ = MinGridSize, to = MaxGridSizeY, width=8, state="readonly", textvariable=self.ny)
        self.YValue.grid(sticky = "nsew", row = 0, column = 1)
        self.YValue.set(y)

        self.nx = tk.IntVar();
        self.XValue = ttk.Spinbox(window, from_ = MinGridSize, to = MaxGridSizeX, width=8, state="readonly", textvariable=self.nx) 
        self.XValue.grid(sticky = "nsew", row = 1, column = 1)
        self.XValue.set(x)

        self.nx.trace_add("write", self.OnNewXY)
        self.ny.trace_add("write", self.OnNewXY)

        self.nm = tk.IntVar();
        self.MineValue = ttk.Spinbox(window, from_ = 1, to = x*y-9, width=8, state="readonly", textvariable=self.nm)
        self.MineValue.grid(sticky = "nsew", row = 2, column = 1)
        self.MineValue.set(count)

        self.ResizeBtn = tk.Button(window,text="Resize",font = UI_font, width=8, command=self.Resize)
        self.ResizeBtn.grid(sticky = "nsew", row = 3, column = 1)
        

        
        self.Mode = tk.Button(window,text="Reveal ?",fg="#2E70BE",font = UI_font,command = self.SetMode,width=10)
        self.Mode.grid(sticky = tk.W, row = 0, column = x + 4)
        self.Mode["state"] = "disabled"


        self.Counter = tk.Label(window,text="⚑ "+str(count),font = UI_font)
        self.Counter.grid(sticky = tk.W, row = 1, column = x + 4)


        self.Click = 0
        self.ClickCounter = tk.Label(window,text="Clicks: 0",font = UI_font)
        self.ClickCounter.grid(sticky = tk.W, row = 2, column = x + 4)

        self.Message = None
        self.Done = None
        
        danger = sample(range(0,x * y), count)
        for i in danger:
            self.Tiles[i // x][i % x].Safe = False
        self.PrintMap()


    def EndGame(self,result):
        for y in range(self.SizeY):
            for x in range(self.SizeX):
                self.Tiles[y][x].Button["state"] = "disabled"
        self.Mode["state"] = "disabled"
        if result:
            self.Message = tk.Label(window,text="You win!",font = UI_font,foreground = "green")
        else:
            self.Message = tk.Label(window,text="You lose!",font = UI_font,foreground = "red")
        self.Message.grid(row = 3, column = self.SizeX + 4)
        self.Done = tk.Button(window,text="Close",font = UI_font,command=DeleteWindow)
        self.Done.grid(row = 4, column = self.SizeX + 4)
        self.ResizeBtn["text"] = "Restart"
            

    def OnNewXY(self, *args):
        try:
            nx = int(self.nx.get())
            ny = int(self.ny.get())
            self.MineValue.configure(to = nx * ny - 9)
            try:
                nm = int(self.nm.get())
                if (nm > nx * ny - 9):
                    self.nm.set(nx * ny - 9)
            except:
                tk.messagebox.showerror(title="Value Error", message="Positive integer inputs only!")
        except:
            tk.messagebox.showerror(title="Value Error", message="Positive integer inputs only!")
        

    def Resize(self):
        try:
            nx = int(self.nx.get())
            ny = int(self.ny.get())
            nm = int(self.nm.get())
            if self.Message == None:
                proceed = tk.messagebox.askokcancel("Resize", "You will lose all current progress.")
                if not proceed:
                    return;
            for y in range(self.SizeY):
                for x in range(self.SizeX):
                    self.Tiles[y][x].Destruct()
            self.Tiles.clear()

            window.grid_columnconfigure(self.SizeX+3, minsize=0)
            window.grid_columnconfigure(nx+3, minsize=25)    
            
            self.SizeX = nx
            self.SizeY = ny
            self.FlagCount = nm
            self.MineCount = nm
            self.Remaining = nx * ny

            for y in range(ny):
                self.Tiles.append([])
                for x in range(nx):
                    self.Tiles[y].append(Tile(x,y,self))

            self.ResizeBtn["text"] = "Resize"

            self.Mode.grid(sticky = tk.W, row = 0, column = nx + 4)
            self.Mode["text"] = "Reveal ?"
            self.Mode["state"] = "disabled"

            self.Counter.grid(sticky = tk.W, row = 1, column = nx + 4)
            self.Counter["text"] = "⚑ " + str(self.FlagCount)

            self.Click = 0
            self.ClickCounter["text"] = "Clicks: 0"
            self.ClickCounter.grid(sticky = tk.W, row = 2, column = nx + 4)
        
            if self.Message != None:
                self.Message.destroy()
                self.Message = None
            if self.Done != None:
                self.Done.destroy()
                self.Done = None

            danger = sample(range(0,nx * ny), nm)
            for i in danger:
                self.Tiles[i // nx][i % nx].Safe = False
            self.PrintMap()
            
            ResizeWindow()
        except:
            tk.messagebox.showerror(title="Value Error", message="Positive integer inputs only!")
        

    def GetMode(self):
        if self.Mode["text"] == "Flag ⚑":
            return FlagMode
        else:
            return RevealMode

    def SetMode(self):
        if self.Mode["text"] == "Flag ⚑":
            self.Mode["text"] = "Reveal ?"
            self.Mode["fg"] ="#2E70BE"
        else:
            self.Mode["text"] = "Flag ⚑"
            self.Mode["fg"] = "#992727"

    def GetClickCount(self):
        return self.Click

    def UpdateRemaining(self,i):
        self.Remaining += i
        if self.Remaining == self.MineCount:
            self.EndGame(True)
    
    def UpdateClickCount(self,i = 1):
        self.Click += i;
        self.ClickCounter["text"] = "Clicks: " + str(self.Click)
        if self.Click == 1:
            self.Mode["state"] = "normal"

    def UpdateFlagCount(self,i):
        self.FlagCount += i
        self.Counter["text"] = "⚑ " + str(self.FlagCount)

    def GetAllSafeTiles(self):
        Safe = []
        for y in range(self.SizeY):
            for x in range(self.SizeX):
                if self.Tiles[y][x].Safe:
                    Safe.append(y * self.SizeX + x)
        return Safe;

    def FirstClickCheck(self,x,y): #Ensure first click is 0
        count = 0;
        neighbours = []
        for dy in range(-1,2):
            for dx in range(-1,2):
                if (0 <= x + dx < self.SizeX) and (0 <= y + dy < self.SizeY):
                    neighbours.append((y+dy) * self.SizeX + x + dx)
                    if not self.Tiles[y + dy][x + dx].Safe:
                        count += 1
                        self.Tiles[y + dy][x + dx].Safe = True
        if (count > 0):
            safe = self.GetAllSafeTiles()
            for i in neighbours:
                safe.remove(i)
            danger = sample(safe, count)
            for i in danger:
                self.Tiles[i // self.SizeX][i % self.SizeX].Safe = False
                
            self.PrintMap()

    def IsValidCoord(self,x,y):
        return (0 <= x < self.SizeX) and (0 <= y < self.SizeY)

    def GetTile(self,x,y):
        if (0 <= x < self.SizeX) and (0 <= y < self.SizeY):
            return self.Tiles[y][x]
        return None

    def GetMineCount(self,x,y):
        count = 0
        for dy in range(-1,2):
            for dx in range(-1,2):
                if (dx != 0 or dy != 0) and (0 <= x + dx < self.SizeX) and (0 <= y + dy < self.SizeY):
                    if not self.Tiles[y + dy][x + dx].Safe:
                        count += 1
        return count

    def PrintMap(self):
        line = ""
        for y in range(self.SizeY):
            for x in range(self.SizeX):
                if self.Tiles[y][x].Safe:
                    line += "."
                else:
                    line += "!"
            line += "\n"
        print(line)


class Tile:
    def __init__(self,x,y,board):
        self.x = x
        self.y = y
        
        self.board = board
        
        self.Button = tk.Button(window,text="?",fg="#3F454E",highlightbackground="#3F454E",font = UI_font,command = self.Pressed,width=1)
        self.Button.grid(column = x + 3, row = y)
        self.State = 0 #0: [?] / 1: [⚑] / 2: [X]
        self.Count = -1
        
        self.Safe = True
        self.MineCount = 0

    def Destruct(self):
        if self.Button != None:
            self.Button.destroy()
            self.Button = None

    def Pressed(self):
        if self.State == TileUncovered: #Chording
            c = 0
            for dy in range(-1,2):
                for dx in range(-1,2):
                    if dx != 0 or dy != 0:
                        t = self.board.GetTile(self.x + dx, self.y + dy)
                        if t != None:
                            if t.State == TileFlagged:
                                c += 1
            if c == self.MineCount:
                reveal_count = 0
                for dy in range(-1,2):
                    for dx in range(-1,2):
                        if dx != 0 or dy != 0:
                            t = self.board.GetTile(self.x + dx, self.y + dy)
                            if t != None:
                                if t.State == TileUnknown:
                                    reveal_count += 1;
                                    t.Reveal()
                if reveal_count > 0:
                    self.board.UpdateClickCount(1)
        elif self.board.GetMode() == FlagMode:
            if self.State == TileUnknown:
                self.State = TileFlagged
                self.Button["text"] = "[⚑]"
                self.Button["fg"] = "#992727"
                self.Button["highlightbackground"] = "#992727"
                self.board.UpdateFlagCount(-1)
            elif self.State == TileFlagged:
                self.State = TileUnknown
                self.Button["text"] = "[?]"
                self.Button["fg"] = "#3F454E"
                self.Button["highlightbackground"] = "#3F454E"
                self.board.UpdateFlagCount(1)
        elif self.State == TileUnknown:
            self.board.UpdateClickCount(1)
            if self.board.GetClickCount() == 1:
                self.board.FirstClickCheck(self.x,self.y)
            if self.Safe:
                self.Reveal()
            else:
                self.Button["text"] = "[!]"
                self.Button["fg"] = "#FF0000"
                self.Button["highlightbackground"] = "#FF0000"
                self.board.EndGame(False)

    def Reveal(self):
        if not self.Safe:
            self.Button["text"] = "[!]"
            self.Button["fg"] = "#FF0000"
            self.Button["highlightbackground"] = "#FF0000"
            self.board.EndGame(False)
        elif self.State != TileUncovered:
            if self.State == TileFlagged: #Auto Un-flag
                self.board.UpdateFlagCount(1)

            self.State = TileUncovered
            self.MineCount = self.board.GetMineCount(self.x, self.y)
            self.Button["text"] = "["+str(self.MineCount)+"]"
            self.Button["highlightbackground"] = NumColour.get(self.MineCount)
            
            self.board.UpdateRemaining(-1)

            if self.MineCount == 0: #Flood-fill #self.Button["text"] == "[0]":
                self.Button["state"] = "disabled"
                for dy in range(-1,2):
                    for dx in range(-1,2):
                        if dx != 0 or dy != 0:
                            t = self.board.GetTile(self.x + dx, self.y + dy)
                            if t != None:
                                if t.State != TileUncovered:
                                    t.Reveal()

#WINDOW & INITIALIZATION
def ResizeWindow():
    window.update_idletasks()
    req_width = window.winfo_reqwidth()
    req_height = window.winfo_reqheight()
    window.minsize(req_width, req_height)
    window.geometry(str(req_width)+"x"+str(req_height))
                                    
def DeleteWindow():
    window.destroy()


window = tk.Tk()
window.resizable(False, False)

window.title('Minesweeper')

board = Board(9,9,10)

ResizeWindow()


window.mainloop()
