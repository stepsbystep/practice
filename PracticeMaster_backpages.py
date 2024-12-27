# immediate to do: 
#     get captions from pracDict
#     rewwork interface ... don't hide selections by default ... 
#     update reported selection info ... should be set in master sheet ... can be shown explicitly, but not necessarily

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime as dt
import datetime as datetime
import pickle
import os.path
from PracticeMaster_fns import *
from PracticeMaster_entry_fns import *

sss=st.session_state

def practiceChoice():
    sss.DefineAct=False
    sss.EnterPracticeData=False
    sss.EnterInformation=False
    sss.ChoosePractice=True

def doPractice():
    sss.DefineAct=True
    sss.EnterPracticeData=True
    sss.ChoosePractice=False

###########################################################################
# css macros
def writeCSS():
    # define some styles
    zcss= """<style type=text/css>
    cspan {
        color: red;
        font-weight: bolder;
        font: 36px Arial, Helvetica, sans-serif;
    }
    tspan {
        font: Arial, Helvetica, sans-serif;
        line-height : 0.8;
    }
    .pm {color : black; font-weight: bolder}
    .sp {color : red; font-weight: 900}
    .bld {font-weight: 835} """
    st.write(zcss, unsafe_allow_html=True)


###########################################################################
# set debugging level
def setDebugLev():

    ix=sss.debugLev
    debugLev=st.radio(label="Select debug level:", 
        options=[0,1,2,3,4,5], index=ix)
    if debugLev!=sss.debugLev:
        sss.debugLev=debugLev

    #sss.debug1=st.checkbox("Debug Y/N") 
    #debug2=" "
    #debug2=st.text_input("Enter debug string", value=sss.debug2)
    #if debug2!=sss.debug2:
    #    sss.debug2=debug2

    print("debugLev", sss.debugLev)
    if st.button("Set debug level"):
        sss.setDebug=False
        st.rerun()

###########################################################################
# defineNav: upper right hand corner navi
def TitleAndNav():
    bCol1, bCol2 = st.columns([0.75,0.25])
    with bCol1:
        if "activePractice" in st.session_state and "pracDict" in st.session_state:
            st.write(f"<tspan class='pm'><font size='5'>Practice Master</font></tspan><br><tspan class='bld'><font color={sss.pracDict.TitleColor}><font size='7'><i>{sss.activePractice}</i></font></tspan>", unsafe_allow_html=True)
        else: 
            st.write(f"<tspan class='pm'><font size='5'>Practice Master</font></tspan><br><tspan class='bld'></font></tspan>", unsafe_allow_html=True)
    with bCol2:
        with st.popover("🌎"):
            if sss.DefineAct:
                if st.button("🌎 Change Practice"):
                    practiceChoice()
                    st.rerun()
            else:
                if st.button("🌎 Do Practice"):
                    doPractice()
                    st.rerun()

            print("before debug", sss.debugLev)
            #with st.container(border=True):
            if st.button("🌎 Debug"):
                sss.setDebug=True
                setDebugLev()
                st.rerun()
            print("after debug", sss.debugLev)

#########################################################################
#


#########################################################################
# choose practice
def ChoosePractice():
    sss.EnterInformation=False
    if stVal("ChoosePractice"):
        print("choosing practice")
        #st.markdown(f"###Select Practice:")
        try:
            pIndex=sss.PractToNum[sss.activePractice]
        except:
            pIndex=0
        print("opts pIndex", pIndex)
        selPractice=st.radio( label="Select Practice:", 
            options=sss.Practices, index=pIndex)
    
        # switch practices
        # second condition is to keep the buttom from showing up after choice is made
        if st.button("Select " + selPractice) and sss.ChoosePractice:
            ###########################################################################
            # need to write new active practice to workbook and update dim sels
            # as in dataUpdate("switch practice")
            sss.newPractice=selPractice
            sss.ChoosePractice=False  
            sss.EnterPracticeData=True
            sss.EnterInformation=False 
            sss.DefineAct=True 
            # update database with current selections for old practice
            #updateAndWriteCurrentSels()
            updateNodeChoices()
            # update practice
            updateAndWriteNewPractice()
            print("XXXXX")
            buildPracticeDataObjects()
            # TEMP
            del sss.sNodes
            del sss.resp
            st.rerun()

