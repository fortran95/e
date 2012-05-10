# -*- coding: UTF-8 -*-
from Tkinter import *

dlgReturn = -1
class LoadingKeyDialog(object):
        
    def __init__(self,master=None,screeninfo=''):
        def accept(m=master):
            global dlgReturn
            dlgReturn = 1
            m.quit()
        self.screen = Text(master)
        self.screen['width'] = 70
        self.screen['height'] = 20
        self.screen['background'] = 'Black'
        self.screen['foreground'] = 'Green'
        self.screen.insert(END,screeninfo)
        self.screen.grid(row=0,column=0,columnspan=2)
        
        self.lbl = Label(master)
        self.lbl['text'] = "您是否允许接收此密钥？"
        self.lbl.grid(row=1,column=0,columnspan=2)
        
        self.yesbutton = Button(master)
        self.yesbutton["text"] = "允许"
        self.yesbutton["foreground"] = "#0A0"
        #self.yesbutton["width"] = 60
        self.yesbutton["pady"] = 10
        self.yesbutton["command"] = accept
        self.yesbutton.grid(row=2,column=0,sticky=W+E+N+S)
        
        self.nobutton = Button(master)
        self.nobutton["text"] = "拒绝"
        self.nobutton["foreground"] = "Red"
        #self.nobutton["width"] = 60
        self.nobutton["pady"] = 10
        self.nobutton["command"] = master.quit
        self.nobutton.grid(row=2,column=1,sticky=W+E+N+S)
        
class ChoosingDialog(Frame):
    def createWidgets(self,keys,label):
        self.lbl = Label(self)
        self.lbl['text'] = label
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
        self.quitbutton["text"] = "取消选择：退出密钥交换程序"
        self.quitbutton["foreground"] = "Red"
        self.quitbutton["width"] = 60
        self.quitbutton["pady"] = 10
        self.quitbutton["command"] = self.quit
        self.quitbutton.pack()

    def __init__(self, keys, master=None, label=''):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets(keys,label)
def loadKey(info):
    global dlgReturn
    dlgReturn = -1
    root = Tk()
    root.title("收到新的密钥")
    app = LoadingKeyDialog(root,screeninfo=info)
    root.mainloop()
    root.destroy()
    return dlgReturn
def keySelect(keys,title,description):
    global dlgReturn
    dlgReturn = -1
    root = Tk()
    root.title(title)
    
    app = ChoosingDialog(keys,master=root,label=description)
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
    #print keySelect([['12345678','2012-12-21','NERV KEY1']])
    print loadKey('[gpg:]')