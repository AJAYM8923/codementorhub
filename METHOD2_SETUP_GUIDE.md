# Google Calendar API Setup (Method 2) - Complete Guide

## ✅ Overview

CodeMentorHub now uses **Google Calendar API (Method 2)** as the primary method to generate actual working Google Meet links.

**Status**: Ready to setup  
**Complexity**: Medium  
**Time Required**: 15-30 minutes  

---

## What is Method 2?

Method 2 creates actual Google Meet links by:
1. Creating a Google Calendar event
2. Adding video conference (Google Meet) to the event
3. Sending calendar invitations to mentor and mentee
4. Extracting the Google Meet link
5. **Result**: Real, professional Google Meet rooms ✅

### Benefits:
✅ Creates actual Google Calendar events  
✅ Sends automatic calendar invitations  
✅ Professional appearance  
✅ Attendee tracking  
✅ Calendar integration  
✅ Real Google Meet links  

---

## Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the **project selector** at the top left
3. Click **"NEW PROJECT"**
4. Enter project name: **"CodeMentorHub"**
5. Click **"CREATE"**
6. Wait for project creation (1-2 minutes)

### Step 2: Enable Google Calendar API

1. In Google Cloud Console, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Calendar API"**
3. Click on **"Google Calendar API"**
4. Click **"ENABLE"**
5. Wait for it to enable (30 seconds)

### Step 3: Create Service Account

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** button
3. Select **"Service Account"**
4. Fill in the form:
   - **Service account name**: `CodeMentorHub`
   - **Service account ID**: auto-filled
   - **Service account description**: `For Google Meet calendar integration`
5. Click **"CREATE AND CONTINUE"**

### Step 4: Grant Permissions

1. Under **"Grant this service account access to project"**:
   - Select Role: **"Editor"**
2. Click **"CONTINUE"**
3. Click **"CREATE KEY"** button
4. Select **"JSON"** format
5. Click **"CREATE"**
6. **A JSON file will download** - **SAVE IT SAFELY** ⚠️

### Step 5: Configure Django

#### Option A: Using Environment Variables (Recommended for Production)

1. Place the downloaded JSON file somewhere safe:
   ```
   /path/to/safe/location/service_account.json
   ```

2. Set environment variable:
   ```bash
   # Linux/Mac
   export GOOGLE_SERVICE_ACCOUNT_FILE="/path/to/safe/location/service_account.json"
   
   # Windows PowerShell
   $env:GOOGLE_SERVICE_ACCOUNT_FILE="C:\path\to\service_account.json"
   ```

3. Verify it's set:
   ```bash
   echo $GOOGLE_SERVICE_ACCOUNT_FILE
   ```

#### Option B: Place in Project (Simple for Development)

1. Copy the downloaded JSON file to:
   ```
   mentorhub/service_account.json
   ```

2. The app will automatically find it
3. **⚠️ IMPORTANT**: Add to `.gitignore`:
   ```
   # .gitignore
   service_account.json
   token.json
   credentials.json
   ```

### Step 6: Install Required Packages

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client google-auth
```

### Step 7: Share Calendar with Service Account

1. Open the downloaded JSON file with a text editor
2. Find the **`"client_email"`** field - copy this email address
3. Go to [Google Calendar](https://calendar.google.com/)
4. Click **Settings** (gear icon) → **"Settings"**
5. Go to **"Sharing settings"** tab
6. Click **"Add people and groups"**
7. Paste the service account email
8. Select permission: **"Make changes to events"** ✅
9. Click **"Send"**

### Step 8: Verify Installation

```bash
# Test if everything is working
python manage.py shell

# Run this Python code
from main.models import Session
from django.conf import settings

# Check if Google Calendar API is enabled
print(f"Google Calendar API Enabled: {settings.GOOGLE_CALENDAR_API_ENABLED}")
print(f"Service Account File: {settings.GOOGLE_SERVICE_ACCOUNT_FILE}")

