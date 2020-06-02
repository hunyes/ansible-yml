#!/usr/bin/python

from autil import *
import getpass
import subprocess
import re

num = []
logfile = []
index =None
helpCommand=["-h", "-help", "--help"]

sgmp_region_dic={"an2":"ap-northeast-2","ew1":"eu-west","uw2":"us-west","as1":"ap-southeast","cn1":"cn-north"}
base_region_dic={"an2":"kr","ew1":"eu","uw2":"us","as1":"sg","cn1":"cn"}

noti_method_arr=["block", "unblock", "alarmcheck"]
service_name_arr=["VisionCloud"]
sgmp_elb={"eu-west":["alb.ath","alb.frnt","alb.rmap","alb.set","alb.tsyn"], "ap-northeast-2":["alb.ath","alb.fdbk","alb.frnt","alb.papi","alb.pdbq","alb.rmap","alb.set","alb.tsyn"], "ap-southeast":["alb.ath","alb.frnt","alb.rmap","alb.set","alb.tsyn"], "us-west":["alb.ath","alb.fdbk","alb.frnt","alb.lan","alb.papi","alb.pdbq","alb.pext","alb.pkbrk","alb.pmat","alb.product","alb.rmap","alb.set","alb.stub","alb.tsyn"], "cn-north":["alb.ath","alb.frnt","alb.lan","alb.set","alb.tsyn"]}
sgmp_dynamo=["analysis-setting-tbl", "tag-storage-tbl"]

try :
    if sys.argv[1] == 'install' or sys.argv[1] == 'cass' or sys.argv[1] == 'system' or sys.argv[1] == 'aws' or sys.argv[1] == 'util' or sys.argv[1] == 'service' :
        pass

    elif sys.argv[1] == "sgmp":
        sys.argv.insert(1, 'util')

    elif sys.argv[1] == "sgmp_elb":
        sys.argv.insert(1, "util")
        sys.argv.insert(3, "ELB")

    else:
        sys.argv.insert(1, 'app')
    
    playbook  = sys.argv[1]
    action = sys.argv[2]
    service = sys.argv[3]    

    if len(sys.argv) > 4 :
        for i in range(4,len(sys.argv)) :
            num.append(sys.argv[i])
    else :
        num = None

except:
    print 'check Usage'
    showUsage()
    if 'playbook' in globals().keys() and playbook in helpCommand:
        showHelp()
    exit()

try :
    who = getpass.getuser()
    # today = dt.datetime.now().strftime("%Y-%m-%d")
    # logger =  open('/storage/scripts/Sexecute/logs/log_'+who,'a')
    # setLogName(logger)
    # logger.write(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' '+str(sys.argv[1:])+'\n')

except:
    print 'error'
    pass
    exit()

# getCompress()
# getDeCompress()

region = os.uname()[1][2:5]
#print "region :" + region

findhosts = getHostInfo(service, num, playbook)
sgmp_elb_name = ""
if sys.argv[3] == "elb":
 
#    nslookup_str= "nslookup " + os.uname()[1] + "|grep Name|awk -F':' '{print$2}'|awk -F'.' '{print$2}'"
#    sgmp_region = commands.getstatusoutput(nslookup_str)[1]
#    if sgmp_region != "ap-northeast-2":
#        sgmp_region = sgmp_region[0:-2]

    sgmp_region = sgmp_region_dic[region]
#    print "sgmp_region" + sgmp_region

#    print sgmp_elb[sgmp_region]
    input_text = "| Input " +sgmp_region + " ELB Name (" + ", ".join(sgmp_elb[sgmp_region]) + ") : "
    findhosts = raw_input(input_text)

elif  sys.argv[3] == "dynamo" :

    sgmp_region = sgmp_region_dic[region]
    dynamo_select = raw_input('| Select Noti Method Number ( 1.analysis-setting-tbl  2.tag-storage-tbl )  :')

    dmn = int(dynamo_select)
    if dmn <=0 and dmn > 2:
        print "Wrong Noti Method NUmber"
        exit()

    findhosts = sgmp_dynamo[dmn-1]


