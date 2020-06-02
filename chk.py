#!/usr/bin/python

import paramiko                                         # SSH CONNECT
import getpass                                          # INPUT PASSWD
import sys, os                                          # INPUT ARGV, FILE CHECK
import commands                                         # COMMAND
from time import sleep                                  # SLEEP
import json                                             # EC2 INFO
from multiprocessing import Process, Lock               # MUTIPROCESSING, PROCESS CONTROL
import socket                                           # GAIERROR EXCEPTION(SSH CONNECT FAIL)
import datetime                                         # DATE TIME

sys.tracebacklimit = 0                                  # TRACEBACK LOG DISABLE

DELAY = 0                                               # RESULT SPEED CONTROL

HOSTNAME = []                                           # HOSTNAME LIST
USERNAME = 'srvadm'                                  # SSH USERNAME
PORT = 22                                             # SSH PORT

RESULTTXT = '/srv/utils/chk/result.txt'              # RESULT LOG FILE

EX = ['grep', 'find', 'cat', 'touch']                   # RESULT EXCEPTION : NO RESULT VALUE
EN = ['ERR', 'No Results']                              # RESULT EXCEPTION : RESULT VALUE PRINT RED COLOR
CN = ['command not found', 'No such file or directory'] # RESULT EXCEPTION : EXCEPT \n

def guide():
        print ('------------------------------')
        print ('ex : chk image 1 hostname')
        print ('ex : chk image 1:10 hostname')
        print ('ex : chk image 1,5,10 hostname')
        print ('ex : chk image 1: "hostname;ls"')
        print ('ex : chk sys all hostname')
        print ('------------------------------')
        print ('ex : chk image 1:10 chkoff')
        print ('ex : chk image 1:10 chkon')
        print ('------------------------------')
        print ('ex : chk image 1:10 inf')
        print ('ex : chk image ip inf')
        print ('ex : chk image 1:10 log')
        print ('ex : chk image 1:10 route53')
        print ('ex : chk sys all sudo')
        print ('-------------------------------')
        exit()

if len(sys.argv) == 4:
        MODULE = sys.argv[1]
        NUM = sys.argv[2]
        CMD = sys.argv[3]

        if MODULE == 'sys' and NUM != 'all':
                guide() # FUNCTION
        elif CMD == 'route53':
                CHOICE = raw_input('1.CREATE, 2.DELETE :  ')
        else:
                if CMD == 'log':
                        USERNAME = 'srvusr'

                PASSWORD = getpass.getpass('PASSWORD :')

                if os.path.exists(RESULTTXT):
                        os.system('rm -f ' + RESULTTXT)

else:
        guide() # FUNCTION

def hostname():
        if MODULE == 'sys' and NUM == 'all':
                sys_last()      # FUNCTION
                return HOSTNAME
        else:
                try:
                        if ':' in NUM:
                                CHECK = NUM.split(':')
                                FIRST = CHECK[0]
                                LAST = CHECK[1]

                                if not LAST:
                                        LAST = sys_last()       # FUNCTION

                                for i in range(int(FIRST), int(LAST) + 1):
                                        TRANS = '{:03d}'.format(i)
                                        HOSTLIST = MODULE + TRANS
                                        HOSTNAME.append(HOSTLIST)
                                return HOSTNAME
                        elif ',' in NUM:
                                CHECK = NUM.split(',')
                                for i in CHECK:
                                        TRANS = '{:03d}'.format(int(i))
                                        HOSTLIST = MODULE + TRANS
                                        HOSTNAME.append(HOSTLIST)
                                return HOSTNAME
                        elif NUM == 'all':
                                LAST = sys_last()       # FUNCTION
                                return HOSTNAME
                        elif NUM == 'ip':       # INFLUXDB DELETE
                                HOSTNAME.append('ip-10')
                                return HOSTNAME
                        else:
                                TRANS = '{:03d}'.format(int(NUM))
                                HOSTLIST = MODULE + TRANS
                                HOSTNAME.append(HOSTLIST)
                                return HOSTNAME
                except:
                        guide() # FUNCTION

def main():
        HOSTNAME = hostname()   # FUNCTION
        LOCK = Lock()           # FUNCTION
        PROCS = []

        LEN = len(HOSTNAME)
        FIRST = 0
        LAST = 20
        try:
                while LEN > FIRST:
                        for i in HOSTNAME[FIRST:LAST]:
                                PROC = Process(target=ssh_connect, args=(LOCK, i, ))
                                PROCS.append(PROC)
                                PROC.start()
                                sleep(float(DELAY))
                        for PROC in PROCS:
                                PROC.join()

                        FIRST = LAST
                        LAST = FIRST + LAST
        except KeyboardInterrupt:
                PROC.terminate()
                for i in PROCS:
                        i.terminate()

