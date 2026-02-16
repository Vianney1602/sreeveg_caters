"""
Brevo (formerly Sendinblue) Email Service
Handles all transactional emails: OTP, order confirmation, order cancellation
"""
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Hotel logo URL (served from the live website)
LOGO_URL = "https://hotelshanmugabhavaan.com/images/ShanmugaBhavaan.png"

# Shared CSS matching the website's font and color scheme
EMAIL_BASE_STYLE = """
    body { margin: 0; padding: 0; background-color: #fff9ed; font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; }
    .wrapper { background: linear-gradient(135deg, #fff9ed 0%, #ffedc7 50%, #fff5db 100%); padding: 30px 10px; }
    .container { max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(122, 0, 0, 0.1); }
    .header { background: linear-gradient(135deg, #7a0000 0%, #d4af37 100%); color: white; padding: 30px 20px; text-align: center; }
    .header img { margin: 0 auto 12px auto; }
    .header h1 { margin: 0; font-size: 22px; font-weight: 700; letter-spacing: 0.5px; }
    .header p { margin: 6px 0 0 0; font-size: 15px; opacity: 0.9; }
    .content { padding: 30px; font-size: 15px; color: #333; }
    .content p { margin: 0 0 14px 0; }
    .content strong { color: #7a0000; }
    .otp-box { background: #fff9ed; border: 2px solid #d4af37; border-radius: 10px; padding: 22px; text-align: center; margin: 24px 0; }
    .otp { font-size: 36px; font-weight: 800; color: #7a0000; letter-spacing: 10px; font-family: 'Segoe UI', Roboto, monospace; }
    .otp-label { margin: 0 0 6px 0; font-size: 13px; color: #666; }
    .otp-expiry { margin: 8px 0 0 0; font-size: 12px; color: #999; }
    .order-box { background: #fff9ed; border: 2px solid #d4af37; border-radius: 10px; padding: 20px; margin: 20px 0; }
    .detail-row { padding: 9px 0; border-bottom: 1px solid #ffedc7; font-size: 14px; }
    .detail-label { font-weight: 700; color: #7a0000; display: inline-block; min-width: 160px; }
    .items-table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; }
    .items-table th { background: #7a0000; color: #ffffff; padding: 12px 10px; text-align: left; font-weight: 600; }
    .items-table td { padding: 10px; border-bottom: 1px solid #ffedc7; }
    .total-box { background: linear-gradient(135deg, #fff9ed, #ffedc7); font-size: 18px; font-weight: 800; color: #7a0000; padding: 16px; text-align: right; border-radius: 10px; margin-top: 10px; border: 1px solid #d4af37; }
    .thank-you { background: linear-gradient(135deg, #fff9ed, #ffedc7); border-left: 4px solid #d4af37; padding: 20px; margin: 20px 0; border-radius: 0 10px 10px 0; }
    .thank-you h2 { color: #7a0000; margin: 0 0 8px 0; font-size: 18px; }
    .thank-you p { margin: 0; font-size: 15px; color: #555; }
    .cancel-box { background: #fff5f5; border: 2px solid #cc0000; border-radius: 10px; padding: 20px; margin: 20px 0; }
    .cancel-box h3 { color: #cc0000; margin: 0 0 12px 0; }
    .refund-notice { background: #e8f5e9; border-left: 4px solid #4caf50; padding: 16px; margin: 20px 0; border-radius: 0 10px 10px 0; font-size: 14px; }
    .contact-box { background: #fff9ed; padding: 16px; border-radius: 10px; margin: 20px 0; text-align: center; border: 1px solid #ffd966; font-size: 14px; }
    .warning { background: #fff3cd; border: 1px solid #ffc107; padding: 12px; border-radius: 8px; margin-top: 16px; font-size: 14px; }
    .footer { background: #fff9ed; padding: 20px; text-align: center; font-size: 12px; color: #888; border-top: 2px solid #ffd966; }
    .footer p { margin: 4px 0; }
    .footer strong { color: #7a0000; }
    .gold-divider { height: 3px; background: linear-gradient(90deg, #d4af37, #ffd966, #d4af37); margin: 0; border: none; }
"""


