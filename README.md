# Lab

## Automated Evening Messages

This repository sends an automated message every evening using a GitHub Actions
workflow (`/.github/workflows/evening-messages.yml`). The workflow is
triggered by a cron schedule and can also be run manually via
`workflow_dispatch`.

### How it works

1. The GitHub Actions workflow fires at **18:00 UTC every day** (configurable
   via the `cron` expression in the workflow file).
2. It runs `send_message.py`, which reads configuration from environment
   variables and dispatches the message to the chosen channel.

### Supported channels

| Channel | Required secret(s) / variable(s) |
|---------|----------------------------------|
| Slack   | `SLACK_WEBHOOK_URL` (secret)      |
| Discord | `DISCORD_WEBHOOK_URL` (secret)    |
| Email   | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_RECIPIENT` (all secrets) |

### Configuration

Set the following in your repository **Settings → Secrets and variables →
Actions**:

#### Variables (non-sensitive)

| Name | Description | Default |
|------|-------------|---------|
| `MESSAGE_CHANNEL` | `slack`, `discord`, or `email` | `slack` |
| `EVENING_MESSAGE` | Custom message text | auto-generated |
| `EMAIL_SUBJECT` | Subject line for email channel | `Evening Message` |

#### Secrets (sensitive)

Add whichever secrets apply to your chosen channel (see table above).

### Running locally

```bash
# Example: send via Slack
export MESSAGE_CHANNEL=slack
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
python send_message.py
```

### Running the tests

```bash
python -m unittest test_send_message -v
```

### Changing the schedule

Edit the `cron` expression in `.github/workflows/evening-messages.yml`:

```yaml
schedule:
  - cron: '0 18 * * *'   # 18:00 UTC = 6 PM UTC every day
```

Use [crontab.guru](https://crontab.guru/) to build a custom expression.
