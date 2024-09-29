import speech_recognition as sr
import easyimap as e
import pyttsx3
import smtplib
import re
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from bs4 import BeautifulSoup

unm = "supu85374@gmail.com"
pwd = "prurbwavlesesaty"
r = sr.Recognizer()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 150)

recipient_dict = {
    "komal": "km347349@gmail.com",
    "revathi": "revatisudhir2001@gmail.com",
    "revati": "revatisudhir2001@gmail.com",
    "supriya": "dandawatesupriya04@gmail.com"
}

def speak(str):
    print(str)
    engine.say(str)
    engine.runAndWait()

def listen():
    max_attempts = 3
    for _ in range(max_attempts):
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            str = "Speak now:"
            speak(str)
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio)
                print("Recognized text:", text)  # Add this line for debugging
                return text.lower()
            except sr.UnknownValueError:
                str = "Sorry, I could not understand what you said. Please try again."
                speak(str)
            except sr.RequestError as e:
                print("Error accessing the speech recognition service:", e)  # Add this line for debugging
                str = "I'm having trouble accessing the speech recognition service. Please check your internet connection."
                speak(str)
    return ""  # Return an empty string if no

def sendmail(recipient_email):
    # Define a dictionary mapping user-friendly names to emoji characters
    emoji_mapping = {
        'sad': '😢',
        'happy': '😊',
        'angry': '😠'
        # Add more mappings as needed
    }
    # Initialize cc_emails as an empty list
    cc_emails = []

    msg = MIMEMultipart()
    msg['From'] = unm
    msg['To'] = recipient_email

    str = f"Please speak the subject of your email to {recipient_email}\n"
    speak(str)
    subject = listen()
    msg['Subject'] = subject

    str = f"Please speak the body of your email to {recipient_email}\n"
    speak(str)
    email_body = listen()

    # Attach the email body as a MIMEText object
    msg.attach(MIMEText(email_body, 'plain', 'utf-8'))

    # Ask the user if they want to add an emoji
    str = "Do you want to add an emoji to the email body? Say 'add' or 'cancel'.\n"
    speak(str)
    response_emoji = listen().lower()

    if response_emoji == 'add':
        str = "Please speak the type of emoji you want to add (e.g., 'sad', 'happy', 'angry').\n"
        speak(str)
        emoji_type = listen().lower()

        # Check if the user's response corresponds to a predefined emoji type
        if emoji_type in emoji_mapping:
            # Get the emoji character corresponding to the user's response
            emoji = emoji_mapping[emoji_type]

            # Append the emoji to the email body
            email_body += f" {emoji}"
        else:
            speak("Sorry, I didn't recognize that emoji type.")

    while True:
        str = f"You have spoken the following message:\nSubject: {subject}\nBody: {email_body}\nIs this correct?\nSay 'confirm' to confirm, 'edit' to edit, or 'cancel' to cancel.\n"
        speak(str)
        confirmation = listen()

        if confirmation == 'confirm':
            break
        elif confirmation == 'edit':
            str = "Do you want to edit the subject? Say 'edit' or 'no.\n"
            speak(str)
            edit_subject = listen()
            if edit_subject == 'edit':
                str = "Please speak the new subject.\n"
                speak(str)
                new_subject = listen()
                if new_subject:
                    subject = new_subject
                    msg['Subject'] = subject
            str = "Do you want to edit the body? Say 'edit' or 'no.\n"
            speak(str)
            edit_body = listen()
            if edit_body == 'edit':
                str = "Please speak the new body.\n"
                speak(str)
                new_body = listen()
                if new_body:
                    email_body = new_body
                    # Update the email body in the message object
                    msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
        elif confirmation == 'cancel':
            return

    # Attach the email body as a MIMEText object
    msg.attach(MIMEText(email_body, 'plain', 'utf-8'))

    str = "Do you want to attach a file to the email? Say 'attach' to attach or 'no' to cancel.\n"
    speak(str)
    attach_file = listen().lower()

    if attach_file == 'attach':
        str = "Please say the name of the file you want to attach with extension, for example, 'example.pdf'.\n"
        speak(str)
        file_name = listen().replace(" dot ", ".").replace(" ", "_")  # Replace "dot" with "." and spaces with underscores

        # Assuming the file is on the desktop, construct the full file path
        file_path = f"C:\\Users\\HP\\OneDrive\\Desktop\\{file_name}"

        if file_name:
            try:
                with open(file_path, 'rb') as attachment:
                    # Read the file
                    attachment_content = attachment.read()

                # Add the attachment to the email
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_content)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {file_name}")

                msg.attach(part)

            except FileNotFoundError:
                speak("File not found. Please make sure the file exists on your desktop.")

    str = "Do you want to add any recipients in CC? If yes, please say 'add', if no then say 'cancel'.\n"
    speak(str)
    add_cc_recipients = listen().lower()  # Convert to lowercase

    if add_cc_recipients == 'add':
        str = "Please speak the names of recipients to add in CC, separated by space.\n"
        speak(str)
        cc_recipients = listen()

        if cc_recipients:
            cc_recipients = cc_recipients.split()
            cc_emails = [recipient_dict.get(name) for name in cc_recipients if name in recipient_dict]
            cc_emails = list(filter(None, cc_emails))
            if cc_emails:
                msg['CC'] = ', '.join(cc_emails)

    # Sending the email
    print(f"Email: {unm}, Password: {pwd}")
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        server.login(unm, pwd)
        server.sendmail(unm, [recipient_email] + cc_emails, msg.as_string())
        server.quit()

        str = f"The email has been sent to {recipient_email}\n"
        speak(str)
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        str = "There was an issue with authentication. Please check your credentials and try again."
        speak(str)

    imap_server = imaplib.IMAP4_SSL("imap.gmail.com")
    imap_server.login(unm, pwd)
        
