import boto.ec2 as ec2

def init():
	conn = ec2.connect_to_region("us-east-1", 
		aws_access_key_id='AKIAINZ24HFKODXM4E2Q',
		aws_secret_access_key='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')

	key = conn.create_key_pair('keyPair0')
	key.save('.')

	group = conn.create_security_group("csc326-group5", "web search called inquest")

	group.authorize(ip_protocol='icmp', from_port=-1, to_port=-1, cidr_ip='0.0.0.0/0')
	group.authorize(ip_protocol='tcp', from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
	group.authorize(ip_protocol='tcp', from_port=80, to_port=80, cidr_ip='0.0.0.0/0')

	resObj = conn.run_instances('ami-8caa1ce4', instance_type='t1.micro', security_groups=[group.name], key_name="keyPair0")
	return  (conn, resObj)

def static_add(conn, resObj):
	address = conn.allocate_address()
	address.associate(instance_id = resObj.instances[0].id)
	return address

def run():
	conn, resObj = init()
	static_add(conn, resObj)
	return resObj, conn