def ssh_connect(LOCK, HOSTNAME):
        try:
                if CMD == 'chkoff' or CMD == 'chkon':                   # CHKOFF&CHKON
                        on_off_check(LOCK, HOSTNAME)    # FUNCTION
                elif CMD == 'inf':                                      # INFLUXDB DELETE
                        influx(LOCK, HOSTNAME)          # FUNCTION
                elif CMD == 'log':                                      # LOG REMOVE
                        log_rename(LOCK, HOSTNAME)      # FUNCTION
                elif CMD == 'route53':                                  # ROUTE53
                        route53(LOCK, HOSTNAME)         # FUNCTION
                elif CMD == 'sudo':                                     # SUDO CHECK
                        sudo(LOCK, HOSTNAME)
                else:
                        result(LOCK, HOSTNAME)          # FUNCTION
        except KeyboardInterrupt:
                interrupt(LOCK, HOSTNAME)               # FUNCTION
        except socket.gaierror:
                exist(LOCK, HOSTNAME)                   # FUNCTION
        except paramiko.AuthenticationException:
                auth(LOCK, HOSTNAME)                    # FUNCTION
        except socket.timeout:
                timout(LOCK, HOSTNAME)                  # FUNCTION


def sys_last():
        global HOSTNAME

        JSON = ec2_info()       #FUNCTION

        if NUM == 'all':
                ROLE = 'tag_role_' + MODULE
                HOSTNAME = JSON[ROLE]
                HOSTNAME.sort()
                return HOSTNAME
        else:
                ROLE = 'tag_role_' + MODULE
                LAST = len(JSON[ROLE])
                return LAST

def ec2_info():
        FILE='/home/srvadm/.ansible/tmp/ansible-ec2.cache'
        F = open(FILE, 'r')
        JSON = json.loads(F.read())
        F.close()
        return JSON

def file_open(WHERE):
        CHECK = []
        if WHERE == 'in.txt':
                READ = open('/srv/utils/chk/in.txt', 'r')
        elif WHERE == 'out.txt':
                READ = open('/srv/utils/chk/out.txt', 'r')

        while True:
                LINE = READ.readline()
                CHECK.append(LINE)
                if not LINE: break
        READ.close()
        return CHECK

def on_off_check(LOCK, HOSTNAME):
        IN_CHECK = []
        OUT_CHECK = []
        DATALIST = []
        STDERR = []

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD, port=PORT, timeout=2)

        IN_CHECK = file_open('in.txt')  # FUNCTION

        CNT = 0
        for i in IN_CHECK:
                stdin, stdout, stderr = client.exec_command(i)
                STDERR.append(stderr.read())

                if STDERR[CNT]:
                        ERR = 'ERR : ' + STDERR[CNT]
                        DATALIST.append(ERR)
                else:
                        DATALIST.append(stdout.read().lstrip())
                        if any(j in i for j in EX) and not DATALIST[CNT]:
                                DATALIST[CNT] = (color.NOR)
                CNT = CNT + 1

        W = open(RESULTTXT, 'a')
        W.write(color.NL + HOSTNAME + color.RN)
        NUM = 1
        for i in DATALIST:
                if i:
                        W.write(str(NUM) + color.DOT + i)
                        NUM = NUM + 1
                W.write('\n')

        LOCK.acquire()
        print (color.NGL + HOSTNAME + color.RE)

        IN_CNT = 0
        while (len(DATALIST) - 1) > IN_CNT:
                IN = DATALIST[IN_CNT]
                if any(j in IN for j in EN):
                        if any(j in IN for j in CN):
                                print (str(IN_CNT + 1) + color.DR + IN + color.END)
                        else:
                                print (str(IN_CNT + 1) + color.DR + IN + color.NE)
                elif not IN:
                        print (str(IN_CNT + 1) + color.DC)
                else:
                        print (str(IN_CNT + 1) + color.DOT + IN)
                IN_CNT = IN_CNT + 1
        LOCK.release()

        if CMD == 'chkoff':
                W.close()
                client.close()

        elif CMD == 'chkon':
                OUT_CHECK = file_open('out.txt')  # FUNCTION

                LOCK.acquire()
                print (color.NY + HOSTNAME + color.CE)

                IN_CNT = 0
                while (len(OUT_CHECK) - 1)  > IN_CNT:
                        if not IN_CHECK[IN_CNT]: break

                        else:
                                IN = DATALIST[IN_CNT].replace('\n', '')
                                OUT = OUT_CHECK[IN_CNT].replace("\n", '')
                                if any(j in IN for j in EN):
                                        print (str(IN_CNT + 1) + color.DR + IN + color.DE + OUT + color.FE)
                                        W.write(str(IN_CNT + 1) + color.DOT + IN + color.DE + OUT + color.FN)
                                elif IN == OUT:
                                        print (str(IN_CNT + 1) + color.DOT + IN + color.DE + OUT + color.T)
                                        W.write(str(IN_CNT + 1) + color.DOT + IN + color.DE + OUT + color.TN)
                                else:
                                        print (str(IN_CNT + 1) + color.DR + IN + color.DE + OUT + color.FE)
                                        W.write(str(IN_CNT + 1) + color.DOT + IN + color.DE + OUT + color.FN)
                        IN_CNT = IN_CNT + 1
                LOCK.release()
        W.close()
        client.close()

