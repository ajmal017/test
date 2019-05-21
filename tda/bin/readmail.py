import smtplib
import time
import imaplib
import email

ORG_EMAIL = "@gmail.com"
FROM_EMAIL = "alerttda" + ORG_EMAIL
FROM_PWD = "welcome3016"
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT = 993

def readmail():
    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(FROM_EMAIL, FROM_PWD)
        mail.select('inbox')

        type, data = mail.search(None, 'ALL')
        mail_ids = data[0]

        id_list = mail_ids.split()
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])

        for i in range(latest_email_id,first_email_id, -1):
            print(i)
            data = mail.fetch(str(i).encode(), '(RFC822)' )


            for resp in data:
                if isinstance(resp, list):
                    #print(str(resp[0]))
                    b = email.message_from_string(str(resp[0]))
                    if b.is_multipart():
                        for payload in b.get_payload():
                            print(payload.get_payload())
                    else:
                        print("hello")
                        print(b.get_payload()['subject'])

            """
            for response_part in data:
                print(type(response_part))
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(str(response_part[0]))
                    print(msg._headers[0][1])
                    email_subject = msg['subject']
                    email_from = msg['from']
                    print('From : ' + email_from + '\n')
                    print('Subject : ' + email_subject + '\n')
            """
    except Exception as e:
        print("Did Nothing", str(e))

if(__name__ == "__main__"):
   readmail()