preConfig(findhosts, playbook,action,service)


#forks = getForks()
forks = "1"
if playbook != 'aws' and playbook != "util":
    forks = getForks()

# passwd = getPasswd()



#ansiblestr = 'ansible-playbook /vcloud/ansible/playbooks/' + playbook + '.yml -e action=' + action + ' -e role=' + service + ' -l ' + findhosts + ' -e serial=' + forks + ' -k '
#ansiblestr = 'ansible-playbook /vcloud/ansible/playbooks/' + playbook + '.yml -e action=' + action + ' -e role=' + service + ' -l ' + findhosts + ' -e serial=' + forks + ' -f ' + forks +  ' -k '
ansiblestr = 'ansible-playbook /vcloud/ansible/playbooks/' + playbook + '.yml -e action=' + action + ' -e role=' + service + ' -e region=' + region + ' -e serial=' + forks +  ' -l ' + findhosts + ' -f ' + forks + ' -k '

if playbook == 'aws':
    hostlist = findhosts.split(":")
    if len(hostlist) != 1:
        print ">>>> You have to select one instance. <<<<"
        exit()

    passwd = getPasswd()
    yn = checkPassword(passwd)
    if yn == False :
        print "Password check failed"
        exit();

    ec2info = getEC2Info(findhosts)
#    print "111:" + ec2info["ec2_id"]
#    print "222:" + ec2info["ec2_region"]
#    print "333:" + ec2info["ec2_subnet_id"]

    ansiblestr = 'ansible-playbook /vcloud/ansible/playbooks/' + playbook + '.yml -e action=' + action + ' -e role=' + service + ' -e ec2_id=' + ec2info["ec2_id"] + ' -e ec2_region=' + ec2info["ec2_region"] + ' -e ec2_subnet_id=' + ec2info["ec2_subnet_id"]
#    print "ansiblestr:" + ansiblestr

elif action == "sgmp" or action == "sgmp_elb":
    noti_method = raw_input('| Select Noti Method Number ( 1.block  2.unblock  3.alarmcheck ) :')

    nmn = int(noti_method)
    if nmn <=0 and nmn > 3:
        print "Wrong Noti Method NUmber"
        exit()

#    snn = int(service_name)
#    if snn <=0 and snn > 3:
#        print "Wrong Service NUmber"
#        exit()


    findhosts = findhosts.replace(" ", "")
    findhosts = findhosts.replace(",", ":")
    new_find_hosts = "\\\"" + findhosts.replace(":", "\\\",\\\"") + "\\\""

#    nslookup_str= "nslookup " + os.uname()[1] + "|grep Name|awk -F':' '{print$2}'|awk -F'.' '{print$2}'"
#    sgmp_region = commands.getstatusoutput(nslookup_str)[1]
#    if sgmp_region != "ap-northeast-2":
#        sgmp_region = sgmp_region[0:-2]

    sgmp_region = sgmp_region_dic[region]
    print "sgmp_region" + sgmp_region

#    ansiblestr = 'ansible-playbook /vcloud/ansible/playbooks/' + playbook + '.yml -e action=' + action + ' -e method=' + noti_method_arr[nmn - 1] + ' -e service=' + service_name_arr[snn-1] + ' -e region=' + sgmp_region +  ' -e host=' + new_find_hosts + ' -l ' +  os.uname()[1] + ' -k '
    ansiblestr = 'ansible-playbook /vcloud/ansible/playbooks/' + playbook + '.yml -e action=' + action + ' -e method=' + noti_method_arr[nmn - 1] + ' -e service=' + service_name_arr[0] + ' -e region=' + sgmp_region +  ' -e host=' + new_find_hosts + ' -l ' +  os.uname()[1] + ' -k '
#    print ansiblestr

