from utility.views import current_date
from time import strftime

class EmailTemplates:
    def welcome_message(self, name, email, mobile_number, password):
        msg = f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">

                <h2 style="color: #6f42c1;">Welcome to Gold Rush Aura</h2>

                <p>Hello <strong>{name}</strong>,</p>

                <p>
                    Congratulations! 🎉 Your account has been successfully created with 
                    <strong>Gold Rush Aura</strong>.
                </p>

                <p>Please use the following credentials to log in to your account:</p>

                <div style="
                    background:#f8f9fa;
                    border:1px solid #e6e6e6;
                    padding:15px;
                    border-radius:6px;
                    margin:20px 0;
                    font-size:15px;
                ">
                    <p style="margin:5px 0;">
                        <strong>Username:</strong> {mobile_number}
                    </p>
                    <p style="margin:5px 0;">
                        <strong>Password:</strong> {password}
                    </p>
                </div>

                <p style="
                    background-color:#fff3cd;
                    color:#856404;
                    padding:10px;
                    border-radius:5px;
                    font-size:14px;
                ">
                    <strong>Security Tip:</strong> For better security, we recommend changing your password after your first login.
                </p>

                <p>
                    You can now access your account and start exploring the services offered by 
                    <strong>Gold Rush Aura</strong>.
                </p>

                <hr style="border:none; border-top:1px solid #eee; margin:20px 0;">

                <p>
                    Regards,<br>
                    <strong>The Gold Rush Aura Team</strong>
                </p>

            </div>
        </body>
        </html>
        '''

        subject = "Welcome to Gold Rush Aura – Your Account is Ready"
        to = email

        data = {
            'to_email': to,
            'subject': subject,
            'msg': msg
        }

        return data
    
    def password_reset_template(self, name, email, username, unique_id, page_name, domain):
        reset_link = f"{domain}{page_name}?id={unique_id}"
        
        msg = f'''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
                    <h2 style="color: #6f42c1;">Password Reset Request</h2>
                    <p>Hello <strong>{name}</strong> from Gold Rush Aura,</p>

                    <p>You're receiving this email because you requested a password reset for your user account at <strong>Gold Rush Aura</strong>.</p>
                    
                    <p>Please click the button below to choose a new password:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" 
                        style="background-color: #d9534f; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            Reset My Password
                        </a>
                    </div>

                    <p style="background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; font-size: 14px;">
                        <strong>Security Note:</strong> This link is valid for <strong>2 hours</strong>. 
                        However, for maximum security, we recommend using it within <strong>2 hours</strong>.
                    </p>

                    <p>For your reference, your username is: <strong>{username}</strong></p>
                    
                    <p>If you didn't request this, you can safely ignore this email. Your password won't change until you access the link above and create a new one.</p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p>Thanks,<br/>
                    <strong>The Gold Rush Aura Team</strong></p>
                </div>
            </body>
            </html>
        '''
        
        subject = "Request for Password Reset - Gold Rush Aura"
        to = email

        data = {
            'to_email': to, 
            'subject': subject, 
            'msg': msg
        }

        return data
    
    def otp_template(self, name, email, otp):
        msg = f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">

                <h2 style="color: #6f42c1;">PIN Reset Verification</h2>

                <p>Hello <strong>{name}</strong>,</p>

                <p>
                    We received a request to reset your <strong>Digital Investment PIN</strong> for your 
                    <strong>Gold Rush Aura</strong> account.
                </p>

                <p>Please use the One-Time Password (OTP) below to continue the reset process:</p>

                <div style="text-align:center; margin:30px 0;">
                    <span style="
                        font-size:32px;
                        letter-spacing:8px;
                        font-weight:bold;
                        background:#f8f9fa;
                        padding:12px 25px;
                        border-radius:6px;
                        display:inline-block;
                        color:#000;">
                        {otp}
                    </span>
                </div>

                <p style="
                    background-color:#fff3cd;
                    color:#856404;
                    padding:10px;
                    border-radius:5px;
                    font-size:14px;">
                    <strong>Security Note:</strong>  
                    This OTP is valid for <strong>5 minutes</strong>.  
                    Do not share this OTP with anyone.
                </p>

                <p>
                    If you did not request a PIN reset, please ignore this email or contact our support team immediately.
                </p>

                <hr style="border:none; border-top:1px solid #eee; margin:20px 0;">

                <p>
                    Regards,<br>
                    <strong>Gold Rush Aura Security Team</strong>
                </p>

            </div>
        </body>
        </html>
        '''

        subject = "PIN Reset OTP - Gold Rush Aura"
        to = email

        data = {
            'to_email': to,
            'subject': subject,
            'msg': msg
        }

        return data