import streamlit as st
import pandas as pd
import numpy as np
from PracticeMaster_entry_fns import *
from datetime import datetime as dt
import datetime as datetime
import pickle
import os.path
from dotDict import dotDict
# streamlit guide to gsheets: https://docs.streamlit.io/develop/tutorials/databases/private-gsheet
# issues with installing streamlit_gsheets: https://discuss.streamlit.io/t/help-with-st-gsheets-connection/58208
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe

sss=st.session_state

def zTime():
    return(f"{dt.now():%H:%M:%S}")

def writeData():
    dataWS = sss.appDATA.worksheet("practData")
    set_with_dataframe(dataWS, sss.practiceData)

def updateAndWriteCurrentSels():
    # master sheet row = practice number plus 2!
    selz=sss.pracToSels[sss.activePractice.replace(" ", "_")]
    for i in range(0, sss.pracDict["NumberOfLevels"]):
        if stVal(sss.LEVZ[i]):
            sss.pracDict.SELZ[sss.LEVZ[i]]=sss[sss.LEVZ[i]]
            selz[i]=sss[sss.LEVZ[i]]
        else:
            sss.pracDict.SELZ[sss.LEVZ[i]]=None
            selz[i]=None
    sss.pracToSels[sss.activePractice.replace(" ", "_")]=selz
    #print("SELZ", sss.pracDict.SELZ)
    #print("selz", selz)

    row=sss.PractToNum[sss.activePractice]+2
    z=list(sss.pracDict.SELZ.values())
    #print("row, z", row , z)
    sss.masterWS.update_cell(row,3, str(z))

def updateAndWriteNewPractice():    
    sss.activePractice=sss.newPractice
    # make sure this is the right cell!  ... E2
    sss.masterWS.update_cell(2,5, sss.activePractice)

def updateNodeChoices():
    tPoint=1
    for key in sss.SELS:
        if sss.SELS[key].lastChoice:
            sss.practWS.update_cell(tPoint,1, key)
            sss.practWS.update_cell(tPoint,2, sss.SELS[key].lastChoice)
            tPoint+=1

def findSel(zItem, zList):
    if zItem==None:
        return(None)
    try:
        zLen=len(zList)
    except:
        return(None)
    for i in range(0,zLen):
        if zItem==zList[i]:
            return(i)
    return(None)

def varRpt(*args):
    def retrieve_name(var):
        import inspect
        import dotDict
        callers_local_vars = inspect.currentframe().f_back.f_back.f_locals.items()
        lvn=[var_name for var_name, var_val in callers_local_vars if var_val is var]
        if len(lvn)>0:
            return(lvn[0])
        else:
            callers_global_vars = inspect.currentframe().f_globals.items()
            gvn=[var_name for var_name, var_val in callers_global_vars if var_val is var]
            if len(gvn)>0:
                return(gvn[0])
            else:
                return(None)            
            
    vString=">>> "
    for var in args:
            vString=vString+" "+retrieve_name(var)+": "+str(var)
    print(vString)

def updateActDefined():
    # update everywhere important
    # master: pracToSels - 
    # pracDict: SELZ -
    print("updateActDefined")
    defined=False
    for node in sss.sNodes:
        if node in [False, None]: 
            break
        if node=="REPORT":
            defined=True
            break

    print("defined, sss.sNodes:", defined, sss.sNodes)

    if defined==True:
        # write to sheet    
        #updateAndWriteCurrentSels()
        sss.ActDefined=True
        return(True)                        
    else:
        sss.ActDefined=False
        return(False)

# get worksheet from a gspread workbook 
def getGSheetAsDF(zWorkbook, sheetName):
    wksh=zWorkbook.worksheet(sheetName)
    df=get_as_dataframe(wksh)
    return(df)

def getGSheetAsDfNoHeader(zWorkbook, sheetName):
    wksh=zWorkbook.worksheet(sheetName)
    df=pd.DataFrame(wksh.get_all_values())
    return(df)


# used with splitList to identify list targ is in
def findSeg(targ, Segs):
    i=0
    for Seg in Segs:
        for item in Seg:
            if targ == item:
                return(i)
        i+=1
    return(None)

def iiff(Bool, Resp):
    if Bool:
        return(Resp)
    else:
        return()