def result(LOCK, HOSTNAME):
        global CMD
        DATALIST = []
        STDERR = []

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD, port=PORT, timeout=2)

        if ';' in CMD:
                CHECK = CMD.split(';')
                CNT = 0
                for i in CHECK:
                        stdin, stdout, stderr = client.exec_command(i)
                        STDERR.append(stderr.read())

                        if STDERR[CNT]:
                                ERR = 'ERR : ' + STDERR[CNT]
                                DATALIST.append(ERR)
                        else:
                                DATALIST.append(stdout.read())
                                if any(j in i for j in EX) and not DATALIST[CNT]:
                                        DATALIST[CNT] = (color.NN)
                        CNT = CNT + 1
        else:
                CNT = 0
                if MODULE == 'qifa' and CMD == 'url':
                        CMD = '/srv/utils/url/url.sh'

                stdin, stdout, stderr = client.exec_command(CMD)
                STDERR.append(stderr.read())

                if STDERR[CNT]:
                        ERR = 'ERR : ' + STDERR[CNT]
                        DATALIST.append(ERR)
                else:
                        DATALIST.append(stdout.read())
                        if any(j in CMD for j in EX) and not DATALIST[CNT]:
                                DATALIST[CNT] = (color.NN)

        W = open(RESULTTXT, 'a')
        W.write(color.NL + HOSTNAME + color.RN)
        NUM = 1
        for i in DATALIST:
                if i:
                        W.write(str(NUM) + color.DOT + i)
                        NUM = NUM + 1
                W.write('\n')
        W.close

        LOCK.acquire()
        print (color.NGL + HOSTNAME + color.RE)
        IN_CNT = 0
        while (len(DATALIST)) > IN_CNT:
                IN = DATALIST[IN_CNT]
                if any(j in IN for j in EN):
                        print (str(IN_CNT + 1) + color.DR + IN.replace('\n', '') + color.NE)
                elif not IN:
                        print (str(IN_CNT + 1) + color.DC)
                else:
                        print (str(IN_CNT + 1) + color.DOT + IN)
                IN_CNT = IN_CNT + 1
        LOCK.release()

        client.close()

def influx(LOCK, HOSTNAME):
        STDERR = []
        DATALIST = []

        REGION = commands.getstatusoutput('hostname | cut -d "-" -f1')[1]

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect('gra001', username=USERNAME, password=PASSWORD, port=PORT, timeout=2)

        for i in HOSTNAME.split('\n'):
                DOCKER = "docker exec -i influxdb influx -execute 'drop series where host =~ /"
                if any(j in MODULE for j in ['qifm', 'qifa']):
                        CMD = DOCKER + i + "/' -database='" + REGION + "-qif'"
                else:
                        CMD = DOCKER + i + "/' -database='" + REGION + "-" + MODULE + "'"
                        print CMD

                stdin, stdout, stderr = client.exec_command(CMD)
                STDERR.append(stderr.read())

                CNT = 0
                if STDERR[CNT]:
                        ERR = 'ERR : ' + STDERR[CNT]
                        DATALIST.append(ERR)
                else:
                        DATALIST.append(stdout.read())
                        if not DATALIST[CNT]:
                                DATALIST[CNT] = (color.CRC)
                CNT = CNT + 1

        LOCK.acquire()
        print (color.NGL + HOSTNAME + color.RE)
        IN_CNT = 0
        while (len(DATALIST)) > IN_CNT:
                IN = DATALIST[IN_CNT]
                if any(j in IN for j in EN):
                        print (str(IN_CNT + 1) + color.DR + IN.replace('\n', '') + color.NE)
                else:
                        print (str(IN_CNT + 1) + color.DOT + IN)
                IN_CNT = IN_CNT + 1
        LOCK.release()

        client.close()

