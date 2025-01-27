import sys
import time
import os
import serial
import re
import datetime
import numpy as np
from optparse import OptionParser

# This function will capture data from the SBE83 at a set frequency and duration
def capture_data(oxy_capture_filename, com_port):
    ser_float = serial.Serial(port= com_port, baudrate=9600, bytesize=8,
                    parity='N', stopbits=1, timeout=1, xonxoff=True)

    oxy_f = open(oxy_capture_filename, 'a+')

    ser_float.flush()

    for k in range(5):
        ser_float.write(b'c\r\n')
        time.sleep(1)
    ser_float.flush()
    ser_float.read_all()

    print("Taking an Oxygen sample every 12 seconds for 10 minutes.\r\n")

    for k in range(20):
        print("Sample: %d" % k)
        n = datetime.datetime.now()
        ser_float.write(b'o')
        time.sleep(1)
        ser_float.write(b's\r\n')
        time.sleep(12)
        out = ser_float.read_all()
        out = out.decode("utf-8")
        out = out.split('\r')[1]
        print(out)
        oxy_f.write('%s ' % n.strftime("%Y-%m-%d-%H:%M:%S"))
        oxy_f.write('%s\r\n' % out.split(":",1)[1])
        oxy_f.flush()


    oxy_f.close()

# This function will provide statistics on the variance of the difference between the red and blue phases
# std(phase) > 20 ns : Large out of family noise, should not be deployed/needs to be repaired.
# 10ns < std(phase) < 20 ns : Small increase in noise, inspect sensor for damage/contamination 
# 10ns < std(phase) : No evidence for elevated noise in sensor, good to deploy 

def analyze_data(oxy_capture_filename):
    phase_list = []
    f = open(oxy_capture_filename, "w+")
    for line in f:
        if "usec" in line:
            split_1 = line.split('C')[1]
            phase = split_1.split('usec')[0].strip()
            phase_list.append(float(phase))

    std_dev = np.std(test_list)
    print("Standard deviation of SBE83 red-blue phase: %f", std_dev)

    if std_dev > 20:
        print("Sensor readings well outside normal noise levels. Needs RMA")
    elif std_dev < 20 and std_dev > 10:
        print("Sensor shows small amount of noise, inspect for damage or contamination")
    elif std_dev < 10:
        print("Sensor readings are OK")

    f.write("\n")
    f.write("Standard Deviation of SBE83 red-blue phase: %f", std_dev)
    f.close()



if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", type="string", dest="filename", help="Name of file")
    parser.add_option("-p", "--port", type="string", dest="port", help="Path to com port")
    (options, args) = parser.parse_args()

    if options.filename is None:
        print("Please provide a file name with -f ")
        sys.exit(1)
    if options.port is None:
        print("Please provide the path to the com port with -p ")
        sys.exit(1)
    
    capture_data(options.filename, options.port)
    analyze_data(options.filename)