# input: string with no curly brackets or quotes
def makeDictFromStringNEW(Str):
    yx= [x.split(":") for x in Str.split(",")]
    yx2=[ [a.strip(), b.strip()] for a, b in yx]
    yz= { a:b for a, b in yx2}
    return(yz)

# input: string WITH curly brackets AND quotes
def makeDictFromString(zVar):
    # seems must use ss var for exec to work properly
    sss.xxx=dotDict()
    exec("sss.xxx={"+zVar+"}")
    return(sss.xxx)

# int not allowed
def makeListFromString(Str):
    Str=Str.strip("[]")
    yx= [x.strip().strip("'") for x in Str.split(",")]
    yx= [None if x=='None' else x for x in yx]
    yx= [str(x) if type(x)==int else x for x in yx]
    return(yx)

# returns true if variable has a value, false if it does not have a value and none if does not exist 
def stVal(zVar):
    exec("sss.xxxxx= '" + zVar + "' in sss")
    # true if var in session_state, so return True if it has a value
    if sss.xxxxx:
        exec("sss.xxxxx_y=sss."+zVar)
        return(sss.xxxxx_y)
    else:
        return(None)

def getLevRange(nodes, point):
    lenz=[]
    tNode=nodes[point]
    if tNode==None:
        return(None, None)
    for path in sss.pracDict.cPATHZ:
        if len(path)>=point+1:
            if path[point]==tNode:
                lenz.append(len(path))
    return(min(lenz)-2, max(lenz)-2)

def lookForUniqueNextNode(nodes, point):
    lenz=[]
    tNode=nodes[point]
    if tNode==None:
        return(None)
    for path in sss.pracDict.cPATHZ:
        if len(path)>=point+2:
            if path[point]==tNode:
                if path[point+1] not in lenz:
                    lenz.append(path[point+1])
    if len(lenz)==1:
        return(lenz[0])
    else:
        return(None)


def getMasterData():

    # basic
    sss.LEVZ=['rowLev1','rowLev2','rowLev3','colLev1','colLev2']

    # gspread
    gc = gspread.service_account(filename='client_secret.json')

    # Create the data connection with target worksheet 
    if len(sss.argv)==1:
        sss.appDATA = gc.open("PracticeMasterData")
    else:
        # assumes named google sheet passed as argument to PracticeMaster.py
        sss.appDATA = gc.open(sss.argv[1])

    # read master sheet
    sss.baseData = getGSheetAsDF(sss.appDATA, "Master")
    #print(sss.baseData)

    # get practice data    
    sss.practiceData = getGSheetAsDF(sss.appDATA, "practData")

    #set Master worksheet as data object
    sss.masterWS = sss.appDATA.worksheet("Master")

    # get base or "master" data columns
    sss.Practices=sss.baseData['Practice'].dropna().tolist()
    sss.Sheets=sss.baseData['Sheet'].dropna().tolist()
    sss.EntryDimSelections=sss.baseData['EntryDimSelections'].dropna().tolist()
    keyz=sss.baseData['Dict Keys'].dropna().tolist()
    valz=sss.baseData['Dict Values'].dropna().tolist()
    
    # convert strings to lists
    for ii in  range(0, len(sss.EntryDimSelections)):
        sss.EntryDimSelections[ii]=makeListFromString(sss.EntryDimSelections[ii])

    #print(sss.baseData, sss.Practices, sss.Sheets)

    # practices to sheets map
    xx=dotDict()
    for x, y in zip(sss.Practices, sss.Sheets):
        exec('xx["' + x.replace(" ","_") + '"] = "'+y+'"', locals()) 
    sss.PractToSheet=xx

    # practices to practice worksheet row
    xx=dotDict()
    i=0
    for pract in sss.Practices:
        xx[pract]=i
        i+=1
    sss.PractToNum=xx

    # practices to stored selection map -- selection map is a string form of a list
    sss.pracToSels=dotDict()
    for x, y in zip(sss.Practices, sss.EntryDimSelections):
        #print("PTS:", x,y)
        xr=x.replace(" ","_")
        if len(y)>0:
            sss.pracToSels[xr] = y 
        else:
            # empty list
            sss.pracToSels[xr] = []
    #print("GetMasterData PracToSels", sss.PracToSels)

    # master dict keys to vals map
    sss.Globals=dotDict()
    for x, y in zip(keyz, valz):
        xr=x.replace(" ","_")
        sss.Globals[xr] = str(y) 

    # Identify active practice    
    sss.activePractice = sss.Globals['activePractice']
    print("activePractice", sss.activePractice)

    if sss.activePractice:
        sss.selectPractice=False

    #print("GLOBALS", sss.Globals)
    sss.masterDataIsRead=True

    # widget key dot dict
    sss.stEKey=dotDict()


