#!/usr/bin/python3.7
from pathlib import Path #getting user home path

import requests, json
import logging
from ip import getip
from sys import version_info
import socket
import keyring #retrieve godaddy secret key

#---------------------------inputs ------------------------------------------------------
domainname = 'sipatron.live'
ttl = 1800 #half hour
urlTimeout = 2 #seconds
filelog = str(Path.home()) + '/godaddy.log' 
ip = None

#--------------------------- logging ------------------------------------------------------
logging.basicConfig(
    filename=filelog,
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO)


#---------------------------Check version  ------------------------------------------------
if version_info.major < 3:
    logging.error('Error, python needs to be V3 (or higher)!')
    exit(1)


#--------------------------- config ------------------------------------------------------
#Domain name server configuration
dnsname = '@'
dnstype = 'A'
#construct url to send to godaddy
url = 'https://api.godaddy.com/v1/domains/{}/records/{}/{}'.format(domainname, dnstype, dnsname)
#packet headers - use json and retrieve godaddy secret key and password
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": "sso-key {}:{}".format(
        keyring.get_password('godaddy', 'key'),
        keyring.get_password('godaddy', 'secret'))
}


#--------------------------- HTTP codes ------------------------------------------------
http_errors = {
    400: 'GoDaddy API URL was malformed.',
    401: 'key or secret option incorrect',
    403: 'customer identified by --key and --secret options denied permission.',
    404: 'Resource not found at GoDaddy.',
    422: 'Invalid domain or lacks A record.',
    429: 'too many requests to GoDaddy within brief period.',
    500: 'Internal server error.',
    504: 'Gateway timeout'
}
http_ok = 200

#--------------------------- Main execution ------------------------------------------------
#easy error quit function
def logandquit(msg):
    logging.error('Could not set ip {} to domain "{}" - {}\n'.format(ip, domainname, msg))
    exit(1)

#get ip address
ip = getip()
if not ip:
    logandquit('Could not retrieve IP address from any sites attempted')

# create json data
data = json.dumps([{
        "data": ip, 
        "ttl": ttl, 
        "name": dnsname, 
        "type": "A" }])
data = data.encode('utf-8')

try:
    # get dns ip address
    server_ip = socket.gethostbyname(domainname)

    # check if need to update
    if server_ip == ip:
        logging.info('IP {} matches dns "{}" - no need for update'.format(ip, domainname))
        exit(0)

    # post data to godaddy
    response = requests.put(url, data=data, headers=headers, timeout=urlTimeout)

    # check code receieved
    code = response.status_code
    
    if code in http_errors:
        logandquit('error code {} received - {}'.format(code, http_errors[code]))
    elif code != http_ok:
        logandquit('error code {} not recognised'.format(code))

# error posting data
except (ConnectionError, requests.RequestException) as e:
    logandquit(e)

# error retrieving server ip address
except socket.gaierror as e:
    logandquit('Could not resolve dns "{}"'.format(dnsname))

    
logging.info('IP address for "{}" set to {}.'.format(domainname, ip))
