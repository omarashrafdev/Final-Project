import smtplib

SUBJECT = "Hello!"
TEXT = "Test"
message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.ehlo()
server.login("caitcancarry@gmail.com", "gcehgnwymspvubkx")
server.sendmail("caitcancarry@gmail.com", "caitcancarry@gmail.com", message)
server.close()