if action == 'deploy' or action == 'autodeploy' or action == 'autodeploy_ig' or action=='send' or action=='autodeploy_ps' or action=='pythondeploy' :
    deploy_dir = raw_input('| Insert deploy source directory  : ')
    war_version = raw_input('| Insert war version : ')
    ansiblestr += ' -e src_dir=' + deploy_dir + ' -e src_war_name=' + war_version

elif action == 'config' or action == 'diff' :
    deploy_dir = raw_input('| Insert deploy source directory  : ')
    ansiblestr += ' -e src_dir=' + deploy_dir

elif action == 'diff_alone' :
    deploy_dir = raw_input('| Insert deploy source directory  : ')
    src_file = raw_input('| Insert build filename : ')
    dest_file = raw_input('| Insert server filename : ')
    ansiblestr += ' -e src_dir=' + deploy_dir + ' -e src_file=' + src_file + ' -e dest_file=' + dest_file

elif action == 'redis_samba' :
    Samba_Install_File = raw_input('| Insert install file name : ')
    ansiblestr += ' -e Samba_Install_File=' + Samba_Install_File

elif action == 'cry' :
    service_id = raw_input('| Insert server.id (ex IoT, ORS) : ')
    ansiblestr += ' -e service_id=' + service_id

elif action == 'cryagent' :
    service_id = raw_input('| Insert server.id (ex bnr, ors) : ')
    canary_ip = raw_input('| Insert canary service ip : ')
    target_pkg = raw_input('| Insert to profile the custom classes-package : ')
    license_key = raw_input('| Insert license.key : ')
    ansiblestr += ' -e service_id=' + service_id + ' -e canary_ip=' + canary_ip
    ansiblestr += ' -e target_pkg=' + target_pkg + ' -e LicenseKey=' + license_key

elif action == 'jenagent' or action =='jenagent45' or action =='jenagent46' or action =='jenagent17900' :
    Jennifer_ip = raw_input('| Insert jennifer service ip : ')
    AgentName = raw_input('| Insert Agent Name (ex,O01 : ')
    ansiblestr += ' -e Jennifer_ip=' + Jennifer_ip + ' -e AgentName=' + AgentName

elif action == 'sed' :
    old = raw_input('| Insert old word : ')
    new = raw_input('| Insert new word : ')
    fileDir = raw_input('| Insert fileDir : ')
    ansiblestr += ' -e old=' + old + ' -e new=' + new + ' -e fileDir=' + fileDir

#elif action == 'isams_env' :
#    old_ip = raw_input('| Insert old ip : ')
#    ansiblestr += ' -e old_ip=' + old_ip

elif action == 'uploader' or action == 'uploader_konan' :
    targetFolder = raw_input('| targetFolder(ex. icls_eu, lrec_kr..) : ')
  #  filesName = raw_input('| ex:/vcloud/tomcat/logs/applogs/role.log : ')
    ansiblestr += ' -e targetFolder=' + targetFolder
  #  ansiblestr += ' -e filesName=' + filesName

elif action == 'k8s_node' and service != 'qif' :
    base_region = base_region_dic[region]
    targetFolder = service + '_' + base_region
    ansiblestr += ' -e targetFolder=' + targetFolder

elif action == 'k8s_node' and service == 'qif' :
    base_region = base_region_dic[region]
    targetFolder_qifa = 'qifa_' + base_region
    ansiblestr += ' -e targetFolder_qifa=' + targetFolder_qifa
    targetFolder_qifm = 'qifm_' + base_region
    ansiblestr += ' -e targetFolder_qifm=' + targetFolder_qifm

#elif action == 'tele' :
#    PID = raw_input('| Insert PID DIR : ')
#    FILE = raw_input('| Insert FILE NAME : ')
#    ansiblestr += ' -e PID=' + PID + ' -e FILE=' + FILE

elif action == 'tele_setdb' :
    PassWD = raw_input('| Insert granafa admin_PW : ')
    Datasource = raw_input('| Insert setup Datasource : ')
    ansiblestr += ' -e PassWD=' + PassWD + ' -e Datasource=' + Datasource

