# Manual Google Meet Link - Quick Start Guide

## 🎯 What Changed?

Instead of the system automatically generating Google Meet links, admins now manually provide them when confirming sessions.

## 📋 Step-by-Step Usage

### For Admin:

1. **Go to Admin Dashboard**
   - Click: Admin → Sessions

2. **Find a Pending Session**
   - Look for sessions with status "Pending"

3. **Click "Confirm with Link" Button**
   - A modal dialog will appear

4. **Paste Google Meet Link**
   - Example: `https://meet.google.com/abc-defg-hij`
   - Click in the text field and paste

5. **Click "Confirm & Send Link"**
   - System will:
     ✓ Save the link
     ✓ Change status to "Confirmed"
     ✓ Send emails to mentor and mentee with the link

### For Mentee:

1. **Check Email**
   - You'll receive a confirmation email with the meeting link

2. **View in Dashboard**
   - Go to "My Sessions"
   - Look for your confirmed session
   - You'll see a blue section with:
     - "📹 Meeting Link Available"
     - "Join Google Meet" button
     - The full meeting link URL

3. **Join the Meeting**
   - Click the "Join Google Meet" button or the link
   - Google Meet will open in a new tab

### For Mentor:

1. **Check Email**
   - You'll receive a confirmation email with the meeting link

2. **View in Mentor Dashboard**
   - Go to your Mentor Dashboard
   - Click on the session details
   - The meeting link will be displayed

3. **Join the Meeting**
   - Click the link to join the Google Meet

## 🔄 What Happens Behind the Scenes

```
Admin Confirms Session + Pastes Link
           ↓
System saves link to database
           ↓
Emails sent to:
  • Mentee (with meeting details & link)
  • Mentor (with meeting details & link)
           ↓
Link appears in both dashboards
           ↓
Users can click to join meeting
```

## 📧 Email Template

When session is confirmed, users receive:

```
Hello [User Name],

Your session with [Mentor Name] has been confirmed!

Session Details:
Date: [Date]
Time: [Time]
Duration: [Duration] minutes
Meeting Link: https://meet.google.com/abc-defg-hij

Please join the meeting 5 minutes before the scheduled time.

Best regards,
CodeMentorHub Team
```

## 🛠️ Technical Notes

- **Field Name**: `admin_provided_link` - stores the link provided by admin
- **Timestamp Field**: `link_provided_at` - tracks when link was provided
- **Fallback**: If no link provided, system auto-generates one (optional)
- **Database**: New fields are stored in the Session model

## ✨ Key Features

- ✅ Simple modal interface for link input
- ✅ Automatic email notifications with link
- ✅ Meeting link visible in user dashboards
- ✅ Direct "Join Google Meet" button for users
- ✅ Timestamp tracking for audit purposes
- ✅ Full URL display for transparency

## 📝 Notes

- Make sure to paste a valid Google Meet link
- The link should start with `https://meet.google.com/`
- Users will receive email confirmation immediately after confirming
- Links are displayed in plain text in emails and dashboards
- Old auto-generated links still work (backward compatible)

---

**Need Help?** Contact the admin team if you have any questions about the new link submission process.
