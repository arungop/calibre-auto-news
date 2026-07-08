#!/usr/bin/env python3
"""Email an .epub file to a Kindle "Send to Kindle" address.

Reads SMTP connection details and the Kindle recipient address from
environment variables (set as GitHub Actions secrets in CI):

    SMTP_HOST      e.g. smtp.gmail.com
    SMTP_PORT      e.g. 587
    SMTP_USER      login username for the SMTP server
    SMTP_PASS      login password / app password for the SMTP server
    SENDER_EMAIL   the "From" address -- must be on Amazon's approved
                   sender list for your Kindle (see README)
    KINDLE_EMAIL   your @kindle.com address

Usage:
    python3 send_to_kindle.py path/to/book.epub
"""
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: send_to_kindle.py <path-to-epub>", file=sys.stderr)
        sys.exit(1)

    epub_path = Path(sys.argv[1])
    if not epub_path.exists():
        print(f"ERROR: {epub_path} not found", file=sys.stderr)
        sys.exit(1)

    try:
        smtp_host = os.environ["SMTP_HOST"]
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ["SMTP_USER"]
        smtp_pass = os.environ["SMTP_PASS"]
        kindle_email = os.environ["KINDLE_EMAIL"]
    except KeyError as e:
        print(f"ERROR: missing required environment variable {e}", file=sys.stderr)
        sys.exit(1)

    sender = os.environ.get("SENDER_EMAIL", smtp_user)

    msg = EmailMessage()
    msg["Subject"] = epub_path.stem
    msg["From"] = sender
    msg["To"] = kindle_email
    msg.set_content("Attached: latest South Asian Lit Digest issue.")

    with open(epub_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="epub+zip",
            filename=epub_path.name,
        )

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls(context=context)
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

    print(f"Sent {epub_path.name} to {kindle_email}")


if __name__ == "__main__":
    main()