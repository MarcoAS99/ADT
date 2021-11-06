import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_validation_email(name, email):
    sender = 'adtis2iamem@gmail.com'
    receivers = [email]

    message = MIMEMultipart("alternative")
    message['From'] = f"ADT_IS2 <{sender}>"
    message['To'] = f"To: {name} <{email}>"
    message['Subject'] = "Validation Account Email"
    html = f"""<h1>Validate your account in the following link:</h1>
        <a href="http://localhost:8000/{email}/validate">Click to validate.</a>"""
    message.attach(MIMEText(html, "html"))
    try:
        print('Sending email...')
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        server.login(sender, 'password#3')
        server.sendmail(from_addr=sender, to_addrs=receivers,
                        msg=message.as_string())
        server.quit()
        print("Successfully sent email.")
    except smtplib.SMTPException:
        print("Error: unable to send email")
