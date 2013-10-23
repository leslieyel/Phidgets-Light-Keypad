
'''
Created on 16 Nov 2012

@author: luy
'''


import wx
#import os
#import time
import datetime
import math

import ConfigParser

from SitwData import SitwPara as sitwPara
#from SitwUtilities import SitwScheduleTools
from SitwUtilities import SitwLog

from ctypes import *
#import sys
#import random

###Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
#from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, OutputChangeEventArgs, SensorChangeEventArgs
from Phidgets.Devices.InterfaceKit import InterfaceKit

import win32api
import win32con
#import win32gui




class SitwPhidgetsKey(wx.Frame):
    
 
    def __init__(self, image, parent = None, id = -1,
                 pos = wx.DefaultPosition, title = sitwPara.Title):
        

        wx.Frame.__init__(self, parent, id, title)
                
        self.SetBackgroundColour((0, 0, 0))    
        self.SetSize((360, 80))
        self.Center()
        self.Iconize()
        
        self.panel = wx.Panel(self, size=(320, 336)) 
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint) 
        #self.panel.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Fit() 
            
        
        self.SampleCount = 12 #for detecting environment 12 x 10sec = 2min
        self.KeyPressed = ''
        self.CurAction = ''
        self.CurPos = win32api.GetCursorPos()
        self.PreAction = ''
        self.PrePos = win32api.GetCursorPos()
        self.bKeyIntervalOK = True
        self.KeyMatReady = False
        self.ListValMat = []
        self.ListValEnv = []
        self.ListValBrt = []
        self.KeySearch = False
        self.dtSearchStart = datetime.datetime.now()
        self.dtAction = datetime.datetime.now()
        self.dtRefresh = datetime.datetime.now()
        self.ChannelCount = 0
        self.bNight = False
        self.ctEvn = 0
        
        #self.edgeTop = 50
        #self.edgeBottom = sitwPara.MoveEdgeBottom1
        #self.edgeLeft = 50
        #self.edgeRight = 50
        
        self.edgeTop = 25
        self.edgeBottom = 25
        self.edgeLeft = 25
        self.edgeRight = 25        
       
        self.strLogAction = ''
        self.strLogBrightness = ''
                      
        self.subp = None
        self.List_ProgramFile = []
        self.List_Program = []
        self.OnScreenApp = ''
        
        #self.utSchedule = SitwScheduleTools(self)
        self.utLogAction = SitwLog(self, 'logAction')
        self.utLogBrightness = SitwLog(self, 'logBrightness')
       
       
       
        
        #self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        
 
        self.prtMsg('PhidgetsKey Starting...')
 
        self.readIniFile()
                
        
        self.initPhidgets()
        self.initKeys()
                            
        
        '''collect ambient light info'''
        self.timer1 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.CheckEnv, self.timer1)
        self.timer1.Start(sitwPara.SampleInterval_Env) #1000 = 1 second        


        '''check if there is any key has been covered'''
        self.timer2 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.CheckKey, self.timer2)
        self.timer2.Start(sitwPara.SampleInterval_Key) #1000 = 1 second   
            
            
        '''find current on screen experience according to schedule file'''    
        ''' -- removed --'''

                
        '''collect sensor readings for analysis'''
        if sitwPara.Log_Brightness == 'Yes':
            print '<Log_Brightness On>'
            self.timer5 = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.logBrightness, self.timer5)
            self.timer5.Start(60 * 1000) #1000 = 1 second   
            
            self.utLogBrightness.logMsg('------ log is starting ------\t' + sitwPara.Title)
            self.logBrightness(None)
        else:
            print '<Log_Brightness Off>'     
            
                        
        '''collect keypad actions for analysis'''
        if sitwPara.Log_Action == 'Yes':
            print '<Log_Action On>'
            self.timer6 = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.logActions, self.timer6)
            self.timer6.Start(9 * 1000) #1000 = 1 second      
            
            self.utLogAction.logMsg('------ log is starting ------\t' + sitwPara.Title)
        else:
            print '<Log_Action Off>'            
            
            
            
        ###Change Cursor
        ###http://converticon.com/
        ### http://stackoverflow.com/questions/7921307/temporarily-change-cursor-using-python
        self.SetSystemCursor = windll.user32.SetSystemCursor #reference to function
        self.SetSystemCursor.restype = c_int #return
        self.SetSystemCursor.argtype = [c_int, c_int] #arguments
        
        self.LoadCursorFromFile = windll.user32.LoadCursorFromFileA #reference to function
        self.LoadCursorFromFile.restype = c_int #return
        self.LoadCursorFromFile.argtype = c_char_p #arguments
         
        CursorPath ='../pic/handr.cur'
        NewCursor = self.LoadCursorFromFile(CursorPath)
        
        if NewCursor is None:
            print "Error loading the cursor"
        elif self.SetSystemCursor(NewCursor, win32con.IDC_ARROW) == 0:
            print "Error in setting the cursor"
        ###Change Cursor
        
                    
        self.DimScreen = wx.DisplaySize()
        print 'Screen Dimensions: ' + str(self.DimScreen[0]) + ' x ' + str(self.DimScreen[1])     
        
                
        ##########################################             
        '''m,b parameters for each sensor'''      
        for i in range(len(sitwPara.List_mb)):
            print '=====   ', sitwPara.List_mb[i][0], sitwPara.List_mb[i][1]            
        ##########################################    
                
                
                
    ### not in use at the moment
    def OnEraseBackground(self, event):
        return True
        
                
                        
    def OnPaint(self, event):
        '''
        # establish the painting surface
        dc = wx.PaintDC(self.panel)
        dc.SetPen(wx.Pen('blue', 4))
        # draw a blue line (thickness = 4)
        dc.DrawLine(50, 20, 300, 20)
        dc.SetPen(wx.Pen('red', 1))
        # draw a red rounded-rectangle
        rect = wx.Rect(50, 50, 100, 100) 
        dc.DrawRoundedRectangleRect(rect, 8)
        # draw a red circle with yellow fill
        dc.SetBrush(wx.Brush('yellow'))
        x = 250
        y = 100
        r = 50
        dc.DrawCircle(x, y, r)
        '''

        #dc = wx.PaintDC(self.panel)
        
        dc = wx.BufferedPaintDC(self.panel)
        dc.SetBackground(wx.BLUE_BRUSH)
        dc.Clear()        
        
        self.onDraw(dc)       

                
                
    def onDraw(self, dc):                

        strColorPen1 = 'red'
        strColorPen2 = 'blue'
        
        for i in range(sitwPara.KeyCount):
            
            rect = sitwPara.List_ButtonPos[i]
            dc.SetBrush(wx.Brush((0, 255*self.ListValBrt[i], 255*self.ListValBrt[i])))    
            if self.KeyPressed == sitwPara.List_Action[i]:
                dc.SetPen(wx.Pen(strColorPen1, 5))
            else:
                dc.SetPen(wx.Pen(strColorPen2, 1))
                #dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRoundedRectangleRect(rect, 8)
        
        
                
    def initPhidgets(self):
        try:
            self.interfaceKit = InterfaceKit()
        except RuntimeError as e:
            print("Runtime Exception: %s" % e.details)
            print("Exiting....")
            exit(1)
        
        try:
            self.interfaceKit.setOnAttachHandler(self.inferfaceKitAttached)
            self.interfaceKit.setOnDetachHandler(self.interfaceKitDetached)
            self.interfaceKit.setOnErrorhandler(self.interfaceKitError)
            self.interfaceKit.setOnInputChangeHandler(self.interfaceKitInputChanged)
            self.interfaceKit.setOnOutputChangeHandler(self.interfaceKitOutputChanged)
            self.interfaceKit.setOnSensorChangeHandler(self.interfaceKitSensorChanged)
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")
            exit(1)
        
        print("Opening phidget object....")
        
        try:
            self.interfaceKit.openPhidget()
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")
            exit(1)
        
        print("Waiting for attach....")
        
        try:
            self.interfaceKit.waitForAttach(10000)
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            self.closePhidgets()
        else:
            self.displayDeviceInfo()
        
        
        #get sensor count
        try:
            self.ChannelCount = self.interfaceKit.getSensorCount()
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            self.closePhidgets()
            sitwPara.KeyCount = 0 #no sensor has been detected
            self.prtMsg('   ****** No sensor has been detected !!!\n')
        
        
        print("Setting the data rate for each sensor index to 4ms....")
        for i in range(sitwPara.KeyCount):
            try:
                self.interfaceKit.setDataRate(i, 4)
            except PhidgetException as e:
                print("Phidget Exception %i: %s" % (e.code, e.details))
        
        
        ### depends on the low light performance of the sensor
        print("Setting the sensitivity for each sensor index to ???....")
        for i in range(sitwPara.KeyCount):
            try:
                self.interfaceKit.setSensorChangeTrigger(i, 2)              #~~~~*YL*~~~~
            except PhidgetException as e:
                print("Phidget Exception %i: %s" % (e.code, e.details))
        
        

    def closePhidgets(self):
        #print("Press Enter to quit....")
        #chr = sys.stdin.read(1)
        #print("Closing...")
        
        try:
            self.interfaceKit.closePhidget()
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")
            exit(1)
        
        #print("Done.")
        #exit(1)



    def initKeys(self):
        
        self.KeyPressed = ''

        self.ListValMat = []                
        for i in range(sitwPara.KeyCount):
            self.ListValEnv = []
            for j in range(self.SampleCount):
                self.ListValEnv.append(self.readSensorValue(i))
            self.ListValMat.append(self.ListValEnv)
        
        self.KeyMatReady = True
     
             
        self.ListValBrt = []
        for i in range(sitwPara.KeyCount):
            self.ListValBrt.append(0)
        
     
     
    def readIniFile(self):
        self.prtMsg('Read system ini file...')
        
        try: 
            config = ConfigParser.ConfigParser()
            config.readfp(open(sitwPara.FilePath_Ini))
            
            for eachIniData in self.iniData():
                Section = eachIniData[0]
                Keys = eachIniData[1]
                            
                for Key in Keys:
                    val = config.get(Section, Key)
                    if (Section == "General"):
                        if (Key == "KeyCount"):
                            sitwPara.KeyCount = int(val)
                        elif (Key == "Sensitivity"):
                            sitwPara.Sensitivity = float(val)
                        elif (Key == "MovingPace"):
                            sitwPara.MovingPace = int(val)                            
                        elif (Key == "SampleInterval_Key"):
                            sitwPara.SampleInterval_Key = int(val)
                        elif (Key == "SampleInterval_Env"):
                            sitwPara.SampleInterval_Env = int(val)           
                        elif (Key == "Log_Action"):
                            sitwPara.Log_Action = str(val)           
                        elif (Key == "Log_Brightness"):
                            sitwPara.Log_Brightness = str(val) 
                                                                                                         
                        else:
                            pass
                            
                    print('[' + Section + '] ' + Key + ' = ' + val)
                    continue
                
        except: #IOError
            self.prtMsg('Error: readIniFile()')
        finally:
            pass
        
                

    def iniData(self):
        return (("General",
                ("KeyCount",
                 "Sensitivity",
                 "MovingPace",
                 "SampleInterval_Key",
                 "SampleInterval_Env",
                 "Log_Action",
                 "Log_Brightness")),)
                 
                 
                     
    #Information Display Function
    def displayDeviceInfo(self):
        print("|------------|----------------------------------|--------------|------------|")
        print("|- Attached -|-              Type              -|- Serial No. -|-  Version -|")
        print("|------------|----------------------------------|--------------|------------|")
        print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (self.interfaceKit.isAttached(), self.interfaceKit.getDeviceName(), self.interfaceKit.getSerialNum(), self.interfaceKit.getDeviceVersion()))
        print("|------------|----------------------------------|--------------|------------|")
        print("Number of Digital Inputs: %i" % (self.interfaceKit.getInputCount()))
        print("Number of Digital Outputs: %i" % (self.interfaceKit.getOutputCount()))
        print("Number of Sensor Inputs: %i" % (self.interfaceKit.getSensorCount()))
    
    
    #Event Handler Callback Functions
    def inferfaceKitAttached(self, e):
        attached = e.device
        print("InterfaceKit %i Attached!" % (attached.getSerialNum()))
    
    
    def interfaceKitDetached(self, e):
        detached = e.device
        print("InterfaceKit %i Detached!" % (detached.getSerialNum()))
    
    def interfaceKitError(self, e):
        try:
            source = e.device
            print("InterfaceKit %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
    
    def interfaceKitInputChanged(self, e):
        source = e.device
        print("InterfaceKit %i: Input %i: %s" % (source.getSerialNum(), e.index, e.state))
    
    
    
    def interfaceKitSensorChanged(self, e):
        
        if not self.KeyMatReady:
            return
                
        #source = e.device
        #print("InterfaceKit %i: Sensor %i: %i" % (source.getSerialNum(), e.index, e.value))
        
        if not self.KeySearch:
            self.KeySearch = True
            
        self.dtSearchStart = datetime.datetime.now()
            
                                       

    def interfaceKitOutputChanged(self, e):
        source = e.device
        print("InterfaceKit %i: Output %i: %s" % (source.getSerialNum(), e.index, e.state))





    def readSensorValue(self, channel_id):
        val = 0.0
        try:
            val = self.interfaceKit.getSensorValue(channel_id)
            #val = self.interfaceKit.getSensorRawValue(channel_id) / 4.095
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))

        #val = 1.478777 * float(val) + 33.67076         #------ for 1142_0: Lux = m * SensorValue + b
        #val = math.exp(0.02385 * float(val) - 0.56905) #------ for 1143_0: Lux = math.exp(m * SensorValue + b)
        #val = math.exp(sitwPara.List_mb[channel_id][0] * float(val) + sitwPara.List_mb[channel_id][1]) #------ for 1143_0: Lux = math.exp(m * SensorValue + b)
        
        return val



    def CheckEnv(self, event):
        
        for i in range(sitwPara.KeyCount):
            
            ValIns = self.readSensorValue(i)
            ValEnv = sum(self.ListValMat[i]) / len(self.ListValMat[i])
            
            if (float(ValIns) / float(ValEnv)) > 0.70 or self.ctEvn >= 2: #natural change or the big change keeps for long time
                self.ListValMat[i].pop(0)
                self.ListValMat[i].append(ValIns)
                self.ctEvn = 0
            else:
                self.ctEvn += 1    #ignore those suddenly changes 
            
            
        ###test 
        #for val in self.ListValMax:
        #    print val, '->', sum(val)/len(val)
        #print '-------------------------------------------------------'
                    

    def CheckKey(self, event):
        
        if not self.KeySearch:
            return
        
        dtCurrentTime = datetime.datetime.now()
        
        if dtCurrentTime - self.dtSearchStart > datetime.timedelta(microseconds = 6000000): # =6s ; 1000000 = 1s 
            self.KeySearch = False
        
        if dtCurrentTime - self.dtAction > datetime.timedelta(microseconds = 500000): # =0.5s ; 1000000 = 1s
            self.bKeyIntervalOK = True
        else:
            self.bKeyIntervalOK = False
        
            
        self.bNight = True
        
        for i in range(sitwPara.KeyCount):
            ValIns = self.readSensorValue(i)
            ValEnv = sum(self.ListValMat[i]) / len(self.ListValMat[i])

            if ValEnv > 20.0:
                self.bNight = False

            self.ListValBrt[i] = float(ValIns) / float(ValEnv) 
            
            if self.ListValBrt[i] > 1.0:
                self.ListValBrt[i] = 1.0
                
                            
        #sort
        #self.ListValBrt.sort(cmp = None, key = None, reverse = False) 
        
        if self.bNight == False:
            NightFactor = 1.0
        else:
            NightFactor = 1.8        
    
    
        #KeyID = self.ListValBrt.index(min(self.ListValBrt))
        for i in range(sitwPara.KeyCount):   
            KeyID = sitwPara.List_KeyCheckOrder[i]
            if self.ListValBrt[KeyID] < (sitwPara.Sensitivity * NightFactor):
                bKey = True                    
                break
            else:
                bKey = False
                
                        
        if bKey == True:                        
            if KeyID == 1:
                if self.KeyPressed == 'left' or self.bKeyIntervalOK == True:
                    self.KeyPressed = 'left'
                    self.dtAction = datetime.datetime.now()
                else:
                    self.KeyPressed = ''                    
            elif KeyID == 2:
                if self.KeyPressed == 'right' or self.bKeyIntervalOK == True:
                    self.KeyPressed = 'right'
                    self.dtAction = datetime.datetime.now()
                else:
                    self.KeyPressed = ''                     
            elif KeyID == 3:
                if self.KeyPressed == 'up' or self.bKeyIntervalOK == True:
                    self.KeyPressed = 'up'
                    self.dtAction = datetime.datetime.now()
                else:
                    self.KeyPressed = ''                             
            elif KeyID == 4:
                if self.KeyPressed == 'down' or self.bKeyIntervalOK == True:
                    self.KeyPressed = 'down'
                    self.dtAction = datetime.datetime.now()
                else:
                    self.KeyPressed = ''                     
            elif KeyID == 0: 
                if self.KeyPressed != 'click' and self.KeyPressed != 'clicked' and self.KeyPressed != 'dclick' and self.KeyPressed != 'dclicked' and self.bKeyIntervalOK == True:
                    self.KeyPressed = 'click'
                    self.dtAction = datetime.datetime.now()       
                elif self.KeyPressed != 'dclick' and self.KeyPressed != 'dclicked' and (dtCurrentTime - self.dtAction > datetime.timedelta(microseconds = 2200000)): # =2.2s ; 1000000 = 1s
                    self.KeyPressed = 'dclick'
                    self.dtAction = datetime.datetime.now()      

        else:
            self.KeyPressed = ''
        
        
        
        if len(self.KeyPressed) > 0:
                        
            ###filter
            #-- removed ---
            ###filter
                        
            pos = win32api.GetCursorPos()
            if self.KeyPressed == 'up':
                if pos[1] >= self.edgeTop:
                    #nx = (pos[0]) * 65535.0 / self.DimScreen[0]
                    #ny = (pos[1] - sitwPara.MovingPace) * 65535.0 / self.DimScreen[1]
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, -sitwPara.MovingPace)
                    #win32api.SetCursorPos((pos[0], pos[1] - sitwPara.MovingPace))            
            elif self.KeyPressed == 'down':
                if pos[1] <= self.DimScreen[1] - self.edgeBottom:
                    #nx = (pos[0]) * 65535.0 / self.DimScreen[0]
                    #ny = (pos[1] + sitwPara.MovingPace) * 65535.0 / self.DimScreen[1]
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, +sitwPara.MovingPace)                   
                    #win32api.SetCursorPos((pos[0], pos[1] + sitwPara.MovingPace))            
            elif self.KeyPressed == 'left':                                                         
                if pos[0] >= self.edgeLeft:
                    #nx = (pos[0] - sitwPara.MovingPace) * 65535.0 / self.DimScreen[0]
                    #ny = (pos[1]) * 65535.0 / self.DimScreen[1]
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -sitwPara.MovingPace, 0)                    
                    #win32api.SetCursorPos((pos[0] - sitwPara.MovingPace, pos[1]))          
            elif self.KeyPressed == 'right':
                if pos[0] <= self.DimScreen[0] - self.edgeRight:
                    #nx = (pos[0] + sitwPara.MovingPace) * 65535.0 / self.DimScreen[0]
                    #ny = (pos[1]) * 65535.0 / self.DimScreen[1]
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, +sitwPara.MovingPace, 0)                    
                    #win32api.SetCursorPos((pos[0] + sitwPara.MovingPace, pos[1]))      
            elif self.KeyPressed == 'click':
                self.click(pos[0], pos[1])
                #print '**********click**************'         
                self.KeyPressed = 'clicked'   
            elif self.KeyPressed == 'dclick':
                self.dclick(pos[0], pos[1])   
                #print '**********dclick**************'         
                self.KeyPressed = 'dclicked'
                    
            
        ###Action Log
        if sitwPara.Log_Action == 'Yes':
            self.CurAction = self.KeyPressed
            self.CurPos = win32api.GetCursorPos()
                         
            if self.CurAction != self.PreAction and len(self.PreAction) > 0:                 
                #dtCurrentTime = datetime.datetime.now()
                #strTimeTag = datetime.datetime.strftime(dtCurrentTime, '%Y-%m-%d %H:%M:%S')
                #pos = win32api.GetCursorPos()
                strLog = self.PreAction + '\t(' + str(self.PrePos[0]) + ',' + str(self.PrePos[1]) + ')' \
                            + '\t' + self.OnScreenApp
                self.utLogAction.logMsg(strLog)
                    
            self.PreAction = self.CurAction
            self.PrePos = self.CurPos
                
        
            
    def click(self, x,y):
        win32api.SetCursorPos((x,y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
        
        
    def dclick(self, x,y):
        win32api.SetCursorPos((x,y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
        


    def logBrightness(self, event):
        strValEnv = ''
        for i in range(sitwPara.KeyCount):
            ValEnv = sum(self.ListValMat[i]) / len(self.ListValMat[i])
            strValEnv += str('%06.2f'%(ValEnv)) + '\t'
        
        self.utLogBrightness.logMsg(strValEnv)    
        self.utLogBrightness.wrtLog(False)



    def logActions(self, event):
        self.utLogAction.wrtLog(False)
                
                        
            
    def GetSchedule(self, event):
        # --removed --
        pass
        
                             

    def FindAppName(self, event):
        # --removed --
        pass
    
                

    def prtMsg(self, strMsg):
        dtCurrentTime = datetime.datetime.now()
        strTimeTag = datetime.datetime.strftime(dtCurrentTime, '%Y-%m-%d %H:%M:%S')
        #strTimeTag += str('%03d'%(int(datetime.datetime.strftime(dtCurrentTime, '%f'))/1000))
        print(strTimeTag + '   ' + strMsg + "\n")  
          
                    

    def OnIdle(self, event):    
        if not self.KeySearch:
            return
        dtCurrentTime = datetime.datetime.now()
        
        if dtCurrentTime - self.dtRefresh > datetime.timedelta(microseconds = 200000): #1000000 = 1s 
            self.dtRefresh = dtCurrentTime
            self.panel.Refresh(eraseBackground = False)
     
        pass


                
                
    def OnCloseWindow(self, event):
        print "Do something b4 closing..."

        ###Change Cursor        
        CursorPath = "../pic/arrow.cur"
        NewCursor = self.LoadCursorFromFile(CursorPath)
        if NewCursor is None:
            print "Error loading the cursor"
        elif self.SetSystemCursor(NewCursor, win32con.IDC_ARROW) == 0:
            print "Error in setting the cursor"
        ###Change Cursor
        
                    
        self.closePhidgets()
        
        self.prtMsg('Destroy Phidgets Key')
   
        if sitwPara.Log_Action == 'Yes':
            self.utLogAction.wrtLog(True) #force to log all messages
        if sitwPara.Log_Brightness == 'Yes':
            self.utLogBrightness.wrtLog(True) #force to log all messages            
        
        #time.sleep(1)
        self.Destroy()
                               
         
        
        
        
class SitwPhidgetsKeyApp(wx.App):
    """Application class."""

    def OnInit(self):
        self.frame = SitwPhidgetsKey("")
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True


if __name__ == '__main__':
    app = SitwPhidgetsKeyApp(False)
    app.MainLoop()
    app.Exit()










    
    


        
        
