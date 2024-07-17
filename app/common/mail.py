from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_otp_email(to_email, code):
    html_content = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #333;">OTP Verification</h2>
                <p style="color: #555;">Dear user,</p>
                <p style="color: #555;">Your OTP code is:</p>
                <p style="font-size: 24px; color: #333; font-weight: bold;"> {code}</p>
                <p style="color: #555;">Please use this code to reset your password. The code is valid for 10 minutes.</p>
                <p style="color: #555;">If you did not request this code, please ignore this email.</p>
                <p style="color: #555;">Thank you,</p>
                <p style="color: #555;">Team Elevate</p>
            </div>
        </div>
    </body>
    </html>
    """

    message = Mail(
        from_email=settings.SENDGRID_SENDER_EMAIL,
        to_emails=to_email,
        subject="OTP Verification",
        html_content=html_content,
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        _ = sg.send(message)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_enquiry_email(description, first_name, company_name, business_email):
    html_content = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #333;">Business Enquiry</h2>
                <p style="color: #555;">Dear Team,</p>
                <p style="color: #555;">You have received a new business enquiry. Here are the details:</p>
                <p><strong>First Name:</strong> {first_name}</p>
                <p><strong>Company Name:</strong> {company_name}</p>
                <p><strong>Business Email:</strong> {business_email}</p>
                <p><strong>Description:</strong></p>
                <p>{description}</p>
                <p style="color: #555;">Please follow up with the enquirer at your earliest convenience.</p>
                <p style="color: #555;">Thank you,</p>
                <p style="color: #555;">Team Elevate</p>
            </div>
        </div>
    </body>
    </html>
    """

    message = Mail(
        from_email=settings.SENDGRID_SENDER_EMAIL,
        to_emails=settings.SENDGRID_COMPANY_INFO_EMAIL,
        subject="New Business Enquiry",
        html_content=html_content,
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        _ = sg.send(message)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_subscription_email(name, email):
    html_content = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #333;">Thank You for Subscribing!</h2>
                <p style="color: #555;">Dear {name},</p>
                <p style="color: #555;">Thank you for signing up for our subscription service. We are excited to have you on board!</p>
                <p style="color: #555;">You will receive regular updates and exclusive offers straight to your inbox.</p>
                <p style="color: #555;">If you have any questions or feedback, feel free to reply to this email. We'd love to hear from you!</p>
                <p style="color: #555;">Thank you again,</p>
                <p style="color: #555;">Team Elevate</p>
            </div>
        </div>
    </body>
    </html>
    """

    message = Mail(
        from_email=settings.SENDGRID_SENDER_EMAIL,
        to_emails=email,
        subject="Thank You for Subscribing!",
        html_content=html_content,
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        _ = sg.send(message)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
