import wx
import wx.aui
import sys
import ExperimentObjects
import time
t0=time.time()

class FlowPanel(wx.ScrolledWindow):
    def __init__(self, parent, id=-1,size = wx.DefaultSize):
        """A panel that shows how the procedures will fit together
        """
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        self.parent=parent   
              
        self.btnSizer = wx.BoxSizer(wx.VERTICAL)
        self.btnAddProc = wx.Button(self,-1,'Add Procedure')   
        self.btnAddLoop = wx.Button(self,-1,'Add Loop')    
                
        #bind events     
        self.Bind(wx.EVT_BUTTON, self.onAddProc,self.btnAddProc)  
        self.Bind(wx.EVT_PAINT, self.onPaint)
        
        self.btnSizer.Add(self.btnAddProc)
        self.btnSizer.Add(self.btnAddLoop)        
        self.SetSizer(self.btnSizer)
        self.SetAutoLayout(True)
        #self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)   
        #self.mainSizer.Add(self.btnSizer)
        #self.mainSizer.Add(self.dc)           
    def onAddProc(self, evt):
        exp = self.parent.exp
        
        #bring up listbox to choose the procedure to add and/or create a new one
        exp.addProcedure('t')
        exp.flow.addProcedure(exp.procs['t'], pos=1)        
        self.Refresh()
        evt.Skip()
        
    def onPaint(self, evt=None):
        expFlow = self.parent.exp.flow #retrieve the current flow from the experiment
        
        t = time.time()-t0
        
        #create a drawing context for our lines/boxes
        pdc = wx.PaintDC(self)
        try:
            self.dc = wx.GCDC(pdc)
        except:
            self.dc = pdc
            
        self.dc.Clear()
        
        #draw the main time line
        linePos = 80
        self.dc.DrawLine(x1=100,y1=linePos,x2=500,y2=linePos)
        
        #step through objects in flow
        currX=120; gap=20
        loopInits = []
        loopTerms = []
        for entry in expFlow:
            if entry.getType()=='LoopInitiator':
                self.drawLoopAttach(pos=[currX,linePos])
                loopInits.append(currX)
            if entry.getType()=='LoopTerminator':
                self.drawLoopAttach(pos=[currX,linePos])
                loopTerms.append(currX)
            if entry.getType()=='Procedure':
                currX = self.drawFlowBox(entry.name, pos=[currX+t,linePos-40])
            currX+=gap
            
        loopTerms.reverse()#reverse the terminators, so that last term goes with first init   
        for n in range(len(loopInits)):
            self.drawFlowLoop('Flow1',startX=loopInits[n],endX=loopTerms[n],base=linePos,height=20)
            
    def drawLoopAttach(self, pos):
        #draws a spot that a loop will later attach to
        self.dc.SetBrush(wx.Brush(wx.Colour(100,100,100, 250)))
        self.dc.SetPen(wx.Pen(wx.Colour(0,0,0, wx.ALPHA_OPAQUE)))
        self.dc.DrawCirclePoint(pos,5)
    def drawFlowBox(self,name,rgb=[200,50,50],pos=[0,0]):
        font = self.dc.GetFont()
        font.SetPointSize(24)
        r, g, b = rgb

        #get size based on text
        self.dc.SetFont(font)
        w,h = self.dc.GetFullTextExtent(name)[0:2]
        pad = 20
        #draw box
        rect = wx.Rect(pos[0], pos[1], w+pad,h+pad) 
        endX = pos[0]+w+20
        #the edge should match the text
        self.dc.SetPen(wx.Pen(wx.Colour(r, g, b, wx.ALPHA_OPAQUE)))
        #for the fill, draw once in white near-opaque, then in transp colour
        self.dc.SetBrush(wx.Brush(wx.Colour(255,255,255, 250)))
        self.dc.DrawRoundedRectangleRect(rect, 8)   
        self.dc.SetBrush(wx.Brush(wx.Colour(r,g,b,50)))
        self.dc.DrawRoundedRectangleRect(rect, 8)   
        #draw text        
        self.dc.SetTextForeground(rgb) 
        self.dc.DrawText(name, pos[0]+pad/2, pos[1]+pad/2)
        return endX
    def drawFlowLoop(self,name,startX,endX,base,height,rgb=[200,50,50]):
        xx = [endX,  endX,   endX,   endX-5, endX-10, startX+10,startX+5, startX, startX, startX]
        yy = [base,height+10,height+5,height, height, height,  height,  height+5, height+10, base]
        pts=[]
        for n in range(len(xx)):
            pts.append([xx[n],yy[n]])
        self.dc.DrawSpline(pts)
        
