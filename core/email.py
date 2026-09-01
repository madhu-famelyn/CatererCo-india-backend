import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def _send_mail(to_email: str, subject: str, html_body: str) -> bool:
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "team@catererco.com")

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print(f"⚠️ SMTP credentials not fully configured. Email '{subject}' for {to_email} was not sent via network.")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, to_email, msg.as_string())
        server.quit()
        print(f"✅ Email '{subject}' sent successfully from {EMAIL_FROM} to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False


def send_password_reset_otp_email(to_email: str, otp: str, user_name: str = "") -> bool:
    subject = f"{otp} is your CatererCo Password Reset Code"
    body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 30px; color: #1a1a1a; max-width: 500px; margin: auto; border: 1px solid #eaeaea; border-radius: 12px; background-color: #ffffff;">
        <div style="text-align: center; margin-bottom: 25px;">
            <h1 style="color: #f97316; font-size: 28px; font-weight: 700; margin: 0; letter-spacing: -0.5px;">CatererCo</h1>
            <p style="color: #666666; font-size: 14px; margin-top: 5px;">Premium Catering Marketplace</p>
        </div>
        
        <h2 style="font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #111111;">Password Reset Request</h2>
        <p style="font-size: 14px; line-height: 1.5; color: #4b5563;">Hello {user_name or 'User'}, we received a request to reset your password. Use the following code to reset your password:</p>
        
        <div style="background-color: #fff7ed; border: 1px solid #ffedd5; border-radius: 8px; padding: 16px; text-align: center; margin: 25px 0;">
            <span style="font-family: monospace; font-size: 32px; font-weight: 700; letter-spacing: 6px; color: #ea580c;">{otp}</span>
        </div>
        
        <p style="font-size: 13px; line-height: 1.5; color: #9ca3af; margin-bottom: 25px;">This code is valid for 10 minutes. If you did not request a password reset, you can safely ignore this email.</p>
        
        <hr style="border: 0; border-top: 1px solid #f3f4f6; margin-bottom: 20px;">
        
        <p style="font-size: 12px; color: #9ca3af; text-align: center; margin: 0;">&copy; 2026 CatererCo. All rights reserved.</p>
    </body>
    </html>
    """
    return _send_mail(to_email, subject, body)


def send_otp_email(to_email: str, otp: str) -> bool:
    subject = f"{otp} is your CatererCo verification code"
    body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 30px; color: #1a1a1a; max-width: 500px; margin: auto; border: 1px solid #eaeaea; border-radius: 12px; background-color: #ffffff;">
        <div style="text-align: center; margin-bottom: 25px;">
            <h1 style="color: #f97316; font-size: 28px; font-weight: 700; margin: 0; letter-spacing: -0.5px;">CatererCo</h1>
            <p style="color: #666666; font-size: 14px; margin-top: 5px;">Premium Catering Marketplace</p>
        </div>
        
        <h2 style="font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #111111;">Verify your account</h2>
        <p style="font-size: 14px; line-height: 1.5; color: #4b5563;">Thank you for signing up with CatererCo. Please use the following one-time verification code (OTP) to complete your action:</p>
        
        <div style="background-color: #f9fafb; border: 1px solid #f3f4f6; border-radius: 8px; padding: 16px; text-align: center; margin: 25px 0;">
            <span style="font-family: monospace; font-size: 32px; font-weight: 700; letter-spacing: 6px; color: #f97316;">{otp}</span>
        </div>
        
        <p style="font-size: 13px; line-height: 1.5; color: #9ca3af; margin-bottom: 25px;">This code is valid for 10 minutes. If you did not request this verification, you can safely ignore this email.</p>
        
        <hr style="border: 0; border-top: 1px solid #f3f4f6; margin-bottom: 20px;">
        
        <p style="font-size: 12px; color: #9ca3af; text-align: center; margin: 0;">&copy; 2026 CatererCo. All rights reserved.</p>
    </body>
    </html>
    """
    return _send_mail(to_email, subject, body)


def send_password_change_email(to_email: str, user_name: str) -> bool:
    subject = "Password Changed Successfully - CatererCo"
    body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 30px; color: #1a1a1a; max-width: 500px; margin: auto; border: 1px solid #eaeaea; border-radius: 12px; background-color: #ffffff;">
        <div style="text-align: center; margin-bottom: 25px;">
            <h1 style="color: #f97316; font-size: 28px; font-weight: 700; margin: 0; letter-spacing: -0.5px;">CatererCo</h1>
            <p style="color: #666666; font-size: 14px; margin-top: 5px;">Premium Catering Marketplace</p>
        </div>
        
        <h2 style="font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #111111;">Hello {user_name},</h2>
        <p style="font-size: 14px; line-height: 1.5; color: #4b5563;">Your CatererCo account password was successfully changed. If you performed this action, no further steps are required.</p>
        
        <div style="background-color: #fef2f2; border: 1px solid #fee2e2; border-radius: 8px; padding: 14px; margin: 20px 0;">
            <p style="font-size: 13px; color: #991b1b; margin: 0;">If you did NOT initiate this password change, please contact our support team immediately at <strong>team@catererco.com</strong> to secure your account.</p>
        </div>
        
        <hr style="border: 0; border-top: 1px solid #f3f4f6; margin-bottom: 20px;">
        
        <p style="font-size: 12px; color: #9ca3af; text-align: center; margin: 0;">&copy; 2026 CatererCo. All rights reserved.</p>
    </body>
    </html>
    """
    return _send_mail(to_email, subject, body)


def send_caterer_approval_email(to_email: str, caterer_name: str) -> bool:
    subject = "🎉 Your CatererCo Partner Application is Approved!"
    body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 30px; color: #1a1a1a; max-width: 500px; margin: auto; border: 1px solid #eaeaea; border-radius: 12px; background-color: #ffffff;">
        <div style="text-align: center; margin-bottom: 25px;">
            <h1 style="color: #f97316; font-size: 28px; font-weight: 700; margin: 0; letter-spacing: -0.5px;">CatererCo</h1>
            <p style="color: #666666; font-size: 14px; margin-top: 5px;">Premium Catering Marketplace</p>
        </div>

        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 20px; text-align: center; margin-bottom: 25px;">
            <div style="font-size: 40px; margin-bottom: 8px;">🎉</div>
            <h2 style="font-size: 20px; font-weight: 700; color: #15803d; margin: 0;">Application Approved!</h2>
        </div>

        <p style="font-size: 14px; line-height: 1.6; color: #4b5563;">
            Congratulations, <strong>{caterer_name}</strong>! Your application to join CatererCo as a verified partner has been reviewed and <strong style="color: #15803d;">approved</strong> by our admin team.
        </p>

        <p style="font-size: 14px; line-height: 1.6; color: #4b5563;">
            Your business is now <strong>live on the marketplace</strong> and visible to thousands of event planners across the UAE. You can start receiving booking requests immediately.
        </p>

        <div style="text-align: center; margin: 28px 0;">
            <a href="http://localhost:5173/caterer/login"
               style="display: inline-block; background: linear-gradient(135deg, #f97316, #ea580c); color: white; text-decoration: none; padding: 14px 32px; border-radius: 10px; font-size: 15px; font-weight: 600; letter-spacing: 0.3px;">
                Sign In to Your Partner Portal →
            </a>
        </div>

        <div style="background-color: #fff7ed; border: 1px solid #fed7aa; border-radius: 8px; padding: 14px; margin-bottom: 20px;">
            <p style="font-size: 13px; color: #92400e; margin: 0;"><strong>Next steps:</strong> Log in, complete your business profile, add your menu items, and upload your gallery to attract more clients.</p>
        </div>

        <hr style="border: 0; border-top: 1px solid #f3f4f6; margin-bottom: 20px;">
        <p style="font-size: 12px; color: #9ca3af; text-align: center; margin: 0;">Questions? Reach us at <a href="mailto:support@catererco.ae" style="color: #f97316;">support@catererco.ae</a> · &copy; 2026 CatererCo</p>
    </body>
    </html>
    """
    return _send_mail(to_email, subject, body)


def send_caterer_rejection_email(to_email: str, caterer_name: str) -> bool:
    subject = "Update on Your CatererCo Partner Application"
    body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 30px; color: #1a1a1a; max-width: 500px; margin: auto; border: 1px solid #eaeaea; border-radius: 12px; background-color: #ffffff;">
        <div style="text-align: center; margin-bottom: 25px;">
            <h1 style="color: #f97316; font-size: 28px; font-weight: 700; margin: 0; letter-spacing: -0.5px;">CatererCo</h1>
            <p style="color: #666666; font-size: 14px; margin-top: 5px;">Premium Catering Marketplace</p>
        </div>

        <h2 style="font-size: 18px; font-weight: 600; margin-bottom: 12px; color: #111111;">Dear {caterer_name},</h2>

        <p style="font-size: 14px; line-height: 1.6; color: #4b5563;">
            Thank you for your interest in joining CatererCo as a verified partner. After reviewing your application, our compliance team was unable to approve it at this time.
        </p>

        <p style="font-size: 14px; line-height: 1.6; color: #4b5563;">
            This may be due to incomplete documentation or information that could not be verified. You are welcome to reapply with updated credentials.
        </p>

        <div style="text-align: center; margin: 24px 0;">
            <a href="http://localhost:5173/caterer/register"
               style="display: inline-block; background-color: #f3f4f6; color: #374151; text-decoration: none; padding: 12px 28px; border-radius: 10px; font-size: 14px; font-weight: 600; border: 1px solid #e5e7eb;">
                Re-apply as a Caterer
            </a>
        </div>

        <p style="font-size: 13px; line-height: 1.5; color: #6b7280;">
            If you believe this was a mistake or need clarification, please contact our support team at <a href="mailto:support@catererco.ae" style="color: #f97316;">support@catererco.ae</a>.
        </p>

        <hr style="border: 0; border-top: 1px solid #f3f4f6; margin-bottom: 20px;">
        <p style="font-size: 12px; color: #9ca3af; text-align: center; margin: 0;">&copy; 2026 CatererCo. All rights reserved.</p>
    </body>
    </html>
    """
    return _send_mail(to_email, subject, body)


def send_booking_email(to_email: str, recipient_name: str, booking_data: dict, is_vendor: bool = False) -> bool:
    booking_id = booking_data.get("id", "N/A")
    event = booking_data.get("event", "Event")
    event_date = booking_data.get("date", "N/A")
    guests = booking_data.get("guests", 0)
    total = booking_data.get("total", 0)
    caterer_name = booking_data.get("caterer_name", "Caterer")
    address = booking_data.get("address", "N/A")

    if is_vendor:
        subject = f"New Catering Booking Received! [{booking_id}] - CatererCo"
        heading = f"New Booking Received, {recipient_name}!"
        message_intro = f"You have received a new booking on CatererCo for <strong>{caterer_name}</strong>."
    else:
        subject = f"Booking Confirmation [{booking_id}] - CatererCo"
        heading = f"Booking Confirmed, {recipient_name}!"
        message_intro = f"Your booking with <strong>{caterer_name}</strong> has been successfully registered."

    body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 30px; color: #1a1a1a; max-width: 550px; margin: auto; border: 1px solid #eaeaea; border-radius: 12px; background-color: #ffffff;">
        <div style="text-align: center; margin-bottom: 25px;">
            <h1 style="color: #f97316; font-size: 28px; font-weight: 700; margin: 0; letter-spacing: -0.5px;">CatererCo</h1>
            <p style="color: #666666; font-size: 14px; margin-top: 5px;">Premium Catering Marketplace</p>
        </div>
        
        <h2 style="font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #111111;">{heading}</h2>
        <p style="font-size: 14px; line-height: 1.5; color: #4b5563;">{message_intro}</p>
        
        <div style="background-color: #f9fafb; border: 1px solid #f3f4f6; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="font-size: 15px; font-weight: 600; margin-top: 0; margin-bottom: 12px; color: #111111;">Booking Details</h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px; color: #374151;">
                <tr>
                    <td style="padding: 6px 0; color: #6b7280; width: 40%;">Booking ID:</td>
                    <td style="padding: 6px 0; font-weight: 600;">{booking_id}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; color: #6b7280;">Event Type:</td>
                    <td style="padding: 6px 0; font-weight: 600;">{event}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; color: #6b7280;">Date:</td>
                    <td style="padding: 6px 0; font-weight: 600;">{event_date}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; color: #6b7280;">Guest Count:</td>
                    <td style="padding: 6px 0; font-weight: 600;">{guests} guests</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; color: #6b7280;">Location:</td>
                    <td style="padding: 6px 0; font-weight: 600;">{address}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; color: #6b7280;">Total Amount:</td>
                    <td style="padding: 6px 0; font-weight: 700; color: #f97316;">AED {total}</td>
                </tr>
            </table>
        </div>
        
        <p style="font-size: 13px; line-height: 1.5; color: #6b7280;">If you have any questions, please contact us at <strong>team@catererco.com</strong>.</p>
        
        <hr style="border: 0; border-top: 1px solid #f3f4f6; margin-top: 25px; margin-bottom: 20px;">
        
        <p style="font-size: 12px; color: #9ca3af; text-align: center; margin: 0;">&copy; 2026 CatererCo. All rights reserved.</p>
    </body>
    </html>
    """
    return _send_mail(to_email, subject, body)


def send_custom_notification_email(to_email: str, title: str, message: str) -> bool:
    subject = f"📢 {title} - CatererCo Announcement"
    body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 30px; color: #1a1a1a; max-width: 550px; margin: auto; border: 1px solid #eaeaea; border-radius: 12px; background-color: #ffffff;">
        <div style="text-align: center; margin-bottom: 25px;">
            <h1 style="color: #f97316; font-size: 28px; font-weight: 700; margin: 0; letter-spacing: -0.5px;">CatererCo</h1>
            <p style="color: #666666; font-size: 14px; margin-top: 5px;">Premium Catering Marketplace</p>
        </div>
        
        <h2 style="font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #111111;">{title}</h2>
        <div style="font-size: 14px; line-height: 1.6; color: #374151; white-space: pre-line; background-color: #f9fafb; border: 1px solid #f3f4f6; border-radius: 8px; padding: 18px; margin: 20px 0;">
            {message}
        </div>
        
        <p style="font-size: 13px; line-height: 1.5; color: #6b7280;">This message was broadcast by the CatererCo Admin Team.</p>
        
        <hr style="border: 0; border-top: 1px solid #f3f4f6; margin-top: 25px; margin-bottom: 20px;">
        
        <p style="font-size: 12px; color: #9ca3af; text-align: center; margin: 0;">&copy; 2026 CatererCo. All rights reserved.</p>
    </body>
    </html>
    """
    return _send_mail(to_email, subject, body)


def send_admin_invite_email(to_email: str, name: str, role: str, permissions: list) -> bool:
    subject = "🔑 Admin Portal Access Granted - CatererCo UAE"
    permissions_html = "".join([f"<li style='margin-bottom: 6px;'>✅ {p}</li>" for p in permissions]) if permissions else "<li>Full Administrator Privileges</li>"
    
    body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 30px; color: #1a1a1a; max-width: 550px; margin: auto; border: 1px solid #eaeaea; border-radius: 12px; background-color: #ffffff;">
        <div style="text-align: center; margin-bottom: 25px;">
            <h1 style="color: #6366f1; font-size: 28px; font-weight: 700; margin: 0; letter-spacing: -0.5px;">CatererCo Admin Hub</h1>
            <p style="color: #666666; font-size: 14px; margin-top: 5px;">Marketplace Management Console</p>
        </div>
        
        <h2 style="font-size: 18px; font-weight: 600; margin-bottom: 12px; color: #111111;">Hello {name},</h2>
        <p style="font-size: 14px; line-height: 1.6; color: #4b5563;">
            You have been granted administrative access to the <strong>CatererCo Admin Hub</strong> as a <strong style="color: #6366f1;">{role}</strong>.
        </p>
        
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; margin: 20px 0;">
            <h3 style="font-size: 15px; font-weight: 600; margin-top: 0; margin-bottom: 12px; color: #1e293b;">Your Assigned Access Points:</h3>
            <ul style="padding-left: 20px; font-size: 14px; color: #334155; margin: 0;">
                {permissions_html}
            </ul>
        </div>
        
        <div style="text-align: center; margin: 28px 0;">
            <a href="http://localhost:5174/admin"
               style="display: inline-block; background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; text-decoration: none; padding: 14px 32px; border-radius: 10px; font-size: 15px; font-weight: 600; letter-spacing: 0.3px;">
                Access Admin Portal →
            </a>
        </div>
        
        <hr style="border: 0; border-top: 1px solid #f3f4f6; margin-top: 25px; margin-bottom: 20px;">
        <p style="font-size: 12px; color: #9ca3af; text-align: center; margin: 0;">&copy; 2026 CatererCo Admin Operations. All rights reserved.</p>
    </body>
    </html>
    """
    return _send_mail(to_email, subject, body)



