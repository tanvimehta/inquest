import sys
import boto.ec2 as ec2

def terminate():
	if len(sys.argv) < 3: 
		print "Invalid Usage: try \"python terminate_instance.py <credentials> <instance_id_to_terminate> \" " 
	instance_id = sys.argv[2]

	d = {}
	file_name = sys.argv[1]
	f = open(file_name)
	for line in f:
		(k, v) = line.split()
		d[k] = v

	region = d['region']
	key_id = d['key_id']
	access_key = d['access_key']

	conn = ec2.connect_to_region(region, 
		aws_access_key_id=key_id,
		aws_secret_access_key=access_key)

	l_t = [ ]
	l_t = conn.terminate_instances(instance_ids=[instance_id])
	print l_t 
	for instance in l_t: 
		if instance_id == str(instance.id):
			print "Instance " + instance_id + " successfully terminated"
			break

if __name__ == "__main__":
	terminate()