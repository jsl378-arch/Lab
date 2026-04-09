"""
Automated Evening Message Sender

This script sends a message every evening. It supports multiple channels:
- Email (via SMTP)
- Slack (via webhook)
- Discord (via webhook)

Configure the desired channel using environment variables (see README.md).
"""

import os
import sys
import smtplib
import urllib.request
import urllib.error
import json
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_message() -> str:
    """Return the evening message to send."""
    custom_message = os.environ.get("EVENING_MESSAGE")
    if custom_message:
        return custom_message
    now = datetime.now(timezone.utc)
    return f"Good evening! This is your automated message for {now.strftime('%A, %B %d, %Y')}."


def send_email(message: str) -> None:
    """Send message via email using SMTP."""
    smtp_host = os.environ["SMTP_HOST"]
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ["SMTP_USER"]
    smtp_password = os.environ["SMTP_PASSWORD"]
    recipient = os.environ["EMAIL_RECIPIENT"]
    subject = os.environ.get("EMAIL_SUBJECT", "Evening Message")

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipient, msg.as_string())

    print(f"Email sent to {recipient}")


def send_slack(message: str) -> None:
    """Send message to a Slack channel via incoming webhook."""
    webhook_url = os.environ["SLACK_WEBHOOK_URL"]
    payload = json.dumps({"text": message}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        if response.status != 200:
            raise RuntimeError(f"Slack webhook returned HTTP {response.status}")
    print("Message sent to Slack")


def send_discord(message: str) -> None:
    """Send message to a Discord channel via webhook."""
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    payload = json.dumps({"content": message}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        if response.status not in (200, 204):
            raise RuntimeError(f"Discord webhook returned HTTP {response.status}")
    print("Message sent to Discord")


CHANNELS = {
    "email": send_email,
    "slack": send_slack,
    "discord": send_discord,
}


def main() -> None:
    channel = os.environ.get("MESSAGE_CHANNEL", "slack").lower()
    if channel not in CHANNELS:
        print(
            f"Error: unsupported MESSAGE_CHANNEL '{channel}'. "
            f"Choose one of: {', '.join(CHANNELS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    message = get_message()
    print(f"Sending evening message via {channel}: {message!r}")
    CHANNELS[channel](message)


if __name__ == "__main__":
    main()
