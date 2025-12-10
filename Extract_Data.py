#!/home/leaf/Downloads/.venv/bin/python3
# Import Libraries, ULDAQ is exclusive driver to Linux Systems
from uldaq import (get_daq_device_inventory, DaqDevice, InterfaceType, AiInputMode, Range, ScanOption, ScanStatus, create_float_buffer, AInScanFlag)
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
import time

def Capture(Sampling_Rate, Time_Duration):

    Samples_Per_Channel = Sampling_Rate * Time_Duration
    
    device = get_daq_device_inventory(InterfaceType.USB)
    if not device:
        print("DAQ Discovery Error")
        return

    # Physical Device Setup
    daq_device = DaqDevice(device[0])
    daq_device.connect() 
    data_buffer = create_float_buffer(1, Samples_Per_Channel)

    # Device Parameters
    Low_Channel = 0
    High_Channel = 0 # If equivalent to Low_Channel, then only single.
    Num_Channels = High_Channel - Low_Channel + 1
    ai_device = daq_device.get_ai_device() # ai = analog input
    ai_range = Range.BIP10VOLTS
    input_mode = AiInputMode.SINGLE_ENDED # Connect Channel H w/ AGND

    try: 
        print(f"Sampling_Rate:{Sampling_Rate/1000} kHz\nSamples_Per_Channel:{Samples_Per_Channel} Samples\nNumber of Channels:{Num_Channels}")

        ai_device.a_in_scan(Low_Channel, High_Channel, input_mode,
                            ai_range, Samples_Per_Channel, Sampling_Rate,
                            ScanOption.DEFAULTIO,AInScanFlag.DEFAULT,
                            data_buffer)

        status, transfer_status = ai_device.get_scan_status()
        while status == ScanStatus.RUNNING:
            time.sleep(0.1) # Interval Checks 
            status, transfer_status = ai_device.get_scan_status()

        print("Done")

    finally:
        if daq_device and daq_device.is_connected():
            ai_device.scan_stop()
            daq_device.disconnect()
            daq_device.release()
        print("Device released and Data Acquired")

        return data_buffer

def Plot(data_buffer, Sampling_Rate, Time_Duration):

    data = np.array(data_buffer[:])

    # Corrections for bias/drift
    data = signal.detrend(data) # DC Bias and Drift Correction

    time_axis = np.linspace(0, Time_Duration, Sampling_Rate * Time_Duration)

    # Plotting Setup
    plt.figure()
    plt.plot(time_axis, data, label='Ultrasonic Signal', color='blue', linewidth=0.8)
    plt.title(f"Ultrasonic Recording For {Sampling_Rate/1000} kHz", size=24)
    plt.xlabel("Time (s)", size=24)
    plt.ylabel("Voltage (V)", size=24)
    plt.xticks(size=24)
    plt.yticks(size=24)
    plt.grid("True", which='both')
    plt.rcParams['agg.path.chunksize'] = 10000 # Computer was crashing due to rendering limits
    plt.show()

if __name__ == '__main__':

    # Input Parameters
    Sampling_Rate = int(input("Sampling_Rate (In Hz):"))
    Time_Duration = int(input("Time_Duration (In s):"))


    Raw_Data = Capture(Sampling_Rate, Time_Duration)
    Plot(Raw_Data, Sampling_Rate, Time_Duration)