elif action == 'tele_rm' :
    module = raw_input('| Insert module name : ')
    num = raw_input('| Insert number ex) 1 | 3,5 | 5:8 : ')
    ansiblestr += ' -e module=' + module + ' -e num=' + num


elif action == 'redis' :
    redis_port = raw_input('| Insert redis service port (ex 13211) : ')
    redis_slaveof = raw_input('| Insert redis slaveof (masterIp, masterPort) : ')
    redis_maxmemory = raw_input('| Insert redis maxmemory (ex 10gb) : ')
    redis_cluster_enabled = raw_input('| redis cluster enabled? (yes/no) : ')
    ansiblestr += ' -e \'redis_port="' + redis_port + '"\' -e \'redis_slaveof="' + redis_slaveof + '"\''
    ansiblestr += ' -e \'redis_maxmemory="' + redis_maxmemory + '"\' -e \'redis_cluster_enabled="' + redis_cluster_enabled + '"\''
    print redis_slaveof

elif action == 'hostname' :
    ansiblestr += ' -e hostname=' + findhosts
#elif action == 'diff' :
#    ansiblestr += ' -e src_dir=' + deploy_dir + ' --check --diff'
#    file_name = raw_input('| Insert build filename : ')
#    file_name2 = raw_input('| Insert server filename : ')

#elif action == 'compact':
#    showResult(logger,chef_compact(passwd))

elif action == 'copy':
    src  = raw_input('| src :')
    dest = raw_input('| dest : ')
    owner = raw_input('| owner (default:vcloudusr) : ')
    group = raw_input('| group (default:vcloud.app) : ')
    mode = raw_input('| mode (default:644) : ')
    if owner == '':
        owner = 'vcloudusr'
    if group == '':
        group = 'vcloud.app'
    if mode == '':
        mode = '644'

#    mode = raw_input('| mode : ')
#    ansiblestr += '-e src=' + src + ' -e dest=' + dest + ' -e owner=' + owner + ' -e group=' + group + ' -e mode=' + mode
    ansiblestr += '-e src=' + src + ' -e dest=' + dest + ' -e owner=' + owner + ' -e group=' + group + ' -e mode=' + mode


if service != 'prx' and service != 'cprx':
    if action == 'taillog' :
        logfile = raw_input('| Insert log file name [tomcat/applog] : ')


if action == 'diff' or action == 'diff_alone' :
    hostname = commands.getstatusoutput('hostname')[1]
    ansiblestr = ansiblestr.replace(findhosts, hostname)

    if action == 'diff' :
        ansiblestr = ansiblestr.replace('action=diff','action=show_val')
    else :
        ansiblestr = ansiblestr.replace('action=diff_alone','action=show_val')
    ansiblestr += ' -e playbook=app'

    pw = getpass.getpass('SSH password: ')
    ansiblestr = ansiblestr.replace(' -k','')
    ansiblestr += ' -e ansible_ssh_pass=' + pw

#    print 'ansiblestr:' + ansiblestr
#    print 'acton:' + action

    command = commands.getstatusoutput(ansiblestr)[1]

    value_dict = parsingValue(command, 'msg')

    if action == 'diff' :
        result = diff_folder(findhosts, value_dict['module_configdir'] + '/' + deploy_dir + '/props', value_dict['module_propertydir'], pw)
        print '====================================='
        for fileObject in result :
            print fileObject[0]
            print fileObject[1]
            for line in fileObject[2] :
                print line
            print '====================================='
    else :
        fileObject = diff_file(findhosts, value_dict['module_configdir'] + '/' + deploy_dir + '/props/' + src_file, value_dict['module_propertydir'] + '/' + dest_file, pw)

        print '====================================='
        print fileObject[0]
        print fileObject[1]
        for line in fileObject[2] :
            print line
        print '====================================='

elif action == 'sgmp' or action == 'sgmp_elb':
    os.system(ansiblestr)

elif playbook == 'util':
    netstat(ansiblestr)

else:
#    print ansiblestr
    os.system(ansiblestr)