@st.fragment
def SelectDimensions():

    stEKey("S", "init")
    if 'resp' not in sss:
        sss.resp=[None for i in range(0,5)]
        sss.sNodes=['START', None, None, None, None, None]

    zSel=None
    #with st.form("zForm", border=True):
    with st.container(border=True):
        lists=['TOP_LEVEL', 'rForms2', 'rForms3', 'Col_One', 'Col_Two']
        #if sss.debugLev>3:
        print("START OF SD - resp", sss.resp)

        for ii in range(5):

            pIndex=None
            curNode=sss.sNodes[ii]

            if not curNode:
                break

            print(f">>>>> curNode: {curNode}")
            print("START OF SD - resp", sss.resp)

            # regular options or switched options
            #print(f"ii {ii}, curNode {curNode}, pIndex {pIndex}")
            if not sss.SELS[curNode].doSwitch:
                OPTS=sss.SELS[curNode].OPTS
            else:
                dow=updateSwitchNodeOptions(curNode)
                OPTS=sss.SELS[curNode].combOPTS
                #print("OPTS:", OPTS)
                if sss.SELS[curNode].doDayFocus:
                    pIndex=dow
                else:
                    pIndex=None

            LAB=sss.SELS[curNode].LAB

            PH="Select option from List"
            if not sss.SELS[curNode].doDayFocus:
                pIndex=findSel(sss.SELS[curNode].lastChoice, OPTS)

            if pIndex!=None:
                zSel=OPTS[pIndex]
                selInCurOpts=True
            else:
                # look for prior node choice
                if sss.SELS[curNode].lastChoice:
                    zSel=sss.SELS[curNode].lastChoice
                    # erase SELZ entry
                    sss.pracDict.SELZ[sss.LEVZ[ii]]=None
                    selInCurOpts=True
                else: 
                    zSel=None
                    selInCurOpts=False

            print("IN SD - ii pIndex, zSel, curNode:", ii, pIndex, zSel, curNode)

            # create and disply entry widget! ... or placeholder        
            if OPTS: 
                #print("COP ii, resp, opt:", ii, sss.resp[ii], OPTS[pIndex])
                REZ=None
                REZ=st.selectbox(label=LAB, options=OPTS, index=pIndex, 
                        placeholder=PH,key=stEKey("S"))
                print(" ")
                print(">>>> REZ", REZ)
                newEntry=False
                # process responses
                if REZ:
                    newEntry=True
                    if pIndex!=None:
                        #print("EQ TEST", "".join(REZ.split()) , "".join(OPTS[pIndex].split()))
                        if REZ.split()==OPTS[pIndex].split():
                            newEntry=False
                        #print(f"REZ TEST w pIndex REZ'{REZ}' OPTS[pIndex]: '{OPTS[pIndex]}' newEntry {newEntry}")
                    elif sss.resp[ii]: 
                        if REZ.split()==sss.resp[ii].split():
                            newEntry=False
                        #print(f"REZ TEST w resp REZ'{REZ}' sss.resp[ii]: '{sss.resp[ii]}' newEntry {newEntry}")
                    else:
                            print(f"REZ NO TEST  REZ '{REZ}' sss.resp[ii]: '{sss.resp[ii]}' ")

                    sss.resp[ii]=REZ

                    # find pIndex value
                    pIndex=findSel(sss.resp[ii], OPTS)
                    # if we have a cond process going on, pIndex must be saved!
                    sss.SELS[curNode].pIndex=pIndex
                    #print("pIndex for entry:", curNode, pIndex)
                    # map next node mapping back to original option in case of switch
                    sss.sNodes[ii+1]=sss.SELS[curNode].MAP[sss.SELS[curNode].OPTS[pIndex]]   
                    sss.pracDict.SELZ[sss.LEVZ[ii]]=sss.resp[ii]
                    sss.SELS[curNode].lastChoice=sss.resp[ii] 
                    print("sss.SELS[curNode].lastChoice:", sss.SELS[curNode].lastChoice)
                    print("RESPONSE FRAG RERUN ii, curNode, sss.resp[ii], newNode: ", ii, curNode, sss.resp[ii], sss.sNodes[ii+1])                        
                    if newEntry:
                        print("doing RERUN")
                        st.rerun (scope="fragment")
            else:
                st.selectbox(label="selections not yet determined", options=[], 
                    placeholder="selections not yet determined",key="C"+stSKey(), disabled=True)
                
            # next node
            if newEntry==False:
                if zSel and selInCurOpts:
                    if zSel in sss.SELS[curNode].MAP.keys():
                        print("**** setNext sel ii, curNode, pIndex, zSel, nextNode:", ii, curNode, pIndex, zSel, sss.SELS[curNode].MAP[zSel])
                        sss.sNodes[ii+1]=sss.SELS[curNode].MAP[zSel]            
                        # update path length
                        minLev, maxLev = getLevRange(sss.sNodes, ii+1)                    

            if sss.sNodes[ii+1]=="REPORT":
                print("Break - REPORT node reached")
                varRpt(ii, curNode, zSel, selInCurOpts)
                break

            elif sss.sNodes[ii+1]==None:
                print("Break - Next node undefined")
                varRpt(ii, curNode, zSel, selInCurOpts)
                break

            if ii>4:
                print("Break - ii>=4")
                break

        print("*** RESP", sss.resp)
        print("*** sNodes", sss.sNodes)
        print("*** SELZ", sss.pracDict.SELZ)
        #submitted = st.form_submit_button("Submit")

    if updateActDefined():
        sss.EnterInformation=True
        #EnterInformation()
    else:
        sss.EnterInformation=False
            

