import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
logger = logging.getLogger(__name__)

SERVICE_ACCOUNT_FILE = r'C:\Users\Predator\Desktop\sunway_RPA\hardy-antonym-457208-h8-3ccfb2cf7534.json'
SHEET_NAME = "Attendence"
ATTACHMENT_PATH = r'C:\Users\Predator\Desktop\sunway_RPA\demo.png'

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'deepeshdhaurali768@gmail.com'
SENDER_PASSWORD = 'lywb dxir zkpc adfc'

scope = ["https://www.googleapis.com/auth/spreadsheets.readonly",
         "https://www.googleapis.com/auth/drive.readonly"]

def send_single_email(to_email, subject, body, attachment_path=None):
    """Sends a single email."""
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    if attachment_path:
        try:
            filename = attachment_path.split('\\')[-1]
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={filename}')
                msg.attach(part)
        except FileNotFoundError:
            logger.error(f"Attachment file not found: {attachment_path}")
        except Exception as e:
            logger.error(f"Error attaching file {attachment_path}: {e}")


    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            text = msg.as_string()
            server.sendmail(SENDER_EMAIL, to_email, text)
            logger.info(f"Email successfully sent to {to_email}")
            return True
    except smtplib.SMTPAuthenticationError:
        logger.error(f"SMTP Authentication Error for {SENDER_EMAIL}. Check email/password/app password.")
        return False
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

def process_and_send_emails():
    """Fetches data from Google Sheets and sends emails to absent students."""
    sent_count = 0
    failed_count = 0
    processed_count = 0

    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        data = sheet.get_all_records()
        logger.info(f"Successfully fetched {len(data)} records from Google Sheet '{SHEET_NAME}'.")
    except FileNotFoundError:
         logger.error(f"Service account key file not found: {SERVICE_ACCOUNT_FILE}")
         return {'error': f"Service account key file not found: {SERVICE_ACCOUNT_FILE}"}
    except gspread.exceptions.SpreadsheetNotFound:
         logger.error(f"Spreadsheet not found: {SHEET_NAME}")
         return {'error': f"Spreadsheet '{SHEET_NAME}' not found or not shared with service account."}
    except Exception as e:
        logger.error(f"Error connecting to Google Sheets: {e}")
        return {'error': f"Error connecting to Google Sheets: {e}"}

    for row in data:
        processed_count += 1
        if 'week 1' not in row or 'Name' not in row or 'Email id' not in row:
            logger.warning(f"Skipping row due to missing required columns: {row}")
            failed_count += 1
            continue

        try:
            attendance_status = row['week 1']
            if isinstance(attendance_status, str) and attendance_status.lower() == 'absent':
                student_name = row['Name']
                student_email = row['Email id']
                if not student_email or '@' not in student_email:
                     logger.warning(f"Skipping row for {student_name} due to invalid email: {student_email}")
                     failed_count += 1
                     continue

                subject = f"Attendance Update: You were marked absent"
                body = f"""
                <html>
                    <body>
                        <p><b>Hello {student_name},</b></p>
                        <p><i>We noticed that you were marked <u>absent</u> in this week's attendance (Week 1).</i></p>
                        <p>Please <a href="https://sunway.edu.np/">click here</a> if you need more information or contact your instructor.</p>
                        <p>If you believe this is an error, please reply to this email.</p>
                        <p>Best regards,<br>Your Course Team</p>
                    </body>
                </html>
                """

                if send_single_email(student_email, subject, body, ATTACHMENT_PATH):
                    sent_count += 1
                else:
                    failed_count += 1
        except Exception as e:
             logger.error(f"Error processing row {row}: {e}")
             failed_count += 1


    logger.info(f"Email processing complete. Total: {processed_count}, Sent: {sent_count}, Failed/Skipped: {failed_count}")
    return {'processed': processed_count, 'sent': sent_count, 'failed': failed_count}