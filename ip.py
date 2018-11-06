import re #regular expression
import requests 
import logging

urls = ['https://api.ipify.org/', 'https://ip.seeip.org/', 'https://canihazip.com/s']


#check string is valid ip
def isip(s):
    #match 1-3 digits and a dot (\d{1,3}.) 3 times {3} followed by another 1-3 digits \d{1,3}
	m = re.match(r'(\d{1,3}.){3}\d{1,3}', s) 
	if m:
		return m.group() == s #check for invalid characters at end
	return False

#get public ip address trying different sites storing it in plain text
def getip(urlTimeout = 2):
    for url in urls:
        try:
            page = requests.get(url, timeout=urlTimeout)
            ipstr = page.content.decode()
            if isip(ipstr):
                return ipstr
            else:
                logging.warning('{} did not retrieve a valid ip, trying next site..\n{}'.format(url, e))
        except (requests.RequestException, ConnectionError) as e:
            logging.warning('{} failed, trying next site...\n{}'.format(url, e))
    return None