def log_rename(LOCK, HOSTNAME):
        LIST = []

        WHERE = '/logs/'
        #WHERE = '/tmp/'

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD, port=PORT, timeout=2)

        sftp = client.open_sftp()
        sftp.chdir(WHERE)

        DATALIST = sftp.listdir(WHERE)

        NOW = datetime.datetime.now()
        DATE = NOW.strftime('%Y-%m-%d_%H')

        HOUR = NOW - datetime.timedelta(hours=1)
        DATE_HOUR = HOUR.strftime('%Y-%m-%d_%H')

        APPLOG = 'app.log.'
        STATLOG = 'app.statistic.log.'
        VILOG = 'vision-cloud.log'
        VISTATLOG = 'vision-cloud.statistic.log'

        LOCK.acquire()
        print (color.NGL + HOSTNAME + color.RE)

        IN_CNT = 0
        while (len(DATALIST)) > IN_CNT:
                IN = DATALIST[IN_CNT]
                if any(j in IN for j in (APPLOG, STATLOG, VILOG, VISTATLOG)):
                        if not any(j in IN for j in ('_0.log', '_1.log', '_2.log', '_3.log')) or 'vision-cloud.log' in IN or 'vision-cloud.statistic.log' in IN:
                                LIST.append(IN)
                IN_CNT = IN_CNT + 1
                LIST.sort()
        print LIST
        for i in LIST:
                try :
                        CNT = 0
                        if APPLOG + DATE  in i or APPLOG + DATE_HOUR in i:
                                FILE = i.split('.')
                                while i:
                                        MODY_FILE = FILE[0] +'.' + FILE[1] + '.' + FILE[2] + '_' + str(CNT) + '.log'
                                        try:
                                                sftp.stat(WHERE + MODY_FILE)
                                                CNT = CNT + 1
                                        except:
                                                sftp.rename(i, MODY_FILE)
                                                print (i + color.DI + MODY_FILE + color.GCE)
                        elif STATLOG + DATE  in i or STATLOG + DATE_HOUR in i:
                                FILE = i.split('.')
                                while i:
                                        MODY_FILE = FILE[0] +'.' + FILE[1] + '.' + FILE[2] + '.' + FILE[3] + '_' + str(CNT) +'.log'
                                        try:
                                                sftp.stat(WHERE + MODY_FILE)
                                                CNT = CNT + 1
                                        except:
                                                sftp.rename(i, MODY_FILE)
                                                print (i + color.DI + MODY_FILE + color.GCE)
                        elif i == VILOG or (i == VISTATLOG and (MODULE != 'image' or MOUDLE != 'lrec')):
                                while i:
                                        MODY_FILE = i + '.' + DATE + '_' + str(CNT)
                                        try:
                                                sftp.stat(WHERE + MODY_FILE)
                                                CNT = CNT + 1
                                        except:
                                                sftp.rename(i, MODY_FILE)
                                                print (i + color.DI + MODY_FILE + color.GCE)
                except:
                        pass
        LOCK.release()

        client.close()

