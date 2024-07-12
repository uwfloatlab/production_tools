import dp700
import datetime
import sys
import time
import paramiko
import os
import serial
import re
from optparse import OptionParser
from sklearn import linear_model
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

host = 'flux'
password = "e=2.718"
last_response = True
ps_com ="/dev/ttyUSB0"
apf11_com="/dev/ttyS0"

ser_dmm = serial.Serial(port='/dev/ttyUSB1', baudrate=115200, bytesize=8,
                      parity='N', stopbits=1, timeout=0.1, xonxoff=1,
                      rtscts=0, dsrdtr=0)

ser_arduino = serial.Serial(port='/dev/ttyUSB2', baudrate=9600, bytesize=8,
                            parity='N', stopbits=1, timeout=0.1, xonxoff=1,
                            rtscts=0, dsrdtr=0)

ser_float = None

voltages = [15.0, 14.0, 13.0, 12.0, 11.0, 10.0, 9.0, 8.0, 7.0, 6.0, 5.0]
resistances = [15, 30, 60, 120, 240, 480, 1000]

regr = linear_model.LinearRegression()

def read_measurement(ser):
    ser.flushInput()
    ser.flushOutput()
    ser.write(('QM' + '\r').encode('utf-8'))

    response = b''
    second_eol = False

    while True:
        c = ser.read(1)
        if c:
            response += c
            if c == b'\r':
                if second_eol:
                    break
                else:
                    second_eol = True
        else:
            break
    return response

def decode_measurement(response):
    global last_response
    if len(response) > 0:
        response_string = response.decode('utf-8')
        response_split = response_string.split('\r')

        if len(response_split) == 3:
            measurement_split = response_split[1].split(',')
            if len(measurement_split) == 4:
                return float(measurement_split[0])
            else:
                print("Incorrect number of fields in measurement")
                last_response = False
        else:
            print("Incorrect number of carriage returns")
            last_response = False
    else:
        print ("No response from dmm")
        last_response = False