# create switched options sets
def updateSwitchNodeOptions(curNode):
    # get dow, curtable
    if sss.SELS[curNode].doSwitchColsByDay:
        days=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
        switchTable=sss.SELS.TABLES[sss.SELS[curNode].currTable]
        sss.SELS[curNode].swOPTS=[]
        sss.SELS[curNode].combOPTS=[]
        for i in range(len(sss.SELS[curNode].OPTS)):
            sss.SELS[curNode].swOPTS.append(switchTable[days[sss.SELS[curNode].switch[0]]][i])
            if sss.SELS[curNode].doCombineStandard==True:
                sss.SELS[curNode].combOPTS.append(sss.SELS[curNode].OPTS[i] + " -> " + sss.SELS[curNode].swOPTS[i])
            #print(sss.SELS[curNode].combOPTS[i])
        return(dt.now().weekday())   
         
    elif sss.SELS[curNode].doSwitchRowsByDay:
        #days=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
        condNode=sss.SELS[curNode].condNode
        targRow=sss.SELS[condNode].pIndex
        #print("ROWS targRow", targRow)
        switchTable=sss.SELS.TABLES[sss.SELS[curNode].currTable]
        sss.SELS[curNode].swOPTS=[]
        sss.SELS[curNode].combOPTS=[]
        #print(f"rows dow: {sss.SELS[curNode].switch[0]}")
        for i in range(len(sss.SELS[curNode].OPTS)):
            sss.SELS[curNode].swOPTS.append(switchTable.iloc[targRow][i])
            if sss.SELS[curNode].doCombineStandard==True:
                sss.SELS[curNode].combOPTS.append(sss.SELS[curNode].OPTS[i] + " -> " + sss.SELS[curNode].swOPTS[i])
            #print(sss.SELS[curNode].combOPTS[i])
        return(dt.now().weekday())        

