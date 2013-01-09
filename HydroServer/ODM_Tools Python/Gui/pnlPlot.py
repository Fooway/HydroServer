#Boa:FramePanel:Panel1

import wx
from wx.lib.pubsub import Publisher


import plotTimeSeries
import plotSummary
import plotHistogram
import plotBoxWhisker
import plotProbability

[wxID_PANEL1, wxID_PAGEBOX, wxID_PAGEHIST, wxID_PAGEPROB, 
wxID_PAGESUMMARY, wxID_PAGETIMESERIES, wxID_TABPLOTS
] = [wx.NewId() for _init_ctrls in range(7)]


class pnlPlot(wx.Notebook):  
    
    
    
    def _init_ctrls(self, prnt):
        wx.Notebook.__init__(self, id=wxID_TABPLOTS, name=u'tabPlots',
              parent=prnt, pos=wx.Point(0, 0), size=wx.Size(491, 288),
              style=wx.BK_DEFAULT)
        
        self.pltTS = plotTimeSeries.plotTimeSeries(id=wxID_PAGETIMESERIES, name='pltTS',
                parent=self, pos=wx.Point(0, 0), size=wx.Size(605, 458),
                style=wx.TAB_TRAVERSAL) 
        self.AddPage(self.pltTS, 'TimeSeries')
        
        self.pltProb = plotProbability.plotProb(id=wxID_PAGEPROB, name='pltProb',
                parent=self, pos=wx.Point(0, 0), size=wx.Size(605, 458),
                style=wx.TAB_TRAVERSAL) 
        self.AddPage(self.pltProb, 'Probablity')        
        
        self.pltHist = plotHistogram.plotHist(id=wxID_PAGEHIST, name='pltHist',
                parent=self, pos=wx.Point(0, 0), size=wx.Size(605, 458),
                style=wx.TAB_TRAVERSAL) 
        self.AddPage(self.pltHist, 'Histogram')

        self.pltBox = plotBoxWhisker.plotBox(id=wxID_PAGEBOX, name='pltBox',
                parent=self, pos=wx.Point(0, 0), size=wx.Size(605, 458),
                style=wx.TAB_TRAVERSAL) 
        self.AddPage(self.pltBox, 'Box/Whisker')
        
        
        self.pltSum = plotSummary.plotSummary( id = wxID_PAGESUMMARY, name=u'pltSum',
              parent=self, pos=wx.Point(784, 256), size=wx.Size(437, 477),
              style=wx.TAB_TRAVERSAL)
        self.AddPage(self.pltSum, 'Summary')
        
        
       

    
    def addPlot(self, Values):
    
        self.dataValues = []
        self.dateTimes= []
        #self.Series = Values[1]
        for dv in Values[0]:
           self.dataValues.append(dv.data_value)
           self.dateTimes.append(dv.local_date_time)
        self.pltSum.addPlot(self.dataValues,  Values[1])
        self.pltTS.addPlot(self.dataValues, self.dateTimes, Values[1])
        self.pltHist.addPlot(self.dataValues, self.dateTimes, Values[1])
        self.pltProb.addPlot(self.dataValues, self.dateTimes, Values[1])
        self.pltBox.addPlot(self.dataValues, self.dateTimes, Values[1])
        


    def selectPlot(self, value):       
        self.SetSelection(value.data)
       
        
    def __init__(self, parent, id, pos, size, style, name):
        self._init_ctrls(parent)
   