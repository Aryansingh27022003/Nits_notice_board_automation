import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import time
import re

url = "http://www.nits.ac.in/noticeboard.php"
pdf_save_path = "./downloaded_pdfs"


def scrape_notice_board():
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        notice_board_content = (
            soup.find("div", {"class": "tab-content1 panel-body panel-border"})
            .get_text()
            .strip()
        )

        # Extract the PDF link using a regular expression (modify as needed)
        pdf_link_match = re.search(r'href="(/notices/\S+\.pdf)"', notice_board_content)
        if pdf_link_match:
            pdf_relative_url = pdf_link_match.group(1)
            pdf_url = f"http://www.nits.ac.in{pdf_relative_url}"
            return notice_board_content, pdf_url, True
        else:
            # Extract the general link
            general_link_match = re.search(r'href="(http[s]?://\S+)"', notice_board_content)
            if general_link_match:
                general_url = general_link_match.group(1)
                return notice_board_content, general_url, False
            else:
                return notice_board_content, None, False

    except requests.RequestException as e:
        print(f"Error occurred while scraping: {e}")
        return None, None, False


def compare_text(old_content, new_content):
    old_cleaned = " ".join(old_content.split())
    new_cleaned = " ".join(new_content.split())
    return old_cleaned == new_cleaned


def download_and_send_pdf(pdf_url, receiver_emails):
    pdf_name = "new_pdf.pdf"
    pdf_path = download_pdf(pdf_url, pdf_name)

    if pdf_path:
        # Send notification with the downloaded PDF
        send_notification(receiver_emails, pdf_path)


def send_notification(receiver_emails, file_path):
    sender_email = "testingwebappsnits@gmail.com"
    subject = "URGENT: CHANGES NOTICED IN INSTITUTE NOTICEBOARD"
    message = "New notice."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    with open(file_path, 'rb') as file:
        attach = MIMEApplication(file.read(), _subtype="pdf")
        attach.add_header('Content-Disposition', 'attachment', filename=str(file_path))
        msg.attach(attach)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, "pjgz xqec tkqc esji")
    for receiver_email in receiver_emails:
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"Mail sent to {receiver_email}\n")
    print("Mail sent\n")


def download_pdf(pdf_url, pdf_name):
    try:
        pdf_response = requests.get(pdf_url)
        pdf_response.raise_for_status()
        pdf_path = os.path.join(pdf_save_path, pdf_name)
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)
        return pdf_path
    except requests.RequestException as e:
        print(f"Error occurred while downloading PDF: {e}")
        return None


if not os.path.exists(pdf_save_path):
    os.makedirs(pdf_save_path)

previous_content, previous_link, is_pdf_link = scrape_notice_board()

if previous_content:
    while True:
        new_content, new_link, is_new_pdf_link = scrape_notice_board()

        if new_content and not compare_text(previous_content, new_content):
            if is_new_pdf_link:
                # Handle PDF link
                receiver_emails = ["rajiv21_ug@cse.nits.ac.in", "aryan21_ug@cse.nits.ac.in",
                                   "piyush21_ug@cse.nits.ac.in", "anish21_ug@cse.nits.ac.in"]
                download_and_send_pdf(new_link, receiver_emails)
            else:
                # Handle general link
                print(f"Found non-PDF link: {new_link}")

            previous_content, previous_link, is_pdf_link = new_content, new_link, is_new_pdf_link

        time.sleep(3600)
        print("\nChecking after 3600s\n")
else:
    print("Failed to retrieve initial content. Exiting.")

print("hello")