def buildPracticeDataObjects():
    import networkx as nx
    sss.selGraph = nx.DiGraph()

    # pracDict is specific to the practice - all prior pracDict data is wiped
    sss.practDict=dotDict()
    sss.SELS=dotDict()
    sss.SELS.TABLES=dotDict()

    # get practice activeSheet 
    AP=sss.activePractice.replace(" ","_")
    TS=sss.PractToSheet[AP] 
    print(f"{dt.now():%H:%M:%S}, AP: {sss.activePractice}, {AP}, TS: {TS}")
    sss.pracDict=dotDict()
    sss.pracDict.hSheet=TS
    sss.practWS = sss.appDATA.worksheet(TS)

    print("getting prac data")
    sData = getGSheetAsDfNoHeader(sss.appDATA, sss.pracDict.hSheet)
    if not isinstance(sData, pd.DataFrame):
        print(f"ERROR READING SHEET {TS}. EXECUTION HALTED")
        st.stop
    sss.nRows, sss.nCols=sData.shape
    
    sss.pracDict.Entry=dotDict()

    # functions for read loop
    def readREC(tPoint, tPair, df):
        from math import isnan
        REC1=df.iloc[tPoint][tPair*2]
        if not isinstance(REC1, str):
            if isnan(REC1):
                REC1=""
        REC2=df.iloc[tPoint][tPair*2+1]
        if not isinstance(REC2, str):
            if isnan(REC2):
                REC2=""
        return(REC1, REC2)

    def readDict(tPoint, tPair, head, REC2):
        from math import isnan
        while True:
            tPoint+=1
            if tPoint>=sss.nRows-1:
                break
            #print("tPoint, tPair:", tPoint, tPair) 
            rec1, rec2 = readREC(tPoint, tPair, sData)
            if len(rec1)==0:
                break
            if rec1[0]=="#":
                continue
            # both strings
            elif isinstance(rec1, str) and isinstance(rec2, str):
                if len(rec1)>0 and len(rec2)>0:
                    sss.pracDict[rec1]=rec2
            # rec1 is string
            elif isinstance(rec1, str):
                if len(rec1)>0 and not isnan(rec2):
                    sss.pracDict[rec1]=rec2 
        return(tPoint)
            
    def readResponses(tPoint, tPair, head, REC2):
        i=0
        while True:
            tPoint+=1
            if tPoint>= sss.nRows-1:
                break
            rec1, rec2 = readREC(tPoint, tPair, sData)
            if len(rec1)==0:
                break
            if rec1[0]=="#":
                continue
            if len(rec1)==0 or len(rec2)==0:
                break
            sss.pracDict.Entry[i]=makeDictFromString(rec2)
            i+=1
        sss.pracDict.Entries=i
        sss.pracDict.EntryVars=[]
        for i in range(0, sss.pracDict.Entries):
            sss.pracDict.EntryVars.append(sss.pracDict.Entry[i]['var'])
        return(tPoint)

    def doSels(tPoint, tPair, head, REC2):

        #print(f"Reading select: {head[1]}.")
        #if head[1].isidentifier():
        #else:
        #    print(f"Error: invalid selection name: {head[1]}. Must be valid Python variable name.")

        def doGET(Table):
            sss.SELS.TABLES[Table]=getGSheetAsDF(sss.appDATA, Table)
            sss.SELS.TABLES[Table].set_index('Practice', inplace=True) 
            try:
                if len(sss.SELS.TABLES[Table])>0:
                    return(True)
            except:
                return(False)

        zHead=True
        sss.selGraph.add_node(head[1])
        #############################
        sss.SELS[head[1]]=dotDict()
        #############################
        sss.SELS[head[1]].doDayFocus=False
        sss.SELS[head[1]].doCombineStandard=False
        sss.SELS[head[1]].doSwitch=False
        sss.SELS[head[1]].doSwitchRowsByDay=False
        sss.SELS[head[1]].doSwitchColsByDay=False
        sss.SELS[head[1]].OPTS=[]
        sss.SELS[head[1]].MAP=dotDict()
        sss.SELS[head[1]].lastChoice=None
        sss.SELS[head[1]].proc="Normal"

        while tPoint<sss.nRows-2:
            tPoint+=1
            REC1, REC2 = readREC(tPoint, tPair, sData)
            # pass over comments
            if len(REC1)==0:
                break
            if REC1[0]=="#":
                continue
            recs=REC1.split("::")
            # double colon record
            if len(recs)>1:
                if zHead==True:
                    if recs[0]=="CAP":
                        #print("head//recs", head, recs)
                        sss.SELS[head[1]].CAP=recs[1]
                    elif recs[0]=="LAB":
                        sss.SELS[head[1]].LAB=recs[1]
                    elif recs[0]=="GET":
                        if recs[1]=='TABLE':
                            rc=doGET(REC2)
                        if rc==True:
                            sss.SELS[head[1]].currTable=REC2
                        else:
                            print(f"Error: Table {REC2} not accessed.")
                    elif recs[0]=="USE":
                        if recs[1]=='TABLE':
                            if REC2 in sss.SELS.TABLES.keys():
                                if isinstance(sss.SELS.TABLES[REC2], pd.DataFrame):
                                    sss.SELS[head[1]].currTable=REC2
                            else:
                                print(f"Error: Table {REC2} not accessed.")
                    elif recs[0]=="SWITCH":
                        sss.SELS[head[1]].doSwitch=True
                        if recs[1]=="ROWS" and REC2=="DOW":
                            sss.SELS[head[1]]['switch']=[dt.now().weekday(), "ROWS"]
                            sss.SELS[head[1]].doSwitchRowsByDay=True
                        elif recs[1]=="COLS" and REC2=="DOW":
                            sss.SELS[head[1]].switch=[dt.now().weekday(), "COLS"]
                            sss.SELS[head[1]].doSwitchColsByDay=True
                    elif recs[0]=="COMBINE":
                        if recs[1]=="STANDARD":
                            sss.SELS[head[1]].doCombineStandard=True
                    elif recs[0]=="SET":
                        if recs[1]=="FOCUS" and REC2=="DOW":
                            sss.SELS[head[1]].doDayFocus=True
                    elif recs[0]=="COND":
                        if recs[1]=="NODE":
                            sss.SELS[head[1]].condNode=REC2
                    else:
                        print(f"Error. Unrecognized tag: {recs[0]}.")
                else:
                    print(f"Error in {head[1]}. Colon record after options. REC1: {REC1}.")
            # not a double column record
            else:
                # presumed option
                opt=recs[0].strip()
                # blank line
                if len(opt)==0:
                    return(tPoint)
                else:
                    #print("head,recs, REC2", head, "///", recs, REC2)
                    # add to list
                    sss.SELS[head[1]].OPTS.append(recs[0])
                    # add to map dict
                    sss.SELS[head[1]].MAP[recs[0]]=REC2
                    #
                    sss.selGraph.add_edge(head[1], REC2)
                    # no more captions or labels
                    zHead=False  
            
        return(tPoint)

    ##################################################################
    # read loop 
    # read pairs of columns
    # create data objects from sets of rows
    tPair=0
    tPoint=0
    sdRows, sdCols = sData.shape
    sdPairs=int(sdCols/2)
    #breakCol=True
    for tPair in range(1, sdPairs):

        # test for column content
        #for i in range(0,10):
        #    if len(sData.iLoc[i,tPair*2])>0:
        #        breakCol=False
        #        break
        #if breakCol==True:
        #    break

        zBlanks=0
        for tPoint in range(0,sdRows-1):
            
            # read next record
            REC1, REC2 =readREC(tPoint, tPair, sData)

            head=REC1.split("::")
            head[0]=head[0].strip()

            # reset blank line counter
            if len(head[0].strip())>0:
                zBlanks=0
            if head[0]=="SEL":
                tPoint=doSels(tPoint, tPair, head, REC2)
            elif head[0]=="READ":
                if head[1]=="DICT":
                    tPoint=readDict(tPoint, tPair, head, REC2)
                elif head[1]=="RESPONSES":
                    tPoint=readResponses(tPoint, tPair, head, REC2)
                else:
                    print(f"Error: invalid read option {head[1]}.")
            # blanks
            if head[0].strip()=="":
                # process blanks
                zBlanks+=1
                # end reding column
                if zBlanks>10:
                    break

    # check for graph errors
    # check for starting nodes other than START
    errs=0
    for node in sss.selGraph.nodes:
        decds=[n for n in sss.selGraph.predecessors(node)]
        if len(decds)==0 and node!="START":
            errs+=1
            print(f"No predecessors for node {node}.")
    if errs==0:
        print("No abnormal starts")
    # check for ending nodes that are not REPORT
    errs=0
    for node in sss.selGraph.nodes:
        decds=[n for n in sss.selGraph.successors(node)]
        if len(decds)==0 and node!="REPORT":
            errs+=1
            print(f"Missing decendants for node {node}.")
    if errs==0:
        print("No abnormal terminations")

    #### wrapup
    # All paths from START to REPORT
    print("GRAPH NODES:", sss.selGraph.nodes)
    #print("GRAPH EDGES:", sss.selGraph.edges)
    sss.pracDict.cPATHZ=sorted(nx.all_simple_paths(sss.selGraph,"START","REPORT"))

    sss.pracDict["NumberOfLevels"]=int(sss.pracDict["NumberOfLevels"])

    # read last node choices
    for tPoint in range(0,1000):                    
        aNode, aChoice = readREC(tPoint, 0, sData)
        if aNode:
            sss.SELS[aNode].lastChoice=aChoice
        else:
            break

    # identify last selected dims 
    # this was not so well thought out!
    selz=sss.pracToSels[sss.activePractice.replace(" ", "_")]
    ls=len(selz)
    print("selz", selz)
    sss.pracDict.SELZ=dotDict()
    for i in range(0, sss.pracDict["NumberOfLevels"]):
        print("i, LEVZ[i] ", i, sss.LEVZ[i])
        print("selz[i] ", selz[i])
        if i<ls:
            sss.pracDict.SELZ[sss.LEVZ[i]]=selz[i]
        else:
            sss.pracDict.SELZ[sss.LEVZ[i]]=None
    #print("SELZ", sss.pracDict.SELZ)



