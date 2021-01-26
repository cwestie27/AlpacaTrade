import smtplib

username = 'firstwestventures@gmail.com'
password = 'Knights11'

vtext = "6158815197@vtext.com"
#vtext = "8452708681@txt.att.net"
message = "test 12"

msg = """From: %s
To: %s
Subject:
%s""" % (username, vtext, message)

server = smtplib.SMTP('smtp.gmail.com',587)
server.starttls()
server.login(username,password)
server.sendmail(username, vtext, msg)
server.quit()
