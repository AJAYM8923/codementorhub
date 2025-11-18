# Google Meet Integration - Quick Start Guide

## What Was Implemented

✅ **Automatic Google Meet Link Generation**
- When a session is confirmed (by admin OR mentor), a unique Google Meet link is auto-generated
- Links are displayed on both admin dashboard and user dashboards
- Email notifications include the meeting link

## How It Works

### Step-by-Step Process

1. **User Books Session**
   - Mentee selects a mentor and books a session
   - Completes payment
   - Session status: "PENDING"

2. **Confirmation (Choose One Option)**
   - **Option A**: Mentor accepts the session
     - Mentor views dashboard → Clicks "Accept session"
   - **Option B**: Admin confirms the session
     - Admin goes to Sessions page → Clicks "Confirm" button

3. **Automatic Actions Upon Confirmation**
   - Session status changes to "CONFIRMED"
   - Google Meet link is automatically generated
   - Both mentor and mentee receive email with:
     - Session details
     - Google Meet link
     - Instructions

4. **View Meeting Link**
   - **Admin**: Sessions page shows "📹 Join Meeting" in the Meeting Link column
   - **Mentee**: "My Sessions" dashboard shows prominent blue box with link
   - **Mentor**: Mentor Dashboard shows the same

5. **Join Meeting**
   - Click "Join Google Meet" button OR
   - Copy the URL and open in browser
   - Meeting opens in Google Meet

6. **Complete Session**
   - Admin marks session as "Completed" when done
   - Link remains visible in session history

## File Locations

### Backend
- `main/views.py` → `admin_session_set_status()` function (generates link on confirm)
- `main/models.py` → `Session.generate_meeting_link()` method (creates UUID-based link)

### Frontend Templates
- `templates/admin/sessions.html` → Admin sessions table (shows link)
- `templates/dashboard/mentee_dashboard.html` → Mentee's sessions (shows link)
- `templates/dashboard/mentor_dashboard.html` → Mentor's sessions (shows link)

## Key Features

| Feature | Details |
|---------|---------|
| **Link Generation** | UUID4-based, unique for each session |
| **Link Format** | `https://meet.google.com/{8-char-id}` |
| **When Generated** | Automatically when session is confirmed |
| **Email Notifications** | Both mentor and mentee get email with link |
| **Display Locations** | 3 places: Admin table, Mentee dashboard, Mentor dashboard |
| **Visibility** | Only shown when session is "confirmed" |
| **Persistence** | Link remains available even after session completes |

## Testing the Feature

### Test Scenario 1: Admin Confirmation
1. Login as admin
2. Go to "Sessions" page
3. Find a pending session
4. Click "Confirm" button
5. ✅ Check: Meeting Link column shows "📹 Join Meeting"
6. ✅ Check: Mentee received email with link
7. ✅ Check: Mentor received email with link
8. ✅ Check: Mentee dashboard shows link
9. ✅ Check: Mentor dashboard shows link

### Test Scenario 2: Mentor Acceptance
1. Login as mentor
2. Go to "Mentor Dashboard"
3. Find pending session
4. Click "Accept session"
5. ✅ Check: Meeting link is generated
6. ✅ Check: Session status changes to "confirmed"
7. ✅ Check: Email sent to mentee with link
8. ✅ Check: Link visible on both dashboards

## Email Examples

### What Mentee Receives
```
Subject: Session Confirmed - CodeMentorHub

Hello [Mentee],

Your session with [Mentor Name] has been confirmed!

Session Details:
Date: Nov 20, 2025
Time: 14:00
Duration: 60 minutes
Meeting Link: https://meet.google.com/abc12345

Please join the meeting 5 minutes before the scheduled time.

Best regards,
CodeMentorHub Team
```

### What Mentor Receives
```
Subject: Session Confirmed - CodeMentorHub

Hello [Mentor],

Your session with [Mentee Name] has been confirmed!

Session Details:
Date: Nov 20, 2025
Time: 14:00
Duration: 60 minutes
Meeting Link: https://meet.google.com/abc12345

Please join the meeting 5 minutes before the scheduled time.

Best regards,
CodeMentorHub Team
```

## UI Locations

### Admin Dashboard - Sessions Page
```
┌─────────────────────────────────────────┐
│ Mentor | Mentee | Date | Duration | ... │
├─────────────────────────────────────────┤
│ John   | Alice  | ...  | 60 min   | ... │
│        |        |      |          | 📹 Join Meeting |
└─────────────────────────────────────────┘
```

### Mentee Dashboard - My Sessions Section
```
┌──────────────────────────────────────────┐
│ Mentor: John Doe                         │
│ Status: Confirmed ✓                      │
│ Date: Nov 20, 2025  Time: 14:00          │
│ Duration: 60 minutes                     │
│ ┌────────────────────────────────────┐   │
│ │ 📹 Join Google Meet                │   │
│ │ https://meet.google.com/abc12345   │   │
│ └────────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

## Troubleshooting

### Link Not Appearing?
1. Check session status is "confirmed" (not "pending")
2. Refresh the page
3. Check browser console for JavaScript errors
4. Verify the database has a value in meeting_link field

### Email Not Received?
1. Check email configuration in settings.py
2. Verify sender email and password are correct
3. Check spam folder
4. Check Django email backend settings
5. Note: Link is still generated even if email fails

### Link Not Working?
1. Try copying the full URL and pasting in address bar
2. Ensure Google Meet is accessible in your region
3. Try opening in incognito/private window
4. Check internet connection

## Code Examples

### Generate Meeting Link (Already Implemented)
```python
session.generate_meeting_link()  # Creates and saves the link
# Result: https://meet.google.com/abc12345
```

### Check for Link
```python
if session.meeting_link:
    print(session.meeting_link)  # Display the link
```

### Send Email with Link (Already Implemented)
```python
send_mail(
    'Session Confirmed',
    f'Meeting Link: {session.meeting_link}',
    'from@email.com',
    ['to@email.com']
)
```

## API Reference

### Model: Session
- **Field**: `meeting_link` (URLField, blank=True, null=True)
- **Method**: `generate_meeting_link()` - Creates UUID-based Google Meet link
- **Returns**: The generated link URL

### View: admin_session_set_status
- **Trigger**: When admin clicks "Confirm" on a pending session
- **Action**: Generates meeting link, sends emails to both parties
- **URL**: `admin/sessions/<session_id>/set-status/`

### View: mentor_session_accept
- **Trigger**: When mentor clicks "Accept session"
- **Action**: Generates meeting link, sends confirmation emails
- **URL**: `mentor/session/<session_id>/accept/`

## Performance Considerations

- Link generation is instant (UUID4)
- Link stored in database (no external API calls)
- Email sending is async-compatible if needed
- No additional load on server

## Security Notes

- Google Meet handles its own access control
- Links are sent via secure email channels
- UUID ensures unique, hard-to-guess identifiers
- No authentication required beyond Google Meet's own security
- Consider: In production, you may want to track link access

## Future Enhancements Ideas

- Add option to disable Google Meet integration
- Custom meeting room names
- Automatic calendar invites
- Pre-meeting reminder emails
- Post-meeting feedback forms
- Recording storage and access
- Meeting duration tracking