# Try to generate a link
session = Session.objects.first()
link = session.generate_meeting_link()
print(f"Generated Link: {link}")
```

Expected output:
```
Google Calendar API Enabled: True
Service Account File: /path/to/service_account.json
✅ Using Google Calendar API - Meeting link: https://meet.google.com/xyz-abcd-efg
Generated Link: https://meet.google.com/xyz-abcd-efg
```

---

## Configuration

### Django Settings

All settings are in `mentorhub/settings.py`:

```python
# Google Calendar API Configuration
GOOGLE_CALENDAR_API_ENABLED = True  # Enable/disable the feature
GOOGLE_SERVICE_ACCOUNT_FILE = '/path/to/service_account.json'  # Path to credentials
GOOGLE_CALENDAR_ID = 'primary'  # Use default calendar
GOOGLE_MEET_TIME_BUFFER = 30  # Minutes before session to create event
```

### Environment Variables

You can override settings via environment variables:

```bash
# Enable/disable
export GOOGLE_CALENDAR_API_ENABLED=True

# Set credentials file path
export GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/service_account.json

# Set calendar ID (optional)
export GOOGLE_CALENDAR_ID=primary

# Or use your calendar ID from Google Calendar
export GOOGLE_CALENDAR_ID=abc123@group.calendar.google.com
```

---

## Testing Setup

### Quick Test (5 minutes)

```bash
# 1. Start Django shell
python manage.py shell

# 2. Import and test
from main.models import Session
from main.google_meet_helper import GoogleMeetHelper

# 3. Check credentials
creds = GoogleMeetHelper._get_service_account_credentials()
print(f"Credentials loaded: {creds is not None}")

# 4. Generate a test link
session = Session.objects.first()
link = session.generate_meeting_link()
print(f"Link: {link}")

# 5. Exit
exit()
```

### Full Integration Test

1. **Book a session** as mentee
2. **Complete payment** (any test data)
3. **Confirm session** as admin or mentor
4. **Check the output** - should see:
   ```
   ✅ Using Google Calendar API - Meeting link: https://meet.google.com/xyz-abcd-efg
   ```
5. **Verify email** - contains Google Meet link
6. **Check Google Calendar** - event should appear
7. **Click link** - Google Meet should open ✅

---

## Troubleshooting

### Issue: "Service account file not found"

**Solution**:
```bash
# Check file exists
ls -la mentorhub/service_account.json  # Linux/Mac
dir mentorhub\service_account.json      # Windows

# Or set environment variable
export GOOGLE_SERVICE_ACCOUNT_FILE=/full/path/to/service_account.json
```

### Issue: "Error loading service account credentials"

**Solution**:
1. Check JSON file is valid (open with text editor)
2. Verify "client_email" field exists
3. Check file permissions: `chmod 644 service_account.json`

### Issue: "Google Meet link not found in calendar event"

**Solution**:
1. Verify Google Calendar API is enabled in Cloud Console
2. Check service account has calendar permissions
3. Verify calendar sharing is set to "Make changes to events"

### Issue: "Module 'google' not found"

**Solution**:
```bash
pip install -r requirements.txt
# Or manually:
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Issue: Falling back to Method 1 (SHA256)

**Check logs**:
```bash
python manage.py shell

from main.models import Session
session = Session.objects.first()
session.generate_meeting_link()
# Check console output for error messages
```

---

## Verification Checklist

- [ ] Google Cloud Project created
- [ ] Google Calendar API enabled
- [ ] Service Account created
- [ ] JSON credentials downloaded
- [ ] JSON file placed safely
- [ ] `settings.py` updated with file path
- [ ] Google packages installed
- [ ] Calendar shared with service account
- [ ] Test shows "✅ Using Google Calendar API"
- [ ] Generated link works in browser
- [ ] Full integration test passes

---

## What Happens Behind the Scenes

### When Session is Confirmed:

```
1. Django calls: session.generate_meeting_link()
2. This calls: GoogleMeetHelper.generate_meet_link_with_calendar()
3. Which:
   - Gets service account credentials from JSON file
   - Builds Google Calendar API client
   - Creates calendar event with video conference
   - Event details:
     - Title: "Mentoring Session: [Mentor] & [Mentee]"
     - Attendees: Mentor + Mentee
     - Time: Session date/time
     - Duration: Session duration
     - Conference: Google Meet (auto-generated)
   - Google Calendar creates Google Meet room
   - Extracts the Meet link: https://meet.google.com/xyz-abcd-efg
   - Saves link to database
   - Sends calendar invitations
4. Link is displayed on dashboards
5. Link is sent via email
```

