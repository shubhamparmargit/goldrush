from utility.views import current_date
from time import strftime

class FCMTemplates:
    def welcome_message(self, name, email, mobile_number, password):
        msg = '''
            <html>
            <body>
            Hello '''+name+''' from GoldMine<br><br>

            Congractulations! You have successfully signed up for GoldMine!<br/><br/>
            
            For reference, here\'s your login information:<br/>
            <strong>Username:</strong> '''+mobile_number+'''<br/>
            <strong>Password:</strong> '''+password+'''<br/><br/>
            
            Thanks,<br/>
            GoldMine
            
            </body>
            </html>
        '''
        subject = "Getting started with Rups Marketing"
        to = email

        data = {'to_email':to, 'subject':subject, 'msg':msg}

        return data