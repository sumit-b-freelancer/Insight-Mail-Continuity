import imaplib
import email
from email.header import decode_header
from django.contrib.auth.models import User
from .models import Email

def clean_encoding(encoding):
    """
    Helper to fix 'unknown-8bit' or None encodings.
    """
    if not encoding or encoding.lower() in ['unknown-8bit', 'x-user-defined']:
        return 'utf-8'
    return encoding

def fetch_gmail_emails(username, password, current_user):
    """
    Connects to Gmail, fetches UNSEEN emails (Newest First), saves them to Django DB.
    """
    # 1. Connect to Gmail
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    
    try:
        mail.login(username, password)
    except Exception as e:
        return f"Login Failed: {e}"

    mail.select("inbox")

    # 2. Search for Unread Emails
    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()

    if not email_ids:
        return "No new emails found."

    # --- THE FIX: PROCESS NEWEST FIRST ---
    # IMAP gives IDs as [1, 2, 3] (Oldest to Newest). 
    # We reverse it to [3, 2, 1] so we get the latest emails first.
    email_ids.reverse()

    count = 0
    for e_id in email_ids:
        try:
            # Fetch the email data
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # --- A. Decode Subject (Robust Fix) ---
                    raw_subject = msg["Subject"]
                    subject = "(No Subject)"
                    
                    if raw_subject:
                        decoded_fragments = decode_header(raw_subject)
                        subject_parts = []
                        for text_bytes, encoding in decoded_fragments:
                            if isinstance(text_bytes, bytes):
                                safe_enc = clean_encoding(encoding)
                                try:
                                    subject_parts.append(text_bytes.decode(safe_enc, errors='replace'))
                                except (LookupError, UnicodeDecodeError):
                                    subject_parts.append(text_bytes.decode('utf-8', errors='replace'))
                            else:
                                subject_parts.append(str(text_bytes))
                        subject = "".join(subject_parts)
                    
                    # --- B. Decode Sender ---
                    sender_str = msg.get("From", "Unknown Sender")
                    
                    # --- C. Extract Body ---
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            
                            try:
                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    payload = part.get_payload(decode=True)
                                    charset = part.get_content_charset()
                                    safe_charset = clean_encoding(charset)
                                    
                                    body = payload.decode(safe_charset, errors='replace')
                                    break 
                            except:
                                pass
                    else:
                        try:
                            payload = msg.get_payload(decode=True)
                            charset = msg.get_content_charset()
                            safe_charset = clean_encoding(charset)
                            body = payload.decode(safe_charset, errors='replace')
                        except:
                            body = "(Could not decode email body)"

                    # --- D. Save to Database ---
                    clean_address = email.utils.parseaddr(sender_str)[1]
                    if not clean_address:
                        clean_address = "unknown@example.com"

                    sender_user, _ = User.objects.get_or_create(
                        username=clean_address.split('@')[0][:30],
                        defaults={'email': clean_address, 'first_name': 'External', 'last_name': 'User'}
                    )

                    Email.objects.create(
                        sender=sender_user,
                        recipient=current_user,
                        subject=subject,
                        body=body,
                        is_read=False 
                    )
                    count += 1
        except Exception as e:
            print(f"Skipping a bad email due to error: {e}")
            continue

    mail.close()
    mail.logout()
    return f"Successfully synced {count} emails!"