def _get_api_instance():
    """Get configured Brevo API instance"""
    api_key = os.environ.get("BREVO_API_KEY")
    if not api_key:
        return None
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key
    return sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))


def _get_sender():
    """Get sender info from environment"""
    return {
        "name": os.environ.get("BREVO_SENDER_NAME", "Hotel Shanmuga Bhavaan"),
        "email": os.environ.get("BREVO_SENDER_EMAIL", "hotelshanmugabhavaan@gmail.com"),
    }


def _wrap_html(body_content):
    """Wrap email body in the shared base template with logo, styles, and footer"""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{EMAIL_BASE_STYLE}</style>
</head>
<body>
    <div class="wrapper">
        <div class="container">
            {body_content}
        </div>
    </div>
</body>
</html>
"""


def _header_section(subtitle):
    """Build standard header with logo and subtitle"""
    return f"""
    <div class="header">
        <img src="{LOGO_URL}" alt="Hotel Shanmuga Bhavaan" width="70" height="70" style="border-radius: 12px; display: block; margin: 0 auto 12px auto;" />
        <h1>Hotel Shanmuga Bhavaan</h1>
        <p>{subtitle}</p>
    </div>
    <hr class="gold-divider" />
"""


def _footer_section():
    """Build standard footer"""
    return """
    <hr class="gold-divider" />
    <div class="footer">
        <p><strong>Hotel Shanmuga Bhavaan Management Team</strong></p>
        <p>📞 79044 79451 &nbsp;|&nbsp; 📧 shanmugapriyaraja31@gmail.com</p>
        <p>&copy; 2026 Hotel Shanmuga Bhavaan. All rights reserved.</p>
        <p style="margin-top: 6px; font-size: 11px; color: #aaa;">This is an automated email. Please do not reply.</p>
    </div>
"""


def send_email(to_email, subject, html_content, text_content=None):
    """
    Send a transactional email via Brevo API.
    Returns True on success, False on failure.
    """
    api_instance = _get_api_instance()
    if not api_instance:
        print(f"⚠️  Brevo API key not configured. Email to {to_email} skipped.")
        return False

    sender = _get_sender()
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"name": sender["name"], "email": sender["email"]},
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Email sent to {to_email}: {subject}")
        return True
    except ApiException as e:
        print(f"❌ Brevo API error sending to {to_email}: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False


# ── Pre-built email templates ────────────────────────────────────────────

def send_otp_email(to_email, otp):
    """Send OTP for user password reset"""
    subject = "Your OTP for Password Reset - Hotel Shanmuga Bhavaan"
    text = (
        f"Hello,\n\n"
        f"You have requested to reset your password for your Hotel Shanmuga Bhavaan account.\n\n"
        f"Your One-Time Password (OTP) is: {otp}\n\n"
        f"This OTP is valid for 10 minutes. Please do not share this code with anyone.\n\n"
        f"If you did not request this password reset, please ignore this email.\n\n"
        f"Best regards,\nHotel Shanmuga Bhavaan Team"
    )
    body = f"""
    {_header_section("Password Reset Request")}
    <div class="content">
        <p>Hello,</p>
        <p>You have requested to reset your password for your <strong>Hotel Shanmuga Bhavaan</strong> account.</p>
        <div class="otp-box">
            <p class="otp-label">Your One-Time Password:</p>
            <div class="otp">{otp}</div>
            <p class="otp-expiry">Valid for 10 minutes</p>
        </div>
        <p><strong>Important:</strong> Please do not share this code with anyone.</p>
        <p style="color: #666; font-size: 14px;">If you did not request this password reset, please ignore this email or contact our support team.</p>
    </div>
    {_footer_section()}
