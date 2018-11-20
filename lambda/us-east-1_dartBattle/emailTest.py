# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.
msg = MIMEText("This is an example email.\nIt contains text.")

# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = 'Dart Battle Beta Test Signup Request'
msg['From'] = "beta.test@dartbattle.fun"
msg['To'] = "beta.test@dartbattle.fun"

# Send the message via our own SMTP server, but don't include the
# envelope header.
s = smtplib.SMTP('localhost')
s.sendmail(me, [you], msg.as_string())
s.quit()
print("Success.")