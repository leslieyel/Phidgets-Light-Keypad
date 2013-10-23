'''
Created on 16 Nov 2012

@author: luy
'''


class SitwPara():
    
    Title = 'SitW Phidgets Key       v4.6 GH v1.3'
    
    
    FilePath_Ini = '..\\cfg\\SitwPhidgetsKey.ini'
    FilePath_Log = '..\\log\\'
  
    
    KeyCount = 5
    Sensitivity = 0.60
    MovingPace = 10
    SampleInterval_Key = 50      #ms
    SampleInterval_Env = 10000   #ms 
    Log_Action = 'No'
    Log_Brightness = 'No'
      
    
    
    List_mb = [(0.02791, -1.3636), (0.02326, 0.04842), (0.02314, -0.8407), (0.02224, -0.3320), (0.02364, -0.4611)]       #NAE 
    #List_mb = [(0.02621, -0.6873), (0.02326, 0.04842), (0.02382, 0.32172), (0.02224, -0.3320), (0.02232, -0.5144)]      #MRL            

    List_ButtonPos = [(110, 120, 100, 100), (10, 120, 100, 100), (210, 120, 100, 100), (110, 20, 100, 100), (110, 220, 100, 100)]
    List_Action = ['clicked', 'left', 'right', 'up', 'down']
    
    List_KeyCheckOrder = [3, 1, 0, 2, 4] #up>left>click>right>down 
    
    

    MoveEdgeBottom1 = 50
    MoveEdgeBottom2 = 300
    
    
    
    '''
    GH V1.3
    Add double-click action after covering 'click' key for 2 seconds
    
    
    GH v1.2
    Remove project relevant parameters
    Change edge area
    
    
    GH v1.1
    Cursor names changed
    
    
    v4.6 GitHub v1.0
    Remove schedule relevant parts - concentrate on Phidgets Light-Keypad
    
    
    v4.6
    fix mouse pointer position when running Mooderator
    download schedule.txt every 5 minutes 
    
    v4.5
    not only determine key pressed by finding the lowest brightness, but also by the position of the key 
    Channel 0: <click>, Channel 1: <left>, Channel 2: <right>, Channel 3: <up>, Channel 4: <down>
    Search order: up>left>click>right>down
     
    v4.4
    use win32api.mouse_event to control mouse movement; a mouse event will be triggered when moving
    '''
    
    
    