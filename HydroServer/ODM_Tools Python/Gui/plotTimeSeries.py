#!/usr/bin/python
import wx


import textwrap
import datetime
import numpy as np
from wx.lib.pubsub import Publisher


import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
# from matplotlib.widgets import Lasso
from mnuPlotToolbar import MyCustomToolbar as NavigationToolbar
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
from matplotlib.font_manager import FontProperties

from matplotlib.widgets import Lasso
from matplotlib import path
from random import *
from wx.lib.pubsub import Publisher




class plotTimeSeries(wx.Panel):


  def _init_coll_boxSizer1_Items(self, parent):
      # generated method, don't edit

      parent.AddWindow(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
      parent.AddWindow(self.toolbar, 0,  wx.EXPAND)


  def _init_sizers(self):
      # generated method, don't edit
      self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)
      self._init_coll_boxSizer1_Items(self.boxSizer1)
      self.SetSizer(self.boxSizer1)



  def _init_ctrls(self, prnt):
      #matplotlib.figure.Figure.__init__(self)
      wx.Panel.__init__(self, prnt, -1)

      # self.figure = Figure()#matplotlib.figure.Figure()

      #init Plot
      # self.timeSeries=self.figure.add_subplot(111)
      self.timeSeries = host_subplot(111, axes_class=AA.Axes)

      # self.timeSeries.axis([0, 1, 0, 1])#
      self.timeSeries.plot([],[])
      self.timeSeries.set_title("No Data To Plot")

      self.canvas = FigCanvas(self, -1, plt.gcf())
      # self.canvas = FigCanvas(self, -1, self.figure)

      self.canvas.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL,
            False, u'Tahoma'))
      # self.canvas.mpl_connect('pick_event', self.on_pick)
      

      # Create the navigation toolbar, tied to the canvas
      self.toolbar = NavigationToolbar(self.canvas, allowselect=True)
      self.toolbar.Realize()


      self.fontP = FontProperties()
      self.fontP.set_size('small')

      self.format = '-o'
      self.SetColor("WHITE")
      #self.canvas.gca().xaxis.set_major_locator()

      #init lists
      self.Plots = []
      self.lines=[]
      self.axes = []
      self.colorlist = ('blue', 'green', 'red', 'cyan', 'orange', 'magenta', 'yellow')

      # self.canvas.mpl_connect('button_press_event', self.onclick)


      self.BuildPopup()
      self.canvas.draw()
      self._init_sizers()

 

  def changeSelectionDT(self, sellist):
     
      # print sellist
      
      sellist = self.selFormat(sellist)
      self.changeSelection(sellist)
      # self.selectedlist= sellist
      # print ['k' if x==0 else 'r' for x in self.selectedlist]
      # print type(self.selectedlist)
  def selFormat(self, pairs):
      print len(pairs)
      if len(pairs) ==0:
        return [False] * len(self.editData.DataValues)
      verts =[ (matplotlib.dates.date2num(x), y) for x,y  in pairs]
      p = path.Path(verts)

      ind = p.contains_points(self.xys)
      return ind


  def changeSelection(self, sellist ):
      self.editPoint.set_color(['k' if x==0 else 'r' for x in sellist])
      self.canvas.draw()

  def onDateChanged(self, date, time):
      # print date
      # self.timeSeries.clear()
      date = datetime.datetime(date.Year, date.Month, date.Day, 0, 0, 0)
      if time == "start":
        self.startDate = date
      else:
        self.endDate = date

      self.plot.set_xbound(self.startDate,self.endDate)
      self.canvas.draw()



  def OnShowLegend(self, isVisible):
    # print self.timeSeries.show_legend
    if isVisible:
      plt.subplots_adjust(bottom=.1+.1)
      self.timeSeries.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
               ncol=2, prop = self.fontP)
          
    else:
      plt.subplots_adjust(bottom=.1)
      self.timeSeries.legend_=None
    # self.timeSeries.plot(legend= not isVisible)
    self.canvas.draw()



  def OnPlotType(self, ptype):
    # self.timeSeries.clear()
    if ptype == "line":
      ls = '-'
      m='None'
    elif ptype == "point":
      ls='None'
      m='o'
    else:
      ls = '-'
      m='o'
    # print plt.setp(self.lines)
    # print(len(self.lines))
    format = ls+m
    for line in self.lines:
      plt.setp(line, linestyle = ls, marker =  m)

    self.canvas.draw()

  def stopEdit(self):
      self.timeSeries.clear()
      self.editDataFilter = None
      self.editCursor =None
      self.editSeries= None
      self.editData = None
      self.editline = None
      self.selectedlist = None
      self.editPoint =None
      self.lman= None
      self.cid=None
      self.toolbar.stopEdit()
      self.RefreshPlot()

  def addEdit(self, cursor, series, Filter):
      self.timeSeries.clear()

      self.editDataFilter = Filter
      self.editCursor = cursor
      self.editSeries= series
      self.toolbar.editSeries()
      #####include NoDV in plot
      # remove from regular 'lines'
      self.removePlot(self.editSeries.id)


      self.editCursor.execute("SELECT  DataValue, LocalDateTime FROM DataValuesEdit "+self.editDataFilter + " ORDER BY LocalDateTime")
      results = self.editCursor.fetchall()

      self.editData = plotData(self.editSeries.id, [x[0] for x in results], [x[1] for x in results],
              "\n".join(textwrap.wrap(self.editSeries.variable_name+ "("+self.editSeries.variable_units_name+")",50)),
              "\n".join(textwrap.wrap(self.editSeries.site_name+" "+self.editSeries.variable_name,55)), 'k')

      #add plot with line only in black
      self.timeSeries.set_title(self.editData.title)
      self.timeSeries.set_ylabel(self.editData.ylabel, color =self.editData.color )
      self.editline= self.timeSeries.plot_date(self.editData.DateTimes, self.editData.DataValues, '-'+self.editData.color, xdate = True, tz = None, label = self.editData.title )

      # add scatterplot with colorlist as colorchart
      self.selectedlist = [False] * len(self.editData.DataValues)
      

      self.editPoint = self.timeSeries.scatter(self.editData.DateTimes, self.editData.DataValues, s= 20, c=['k' if x==0 else 'r' for x in self.selectedlist])
      self.xys = [(matplotlib.dates.date2num(x), y) for x, y in zip(self.editData.DateTimes, self.editData.DataValues) ]
      

      self.cid = self.canvas.mpl_connect('button_press_event', self.onpress)
      # self.editPoint.set_picker(True)
      # self.lman = LassoManager(self.timeSeries, self.editData.DateTimes, self.editData.DataValues, self.selectedlist)
      

      self.timeSeries.set_xlabel("Date Time")

      self.canvas.draw()


  def updateValues(self):
    self.addEdit(self.editCursor, self.editSeries, self.editDataFilter)

  def addPlot(self, cursor, series, Filter):
    self.dataFilter = Filter
    self.cursor = cursor
    # print Values[1]
    # series= Values[1]

    # print series
    isplotted= False
    for ind  in range(len(self.Plots)):
        if self.Plots[ind].SeriesID == series.id:
          isplotted = True

    if not isplotted:
      self.cursor.execute("SELECT  DataValue, LocalDateTime FROM DataValues "+self.dataFilter +" ORDER BY LocalDateTime")
      results = self.cursor.fetchall()
     # self, sID, dValues, dTimes, sDate, eDate, ylabel, title, color, axesid

      self.Plots.append(plotData(series.id, [x[0] for x in results], [x[1] for x in results],
              "\n".join(textwrap.wrap(series.variable_name+ "("+series.variable_units_name+")",45)),
              "\n".join(textwrap.wrap(series.site_name+" "+series.variable_name,50)), self.colorlist[len(self.Plots)]))


      self.RefreshPlot()

      #prepare the axes


  def RefreshPlot(self):

    ##reset plot
      for ax in self.axes:
        ax.axis.clear()
      # self.timeSeries.clear()
      lines = []
      self.axes = []
      # self.figure.subplots_adjust(right=90, left = 10)

      ##create Axes
      adj=.05

      for x in range(len(self.Plots)):
        # print x
        # if not((x+1) % 2==0):
          # axes.append(axisData(x, self.timeSeries.twinx(),  -1.2*x, "left", leftadjust= .75*(x-1)))
        if x==0 :
          self.axes.append(axisData(x, self.timeSeries,  0, 'left', leftadjust = .10))
        elif x == 1:
          self.axes.append(axisData(x, self.timeSeries.twinx(),  1, 'right', rightadjust= .90))
        elif x==2:
          self.axes.append(axisData(x, self.timeSeries.twinx(),  60, 'right', rightadjust= .9-(adj*x)))
          # print .9-(adj*x)
        else:
          # axes.append(axisData(x, self.timeSeries.twinx(),  1.2*(x-1), 'right', rightadjust= .75*(x-1)))
          self.axes.append(axisData(x, self.timeSeries.twinx(),  -60, 'left', leftadjust= .10+(adj*2)))

     
      for currPlot, ax, val  in zip (self.Plots, self.axes, range(len(self.Plots))):
        if val >1:
          new_fixed_axis = ax.axis.get_grid_helper().new_fixed_axis
          ax.axis.axis[ax.side] = new_fixed_axis(loc = ax.side, axes= ax.axis, offset= (ax.position ,0))
          ax.axis.axis[ax.side].toggle(all=True)
          if val > 1 and ax.side== "left":
            ax.axis.axis["right"].toggle(all=False)

        if ax.rightadjust:
          plt.subplots_adjust(right=ax.rightadjust)
        if ax.leftadjust:
          plt.subplots_adjust(left=ax.leftadjust)

        ax.axis.set_ylabel(currPlot.ylabel)

        # self.timeSeries.set_xlim(min(currPlot.DateTimes), max(currPlot.DateTimes))
        # ax.axis.set_ylim(min(currPlot.DataValues), max(currPlot.DataValues))

        self.lines.append(ax.axis.plot_date(currPlot.DateTimes, currPlot.DataValues, self.format, color=currPlot.color, xdate = True, tz = None, label = currPlot.title ))


        if len(self.axes) >1:
          if val ==1:
            ax.axis.set_title("Multiple Series plotted")
            plt.subplots_adjust(bottom=.1+.1)
           
          self.timeSeries.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
               ncol=2, prop = self.fontP)
          
        else:
          ax.axis.set_title(currPlot.title)
          plt.subplots_adjust(bottom=.1)
          self.timeSeries.legend_=None

      self.timeSeries.set_xlabel("Date Time")
      
      self.canvas.draw()
      # plt.close()

  def callback(self, verts):
        
        # print verts 


        p = path.Path(verts)
        ind = p.contains_points(self.xys)
        self.changeSelection(ind)

        # xys= [(matplotlib.dates.num2date(x), y) for x, y in zip(self.editData.DateTimes, self.editData.DataValues) ]
        # vals = [(matplotlib.dates.num2date(x), y) for x,y in verts]

        # p = path.Path(vals)
        # ind = p.contains_points(xys)

        # self.changeSelection(ind)
        # print vals

        self.canvas.draw_idle()
        self.canvas.widgetlock.release(self.lasso)
        del self.lasso


  def onpress(self, event):
        if self.canvas.widgetlock.locked(): return
        if event.inaxes is None: return
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.callback)
        # acquire a lock on the widget drawing
        self.canvas.widgetlock(self.lasso)


  def removePlot(self, seriesID):
     #if series id matches a key in the dictionary

      for ind  in range(len(self.Plots)):
        if self.Plots[ind].SeriesID == seriesID:
          # print ind
          self.axes[ind].axis.clear()
          self.Plots.pop(ind)

          # self.timeSeries.lines.pop(ind).remove()
      # for p in self.Plots:
      #   print p.SeriesID
      self.RefreshPlot()



  def SetColor( self, color):
      """Set figure and canvas colours to be the same."""
      plt.gcf().set_facecolor( color )
      plt.gcf().set_edgecolor( color )
      self.canvas.SetBackgroundColour( color )

  def on_pick(self, event):
      # print dir(event)
      # print "artist", dir(event.artist)
      # print "picker", dir(event.artist.get_picker)
      # print "pickradius", dir(event.artist.get_pickradius)
      # print "get_snaP", dir(event.artist.get_snap)
      # ind = event.ind

      selectedlist = [False] * len(self.editData.DataValues)
      print len(selectedlist)
      for ind in event.ind:
        self.selectedlist[ind]=True
      #change slecteion on plot
      self.changeSelection(selectedlist)
      #change selection in table
      Publisher().sendMessage(("changeTableSelection"), selectedlist)


      # print(event.ind, np.take(self.editDateTimes, event.ind), np.take(self.editDataValues, event.ind))

  def Close(self):
    plt.close()



  # def onclick(self, event):
  #     print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(event.button, event.x, event.y, event.xdata, event.ydata)

  def BuildPopup(self):
      # build pop-up menu for right-click display
      self.popup_unzoom_all = wx.NewId()
      self.popup_unzoom_one = wx.NewId()
      self.popup_config     = wx.NewId()
      self.popup_save   = wx.NewId()
      self.popup_menu = wx.Menu()
      self.popup_menu.Append(self.popup_unzoom_one, 'Zoom out')
      self.popup_menu.Append(self.popup_unzoom_all, 'Zoom all the way out')
      self.popup_menu.AppendSeparator()




  def __init__(self, parent, id, pos, size, style, name):
      self._init_ctrls(parent)




class plotData (object):
  def __init__(self, sID, dValues, dTimes,  ylabel, title, color ):
    self.SeriesID= sID
    self.DataValues = dValues
    self.DateTimes=dTimes

    self.startDate= min(dTimes)
    self.endDate=max(dTimes)
    self.ylabel = ylabel
    self.title = title
    self.color = color

class axisData (object):
  def __init__(self, axisid, axis,  position, side="", rightadjust="", leftadjust="", minx="", maxx=""):
    self.axisid= axisid
    self.axis = axis
    self.rightadjust= rightadjust
    self.leftadjust = leftadjust
    self.position = position
    self.side = side
    self.minx= minx
    self.maxx= maxx

  def __repr__(self):
    return "<AxisData(id:'%s', axis:'%s', pos:'%s', side:'%s', radj:'%s', ladj:'%s')>" % (self.axisid, self.axis, self.position, self.side, self.rightadjust, self.leftadjust)



