import streamlit as st
import datetime
from stopwatch import stopwatch 
from datetime import datetime as dt
from streamlit_mic_recorder import mic_recorder, speech_to_text

sss=st.session_state

def stEKey(PRE="X", init=""):
    if init=="init":
        sss.stEKey[PRE]=0
        return()
    else:
        sss.stEKey[PRE]+=1
        return("STeKEY"+"-"+PRE+"-"+str(sss.stEKey[PRE]))

def runUpdate(time):
    if "elapsedTime" in sss and time !=0:
        td_time60upd = datetime.timedelta(seconds=((dt.combine(dt.min,time)-dt.min).total_seconds())/60)
        sss.elapsedTime = td_time60upd
        st.rerun()

#######################################
def Feedback(label="", option='stars'):
    with st.container(border=True):
        #print("options, keys", options, key)
        if len(label)>1:
            st.write(label)
        rez=st.feedback(options=option, key=stEKey('E'))
    return(rez)

#######################################
def Radio(label="", options="", horizontal=True):
    with st.container(border=True):
        rez=st.radio(label=label, options=options, horizontal=horizontal, key=stEKey('E'))
    return(rez)

#######################################
def CheckBox(label=""):
    rez=st.checkbox(label=label, key=stEKey('E'))
    return(rez)

#######################################
def Toggle(label=""):
    rez=st.toggle(label=label, key=stEKey('E'))
    return(rez)

#######################################
#@st.fragment
def EnterText(label="", currentText=""):
    if 'text_received' not in sss:
        sss.text_received = []
        sss.oText=""
        sss.transcribe=True

    ENTRY = st.container(border=True)
    with ENTRY:
        tCol1, tCol2 = st.columns([.75,.25])
        with tCol1:
            FE = st.container()
        with tCol2:
            SE = st.container()

    def update_text():
        sss.text_received = [sss.nText]
        sss.oText=sss.nText
        print("callback", sss.nText)

    with FE:
        sss.nText=''      
        sss.nText = st.text_area(label=label, value=sss.oText, on_change=update_text(), height=68, key=stEKey('E'))
        print("right after", sss.nText)
        if sss.nText!=sss.oText and sss.nText!="":
            sss.oText=sss.nText
            sss.text_received=[sss.oText]

    with SE:
        text = speech_to_text(language='en', use_container_width=True, just_once=True, key=stEKey('E'))
        if text:
            sss.text_received.append(text)
            sss.oText=sss.oText+" "+text
        if st.button("Clear Text", use_container_width=True):
            sss.oText=""
            sss.text_received = []
        #with tCol3:
        #    if st.button("Finish", use_container_width=True):
        #        sss.transcribe=False

    return(sss.oText)

########################################
# time with popup and time entry widget             
# actually, hours and minutes are entered, so time must be divided by 60 ... or something like that
# in title, options => out var
# this version with popup
def EnterTimePopup():
    with st.container(border=True):
        st.write("Practice timer")
        col1, col2 = st.columns(2)
        if "elapsedTime" not in sss:
            ET=dt.now()-dt.now()+datetime.timedelta(milliseconds=10)
        else:
            ET=sss.elapsedTime
            #st.rerun()
        with col1:
            #if "elapsedTime" in sss:
            #    #print("elapsedTime:", sss.elapsedTime)
            time60=(dt.min+datetime.timedelta(seconds=60*ET.total_seconds())).time()
            print("Time60 before time input widget:", time60)
            tMinSec=0
            tMinSec = st.time_input("Optional: enter time (min:sec) or use stopwatch", time60, step=60, 
                                    on_change=runUpdate(tMinSec),key=key)
            td_time60upd = datetime.timedelta(seconds=((dt.combine(dt.min,tMinSec)-dt.min).total_seconds())/60)
            if "elapsedTime" in sss:
                sss.elapsedTime = td_time60upd
        with col2:
            print(dt.now(), "launch stopwatch. ET:", ET)
            sss.final_started=True
            if ET != None and "sw__showatch" in sss: 
                del sss["sw__showWatch"]
            # minus 1 tab end
            ET=stopwatch(sss.final_started)
            print("return. ET:", ET)
            if ET != None and sss.final_started==True:
                sss.elapsedTime=ET
                sss.final_started=False
                st.rerun()
    if "elapsedTime" in sss:
        return(sss.elapsedTime)
    else:
        return()
########################################
# Enter time no time input wideget or popup
# no popup
def EnterTime():
    with st.container(border=True):
        #st.write("Practice timer")
        #col1, col2 = st.columns(2)
        if "elapsedTime" not in sss:
            ET=dt.now()-dt.now()+datetime.timedelta(milliseconds=10)
        else:
            ET=sss.elapsedTime
            #st.rerun()
        
        #if True:
        #with col1:
            #if "elapsedTime" in sss:
            #    #print("elapsedTime:", sss.elapsedTime)
            time60=(dt.min+datetime.timedelta(seconds=60*ET.total_seconds())).time()
            #print("Time60 before time input widget:", time60)
            #tMinSec=0
            #tMinSec = st.time_input("Optional: enter time (min:sec) or use stopwatch", time60, step=60, 
            #                        on_change=runUpdate(tMinSec),key=key)
            #td_time60upd = datetime.timedelta(seconds=((dt.combine(dt.min,tMinSec)-dt.min).total_seconds())/60)
            #if "elapsedTime" in sss:
            #    sss.elapsedTime = td_time60upd
        if True:
        #with col2:
            print(dt.now(), "launch stopwatch. ET:", ET)
            sss.final_started=True
            if ET != None and "sw__showatch" in sss: 
                del sss["sw__showWatch"]
            # minus 1 tab end
            ET=stopwatch(sss.final_started, POPUP=False)
            print("return. ET:", ET)
            if ET != None and sss.final_started==True:
                sss.elapsedTime=ET
                sss.final_started=False
                st.rerun()
    if "elapsedTime" in sss:
        return(sss.elapsedTime)
    else:
        return()


def CustomQi():

    # get data from companion sheet
    from PracticeMaster_fns import getGSheetAsDF, dotDict
    sss.appDict.QiData = getGSheetAsDF(sss.appDATA, "EZ2")
    # print(sss.appDict.QiData)

    daysOfWeek={6:'Sunday',0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday'}
    # day of week
    #print("dt.now(), dt.now().weekday()", dt.now(), dt.now().weekday())
    sss.appDict.DOW=daysOfWeek[dt.now().weekday()]

    # QiDOW is list relating practice areas to specific practices based on days of week.  
    dowqi=sss.appDict.QiData[['Practice',sss.appDict.DOW]]
    sss.appDict.QiDOW=[]
    sss.appDict.qiList=[]
    for r in dowqi.iterrows():
        sss.appDict.QiDOW.append(r[1][0]+" : "+r[1][1])
        sss.appDict.qiList.append(r[1][0])        
    
    print("CustomQi", sss.appDict.DOW, sss.appDict.QiDOW)

    # assign 
    sss.appDict.DimDefs.Day_of_Week_Practices_One=[[sss.appDict.qiList],sss.appDict.qiDOW]
    print("DimDefs", sss.appDict.DimDefs.Day_of_Week_Practices_One)

    sss.appDict.dowPracts=dotDict
    for pract in sss.appDict.qiList:
        practDat=dict(sss.appDict.QiData[sss.appDict.QiData['Practice']==pract])
        #print(pract, practDat)
        #sss.appDict.dowPracts[pract[0]]=dict(practDat)
    #print(sss.appDict.dowPracts)
