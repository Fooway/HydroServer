#Boa:Frame:ODMTools

import wx
import wx.grid
import wx.lib.agw.ribbon as RB
import wx.aui
import wx.richtext
import wx.stc
import datetime
from wx.lib.pubsub import Publisher
from numpy import arange, sin, cos, exp, pi


from odmservices.series_service import SeriesService
import pnlSeriesSelector
import pnlPlot
import mnuRibbon


# import sys
# sys.path.append('C:\DEV\ODM\HydroServer\ODM_Tools Python')


def create(parent):
    return frmODMToolsMain(parent)

[wxID_ODMTOOLS, wxID_ODMTOOLSCHECKLISTBOX2, wxID_ODMTOOLSCOMBOBOX1, 
 wxID_ODMTOOLSCOMBOBOX2, wxID_ODMTOOLSCOMBOBOX4, wxID_ODMTOOLSCOMBOBOX5, 
 wxID_ODMTOOLSGRID1, wxID_ODMTOOLSPANEL1, wxID_ODMTOOLSPANEL2, 
 wxID_ODMTOOLSTOOLBAR1,  wxID_PNLSELECTOR,  wxID_TXTPYTHONSCRIPT, 
 wxID_TXTPYTHONCONSOLE, 
] = [wx.NewId() for _init_ctrls in range(13)]



class frmODMToolsMain(wx.Frame):

#############Entire Form Sizers##########  
    def _init_sizers(self):
        # generated method, don't edit
        self.s = wx.BoxSizer(wx.VERTICAL)        
        
        self._init_s_Items(self.s)        
        
        self.SetSizer(self.s)
    
    def _init_s_Items(self, parent):
        # generated method, don't edit
        
        parent.AddWindow(self._ribbon, 0, wx.EXPAND)
        parent.AddWindow(self.pnlDocking, 85, flag=wx.ALL | wx.EXPAND)
   

###################### Form ################
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_ODMTOOLS, name=u'ODMTools', parent=prnt,
              pos=wx.Point(150, 150), size=wx.Size(1190, 812),
              style=wx.DEFAULT_FRAME_STYLE, title=u'ODM Tools')
        Publisher().subscribe(self.addPlot, ("add.NewPlot")) 



############### Ribbon ###################
        self._ribbon = mnuRibbon.mnuRibbon(parent=self, id=wx.ID_ANY, name ='ribbon')
              

################ Docking Tools##############
        self.pnlDocking = wx.Panel(id=wxID_ODMTOOLSPANEL1, name='pnlDocking',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(605, 458),
              style=wx.TAB_TRAVERSAL)
              
        self.grid1 = wx.grid.Grid(id=wxID_ODMTOOLSGRID1, name='grid1',
              parent=self.pnlDocking, pos=wx.Point(64, 160), size=wx.Size(376, 280),
              style=0)
        # self.txtPythonScript = wx.stc.StyledTextCtrl(id=wxID_TXTPYTHONSCRIPT,
        #       name=u'txtPython', parent=self, pos=wx.Point(72, 24),
        #       size=wx.Size(368, 168), style=0)
              
        # self.txtPythonConsole = wx.stc.StyledTextCtrl(id=wxID_TXTPYTHONCONSOLE,
        #       name=u'txtPython', parent=self, pos=wx.Point(72, 24),
        #       size=wx.Size(368, 168), style=0)
        self.grid1.EnableGridLines(True)        


        
################ Series Selection Panel ##################           

        self.pnlSelector = pnlSeriesSelector.pnlSeriesSelector(id=wxID_PNLSELECTOR, name=u'pnlSelector',
               parent=self.pnlDocking, pos=wx.Point(0, 0), size=wx.Size(770, 388),
               style=wx.TAB_TRAVERSAL, dbservice= self.sc)       



############# Graph ###############
        
       
        self.pnlPlot= pnlPlot.pnlPlot(id=wxID_ODMTOOLSPANEL1, name='pnlPlot',
              parent=self.pnlDocking, pos=wx.Point(0, 0), size=wx.Size(605, 458),
               style=wx.TAB_TRAVERSAL)
        # wx.Panel(id=wxID_ODMTOOLSPANEL1, name='plotPanel',
        #       parent=self.pnlDocking, pos=wx.Point(0, 0), size=wx.Size(605, 458),
        #       style=wx.TAB_TRAVERSAL)
        
                  





############ Docking ###################
       
        self._mgr = wx.aui.AuiManager(self.pnlDocking)
        self._mgr.AddPane(self.grid1, wx.RIGHT, 'Table View')
        self._mgr.AddPane(self.pnlSelector, wx.BOTTOM, 'Series Selector')
        #self._mgr.AddPane(self.txtPythonScript, wx.BOTTOM , 'Script')
        #self._mgr.AddPane(self.txtPythonConsole, wx.BOTTOM , 'Python Console')
        #self._mgr.AddPane(self._ribbon, wx.TOP)
        self._mgr.AddPane(self.pnlPlot, wx.CENTER)


        self._mgr.Update()
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self._init_sizers()
        self._ribbon.Realize()       


    def __init__(self, parent):
        self.createdummyService()
        self._init_ctrls(parent)
        self.Refresh()
    
    
    def addPlot(self, Values):
        self.pnlPlot.addPlot(Values)

        
    def OnClose(self, event):
        # deinitialize the frame manager
        self._mgr.UnInit()
        # delete the frame
        self.Destroy()

    
    
    def createdummyService(self):
        self.sc = SeriesService(connection_string="mssql+pyodbc://ODM:odm@(local)\sqlexpress/LittleBear11")#connection_string="mssql+pyodbc://ODM:odm@Arroyo/LittleBear11")
        
        

##    def BindAction(self):
##        #self.Bind(wx.EVT_MENU, self.test, None, 1)
##        #self.Bind(wx.EVT_BUTTON, self.OnBtnAdvButton, id = )
##        
##    def OnBtnAdvButton(self, event):
##        self.new = NewWindow(parent=None, id=-1)
##        self.new.Show()
    
    
    
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = create(None)
    frame.Show()

    app.MainLoop()
    