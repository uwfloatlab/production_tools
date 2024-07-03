import pydp700
import datetime
import sys
import time
import cv2
import paramiko
import os
import serial
from optparse import OptionParser

host = 'flux'
password = "e=2.718"
last_response = True
ps_com ="/dev/com1"
apf11_com="/dev/com2"

#ser_v = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, bytesize=8,
#                      parity='N', stopbits=1, timeout=0.1, xonxoff=1,
#                      rtscts=0, dsrdtr=0)

#ser_c = serial.Serial(port='/dev/ttyUSB1', baudrate=115200, bytesize=8,
#                      parity='N', stopbits=1, timeout=0.1, xonxoff=1,
#                      rtscts=0, dsrdtr=0)

ser_float = None

voltages = [15.0, 14.0, 13.0, 12.0, 11.0, 10.0, 9.0, 8.0, 7.0, 6.0, 5.0]
resistance = [15, 30, 60, 120, 240, 480, 1000]

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
    ps_voltage_read = None

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
    file.write('//     counts  voltage ( Fluke Mulitimeter used for voltage readings )\n')
    
    # Run Voltage Cal here

    file.write('}\n')

    #ps.set_output_voltage(15.0)
    #ps.enable_output(True)

    ser_float = serial.Serial(port=apf11_com, baudrate=9600, bytesize=8,
                      parity='N', stopbits=1, timeout=1, xonxoff=True)
    
    time.sleep(1)
    ser_float.flush()
    ser_float.write(b'c\r\n')
    apf11_reading = ser_float.read_until(b' ] ')
    apf11_split_1 = apf11_reading.decode('utf8').split('] ')[0].replace('Battery [','').replace(',','')
    apf11_split_2 = apf11_split_1.split(' ')
    counts = apf11_split_2[1].replace('cnt','')
    float_v = apf11_split_2[2].replace('V','')
    print(counts)
    print(float_v)
    ser_float.close()
    sys.exit(0)

    for voltage in voltages:
        #ps.set_output_voltage(voltage)
        time.sleep(1)
        #ps_voltage_read = ps.get_output_voltage()
        file.write('          ')
        file.write(str(counts))
        file.write('     ')
        #file.write(str(float_v))
        file.write(str(ps_voltage_read))
        file.write('\r\n')

    ps.enable_output(False)

    return

def current_calibration(ps, file, floatnum, user):
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
    file.write('//  counts  current(Fluke ma) // Current(Float ma) // voltage(fluke) voltage(float)  switch\n')
    
    # Run Current Cal here

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
    ps = None
    #ps = pydp700.PowerSupply(port=ps_com)

    batt_filename = "battery-calibration." + str(floatnum)
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
    sys.exit(0)

    flux_batt_file = "/net/alace/" + str(floatnum) + "/" + batt_filename
    flux_curr_file = "/net/alace/" + str(floatnum) + "/" + curr_filename
    flux_vac_file = "/net/alace/" + str(floatnum) + "/" + vac_filename
    username = "f" + str(floatnum)

    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser(os.path.join("~",".ssh","known_hosts")))
    ssh.connect(host, username=username, password=password)
    sftp = ssh.open_sftp()
    sftp.put(batt_filename, flux_batt_file)
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