def readmail(keyword):
    server = e.connect("imap.gmail.com", unm, pwd)
    server.listids()

    matching_emails = []

    for email_id in server.listids():
        email = server.mail(email_id)
        email_text = re.sub(r'<[^>]+>', ' ', email.body)  # Remove HTML tags and replace with space
        email_text = ' '.join(email_text.split())  # Remove extra spaces

        if keyword.lower() in email_text.lower():
            matching_emails.append(email_text)

    if not matching_emails:
        str = f"No emails found with the keyword '{keyword}' in the body."
        speak(str)
        return

    for email_text in matching_emails:
        str = "Found an email with the keyword in the body."
        speak(str)

        # Speak the email content line by line
        email_lines = email_text.split('\n')
        for line in email_lines:
            if line.strip():  # Check if the line is not empty0-[p]
                speak(line.strip())  # Speak each non-empty line

        # Add a pause to separate email content from the next email
        speak("End of email.")

def get_spam_count(imap_server):
    # Select the Spam folder
    status, messages = imap_server.select("[Gmail]/Spam")
    if status == 'OK':
        # Get the count of spam emails
        _, message_numbers = imap_server.search(None, 'ALL')
        spam_count = len(message_numbers[0].split())
        return spam_count
    else:
        return 0

def read_latest_spam_email(imap_server):
    # Search for unread spam emails
    _, email_ids = imap_server.search(None, "UNSEEN")
     
    # If there are no unread spam emails, inform the user and return
    if not email_ids[0]:
        str = "No new unread spam emails found."
        speak(str)
        return

    # Get the latest unread spam email
    latest_email_id = email_ids[0].split()[-1]
    _, email_data = imap_server.fetch(latest_email_id, "(RFC822)")

    # Parse the email content
    email_message = email.message_from_bytes(email_data[0][1])
    email_subject = email_message["subject"]
    email_text = ""

    # Extract plain text from the email body
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                
                email_text = part.get_payload(decode=True).decode("utf-8")
                break
    else:
        email_text = email_message.get_payload(decode=True).decode("utf-8")

    str = "Found a new unread spam email."
    speak(str)

    str = "Subject: " + email_subject
    speak(str)

    str = "Email Content:"
    speak(str)
    speak(email_text)
    
    speak("Do you want to delete this spam email? Say 'delete', 'important', or 'cancel'.")
    response = listen().lower()

    if response == 'delete':
        # Delete the email
        imap_server.store(latest_email_id, '+FLAGS', '(\Deleted)')
        imap_server.expunge()
        str = "The email has been deleted."
        speak(str)
    elif response == 'important':
        # Mark the email as important
        imap_server.store(latest_email_id, "+FLAGS", "\\Flagged")
        str = "The email has been marked as important."
        speak(str)
    elif response == 'cancel':
        # Do something else when user cancels
        pass