"""
    html = _wrap_html(body)
    return send_email(to_email, subject, html, text)


def send_admin_otp_email(to_email, otp):
    """Send OTP for admin password reset"""
    subject = "Admin Password Reset OTP - Hotel Shanmuga Bhavaan"
    text = (
        f"Hello Admin,\n\n"
        f"You have requested to reset your admin password for Hotel Shanmuga Bhavaan Dashboard.\n\n"
        f"Your One-Time Password (OTP) is: {otp}\n\n"
        f"This OTP is valid for 10 minutes. Please do not share this code with anyone.\n\n"
        f"If you did not request this password reset, please secure your account immediately.\n\n"
        f"Best regards,\nHotel Shanmuga Bhavaan System"
    )
    body = f"""
    {_header_section("Admin Password Reset")}
    <div class="content">
        <p>Hello <strong>Admin</strong>,</p>
        <p>You have requested to reset your admin password for the <strong>Hotel Shanmuga Bhavaan Dashboard</strong>.</p>
        <div class="otp-box">
            <p class="otp-label">Your One-Time Password:</p>
            <div class="otp">{otp}</div>
            <p class="otp-expiry">Valid for 10 minutes</p>
        </div>
        <p><strong>Important:</strong> Please do not share this code with anyone.</p>
        <div class="warning">
            <strong>⚠️ Security Notice:</strong> If you did not request this password reset, please secure your account immediately.
        </div>
    </div>
    {_footer_section()}
"""
    html = _wrap_html(body)
    return send_email(to_email, subject, html, text)


def send_order_confirmation_email(order, menu_items_details):
    """Send order confirmation email to customer"""
    subject = f"Order Confirmation #{order.order_id} - Hotel Shanmuga Bhavaan"

    items_text = "\n".join(
        [f"- {item['name']} x {item['quantity']} - ₹{item['price']:.2f}" for item in menu_items_details]
    )
    text = (
        f"Dear {order.customer_name},\n\n"
        f"Thank you for choosing Hotel Shanmuga Bhavaan!\n\n"
        f"Your order has been successfully placed.\n\n"
        f"Order #: {order.order_id}\n"
        f"Event Type: {order.event_type}\n"
        f"Number of Guests: {order.number_of_guests}\n"
        f"Event Date: {order.event_date}\n"
        f"Event Time: {order.event_time}\n"
        f"Venue: {order.venue_address}\n"
        f"Total Amount: ₹{order.total_amount:.2f}\n"
        f"Payment Method: {order.payment_method.title()}\n\n"
        f"Items Ordered:\n{items_text}\n\n"
        f"Best regards,\nHotel Shanmuga Bhavaan Management Team"
    )

    items_html = ""
    for item in menu_items_details:
        items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ffedc7;">{item['name']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ffedc7; text-align: center;">{item['quantity']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ffedc7; text-align: right;">₹{item['price']:.2f}</td>
            </tr>
        """

    body = f"""
    {_header_section("Order Confirmation")}
    <div class="content">
        <p>Dear <strong>{order.customer_name}</strong>,</p>

        <div class="thank-you">
            <h2>🙏 Thank You for Choosing Our Hotel! 🙏</h2>
            <p>We are honored to be part of your special event. Your trust means everything to us, and we promise to deliver an unforgettable culinary experience!</p>
        </div>

        <div class="order-box">
            <h3 style="color: #7a0000; margin: 0 0 14px 0; font-size: 17px;">📋 Order Details</h3>
            <div class="detail-row"><span class="detail-label">Order Number:</span> <span>#{order.order_id}</span></div>
            <div class="detail-row"><span class="detail-label">Event Type:</span> <span>{order.event_type}</span></div>
            <div class="detail-row"><span class="detail-label">Number of Guests:</span> <span>{order.number_of_guests}</span></div>
            <div class="detail-row"><span class="detail-label">Event Date:</span> <span>{order.event_date}</span></div>
            <div class="detail-row"><span class="detail-label">Event Time:</span> <span>{order.event_time}</span></div>
            <div class="detail-row"><span class="detail-label">Venue:</span> <span>{order.venue_address}</span></div>
            <div class="detail-row" style="border-bottom: none;"><span class="detail-label">Payment Method:</span> <span>{order.payment_method.title()}</span></div>
        </div>

        <h3 style="color: #7a0000; font-size: 17px;">🍽️ Items Ordered:</h3>
        <table class="items-table">
            <thead>
                <tr>
                    <th>Item</th>
                    <th style="text-align: center;">Qty</th>
                    <th style="text-align: right;">Price</th>
                </tr>
            </thead>
            <tbody>{items_html}</tbody>
        </table>

        <div class="total-box">Total Amount: ₹{order.total_amount:.2f}</div>

        <p style="margin-top: 24px; font-size: 14px; color: #666;">
            We look forward to making your event memorable! If you have any questions or special requests,
            please don't hesitate to contact us.
        </p>
    </div>
    {_footer_section()}
"""
    html = _wrap_html(body)
    return send_email(order.email, subject, html, text)