def route53(LOCK, HOSTNAME):
        if CHOICE == '1':
                ACTION = 'CREATE'
        elif CHOICE == '2':
                ACTION = 'DELETE'
        else:
                exit(0)

        DATALIST = []
        REGION = commands.getstatusoutput('hostname | cut -d "-" -f1')[1]

        JSON = ec2_info()       # FUNCTION

        HOST = REGION + '-' + HOSTNAME

        IP = JSON['_meta']['hostvars'][HOST]['ec2_private_ip_address']
        DNS = JSON['_meta']['hostvars'][HOST]['ec2_private_dns_name'].split(".")[0]

        if REGION == 'p1uw2':
                RECORDSET = '.us-west-2.compute.internal.'
                ROUTE53KEY = 'ABC12345XXX'
        elif REGION == 'p1ew1':
                RECORDSET='.eu-west-1.compute.internal.'
                ROUTE53KEY = 'ABC12345XXX'
        elif REGION == 'p1as1':
                RECORDSET = '.ap-southeast-1.compute.internal.'
                ROUTE53KEY = 'ABC12345XXX'
        elif REGION == 'p1an2':
                RECORDSET = '.ap-northeast-2.compute.internal.'
                ROUTE53KEY = 'ABC12345XXX'
        else:
                exit(0)

        DATALIST.append([HOST, HOSTNAME, IP, DNS])

        LOCK.acquire()
        print (color.NGL + HOSTNAME + color.RE)

        CNT = 0
        for i in DATALIST[CNT]:
                if IP != i:
                        NUM = HOSTNAME + "_" + str(CNT) + '.json'
                        STRING = {"Comment":"request","Changes":[{"Action":ACTION,"ResourceRecordSet":{"ResourceRecords":[{"Value":IP}],"Name":i + RECORDSET,"Type":"A","TTL":300}}]}
                        SEND = 'aws route53 change-resource-record-sets --hosted-zone-id ' + str(ROUTE53KEY) + ' --change-batch file:///tmp/' + NUM

                        with open('/tmp/' + NUM, 'w') as make_file:
                                json.dump(STRING, make_file, indent=4)

                        print commands.getstatusoutput(SEND)
                        os.remove('/tmp/' + NUM)
                        CNT = CNT + 1
        LOCK.release()

def sudo(LOCK, HOSTNAME):
        NOW = datetime.datetime.now()
        TODAY = NOW.strftime("%Y%m%d")

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD, port=PORT, timeout=2)

        stdin, stdout, stderr = client.exec_command("cat /usr/local/secuve/TOSSuite/Config/CmdCtrl.agt | grep cmdctlusradd | grep sudo | grep date | awk -F '=' '{print $11}'")

        DATE = stdout.readline()
        stdin, stdout, stderr = client.exec_command('ec2metadata | grep instance-id')
        ID=stdout.readline()

        LOCK.acquire()
        print (color.NGL + HOSTNAME + color.RE)
        if not DATE:
                print (color.RED + 'CmdCtrl.agt file is empty or cmdctlusradd field for sudo is not in the file' + color.END)

        else:
                SUDODATE = DATE[13:21]
                EXPR = int(SUDODATE) - int(TODAY)

                if SUDODATE and EXPR > 30:
                        print ID
                        print "sudo is allowed, sudo cmd will be expired on %s" % SUDODATE
                elif SUDODATE and EXPR < 31:
                        print color.YELLOW + ID
                        print "sudo is allowed, sudo cmd will be expired on "  + str(EXPR) + ' days' + color.END
                else:
                        print color.RED + ID
                        print color.RED + "sudo is not allowed, expirary date was %s" % SUDODATE + color.END
        LOCK.release()

def interrupt(LOCK, HOSTNAME):
        LOCK.acquire()
        print (color.NGL + HOSTNAME + color.RE)
        print (color.KIE)
        LOCK.release()

def exist(LOCK, HOSTNAME):
        LOCK.acquire()
        print (color.NGL + HOSTNAME + color.RE)
        print (color.HNE)
        LOCK.release()

def auth(LOCK, HOSTNAME):
        LOCK.acquire()
        print (color.NGL + HOSTNAME + color.RE)
        print (color.RAE)
        LOCK.release()

def timeout(LOCK, HOSTNAME):
        LOCK.acquire()
        print (color.NGL + HOSTNAME + color.RE)
        print (color.RTE)
        LOCK.release()

class color:
        GREEN = '\033[32m'
        RED = '\033[31m'
        YELLOW = '\033[33m'
        END = '\033[0m'
        DOT = '. '
        LEFT = '['
        RIGHT = ']'
        EXK = 'Keyboard interrupt!!'
        EXH = 'Host not exist!!'
        CRC = 'Command run completed!\n'
        CPS = ' Compare start'
        COM = ' Complete!'
        NOR = 'No Results'
        AUE = 'Authentication Exception!!'
        TO = 'Time Out!!'
        N = '\n'
        T = ' = TRUE'
        F = ' = FALSE'
        DE = ' || '
        DI = ' -> '

        RE = RIGHT + END
        DR = DOT + RED
        NE = N + END
        DC = DOT + CRC
        FE = F + END
        RN = RIGHT + N
        FN = F + N
        TN = T + N
        CE = CPS + END
        NL = N + LEFT
        NY = N + YELLOW
        NN = NOR + N

        KIE = RED + EXK + END
        HNE = RED + EXH + NE
        NGL = N + GREEN + LEFT
        GCE = GREEN + COM + END
        RAE = RED + AUE + END
        RTE = RED + TO + END

if __name__ == "__main__":
        main()
