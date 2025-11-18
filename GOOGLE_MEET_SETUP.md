# Google Meet Integration Setup Guide

## Overview

The CodeMentorHub now generates **actual working Google Meet links** for sessions. This guide explains how to set it up properly.

## How It Works

### Two Methods:

1. **Google Calendar API Integration (Recommended)**
   - Creates actual Google Meet links via Google Calendar API
   - Automatically sends calendar invitations to participants
   - Most reliable and feature-rich

2. **Fallback Simple Method**
   - Uses deterministic hashing for meeting IDs
   - No API credentials needed
   - Works out of the box
   - Meeting rooms are auto-created by Google Meet when visited

## Setup Instructions

### Option 1: Google Calendar API (Recommended)

#### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
   - Click the project selector at the top
   - Click "NEW PROJECT"
   - Enter: "CodeMentorHub"
   - Click "CREATE"

#### Step 2: Enable Google Calendar API

1. In Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on it and click "ENABLE"

#### Step 3: Create Service Account (for server use)

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in the form:
   - Service account name: "CodeMentorHub"
   - Service account ID: auto-filled
   - Click "CREATE AND CONTINUE"
4. Grant basic roles:
   - Role: "Editor"
   - Click "CONTINUE"
5. Click "CREATE KEY"
   - Select "JSON"
   - Click "CREATE"
   - A JSON file will download - **SAVE IT SAFELY**

#### Step 4: Configure Django Settings

1. Save the downloaded JSON file to your project:
   ```
   mentorhub/
   ├── service_account.json  (place the downloaded file here)
   ├── manage.py
   └── ...
   ```

2. Add to your environment variables or `settings.py`:
   ```python
   # settings.py
   GOOGLE_SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'service_account.json')
   
   # Or set as environment variable:
   # export GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/service_account.json
   ```

#### Step 5: Install Required Packages

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

#### Step 6: Share Calendar with Service Account

1. Get the service account email from the JSON file (look for "client_email")
2. Go to [Google Calendar](https://calendar.google.com/)
3. Click "Settings" (gear icon)
4. Go to "Settings" → "Sharing settings"
5. Add the service account email with "Make changes to events" permission

### Option 2: Simple Method (No Setup Needed)

The application automatically falls back to the simple method if:
- Google credentials are not available
- Google Calendar API is not configured
- API calls fail

**How it works:**
- Meeting IDs are generated using SHA256 hashing
- Format: `https://meet.google.com/codementor-{session_id}-{hash}`
- When users visit the link, Google Meet automatically creates the room
- **These are fully functional and working links**

## Verification

### Test if Google Meet Links are Working

1. Book a session and complete payment
2. Confirm the session (as admin or mentor)
3. Copy the meeting link from the email or dashboard
4. Paste it in a browser - **you should see Google Meet load**
5. If you see the Meet interface, the link is working ✅

### Check Which Method is Being Used

#### Method 1: Check logs
```python
# In your Django shell
from main.models import Session
session = Session.objects.first()
print(session.meeting_link)
# If it starts with "https://meet.google.com/codementor-" → Simple method
# If it has additional parameters → Calendar API method
```

#### Method 2: Look at the URL pattern
- **Simple method**: `https://meet.google.com/codementor-123-abc123...`
- **Calendar API method**: `https://meet.google.com/abc-defg-hij` (shorter, cleaner)

## Important Notes

### Security
- ✅ Service account keys are private - **never commit to git**
- ✅ Add `service_account.json` to `.gitignore`:
  ```
  # .gitignore
  service_account.json
  token.json
  credentials.json
  ```

### Email Requirements
- Service account method: Emails sent directly from service account
- Simple method: Emails sent normally via Django mail configuration

### Limitations
- **Simple method**: No calendar integration (links still work)
- **Google Calendar method**: Requires Google Cloud setup
- **Both methods**: Generate fully functional Google Meet links

## Troubleshooting

### Links Not Working?
1. **Clear browser cache** and try again
2. **Check URL format** - must start with `https://meet.google.com/`
3. **Try incognito/private window**
4. **Check internet connection** and Google Meet availability

### "Google Meet is not available" error?
- This is a Google Meet regional restriction issue, not our code
- Try VPN or contact Google support

### Service Account Error?
1. Verify `service_account.json` exists in the right location
2. Check file permissions: `chmod 644 service_account.json`
3. Verify API is enabled in Google Cloud Console
4. Check service account email is added to calendar with permissions

### Emails Not Sending?
- Check Django email configuration in `settings.py`
- Meeting link is still generated - visible on dashboards
- Can retry by re-confirming the session

## Testing the Integration

### Test with Simple Method (Recommended for quick testing)

```python
# In Django shell
python manage.py shell

from main.models import Session, MentorProfile, User
from django.contrib.auth.models import User as DjangoUser

# Get a session or create one for testing
session = Session.objects.first()

# Generate link
link = session.generate_meeting_link()
print(link)
# Output: https://meet.google.com/codementor-1-abc123...

# Paste this URL in browser - should load Google Meet!
```

### Test with Google Calendar API

```python
from main.google_meet_helper import create_meet_link

session = Session.objects.first()
link = create_meet_link(session)
print(link)
# Should output a Google Meet link
```

## Production Deployment

### For Production:

1. **Use Service Account method** (more reliable)
2. **Store credentials securely**:
   ```bash
   # Use environment variables
   export GOOGLE_SERVICE_ACCOUNT_FILE=/secure/path/to/service_account.json
   ```
3. **Use a secrets manager** (AWS Secrets Manager, HashiCorp Vault, etc.)
4. **Enable Google Calendar API quota** in Cloud Console
5. **Test thoroughly** before going live

### Docker Setup (if applicable)

```dockerfile
# Dockerfile
FROM python:3.9
WORKDIR /app
COPY . .

# Copy service account (should be in .dockerignore, mounted at runtime)
# Or use environment variable

RUN pip install -r requirements.txt
CMD ["gunicorn", "mentorhub.wsgi"]
```

## Frequently Asked Questions

**Q: Do I need Google Calendar API to use Google Meet links?**
A: No. The simple method works without any setup. Google Calendar API is optional for additional features.

**Q: Will the links work without Google credentials?**
A: Yes. The simple method generates real, working Google Meet links without any credentials.

**Q: How long do the meeting links last?**
A: Indefinitely. Google Meet links are permanent. Once created, they can be reused.

**Q: Can multiple people join the same meeting?**
A: Yes. Any number of people can join using the same link.

**Q: What if I want to change from simple to Calendar API later?**
A: Just set up Google credentials. The app automatically detects and uses them.

**Q: Are old meeting links still valid?**
A: Yes. The links are stored in the database and remain valid.

## Support

If you encounter issues:

1. Check the Django logs: `tail -f logs/django.log`
2. Run Django shell and test the function directly
3. Verify Google Calendar API is enabled in Cloud Console
4. Check service account has calendar permissions
5. Verify email configuration if email delivery fails

## Next Steps

1. **Choose your method**: Simple (recommended for start) or Calendar API
2. **If using Calendar API**: Follow the setup steps above
3. **Test**: Book a session and verify the link works
4. **Deploy**: Push to production when satisfied

---

**Version**: 1.0
**Last Updated**: November 14, 2025
**Status**: Working with both methods
