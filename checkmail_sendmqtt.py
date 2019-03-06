import smtplib
import time
import imaplib
import email
from pyquery import PyQuery    
import json
import sys
# -------------------------------------------------
#
# Utility to read email from Gmail Using Python
#
# ------------------------------------------------

FROM_EMAIL  = sys.argv[1] 
FROM_PWD    = sys.argv[2]
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT   = 465
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT   = 993
EMAIL_ALARM = sys.argv[3]
email_date_last = ''
new_inbox = False
alarmJson = ''
def read_email_from_gmail():
    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(FROM_EMAIL,FROM_PWD)
        mail.select('inbox')

        type, data = mail.search(None, 'ALL')
        mail_ids = data[0]

        id_list = mail_ids.split()   
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])
        typ, data = mail.fetch(latest_email_id, '(RFC822)' )
        # email_date_last = 'a'
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1])
                html = response_part[1]
                pq = PyQuery(html)
                tag = pq('div') # or     tag = pq('div.class')
                global new_inbox
                global email_date_last
                email_subject = str(msg['subject'])
                email_from = msg['from'].split('<')[1].split('>')[0]
                email_date = str(msg['Date'])
                global alarmJson
                if email_date_last != email_date:
                    email_date_last = email_date
                    if(email_from == EMAIL_ALARM):
                        # print tag.text()
                        m = tag.text().replace('.','')
                        p = m.split('\n')
                        alarmJson = "{"
                        for j in range (0,len(p)):
                            a = p[j].split(': ')
                            if len(a) == 1 :
                                a = p[j].split(':')
                                b = '"'+a[0]+ '":"",'
                            else:    
                                b = '"'+a[0]+'":"'+a[1]+'",'
                            if j == (len(p)-1):
                                b = b.split(',')[0]
                            alarmJson = alarmJson + b
                            # print(b)
                        alarmJson = alarmJson + '}'
                        alarmJson = eval(alarmJson)
                        # alarmJson = json.dumps(alarmJson)
                        # alarmJson = json.loads(alarmJson)
                        print alarmJson['Alarm Event']
                        new_inbox = True    
    except Exception, e:
        print str(e)


import paho.mqtt.client as mqtt #import the client1
import time
def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
broker_address="cretatech.com"
client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback
client.connect(broker_address,port=1883, keepalive=60, bind_address="") #connect to broker
############
client.loop_start() #start the loop
client.subscribe("house1")
objAlarm = {"id": "cretaalarm001","data":"hello","func":0}
while 1:        
    read_email_from_gmail()
    if new_inbox == True:
        new_inbox = False
        objAlarm["data"]= alarmJson
        client.publish("esp/cretaalarm001/status",json.dumps(objAlarm))
        print objAlarm["data"]
    