# -*- coding: utf-8 -*-
import httplib2
import json
from config_default import configs

#httplib2.debuglevel = 1
h = httplib2.Http('.cache')

def get_dl_ticket(file, login, key):
    url = 'https://api.openload.co/1/file/dlticket?file=%s&login=%s&key=%s' % (file, login, key)

    response, content = h.request(url, 'GET')
    contect = json.loads(content)

    ticket = ''
    if (contect.get('status') == 200):
        ticket = contect.get('result').get('ticket')
    
    return ticket

def get_dl_link(file):
    ticket = get_dl_ticket(file, configs.get('login'), configs.get('key'))
    url = 'https://api.openload.co/1/file/dl?file=%s&ticket=%s' % (file, ticket)

    response, content = h.request(url, 'GET')
    contect = json.loads(content)

    link = ''
    if (contect.get('status') == 200):
        link = contect.get('result').get('url')

    return link