def read_latest_unread_email(unm, pwd):
    # Connect to the Gmail IMAP server
    imap_server = imaplib.IMAP4_SSL("imap.gmail.com")
    imap_server.login(unm, pwd)
    imap_server.select("inbox")  # Select the inbox folder

    # Search for unread emails
    _, email_ids = imap_server.search(None, "UNSEEN")

    # If there are no unread emails, inform the user and return
    if not email_ids[0]:
        str = "No new unread emails found."
        speak(str)
        imap_server.logout()
        return

    # Get the latest unread email
    latest_email_id = email_ids[0].split()[-1]
    _, email_data = imap_server.fetch(latest_email_id, "(RFC822)")

    # Parse the email content
    email_message = email.message_from_bytes(email_data[0][1])
    email_subject = email_message["subject"]
    email_text = ""

    # Extract plain text from the email body
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                email_text = part.get_payload(decode=True).decode("utf-8")
                break
    else:
        email_text = email_message.get_payload(decode=True).decode("utf-8")

    str = "Found a new unread email."
    speak(str)

    str = "Subject: " + email_subject
    speak(str)

    str = "Email Content:"
    speak(str)
    speak(email_text)

    # Ask the user if they want to delete the email
    speak("Do you want to delete this email? Say 'delete', 'reply', or 'cancel'.")
    response_delete = listen().lower()

    if response_delete == 'delete':
        # Delete the email
        imap_server.store(latest_email_id, '+FLAGS', '(\Deleted)')
        imap_server.expunge()
        str = "The email has been deleted."
        speak(str)
    elif response_delete == 'reply':
        # Ask the user for the reply content
        speak("Please dictate your reply.")
        reply_content = listen()

        # Send the reply
        reply_message = email.message.EmailMessage()
        reply_message.set_content(reply_content)
        reply_message["Subject"] = "Re: " + email_subject
        reply_message["From"] = "supu85374@gmail.com"  # Replace with your email
        reply_message["To"] = email_message["from"]

        imap_server.append("inbox", None, None, reply_message.as_bytes())
        str = "Your reply has been sent."
        speak(str)
    else:
        # Ask the user if they want to mark the email as important
        speak("Do you want to mark this email as important? Say 'mark' or 'cancel'.")
        response_mark = listen().lower()

        if response_mark == 'mark':
            # Mark the email as important
            imap_server.store(latest_email_id, "+FLAGS", "\\Flagged")
            str = "The email has been marked as important."
            speak(str)

    # Logout and close the connection
    imap_server.logout()

while True:
    str = "What do you want to do?"
    speak(str)

    str = "Speak 'SEND' to send email, 'SEARCH' to search email, 'LATEST' to read the latest unread email, 'report' to check spam emails, 'EXIT' to exit"
    speak(str)
    ch = listen()

    if ch == 'send':
        str = "You have chosen to send an email. Please say the recipient's name."
        speak(str)
        recipient_name = listen()
        recipient_email = recipient_dict.get(recipient_name)
        if recipient_email:
            sendmail(recipient_email)
        else:
            str = f"Recipient {recipient_name} not found in the list."
            speak(str)
    elif ch == 'search':
        str = "You have chosen to search for emails. Please provide a search keyword."
        speak(str)
        keyword = listen()
        if keyword:
            readmail(keyword)
    elif ch == 'latest':
        read_latest_unread_email(unm, pwd)
    elif ch == 'report':
        # Connect to the Gmail IMAP server
        imap_server = imaplib.IMAP4_SSL("imap.gmail.com")
        imap_server.login(unm, pwd)

        # Get and speak the count of spam emails
        spam_count = get_spam_count(imap_server)
        str = f"You have {spam_count} unread spam emails."
        speak(str)

        # Ask the user if they want to read the latest spam email
        speak("Do you want to read the latest spam email? Say 'read' or 'cancel'.")
        response_read_spam = listen().lower()

        if response_read_spam == 'read':
            read_latest_spam_email(imap_server)

        imap_server.logout()
    elif ch == 'exit':
        str = "You have chosen to exit, bye-bye"
        speak(str)
        break