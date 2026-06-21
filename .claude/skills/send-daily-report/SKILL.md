---
name: send-daily-report
description: Send a professional daily email report to your manager with data analysis summary, key metrics, and visualization insights. Use this skill whenever you want to email a daily report of data metrics, sales analysis, visualization summaries, or business intelligence to stakeholders or managers. Includes automatic HTML formatting, KPI calculations, and insights from generated visualizations.
---

# Send Daily Report Skill

## Overview
This skill generates and sends a professional HTML email report containing:
- Executive summary with key metrics (Total Sales, Returns, Net Sales, Return Rate)
- Sales insights (top products, stores, customers)
- Returns analysis (problem areas, trends)
- Links to visualization charts for deeper analysis

## Prerequisites

### 1. Gmail Setup (One-time configuration)
To send emails via Gmail, you need to create an **App-specific password** (not your regular Gmail password):

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (if not already enabled)
3. Go to **App passwords** (appears only after 2-Step Verification is on)
4. Select "Mail" and "Windows Computer"
5. Google will generate a 16-character password
6. Save this password — you'll need it for the environment variable setup

### 2. Environment Variables
Create or update your `.env` file or system environment variables with:

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-specific-password
MANAGER_EMAIL=manager@example.com
```

For this project, since the sender and manager are the same person, use:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=nikhil.reddy0005@gmail.com
SENDER_PASSWORD=<your-16-char-app-password>
MANAGER_EMAIL=nikhil.reddy0005@gmail.com
```

## How to Use

### Quick Start: Send a Report Now
Simply invoke the skill when you want to send a daily report:

```
/send-daily-report
```

The script will:
1. ✅ Read the latest visualization data from `.claude/skills/visualize/visualizations/`
2. ✅ Calculate key metrics from the parquet files
3. ✅ Generate a professional HTML email
4. ✅ Send it to your manager via Gmail SMTP
5. ✅ Print confirmation with timestamp

### Example Output
```
[INFO] Loading visualization data...
[INFO] Calculating metrics...
[INFO] Generating HTML report...
[INFO] Sending email to manager@example.com...
[SUCCESS] Report sent successfully at 2026-06-20 14:30:45
```

## Email Content Format

The email includes:

### 1. Executive Summary
- Total Sales amount
- Total Returns amount  
- Net Sales (after returns)
- Return Rate percentage

### 2. Sales Insights
- Top performing product
- Store performance summary
- Top customer by sales
- Sales trend observation

### 3. Returns Analysis
- High-risk products
- Store return patterns
- Customer return issues
- Return trend observation

### 4. Action Items & Next Steps

## Troubleshooting

### "SMTP Authentication Failed"
- Verify you're using an **App-specific password**, not your regular Gmail password
- Check that the environment variables are set correctly
- Confirm 2-Step Verification is enabled on your Google account

### "Connection refused / SMTP port error"
- Ensure SMTP_PORT is set to `587` (not 465)
- Check your firewall allows outbound SMTP connections

### "File not found" errors
- Verify that visualizations exist in `.claude/skills/visualize/visualizations/`
- Run the `/visualize` skill first to generate the charts

### "Environment variable not found"
- On Windows PowerShell: `$env:SENDER_EMAIL = "your-email@gmail.com"`
- Or create a `.env` file in the project root
- Restart your terminal/IDE after setting environment variables

## Advanced: Scheduling Daily Emails

To run this automatically every day, see the **Scheduling** section in CLAUDE.md or set up:

**Windows Task Scheduler:**
```powershell
$action = New-ScheduledTaskAction -Execute "C:\ClaudeCode\.venv\Scripts\python.exe" `
  -Argument ".\.claude\skills\send-daily-report\scripts\send_report.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 9AM
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "DailyDataReport"
```

**Claude Code Hook (in settings.json):**
```json
{
  "hooks": {
    "before_day_end": ".\.claude\skills\send-daily-report\scripts\send_report.py"
  }
}
```

## File Structure
```
send-daily-report/
├── SKILL.md              (this file)
└── scripts/
    └── send_report.py    (main email sending script)
```

## Script Details

The `send_report.py` script:
- Reads parquet files from `.claude/skills/migrate/data/` and visualization directory
- Calculates KPIs and metrics
- Generates professional HTML using CSS
- Connects to Gmail SMTP on port 587
- Sends with TLS encryption
- Logs all actions with timestamps
- Raises errors if email fails (no silent failures)

## Security Notes
- Never commit `.env` files with credentials to version control
- Use App-specific passwords, not your main Gmail password
- The script logs actions but never prints sensitive credentials
- SMTP connection uses TLS encryption

## Support
If you need to modify email recipients, metrics, or scheduling, update the environment variables or edit `send_report.py` directly. The script is well-commented for customization.
