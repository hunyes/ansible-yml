#!/usr/bin/python
import json
import os
import commands
import string
import subprocess
#### before used (/vcloud/ansible/ec2.py --refresh-cache)
json_data=open("/home/admuser/.ansible/tmp/ansible-ec2.index").read()
json_data2=open("/home/admuser/.ansible/tmp/ansible-ec2.cache").read()
data = json.loads(json_data)
data2 = json.loads(json_data2)
instance_list = data.keys()
instance_list.sort()
key_list = []

tag_Class0=""
tag_Class1=""
tag_role1=""
tag_role2=""
SEC_ASSETS=""

#print instance_list
def define_name(instance_name):
        short_name = instance_name.split('-')
        return short_name[1][:-3]


def create_tag_class0(sName, instance_id):
        if sName in ('service1','service2'):
                class0Name = 'VCloud3.0'
        else:
                class0Name= 'VCloud1.0'

        subprocess.call('aws ec2 create-tags --resources ' + instance_id  + ' --tags \'Key=Class0,Value=' + class0Name + '\' ' , shell=True)

def create_tag_class1(sName, instance_id):
        if sName in ('testa','testb'):
                class1Name = 'Common'
        elif sName in ('testc','testd'):
                class1Name = 'IGService'
        else:
                class1Name= 'check'

        subprocess.call('aws ec2 create-tags --resources ' + instance_id  + ' --tags \'Key=Class1,Value=' + class1Name + '\' ' , shell=True)


def create_tag_role(sName, instance_id):
        subprocess.call('aws ec2 create-tags --resources ' + instance_id  + ' --tags \'Key=role,Value=' + sName + '\,sys\,\' ' , shell=True)

def create_SEC_ASSETS(sName, instance_id):
        if sName in ('testa'):
                SEC_ASSETS = "Image Test Server"
        elif sName in ('testb'):
                SEC_ASSETS = "Movie Test Server"
        elif sName in ('testc'):
                SEC_ASSETS = "Game Test Server"
        elif sName in ('testd'):
                SEC_ASSETS = "Music Test Server"

        subprocess.call('aws ec2 create-tags --resources ' + instance_id  + ' --tags \'Key=SEC_ASSETS,Value=' + SEC_ASSETS + '\' ' , shell=True)

def des_tag():
    for i in instance_list:
        try:
                global tag_Class0
                global tag_Class1
                global tag_role1
                global tag_role2
                global SEC_ASSETS
                key_list =  data2['_meta']['hostvars'][i].keys()

                #print key_list
                if 'ec2_tag_Class0' in key_list :
                        if data2['_meta']['hostvars'][i]['ec2_tag_Class0']:
                                tag_Class0 = data2['_meta']['hostvars'][i]['ec2_tag_Class0']
                        else:
                                print i
                                sName =define_name(i)
                                instance_id = data2['_meta']['hostvars'][i]['ec2_id']
                                create_tag_class0(sName, instance_id) #aws cli create tag
                else:
                        print i
                        sName =define_name(i)
                        instance_id = data2['_meta']['hostvars'][i]['ec2_id']
                        create_tag_class0(sName, instance_id) #aws cli create tag

                if 'ec2_tag_Class1' in key_list :
                        if data2['_meta']['hostvars'][i]['ec2_tag_Class1']:
                                tag_Class1 = data2['_meta']['hostvars'][i]['ec2_tag_Class1']
                        else:
                                print i
                                sName =define_name(i)
                                instance_id = data2['_meta']['hostvars'][i]['ec2_id']
                                create_tag_class1(sName, instance_id)  #aws cli create tag
                else:
                        print i
                        sName =define_name(i)
                        instance_id = data2['_meta']['hostvars'][i]['ec2_id']
                        create_tag_class1(sName, instance_id)  #aws cli create tag


                if 'ec2_tag_role' in key_list :
                        if data2['_meta']['hostvars'][i]['ec2_tag_role']:
                                tag_role1 = data2['_meta']['hostvars'][i]['ec2_tag_role'][0]
                                tag_role2 = data2['_meta']['hostvars'][i]['ec2_tag_role'][1]
                        else:
                                print i
                                sName =define_name(i)
                                instance_id = data2['_meta']['hostvars'][i]['ec2_id']
                                create_tag_role(sName, instance_id)  #aws cli create tag
                else:
                        print i
                        sName =define_name(i)
                        instance_id = data2['_meta']['hostvars'][i]['ec2_id']
                        create_tag_role(sName, instance_id)  #aws cli create tag

                if 'ec2_tag_SEC_ASSETS' in key_list :
                        if data2['_meta']['hostvars'][i]['ec2_tag_SEC_ASSETS']:
                                SEC_ASSETS = data2['_meta']['hostvars'][i]['ec2_tag_SEC_ASSETS']
                        else:
                                print i
                                sName =define_name(i)
                                instance_id = data2['_meta']['hostvars'][i]['ec2_id']
                                create_SEC_ASSETS(sName, instance_id)  #aws cli create tag
                else:
                        print i
                        sName =define_name(i)
                        instance_id = data2['_meta']['hostvars'][i]['ec2_id']
                        create_SEC_ASSETS(sName, instance_id)  #aws cli create tag

                print  i + '\t' + tag_Class0 + '\t' + tag_Class1 + '\t' + '\t' + tag_role1 + '\t' + tag_role2 + '\t' + SEC_ASSETS

        except ValueError:
            pass


des_tag()
