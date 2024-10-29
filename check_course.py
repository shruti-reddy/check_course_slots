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
    courses_to_check = {"DATA COMMUNICATIONS AND NETWOR":3}

    # Send the POST request
    response = requests.post(url, data=payload)
    response.raise_for_status()  # Check for HTTP request errors

    soup = BeautifulSoup(response.text, 'html.parser')
    alert_messages = []
    for course_name, threshold in courses_to_check.items():
        # Find all instances of the course
        courses = [course for course in soup.find_all("tr") if course_name in course.text]
        
        # Check if the number of instances exceeds the threshold
        if len(courses) >= threshold:
            course_message = f"'{course_name}' has {len(courses)} instances (threshold: {threshold}):\n"
            for course in courses:
                course_message += f"{course.get_text(separator=' ')}\n"
            alert_messages.append(course_message)

    if alert_messages:
        email_body = "\n\n".join(alert_messages)
    else:
        print("courses not found")
        return
    

    # Email setup
    sender_email = os.getenv("EMAIL_USER")
    receiver_emails = os.getenv("RECEIVER_EMAILS").split(",")
    password = os.getenv("EMAIL_PASS")
    subject = "Multiple Instances of Advanced Software Engineering Detected"

    # Compose email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_emails)
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
            server.sendmail(sender_email, receiver_emails, message.as_string())
            print("Email sent successfully to all recipients.")
        except smtplib.SMTPException as e:
                    print("Error during SMTP communication:", e)    


if __name__ == "__main__":
    check_and_notify()
