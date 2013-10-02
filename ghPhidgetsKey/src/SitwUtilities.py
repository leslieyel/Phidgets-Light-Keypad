'''
Created on 29 Jan 2013

@author: YL
'''


import os
import datetime
#import urllib2
from SitwData import SitwPara as sitwPara



    
class SitwLog():
    
    def __init__(self, parent, logName):

        self.phidgetsKey = parent
        self.logName = logName        
        self.logPath = sitwPara.FilePath_Log + self.logName
        self.logMessage = '\n\n'
        self.logReady = False
        
        if self.makeDir(self.logPath) == True:
            self.phidgetsKey.prtMsg('Log directory <' + self.logPath + '> is ready')
            self.logReady = True
        else:
            self.phidgetsKey.prtMsg('Log directory <' + self.logPath + '> is NOT ready')
            
        
                
    def logMsg(self, strLog):    
        
        dtCurrentTime = datetime.datetime.now()
        strTimeTag = datetime.datetime.strftime(dtCurrentTime, '%Y-%m-%d %H:%M:%S')
        strLog = strTimeTag + '\t' + strLog
        print(strLog)  
        self.logMessage += strLog + '\n'
    
    
    
    def wrtLog(self, bForce):
        
        if self.logReady == False:
            self.phidgetsKey.prtMsg('Log directory <' + self.logPath + '> is NOT ready')
            return        
        
        if bForce or len(self.logMessage) > 1024:
            '''save to file....'''
            log = None
            logFile = self.logPath + '\\' + self.getFileName()
            
            try:                
                log = open(logFile, 'a')
                log.write(self.logMessage)
                
            except: #IOError
                self.phidgetsKey.prtMsg('Error >>> ' + logFile + ' write failure.')
            
            finally:
                if log:
                    log.close()               
            
            self.logMessage = ''
    

    
    def getFileName(self):
        
        dtCurrentTime = datetime.datetime.now()
        self.strFileNameDate = datetime.datetime.strftime(dtCurrentTime, '%Y%m%d')
        #self.strFileNameTime = datetime.datetime.strftime(dtCurrentTime, '%H%M%S')
        strFileName = self.logName + '_' + self.strFileNameDate + '.txt'
        return strFileName
    
    
    
    def makeDir(self, logPath):
        
        try:
            if not os.path.exists(logPath):
                os.makedirs(logPath)
        except Exception:
            pass  
        
        if os.path.exists(logPath):
            return True
        else:
            return False    
    
        