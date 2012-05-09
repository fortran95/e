from Tkinter import *

dlgReturn = -1
class ChoosingDialog(Frame):
    def createWidgets(self,keys):
        self.lbl = Label(self)
        self.lbl['text'] = 'You are going to sign a new transfer-key.\nPlease select the identifing PGP secret key that you want to use.\n'
        self.lbl.pack()
        
        self.buttons = []
        for k in keys:
            b = Button(self)
            b["text"] = k[2]
            def onClick(self,root=self,kid=keys.index(k)):
                global dlgReturn
                dlgReturn = kid
                root.quit()
            b.bind('<Button-1>',onClick)
            b["width"] = 60
            b.pack()
            self.buttons.append(b)
            
        self.quitbutton = Button(self)
        self.quitbutton["text"] = "Cancel: Select none of the above keys and exit program."
        self.quitbutton["foreground"] = "Red"
        self.quitbutton["width"] = 60
        self.quitbutton["pady"] = 10
        self.quitbutton["command"] = self.quit
        self.quitbutton.pack()

    def __init__(self, keys, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets(keys)

def keySelect(keys):
    global dlgReturn
    root = Tk()
    root.title('Select your identifing secret key')
    
    app = ChoosingDialog(keys,master=root)
    root.update_idletasks()
    
    w = root.winfo_width()
    h = root.winfo_height()
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    # calculate position x, y
    x = (ws/2) - (w/2) 
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    root.resizable(0,0)
    
    app.mainloop()
    root.destroy()
    return dlgReturn

if __name__ == '__main__':
    print keySelect([['12345678','2012-12-21','NERV KEY1']])