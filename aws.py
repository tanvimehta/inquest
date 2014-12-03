import boto.ec2 as ec2
import sys
from subprocess import call
import os
import paramiko 
import StringIO
import time

def init(d):
	region = d['region']
	key_id = d['key_id']
	access_key = d['access_key']

	conn = ec2.connect_to_region(region, 
		aws_access_key_id=key_id,
		aws_secret_access_key=access_key)

	key = conn.create_key_pair('keyPair1')
	key.save('.')

	groups = conn.get_all_security_groups()
	found = False
	for group in groups: 
		if group.name == "csc326-group5":
			found = True 
			break 
	if found == False: 
		group = conn.create_security_group("csc326-group5", "web search called inquest")
		group.authorize(ip_protocol='icmp', from_port=-1, to_port=-1, cidr_ip='0.0.0.0/0')
		group.authorize(ip_protocol='tcp', from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
		group.authorize(ip_protocol='tcp', from_port=80, to_port=80, cidr_ip='0.0.0.0/0')

	resObj = conn.run_instances('ami-8caa1ce4', instance_type='t1.micro', security_groups=[group.name], key_name="keyPair1")
	return  (conn, resObj)

def wait(conn, inst_id):
	while True:
		print "Waiting for instance " + str(inst_id) + " to start running "
		time.sleep(5)
		a = conn.get_all_instances()
		for i in a: 
			if i.instances[0].id == inst_id:
				if i.instances[0].state == u'running':
					return
				break

def wait_machine(pub_ip):
	while True: 
		print "Waiting for machine to receive ping"
		time.sleep(5)
		a = os.system('ping -c 4 ' + pub_ip)
		if a == 0: 
			break;


def static_add(conn, resObj):
	address = conn.allocate_address()
	address.associate(instance_id = resObj.instances[0].id)
	return address

def run():
	d = {}
	file_name = sys.argv[1]
	f = open(file_name)
	for line in f:
		(k, v) = line.split()
		d[k] = v

	os.system('wget https://pypi.python.org/packages/source/b/boto/boto-2.34.0.tar.gz#md5=5556223d2d0cc4d06dd4829e671dcecd ; tar -zxvf boto-2.34.0.tar.gz')
	os.system('cd boto-2.34.0; python setup.py install --user')
	conn, resObj = init(d)
	wait(conn, resObj.instances[0].id)
	my_ip = static_add(conn, resObj)
	wait_machine(my_ip.public_ip)
	ip = copy(my_ip.public_ip, 'keyPair1.pem')
	#return resObj, conn , ip
	time.sleep(2)
	print 'IP address = ' + ip + ' Instance Id ' + str(resObj.instances[0].id)
	return ip

def print_messages(stdout, stderr, stdin):
	print stdout.readlines()

def copy(ip, key_file):
	# Copy my files
	my_machine = 'ubuntu@' + ip
	remote_address = 'ubuntu@' + ip + ":~/"
	os.system('mkdir local_dir')
	os.system('cp inquest.py local_dir/')
	os.system('cp -r static local_dir/')
	os.system('cp trie_implementation.py local_dir/')
	scp_string = "scp -o StrictHostKeyChecking=no -i " + key_file + " -r local_dir " + remote_address
	os.system(scp_string)
	os.system("rm -rf local_dir")

	ssh_string_f = 'ssh -o StrictHostKeyChecking=no -f -i ' +  key_file  +  ' ' + my_machine 
	ssh_string_nof = 'ssh -o StrictHostKeyChecking=no -i ' +  key_file  +  ' ' + my_machine 

	#Download dependencies 
	os.system(ssh_string_nof + ' \" cd ~/local_dir; wget https://pypi.python.org/packages/source/b/bottle/bottle-0.12.7.tar.gz ; tar -zxvf bottle-0.12.7.tar.gz \"')
	os.system(ssh_string_nof + ' \" cd ~/local_dir; sudo apt-get -y install git\"')
	os.system(ssh_string_nof + ' \" cd ~/local_dir; git clone https://github.com/bbangert/beaker.git\"')
	os.system(ssh_string_nof + ' \" cd ~/local_dir; git clone --recursive git://github.com/google/google-api-python-client.git \"')

	#Install dependencies
	os.system(ssh_string_nof +  ' \" cd ~/local_dir/beaker; sudo apt-get install python-setuptools; python setup.py install --user \" ')
	os.system(ssh_string_nof +  ' \" cd local_dir/google-api-python-client; python setup.py install --user  \" ')
	os.system(ssh_string_nof +  ' \" cd local_dir/bottle-0.12.7; python setup.py install --user  \"')

	#Launch the search engine
	os.system(ssh_string_f +  ' \" cd local_dir; sudo python inquest.py > /dev/null \"')

	return ip

def copy_main():
	copy(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
	run()