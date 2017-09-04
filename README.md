# dhcp-radius
Convert DHCP replays to radius sesson.

required:
ISC-DHCP
rabbitmq
python3 and modules from requirements

ISC-DHCP create log for commit, release and expirity lease events.
rsyslog send log to file and rabiitmq.
dhcp-rad.py give dhcp events from rabbitmq (vlan, ip, status) ==>> give from billing clientid by vlan ==>> send data to radius via pyrad