########################################################################################
# Enter the information
# session_state variables controling showing of data entry:
#    show_form
#    show_confirm
#    final_started

def EnterInformation():
    
    if True:
        # the act defined:
        sss.selStr=""
        sss.Choices=[]
        sss.reptChoices=[]
        for node in sss.sNodes:
            if node == None or node=="REPORT":
                break
            if len(sss.selStr)>1:
                sss.selStr=sss.selStr + " > "
            sss.selStr = sss.selStr + sss.SELS[node].lastChoice
            sss.Choices.append(sss.SELS[node].lastChoice)
            sss.reptChoices.append(sss.SELS[node].lastChoice)
        print("CHOICES: ",  sss.Choices)

        while len(sss.reptChoices)<5:
            sss.reptChoices.append(None)

        # 
        if "show_form" not in sss:
            sss.show_form = False
            sss.show_confirm = False
            sss.final_started=False
    
        #if sss.show_form == False:
        #    st.write("Selected Act: " + sss.selStr)

        ##############################################################################
        # Navigation choices for entery data
        # column structure for navigation choices: rate, history, hide sel tabs, show sel tabs, enter data    
        with st.container(border=True):
            aCol1, aCol2, aCol3 = st.columns(3)
            with aCol1:
                if sss.show_form == False:
                    # show define new act buton
                    if st.button("Rate",use_container_width=True):
                        sss.show_form = True
                        sss.DefineAct = False
                        sss.DisplayIt = True
                        st.rerun()
            with aCol2:
                if sss.show_form==False and sss.AskGetHistory:
                    if sss.ReportHistory==False:
                        if st.button("Show History",use_container_width=True):
                            sss.ReportHistory = True
                            st.rerun()
                    else:
                        if st.button("Hide History",use_container_width=True):
                            sss.ReportHistory = False
                            st.rerun()
        
            with aCol3:
                if sss.DefineAct:
                    if st.button("Hide Selection Tabs",use_container_width=True ):
                        sss.DefineAct=False
                        st.rerun()        
                # show define new act buton
                if sss.DefineAct==False:
                    if st.button("Show Selection Tabs",use_container_width=True):
                        sss.show_form = False
                        sss.DefineAct = True
                        st.rerun()    
        
        # condition test based on the choice made at a node
        # returns true unless there is an unmet condition
        def condTest(ENT):
            doProc=False
            if 'cond' in ENT.keys():
                if sss.SELS[ENT['cond'][0]]:
                    if sss.SELS[ENT['cond'][0]].lastChoice:
                        if sss.SELS[ENT['cond'][0]].lastChoice==ENT['cond'][1]:
                            doProc=True
            else:
                doProc=True
            return(doProc)

        ################################################################################################
        # Enter the data!
        if sss.show_form == True:
            #with st.form("enter_data"):
            VARZ={}
            with st.container():
                print(f"{dt.now():%H:%M:%S}, main panel entry")
                st.write("Enter data for selection")
                st.write(sss.selStr)
                stEKey("E", "init")

                for i in range(0, sss.pracDict.Entries):
                    ENT=sss.pracDict.Entry[i]
                    print(f"Entry {i} of {sss.pracDict.Entries}. Response by {ENT['wid']}")
                    if ENT['wid']=='feedback':
                        ########################################
                        # skill rating
                        if condTest(ENT):
                            VARZ[ENT['var']] = Feedback(label=ENT['label'], option=ENT['opts'])
                    elif ENT['wid']=='radio':
                        ########################################
                        # climb "depth"
                        if condTest(ENT):
                            VARZ[ENT['var']] = Radio(label=ENT['label'], 
                                options=ENT['opts'],
                                horizontal=True)
                    elif ENT['wid']=='EnterTime':
                        ########################################
                        # enter time achieved            
                        # actually, hours and minutes are entered, so time must be divided by 60 ... or something like that
                        if condTest(ENT):
                            VARZ[ENT['var']]=EnterTime()
                    elif ENT['wid']=='EnterText':
                        print("Entering text")
                        ########################################
                        # text entery
                        if condTest(ENT):
                            VARZ[ENT['var']] = EnterText(label=ENT['label'])
                    elif ENT['wid']=='CheckBox':
                        print("Checkbox")
                        ########################################
                        # text entery
                        if condTest(ENT):
                            VARZ[ENT['var']] = CheckBox(label=ENT['label'])
                    elif ENT['wid']=='Toggle':
                        print("Checkbox")
                        ########################################
                        # text entery
                        if condTest(ENT):
                            VARZ[ENT['var']] = Toggle(label=ENT['label'])
                    else:
                        print("Function not found")
                sss.pracDict.VARZ=VARZ
                del ENT
                print("VARZ", sss.pracDict.VARZ)
                sss.DisplayIt = False
                  
                varStr=""
                pre= " "
                for key in sss.pracDict.VARZ.keys():
                    varStr=varStr+ pre + str(key) + " " + str(sss.pracDict.VARZ[key])
                    if pre==" ":
                        pre=", "
                sss.responseStr=varStr

                ################################################################################
                # submit entry data
                with st.container(border=True):
                    zCol1, zCol2 = st.columns(2)
                    with zCol1:
                        if st.button("Submit practice data", use_container_width=True):            
                            sss.timeStamp=dt.now()
                            st.write(varStr)
                            sss.show_form=False
                            sss.show_confirm=True
                            st.rerun()
                    with zCol2:
                        if st.button("Abort data entry", use_container_width=True):
                            sss.show_form = False
                            st.rerun()
                        
    #########################################################################################
    # Stage 3: confirm information
    #########################################################################################
    
    # next line redundant
    #if updateActDefined():
        # enter information!
        if sss.show_confirm == True:
            #with st.form("options_form", clear_on_submit=True):
            #    st.write(f"Current skill selection: {sss.selStr}")
            #    st.write("Entered information: " + sss.responseStr)
            #    #if sss.oText:
            #    #    st.write("Comment: " , sss.oText)
            #    Decision = st.radio(" ", ["Confirm Entry", "Correct Entry"], index=None)
            #    if st.form_submit_button("Push to confirm decision!"):
            #        if Decision=="Confirm Entry":
            if True:
                if True:
                    if True:
                        for key in sss.pracDict.VARZ.keys():
                            rez=[sss.timeStamp, sss.activePractice, 
                                 sss.reptChoices[0], sss.reptChoices[1], sss.reptChoices[2],
                                 sss.reptChoices[3], sss.reptChoices[4],
                                key, sss.pracDict.VARZ[key]]
                            sss.practiceData.loc[len(sss.practiceData)]=rez
                        writeData()
                        sss.show_form = False
                        sss.show_confirm = False
                        sss.td_time60upd=0
                        sss.elapsedTime=0
                        del sss["elapsedTime"]
                        st.rerun()
    
                    else:
                        sss.show_form = True
                        sss.show_confirm = False
                        st.rerun()