class Procedure(wx.Panel):
    """A frame to represent a single procedure
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self,parent)
        self.parent=parent            
class ProceduresPanel(wx.aui.AuiNotebook):
    """A notebook that stores one or more procedures
    """
    def __init__(self, parent, id=-1):
        self.parent=parent
        wx.aui.AuiNotebook.__init__(self, parent, id,)
        self.addProcedure('first')
    def addProcedure(self, procName):
        text1 = Procedure(parent=self)
        self.AddPage(text1, procName)
    
class ProcButtonsPanel(wx.Panel):
    def __init__(self, parent, id=-1):
        """A panel that shows how the procedures will fit together
        """
        wx.Panel.__init__(self,parent,size=(80,600))
        self.parent=parent    
        self.sizer=wx.BoxSizer(wx.VERTICAL)
        
        textImg = wx.Bitmap("res//text.png")
        self.textBtn = wx.BitmapButton(self, -1, textImg, (20, 20),
                       (textImg.GetWidth()+10, textImg.GetHeight()+10))
                       
        patchImg= wx.Bitmap("res//patch.png")
        self.patchBtn = wx.BitmapButton(self, -1, patchImg, (20, 20),
                       (patchImg.GetWidth()+10, patchImg.GetHeight()+10))
                       
        mouseImg= wx.Bitmap("res//mouse.png")
        self.mouseBtn = wx.BitmapButton(self, -1, mouseImg, (20, 20),
                       (mouseImg.GetWidth()+10, mouseImg.GetHeight()+10))
#        patchImg= wx.Bitmap("res//patch.png")
#        self.textBtn = wx.BitmapButton(self, -1, patchImg, (20, 20),
#                       (patchImg.GetWidth()+10, patchImg.GetHeight()+10))
#        patchImg= wx.Bitmap("res//patch.png")
#        self.textBtn = wx.BitmapButton(self, -1, patchImg, (20, 20),
#                       (patchImg.GetWidth()+10, patchImg.GetHeight()+10))
        
        self.sizer.Add(self.patchBtn, 0,wx.EXPAND|wx.ALIGN_CENTER )
        self.sizer.Add(self.textBtn, 0,wx.EXPAND|wx.ALIGN_CENTER)
        self.sizer.Add(self.mouseBtn, 0,wx.EXPAND|wx.ALIGN_CENTER)
        self.SetSizer(self.sizer)
class BuilderFrame(wx.Frame):

    def __init__(self, parent, id=-1, title='PsychoPy Builder',
                 pos=wx.DefaultPosition, size=(800, 600),files=None,
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        self.parent=parent
        self._mgr = wx.aui.AuiManager(self)
        
        #create a default experiment (maybe an empty one instead)
        self.exp = ExperimentObjects.Experiment()
        self.exp.addProcedure('trial') #create the trial procedure
        self.exp.flow.addProcedure(self.exp.procs['trial'], pos=1)#add it to flow
        #adda loop to the flow as well
        trialInfo = [ {'ori':5, 'sf':1.5}, {'ori':2, 'sf':1.5},{'ori':5, 'sf':3}, ] 
        self.exp.flow.addLoop(
            ExperimentObjects.LoopHandler(name='trialLoop', loopType='rand', nReps=5, trialList = trialInfo),
            startPos=0.5, endPos=1.5,#specify positions relative to the
            )
        
        # create our panels
        self.flowPanel=FlowPanel(parent=self, size=(600,200))
        self.procPanel=ProceduresPanel(self)
        self.procButtons=ProcButtonsPanel(self)
        # add the panes to the manager
        self._mgr.AddPane(self.procPanel,wx.CENTER, 'Procedures')
        self._mgr.AddPane(self.procButtons, wx.RIGHT)
        self._mgr.AddPane(self.flowPanel,wx.BOTTOM, 'Flow')

        # tell the manager to 'commit' all the changes just made
        self._mgr.Update()

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        # deinitialize the frame manager
        self._mgr.UnInit()
        # delete the frame
        self.Destroy()


class BuilderApp(wx.App):
    def OnInit(self):
        if len(sys.argv)>1:
            if sys.argv[1]==__name__:
                args = sys.argv[2:] # program was excecuted as "python.exe PsychoPyIDE.py %1'
            else:
                args = sys.argv[1:] # program was excecuted as "PsychoPyIDE.py %1'
        else:
            args=[]
        self.frame = BuilderFrame(None, -1, 
                                      title="PsychoPy Experiment Builder",
                                      files = args)
                                     
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True
    def MacOpenFile(self,fileName):
        self.frame.setCurrentDoc(fileName) 

if __name__=='__main__':
    app = BuilderApp(0)
    app.MainLoop()