def send_order_cancellation_email(order):
    """Send order cancellation notification email to customer"""
    subject = f"Order #{order.order_id} Cancelled - Hotel Shanmuga Bhavaan"
    text = (
        f"Dear {order.customer_name},\n\n"
        f"We regret to inform you that your order #{order.order_id} has been cancelled.\n\n"
        f"Order Details:\n"
        f"Order #: {order.order_id}\n"
        f"Event Type: {order.event_type}\n"
        f"Event Date: {order.event_date}\n"
        f"Total Amount: ₹{order.total_amount:.2f}\n\n"
        f"If you have already made a payment, your refund will be processed within 5-7 business days.\n\n"
        f"If you have any questions or wish to place a new order, please feel free to contact us.\n\n"
        f"Phone: 79044 79451\n"
        f"Email: shanmugapriyaraja31@gmail.com\n\n"
        f"Best regards,\nHotel Shanmuga Bhavaan Management Team"
    )
    body = f"""
    {_header_section("Order Cancellation")}
    <div class="content">
        <p>Dear <strong>{order.customer_name}</strong>,</p>
        <p>We regret to inform you that your order has been cancelled.</p>

        <div class="cancel-box">
            <h3>❌ Cancelled Order Details</h3>
            <div class="detail-row"><span class="detail-label">Order Number:</span> <span>#{order.order_id}</span></div>
            <div class="detail-row"><span class="detail-label">Event Type:</span> <span>{order.event_type}</span></div>
            <div class="detail-row"><span class="detail-label">Event Date:</span> <span>{order.event_date}</span></div>
            <div class="detail-row"><span class="detail-label">Number of Guests:</span> <span>{order.number_of_guests}</span></div>
            <div class="detail-row" style="border-bottom: none;"><span class="detail-label">Total Amount:</span> <span style="font-weight: 700; color: #7a0000;">₹{order.total_amount:.2f}</span></div>
        </div>

        <div class="refund-notice">
            <strong>💰 Refund Information:</strong>
            <p style="margin: 5px 0 0 0;">If you have already made a payment, your refund will be processed within <strong>5-7 business days</strong>.</p>
        </div>

        <div class="contact-box">
            <p style="margin: 0 0 6px 0; font-weight: 700; color: #7a0000;">Need Help?</p>
            <p style="margin: 0;">📞 Phone: 79044 79451</p>
            <p style="margin: 0;">📧 Email: shanmugapriyaraja31@gmail.com</p>
        </div>

        <p style="font-size: 14px; color: #666;">
            We apologize for any inconvenience caused. We hope to serve you again in the future!
        </p>
    </div>
    {_footer_section()}
"""
    html = _wrap_html(body)
    return send_email(order.email, subject, html, text)
