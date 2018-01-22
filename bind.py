##############################################################################################
#  This script takes a comma-separated list of LDAP servers and pings them to verify         #
#  reachability.  If a server does not respond to ping it is removed from the list.          #
#  A server is then randomly chosen from those remaining in the list and, based on a         #
#  user provided list of usernames and passwords, attempts an LDAP bind to verify whether    #
#  or not the account information is active.  Successful and failed accounts are then logged #
#  to separate files based on user-provided input.                                           #
#  The script expects a colon-delimited user list in this format:                            #
#  username@domain.com:password                                                              #                                          
#                                                                                            #
##############################################################################################

import ldap
import os
import random
import subprocess
import sys

print"\n*********************************************************************"
print"***********************LDAP BIND ACCOUNT TEST************************"
print"*********************************************************************\n" 

account_list = raw_input("Enter the full path for the list of accounts/passwords to test: ")

print "\n"

successful_bind = raw_input("Enter the full path for the file to store successful bind attempts: ")

print "\n"

failed_bind = raw_input("Enter the full path for the file to store failed bind attempts: ")

print "\n"

servers = raw_input("Enter a comma-separated list of LDAP servers: ")
servers = servers.split(',')

print "\nVerifying server reachability with an ICMP ping..."

for server in servers:
    with open(os.devnull, 'w') as DEVNULL:
        try:
            subprocess.check_call(
                ['ping', '-c', '1', server],
                stdout=DEVNULL, #suppresses command output
                stderr=DEVNULL
            )
            is_up = True
        except subprocess.CalledProcessError:
            is_up = False
            print "\nHost " + server + " is not responding to ping and may be down..."
            print "Removing it from the list..."
            if server in servers:
                servers.remove(server)

print "\nList of servers is now: " + str(servers)

LDAPServer = random.choice(servers)
print "\nRandomly selected " + LDAPServer + " as the LDAP server to test account binding."

conn = ldap.initialize('ldap://' + LDAPServer)
conn.protocol_version = 3
conn.set_option(ldap.OPT_REFERRALS, 0)
live = open(successful_bind, 'w')
bad = open(failed_bind, 'w')

print "\nStarting LDAP Bind Test...  This may take some time...\n"

with open(account_list) as f:
    for line in f:
        try:        
            line = line.split(':')
            username = line[0].rstrip()
            password = line[1].rstrip()
            conn.simple_bind_s(username, password)
            live.write(username+'\n')
        except Exception:
            bad.write(username+'\n')
    
live.close()
bad.close()

print "LDAP Bind Test complete.  Output files should be in the locations specified above.  Exiting..."
sys.exit()
