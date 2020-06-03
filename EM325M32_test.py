#!/cygdrive/c/Users/miyam/AppData/Local/Programs/Python/Python38/python.exe
#
# EM-325M32-2 Multichannel Trigger box test program
#   usage: EM325M32_test.py [MKON | MKOFF | INT | EXTON | EXTOFF | MEAS]

import nidaqmx
import sys
import time
from nidaqmx.constants import (LineGrouping)

def setIO(port, data):
    # print(data)
    port.write(list(map(lambda x:not x ,data)), auto_start=True)

args = sys.argv[1 ]

device='Dev2'
port='port0'
devicePort=device+'/'+port+'/'

with nidaqmx.Task() as task, nidaqmx.Task() as pioRead:
    task.do_channels.add_do_chan(
        devicePort+'line0','measStart',
        line_grouping=LineGrouping.CHAN_PER_LINE)
    # Control Internal Trigger signal [Hi]:TRUE / [Lo]:FALSE

    task.do_channels.add_do_chan(
        devicePort+'line1','intTriggerSig',
        line_grouping=LineGrouping.CHAN_PER_LINE)
    # Initiate Internal Trigger signal [Hi]:TRUE / [Lo]:FALSE

    task.do_channels.add_do_chan(
        devicePort+'line2','trigSelIntExt',
        line_grouping=LineGrouping.CHAN_PER_LINE)
    # Select [Internal Trigger]:TURE or [External Trigger]:FALSE

    task.do_channels.add_do_chan(
        devicePort+'line3','eventMarkEnable',
        line_grouping=LineGrouping.CHAN_PER_LINE)
    # Enable Trigger output for RJ45 Line (as EVENT MARK signal)

    task.do_channels.add_do_chan(
        devicePort+'line4','trigSelExtMarker',
        line_grouping=LineGrouping.CHAN_PER_LINE)
    # Select Triger input [form BNC(PE32)]:TRUE or [from marker coil driver]:FALSE

    task.do_channels.add_do_chan(
        devicePort+'line5','trigOutEnable',
        line_grouping=LineGrouping.CHAN_PER_LINE)
    # Enable Trigger output for BNC connector

    task.do_channels.add_do_chan(
        devicePort+'line6','makerPower',
        line_grouping=LineGrouping.CHAN_PER_LINE)
    # Control Power for the Markercoil Driver [on]:TRUE / [off]:FALSE


 #  READ PORT
    pioRead.di_channels.add_di_chan(
        device+'/port2/'+'line2','trigStrobe',
        line_grouping=LineGrouping.CHAN_PER_LINE)
    # Trigger singal stroble input

    pioRead.di_channels.add_di_chan(
        device+'/port1/'+'line0:5','trigCode',
        line_grouping=LineGrouping.CHAN_PER_LINE)
    # Trigger singal stroble input


    p0=[False] * 7

    mode={'default':p0, 'ExtTriggerMarkercoil':p0, 'IntTriggerDo':p0, 'ExtTriggerPE32':p0}

    mode['default'][4] = True

    mode['ExtTriggerMarkercoil'][2]=False
    mode['ExtTriggerMarkercoil'][4]=False

    mode['IntTriggerDo'][2]=True
    mode['IntTriggerDo'][4]=True

    mode['ExtTriggerPE32'][2]=False
    mode['ExtTriggerPE32'][4]=True

    # print(task.read())
    # print(mode)

    if args=='RESET':
        print('Set to Default state ....')
        setIO(task, mode['default'])

    if args=='TRIGOUTOFF':
        print('Disable signal from TRIG OUT terminal....')
        status=list(map(lambda x:not x ,task.read()))
        status[5]=False
        setIO(task, status)

    if args=='TRIGOUTON':
        print('Disable signal from TRIG OUT terminal....')
        status=list(map(lambda x:not x ,task.read()))
        status[5]=True
        setIO(task, status)

    if args=='MKON':
        print('Turn the Marker coil driver on...')
        setIO(task, mode['default'])
        status=list(map(lambda x:not x ,task.read()))
        status[5]=True
        status[2]=False
        status[4]=False
        status[6]=True
        setIO(task, status)


    if args=='MKOFF':
        print('Turn the Marker coil driver off...')
        setIO(task, mode['default'])

    if args=='EXTON':
        print('PE32 input is now abailable. watch TRIG OUT terminal.')
        setIO(task, mode['default'])
        status=list(map(lambda x:not x ,task.read()))
        status[5]=True
        status[2]=False
        status[4]=True
        setIO(task, status)

        while True:
            trigStb=pioRead.read()[0]
            while (trigStb):
                trigStb=pioRead.read()[0]

            while not(trigStb):
                trigStb=pioRead.read()[0]
                trigCode=pioRead.read()[1:6]

            #clear EVENT MARK mask circuit
            print('Found Trigger! : ', list(map(lambda x: '0' if x else '1'  ,trigCode)) )
            status[3]=True
            setIO(task, status)
            time.sleep(0.01)
            status[3]=False
            setIO(task, status)


    if args=='EXTOFF':
        print('Set to Default state ....')
        setIO(task, mode['default'])

    if args=='INT':
        print('INPUT: Internal Trigger .. Please checkout the Trigger Out singal')
        print('you can see 100us positive pulse on the scope.')

        # status=list(map(lambda x:not x ,task.read()))
        status=mode['default']
        status[5]=True
        status[2]=True
        setIO(task, status)

        for n in range(10):
            status[1]=True
            setIO(task, status)
            time.sleep(0.8)

            status[1]=False
            setIO(task, status)
            time.sleep(0.1)

            #clear EVENT MARK mask circuit
            status[3]=True
            setIO(task, status)
            time.sleep(0.1)
            status[3]=False


    if args=='MEAS':
        print('Generating MEAS START signal ')

        # status=list(map(lambda x:not x ,task.read()))
        status=mode['default']
        setIO(task, status)

        for n in range(10):
            status[0]=True
            setIO(task, status)
            time.sleep(0.5)

            status[0]=False
            setIO(task, status)
            time.sleep(0.5)