def ReportHistory():

    # select filter options
    selDims = st.multiselect("Select reporting dimensions", 
        sss.Choices, sss.Choices)
    dsQuery=sss.practiceData.copy()
    #print(dsQuery.dtypes)
    #print(dsQuery.columns)
    dsQuery['date/time'] = pd.to_datetime(dsQuery['date/time'])
    #dsQuery['date/time'] = pd.to_datetime(dsQuery['date/time'].dt.strftime('%Y-%m-%d %H:%M:%S'))
    for i in range(len(sss.Choices)):
        if sss.Choices[i] in selDims:
            try:
                dsQuery=dsQuery[dsQuery[sss.LEVZ[i]]==sss.Choices[i]]
            except:
                x=x
    if len(dsQuery)>0:
        dsQuery = dsQuery.pivot(index=['date/time'], columns='Field', values='Value')
        dsQuery['elapsedTime'] = pd.to_datetime(dsQuery['elapsedTime'], 
                                        format='0 days %H:%M:%S.%f', errors='coerce').dt.time
        test=dsQuery['elapsedTime'].isna()
        for i in range(len(dsQuery)):
                # true that there is no valid time value
            if test[i]: 
                dsQuery['elapsedTime'][i]=0 
        st.dataframe(dsQuery)
    else:
        st.write("No history for this act.")

    if st.button("Close data history report"):
        sss.ReportHistory=False
        st.rerun()