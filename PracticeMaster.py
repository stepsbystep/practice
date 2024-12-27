import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime as dt
import datetime as datetime
import pickle
import os.path
import sys

from PracticeMaster_fns import *
from PracticeMaster_backpages import *
from stopwatch import stopwatch

sss=st.session_state
sss.argv=sys.argv

##############################################################################
# Start of Execution
#
##############################################################################
# set row selections

print(f">>>> Time at start of execution {dt.now():%H:%M:%S}.")

# session_state.DefineAct:  allow dimensional selections to be made
# session_state.ActDefined: selections made to define act 

# check for passed args, particularly alt file name

# reduce headspace
if False:
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 10rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

# read masterData if not read
if "masterDataIsRead" not in sss:
    print(">>>>>> Reading master data!")
    getMasterData()
    sss.DefineAct=True
    # read practice data if there is an active practice
    #if stVal("activePractice"):
    if "activePractice" in sss:
        sss.ChoosePractice=False
        print(">>>> Reading Practice Data called from main.")
        buildPracticeDataObjects()
    else:
        sss.ChoosePractice=True
    sss.EnterInformation=False
    sss.ReportHistory=False
    sss.SummarizeHistory=False
    sss.setDebug=False
    sss.debugLev=0
    sss.AskGetHistory=True
    sss.GetHistory=False
    # css command defs
    writeCSS()

if "Banner" not in sss:
    # title and navigation
    TitleAndNav()
    sss.banner=True


if sss.setDebug:
    setDebugLev()

#################################################################################
# Stage 0: select Practice
#################################################################################
if  sss.ChoosePractice:
    ChoosePractice()

#################################################################################
# Stage 1: Select Act to be reported
#################################################################################
if sss.DefineAct:
    SelectDimensions()

##############################################################################
# Stage 2: Enter Information: Make a dimensional defininition of a particular act
# Enter information on act -- This should be shown except when stage 2: entry of the act data starts
##############################################################################
print("Before enter info")
if sss.EnterInformation:
    print("Calling Enter Information")
    EnterInformation()

###############################################################################
# Report History
###############################################################################
if sss.ReportHistory:
    ReportHistory()

###############################################################################
# Summarize History
###############################################################################
if sss.SummarizeHistory:
    SunnarizeHistory()
