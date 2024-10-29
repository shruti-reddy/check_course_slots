import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def check_and_notify():
    # Define the URL and payload
    url = "https://banner.tamucc.edu/schedule/BPROD.php"
    payload = {
        'frmTerm': '202501',
        'frmCampus': 'M',
        'frmPrefix': 'COSC-Computer Science',
        'frmGroup': 'one',
        'frmSelectSchedule': 'View'
    }

    # Send the POST request
    response = requests.post(url, data=payload)
    response.raise_for_status()  # Check for HTTP request errors

    soup = BeautifulSoup(response.text, 'html.parser')
    course_name = "ADVANCED SOFTWARE ENGINEERING"
    courses = [course for course in soup.find_all("tr") if course_name in course.text]

    # Check if there’s more than one instance of the course
    if len(courses) > 1:
        # Prepare the email content
        email_body = f"Multiple instances of the course '{course_name}' were found:\n"
        for course in courses:
            email_body += f"{course.get_text(separator=' ')}\n\n"
    else:
        print("only one course found")
        return

    # Email setup
    sender_email = os.getenv("EMAIL_USER")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    password = os.getenv("EMAIL_PASS")
    subject = "Multiple Instances of Advanced Software Engineering Detected"

    # Compose email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(email_body, "plain"))

    # Send the email
    print(sender_email)
    print(password)

    with smtplib.SMTP(os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT")) as server:
        try:
            server.connect(os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT"))  # Explicitly connect
            server.ehlo()  # Identify to the server
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        except smtplib.SMTPException as e:
                    print("Error during SMTP communication:", e)    


if __name__ == "__main__":
    check_and_notify()