def voltage_calibration(ps, file, floatnum, user):
    ps_voltage = None
    measured_counts = []
    measured_voltages = []

    timestr = time.strftime("%Y/%m/%d %H:%M:%S ")
    file.write('/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
    file.write(' * $Id: battery-calibration.')
    file.write(str(floatnum))
    file.write(',v 1.1 ')
    file.write(timestr)
    file.write(str(user))
    file.write(' Exp $\n')
    file.write(' *~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
    file.write(' * RCS Log:\n')
    file.write(' *\n')
    file.write(' * $Log: battery-calibration.')
    file.write(str(floatnum))
    file.write(',v $\n')
    file.write(' * Revision 1.1 ')
    file.write(timestr)
    file.write(str(user))
    file.write('\n')
    file.write(' * Initial revision\n')
    file.write(' *\n')
    file.write(' *~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/\n')
    file.write('// Calibration done ')
    file.write(str(floatnum))
    file.write(' -')
    file.write(str(user))
    file.write('\n')
    file.write('Calibration battery-voltage-apex-')
    file.write(str(floatnum))
    file.write('\n{\n')
    file.write('//     counts  voltage ( DP712 Power Supply used for voltage readings )\n')
    
    ps.set_output_voltage(15.0)
    ps.enable_output(True)

    ser_float = serial.Serial(port=apf11_com, baudrate=9600, bytesize=8,
                      parity='N', stopbits=1, timeout=1, xonxoff=True)

    input("Reset the Apf11. Then, press Enter to continue...")
    time.sleep(7)

    for i in tqdm(range(len(voltages))):
        voltage = voltages[i]
        ps.set_output_voltage(voltage)
        time.sleep(1)
        ps_voltage = ps.get_output_voltage()
        ser_float.flush()
        ser_float.write(b'c\r\n')
        time.sleep(1)
        apf11_reading = ser_float.read_until(b'Current')
        splits = apf11_reading.decode("utf-8").split("Battery [",1)[1].split("]")[0].replace(' ','').split(",")
        counts = splits[0].replace('cnt','')
        float_v = splits[1].replace('V','')
        file.write('          ')
        for i in range(3 - len(str(counts))):
            file.write(' ')
        file.write(str(counts))
        measured_counts.append(int(counts))
        file.write('   ')
        for i in range(6 - len(str(ps_voltage))):
            file.write(' ')
        file.write(str(ps_voltage))
        measured_voltages.append(float(ps_voltage))
        file.write('\r\n')

    ps.enable_output(False)
    ser_float.close()

    coef,(SSE,), *_ = np.polyfit(measured_counts, measured_voltages, 1, full=True)
    poly1d_fn = np.poly1d(coef)

    plt.plot(measured_counts,measured_voltages, 'bo', measured_counts, poly1d_fn(measured_counts), '--k')
    plt.title('Float ' + str(floatnum) + ' Voltage Linear Regression')
    plt.xlabel('Voltage ADC Reading (counts)')
    plt.ylabel('Voltage Fluke Reading (V)')
    plt.show()

    while True:
        answer = input("Does this regression look ok? [yes/no] ")
        if answer == 'yes':
            break
        elif answer == 'no':
            print("Please check the test automation setup and try again")
            file.close()
            sys.exit(1)
        else:
            print("Please enter yes or no.")

    plt.savefig('battery-calibration-' + str(floatnum) + '.png', bbox_inches='tight')

    file.write('/*\r\n')
    file.write('\n$ Polynomial form: f(x) = (A0 + x(A1 + x(A2 + x(A3 + ... + x(An)))))\r\n')
    file.write('$ Polynomial order = 1\r\n')
    file.write('$ Number of data points used in fit = ')
    file.write(str(len(measured_counts)))
    file.write('\r\n')
    file.write('$ Sum of Square Residual Error = ' + str(SSE) +'\r\n')
    file.write('$ A0 = ' + str(coef[0]) + '\r\n')
    file.write('$ A1 = ' + str(coef[1]) + '\r\n')
    file.write('$\r\n')
    file.write('$ #             x             y          f(x)      y - f(x)\r\n')

    file.write('$\r\n')
    file.write('$ End of Stream\r\n')
    file.write('*/\r\n')
    file.write('}\n')

    return

def current_calibration(ps, file, floatnum, user):
    ps_voltage = None
    dmm_current = None

    timestr = time.strftime("%Y/%m/%d %H:%M:%S ")
    file.write('/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
    file.write(' * $Id: current-calibration.')
    file.write(str(floatnum))
    file.write(',v 1.1 ')
    file.write(timestr)
    file.write(str(user))
    file.write(' Exp $\n')
    file.write(' *~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
    file.write(' * RCS Log:\n')
    file.write(' *\n')
    file.write(' * $Log: current-calibration.')
    file.write(str(floatnum))
    file.write(',v $\n')
    file.write(' * Revision 1.1 ')
    file.write(timestr)
    file.write(str(user))
    file.write('\n')
    file.write(' * Initial revision\n')
    file.write(' *\n')
    file.write(' *~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/\n')
    file.write('/*\n APF9 Current Calibration done ')
    file.write(timestr)
    file.write(' -')
    file.write(str(user))
    file.write('\n*/\n')
    file.write('Calibration Current-apex-')
    file.write(str(floatnum))
    file.write('\n{\n')
    file.write('//  counts  current(Fluke ma) // Current(Float ma) // voltage(DP712) voltage(float)  switch\n')
    
    # Run Current Cal here
    ps.set_output_voltage(15.0)
    ps.enable_output(True)

    ser_float = serial.Serial(port=apf11_com, baudrate=9600, bytesize=8,
                      parity='N', stopbits=1, timeout=1, xonxoff=True)

    input("Reset the Apf11 and power on the Fluke DMM. Then, press Enter to continue...")
    time.sleep(7)

    for i in tqdm(range(len(voltages))):
        voltage = voltages[i]
        for j in range(len(resistances)):
            resistance = resistances[j]
            ser_arduino.write(str(j).encode())
            ps.set_output_voltage(voltage)
            ps_voltage = ps.get_output_voltage()
            ser_float.flush()
            for k in range(10):
                ser_float.write(b'c\r\n')
                time.sleep(1)
            ser_float.read_all()
            ser_float.write(b'c\r\n')
            apf11_reading = ser_float.read_until(b'Barometer')
            splits = apf11_reading.decode("utf-8").split("Battery [",1)[1].split("]")
            voltage_reading = splits[0].replace(' ','').split(",")
            current_reading = splits[1].split("Current [",1)[1].split("]")[0].replace(' ','').split(",")
            #batt_counts = voltage_reading[0].replace('cnt','')
            batt_float = voltage_reading[1].replace('V','')
            current_counts = current_reading[0].replace('cnt','')
            current_float = current_reading[1].replace('mA','')

            dmm_current = decode_measurement(read_measurement(ser_dmm))

            if dmm_current == None:
                print("Unable to communicate with Fluke. Please make sure the DMM is on")
                sys.exit(1)
            
            file.write('     ')
            for i in range(3 - len(str(current_counts))):
                file.write(' ')
            file.write(str(current_counts))

            file.write('    ')
            for i in range(6 - len(str(dmm_current))):
                file.write(' ')
            file.write(str(dmm_current))

            file.write('            // ')
            for i in range(6 - len(str(current_float))):
                file.write(' ')
            file.write(str(current_float))

            file.write('               ')
            for i in range(6 - len(str(ps_voltage))):
                file.write(' ')
            file.write(str(ps_voltage))

            file.write('          ')
            for i in range(4 - len(str(batt_float))):
                file.write(' ')
            file.write(str(batt_float))

            file.write('            ')
            for i in range(4 - len(str(resistance))):
                file.write(' ')
            file.write(str(resistance))
            file.write('\r\n')

    ser_arduino.write("off\r\n".encode())
    ps.enable_output(False)
    ser_float.close()

    file.write('}\n')
    return

def vacuum_calibration(ps, file, floatnum, user):
    timestr = time.strftime("%Y/%m/%d %H:%M:%S ")
    file.write('/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
    file.write(' * $Id: vacuum-calibration.')
    file.write(str(floatnum))
    file.write(',v 1.1 ')
    file.write(timestr)
    file.write(str(user))
    file.write(' Exp $\n')
    file.write(' *~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
    file.write(' * RCS Log:\n')
    file.write(' *\n')
    file.write(' * $Log: vacuum-calibration.')
    file.write(str(floatnum))
    file.write(',v $\n')
    file.write(' * Revision 1.1 ')
    file.write(timestr)
    file.write(str(user))
    file.write('\n')
    file.write(' * Initial revision\n')
    file.write(' *\n')
    file.write(' *~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/\n')
    file.write('/*\n Absolute Vacuum Calibration done ')
    file.write(timestr)
    file.write(' -')
    file.write(str(user))
    file.write('\n*/\n')
    file.write('Calibration vacuum-apex-')
    file.write(str(floatnum))
    file.write('\n{\n')
    file.write('//  counts   Vac(psi) // comments\n')

    # Run Vacuum Cal here 

    file.write('}\n')
    return

def main(floatnum, user):
    print("Apex Calibration Automation Script")
    
    # Open DP712
    #ps = None
    ps = dp700.PowerSupply(port=ps_com)

    batt_filename = "battery-calibration." + str(floatnum)
    batt_image_filename = "battery-calibration-" + str(floatnum) + ".png"
    curr_filename = "current-calibration." + str(floatnum)
    vac_filename = "vacuum-calibration." + str(floatnum)

    batt_f = open(batt_filename, 'w+')
    curr_f = open(curr_filename, 'w+')
    vac_f = open(vac_filename, 'w+')
    
    # Execute Tests
    voltage_calibration(ps, batt_f, floatnum, user)
    current_calibration(ps, curr_f, floatnum, user)
    vacuum_calibration(ps, vac_f, floatnum, user)

    batt_f.close()
    curr_f.close()
    vac_f.close()

    flux_batt_file = "/net/alace/" + str(floatnum) + "/" + batt_filename
    flux_batt_image = "/net/alace/" + str(floatnum) + "/"  + batt_image_filename
    flux_curr_file = "/net/alace/" + str(floatnum) + "/" + curr_filename
    flux_vac_file = "/net/alace/" + str(floatnum) + "/" + vac_filename
    username = "f" + str(floatnum)

    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser(os.path.join("~",".ssh","known_hosts")))
    ssh.connect(host, username=username, password=password)
    sftp = ssh.open_sftp()
    sftp.put(batt_filename, flux_batt_file)
    sftp.put(batt_image_filename, flux_batt_image)
    sftp.put(curr_filename, flux_curr_file)
    sftp.put(vac_filename, flux_vac_file)
    sftp.close()
    ssh.close()


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--floatnum", dest="floatnum",
                      help="Provide floatnum")
    parser.add_option("-u", "--user", dest="user",
                      help="Provide username")
    (options,args) = parser.parse_args()

    if not options.floatnum:
        print("Bleep Blorp, Please provide a float number using the -f option")
        sys.exit(1)

    if not options.user:
        print("Bleep Blorp, please tell me who's running the test with the -u option")
        sys.exit(1)

    main(options.floatnum, options.user)