---

## Advanced Configuration

### Use Custom Calendar

```python
# In settings.py
GOOGLE_CALENDAR_ID = 'your-calendar@gmail.com'
```

Get your calendar ID from Google Calendar:
1. Go to Calendar Settings → "Integrate calendar"
2. Copy the "Calendar ID"

### Adjust Time Buffer

```python
# Create event 30 minutes before session
GOOGLE_MEET_TIME_BUFFER = 30
```

### Disable Feature (Fallback to Method 1)

```python
# In settings.py
GOOGLE_CALENDAR_API_ENABLED = False
```

Or via environment:
```bash
export GOOGLE_CALENDAR_API_ENABLED=False
```

---

## Security Best Practices

✅ **DO**:
- Store JSON file outside of git repository
- Use environment variables in production
- Add `service_account.json` to `.gitignore`
- Use different service accounts for dev/prod
- Rotate credentials periodically
- Set restrictive file permissions: `chmod 600`

❌ **DON'T**:
- Commit `service_account.json` to git
- Share credentials with others
- Use same credentials across environments
- Leave JSON files in temporary folders
- Hardcode file path in code

---

## Deployment

### Development
```bash
# Put JSON file in project folder
cp downloaded_file.json mentorhub/service_account.json
```

### Production
```bash
# Use environment variable pointing to secure location
export GOOGLE_SERVICE_ACCOUNT_FILE=/secure/path/service_account.json
```

### Docker
```dockerfile
# In Dockerfile
ENV GOOGLE_SERVICE_ACCOUNT_FILE=/run/secrets/service_account.json

# Use Docker secrets to mount the file
```

---

## Monitoring

### Check if Google Calendar API is Being Used

```bash
# Look at application logs
tail -f logs/application.log

# Should show:
# ✅ Using Google Calendar API - Meeting link: https://meet.google.com/xyz-abcd-efg
```

### Check Google Calendar

Visit [Google Calendar](https://calendar.google.com/) and look for:
- CodeMentorHub sessions as calendar events
- Google Meet links in event details
- Attendees (mentor and mentee)

---

## Fallback System

If anything fails:

1. Google Calendar API unavailable? → Fallback to Method 1 (SHA256)
2. Credentials missing? → Fallback to Method 1
3. API quota exceeded? → Fallback to Method 1

**The system always generates a working link!** ✅

---

## Support & Help

- **Setup Issues?** Check the "Troubleshooting" section
- **Google Cloud Help?** Visit [Google Cloud Documentation](https://cloud.google.com/docs)
- **Still stuck?** Check application logs for error messages

---

## FAQ

**Q: Can I use my personal Google account?**
A: No, must use service account. Personal accounts require OAuth consent screen setup.

**Q: Will mentors and mentees get calendar invitations?**
A: Yes, they'll receive Google Calendar invitations automatically.

**Q: Can I change which calendar the events go to?**
A: Yes, set `GOOGLE_CALENDAR_ID` in settings.

**Q: What if I don't setup Google Calendar API?**
A: It will automatically fall back to Method 1 (SHA256 links still work).

**Q: Can I have multiple calendars?**
A: Yes, set different calendar IDs in settings.

**Q: How do I know if it's working?**
A: Check the console output for "✅ Using Google Calendar API" message.

---

## Summary

✅ **Setup Time**: 15-30 minutes  
✅ **Complexity**: Medium  
✅ **Reliability**: Very High  
✅ **User Experience**: Professional  
✅ **Cost**: Free (Google Cloud free tier covers this)  

You're now ready to use Method 2 (Google Calendar API) for professional Google Meet integration! 🎉

---

**Last Updated**: November 14, 2025  
**Status**: Ready for Setup  
**Version**: 2.0 - Method 2 Primary
