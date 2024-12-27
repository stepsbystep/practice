
def stopwatch(START, POPUP=True):

    import streamlit as st
    import asyncio
    from datetime import datetime as dt
    import datetime
    from PracticeMaster_fns import zTime
    sss=st.session_state

    print("start stopwatch")

    if "sw__showWatch" not in sss and START:
        sss.sw__showWatch=True
        sss.sw__pause=False
        sss.sw__restart=False
        sss.sw__updateTime=False
        sss.sw__stopwatchRunning=False
        sss.sw__elapsedTime = datetime.timedelta(microseconds=0)
        sss.sw__makeFinal=False
        sss.sw__runLoop=True
        sss.sw__EXIT=False
        sss.sw__start=False
        sss.sw__pause=False
        #sss.ET=sss.sw__elapsedTime-datetime.timedelta(microseconds=0)
    print("init!")

    # css
    st.markdown(
        """
        <style>
        .time {
            font-size: 64px !important;
            font-weight: 200 !important;
            color: #ec5953 !important;
            line-height : 0.8;
      }
        </style>
        """,
        unsafe_allow_html=True
    )

    # async function
    async def watch():
        while sss.sw__runLoop:
            if sss.sw__updateTime:
                sss.sw__elapsedTime=dt.now()-sss.sw__startTime
                sss.ET=sss.sw__elapsedTime-datetime.timedelta(microseconds=sss.sw__elapsedTime.microseconds)
                print("ET now:", sss.ET)
            sss.ET=sss.sw__elapsedTime-datetime.timedelta(microseconds=sss.sw__elapsedTime.microseconds)
            sss.sw__test.markdown(
                f"""
                <p class="time">
                    {str(sss.ET)}
                </p>
                """, unsafe_allow_html=True)
            print("async running!")
            await asyncio.sleep(0.993)
        

    #internal stopwatch function
    def theStopWatch():

        def theWatchDisplay():
            sss.sw__test = st.empty()
            if "ET" not in st.session_state:
                sss.sw__test.markdown(
                    f"""
                    <p class="time">
                        {"0:00:00"}
                    </p>
                    """, unsafe_allow_html=True)
            else:
                sss.sw__test.markdown(
                    f"""
                    <p class="time">
                        {sss.ET}
                    </p>
                    """, unsafe_allow_html=True)
            if sss.sw__stopwatchRunning==False:
                print("showWatch initialization!")
                sss.sw__stopwatchRunning=True
                sss.sw__startTime=dt.now()
                sss.sw__startinit=True
                sss.sw__updateTime=False
                #sss.sw__update=False
    
        def theWatchStartReset():
            if sss.sw__start==False:
                label="Start"
                highlight="primary"
            else:
                label="Reset"
                highlight="secondary"
            print(f"stopwatch start button {zTime()} sw__start: {sss.sw__start} label: {label} highlight: {highlight}")
            if st.button(label, type=highlight, key="ST01", use_container_width=True):
                if sss.sw__start==False:
                    sss.sw__start=True
                else:
                    sss.sw__start=False
                sss.sw__startTime=dt.now()
                sss.sw__updateTime=True
                sss.sw__pause=False
                print("start/reset")
                asyncio.run(watch())
                
        def theWatchPauseResume():
            if sss.sw__pause==True:
                label="Resume"
            else:
                label="Pause"
            if sss.sw__start==True:
                highlight="primary"
            else:
                highlight='secondary'
            if st.button(label, type=highlight, key="ST02", use_container_width=True):
                if sss.sw__pause==True:
                    sss.pause=False
                else:
                    sss.sw__pause=True
                if sss.sw__updateTime==True:
                    sss.sw__updateTime=False
                    sss.sw__pause=True
                    sss.sw__pauseTime=dt.now()
                    sss.sw__elapsedTime=dt.now()-sss.sw__startTime                
                    print("pause")
                # resume
                else:
                    sss.sw__pause=False
                    sss.sw__updateTime=True
                    sss.sw__startTime=dt.now()-sss.sw__elapsedTime
                    print("resume")    
                asyncio.run(watch())

        def theWatchResume():
            if sss.sw__pause==True:
                label="Resume"
            else:
                label="Pause"
            if sss.sw__start==True:
                highlight="primary"
            else:
                highlight='secondary'
            if st.button("Resume", type=highlight, key="ST02B", use_container_width=True):
                if sss.sw__pause==True:
                    sss.pause=False
                else:
                    sss.sw__pause=True
                if sss.sw__updateTime==True:
                    sss.sw__updateTime=False
                    sss.sw__pause=True
                    sss.sw__pauseTime=dt.now()
                    sss.sw__elapsedTime=dt.now()-sss.sw__startTime                
                    print("pause")
                # resume
                else:
                    sss.sw__pause=False
                    sss.sw__updateTime=True
                    sss.sw__startTime=dt.now()-sss.sw__elapsedTime
                    print("resume")    
                asyncio.run(watch())



        def theWatchStop():
            if sss.sw__start==True:
                highlight="primary"
            else:
                highlight="secondary"
            if st.button("Stop", type=highlight, key="ST03", use_container_width=True):
                if sss.sw__pause==True:
                    sss.sw__startTime=dt.now()-sss.sw__elapsedTime
                    sss.sw__pause=False
                sss.sw__startinit=False
                sss.sw__updateTime=False
                sss.sw__makeFinal=True
                sss.sw__elapsedTime=dt.now()-sss.sw__startTime
                sss.sw__showWatch=False
                sss.sw__EXIT=True
                print("stop")
                st.rerun()

        if sss.sw__showWatch:
            if POPUP:
                with st.popover("Show/Hide Stopwatch"): 
                    theWatchDisplay()
                    theWatchStartReset()
                    theWatchPauseResume()
                    theWatchResume()
                    theWatchStop()
            else:
                with st.container():
                    z1, z2 = st.columns([.75,.25])
                    with z1:
                        st.write("Practice timer")
                        theWatchDisplay()
                    with z2:
                        theWatchStartReset()
                        theWatchPauseResume()
                        theWatchResume()
                        theWatchStop()
                 
        # exit when done!
        if sss.sw__EXIT:    
            #print("internal function exit. time", sss.sw__elapsedTime)
            #st.rerun()
            return(sss.sw__elapsedTime)

    # call internal function
    theTime=theStopWatch()
    print("internal function return. time", theTime )
    # return main function
    del sss.sw__showWatch
    return(theTime)


