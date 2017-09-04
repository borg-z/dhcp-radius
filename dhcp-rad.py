import pika
import requests
from subprocess import getoutput
import pyrad.packet
from pyrad.client import Client
from pyrad.dictionary import Dictionary


cred = pika.PlainCredentials('sorm', 'qYVpTuGR')  # rabbit
param = pika.ConnectionParameters('dhcp1', 5672, '/', cred)  # rabbit

srv = Client(server="127.0.0.1", secret=b"Kah3choteereethiejeimaeziecumi",
			 dict=Dictionary("dictionary"))  # radius


def callback(ch, method, properties, body):
	#	print (body)
	body = body.decode("utf-8").split()
	if 'commit' in body:
		#		print (body)
		ip = body[5]
		vlan = body[7]
		status = 'Start'
		getid_by_vlan(vlan, ip, status)
	elif 'expiry' in body:
		ip = body[5]
		vlan = getoutput(
			"grep " + ip + " /var/log/dhcpd.log | grep exp -B1 | tail -n2").split('\n')[0].split()[9]
		status = 'Stop'
		getid_by_vlan(vlan, ip, status)

	elif 'release' in body:
		ip = body[5]
		vlan = body[7]
		status = 'Stop'
		getid_by_vlan(vlan, ip, status)


def getid_by_vlan(vlan, ip, status):
	resp = requests.get(
		'https://site.com/monitoring/opticalaccountidbyvlan?vlan=' + vlan)
	clientid = resp.content.decode("utf-8")
	try:
		int(clientid)
	except:
		pass
	else:
		send(ip, clientid, status)


def send(ip, clientid, status):
	print('ip: {} id: {} status {}'.format(ip, clientid, status))
	req = srv.CreateAcctPacket(User_Name=clientid)
	req["Framed-IP-Address"] = ip
	req["Acct-Status-Type"] = status
	try:
		srv.SendPacket(req)
	except pyrad.client.Timeout:
		print("RADIUS server does not reply")
		pass

	except socket.error as error:
		print("Network error: " + error[1])
		pass


def connect():
	connection = pika.BlockingConnection(param)
	channel = connection.channel()
	channel.queue_declare(queue='sorm', durable=True)
	channel.basic_consume(callback,
						  queue='sorm',
						  no_ack=True)
	return channel


channel = connect()

while channel.is_open == True:
	try:
		channel.start_consuming()
		a = a + 1
		print(a)

	except:
		connect()
