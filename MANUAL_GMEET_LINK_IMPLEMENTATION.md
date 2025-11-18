# Manual Google Meet Link Implementation

## Overview
The system has been updated to allow admins to manually provide Google Meet links instead of automatically generating them. When an admin confirms a session, they can paste a Google Meet link which is then sent to both the mentor and mentee via email, and displayed in their respective dashboards.

## Changes Made

### 1. **Database Model Changes** (`main/models.py`)

Added two new fields to the `Session` model:

```python
# Admin-provided meeting link (manual)
admin_provided_link = models.URLField(blank=True, null=True, help_text="Link provided by admin when confirming session")
link_provided_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp when admin provided the link")
```

Added a new property to the `Session` model:

```python
@property
def get_meeting_link(self):
    """Return admin-provided link if available, otherwise return auto-generated link"""
    return self.admin_provided_link or self.meeting_link
```

**Migration Applied**: `0008_session_admin_provided_link_session_link_provided_at_and_more.py`

### 2. **Admin Dashboard Template** (`templates/admin/sessions.html`)

#### Updated Features:

- **Replaced Confirm Button**: The "Confirm" button now opens a modal dialog instead of directly confirming the session.

- **Modal Dialog**: Added a modal with:
  - URL input field for pasting Google Meet link
  - Cancel and Confirm buttons
  - Proper form handling with CSRF token

- **Updated Meeting Link Display**: Changed to use `session.get_meeting_link` to show either admin-provided or auto-generated links

#### Key Changes:
```html
<!-- Replaced direct confirm button with modal trigger -->
<button type="button" class="action-btn btn-confirm" onclick="openMeetingLinkModal({{ session.id }})">
    ◇ Confirm with Link
</button>
```

### 3. **Admin View Logic** (`main/views.py`)

Updated the `admin_session_set_status()` function to:

- **Accept Meeting Link**: Captures the `meeting_link` POST parameter
- **Store Admin-Provided Link**: When confirming a session with a link:
  ```python
  if session.status == 'confirmed' and meeting_link:
      session.admin_provided_link = meeting_link
      session.link_provided_at = timezone.now()
  ```

- **Fallback to Auto-Generation**: If no link is provided, the system falls back to auto-generating a link (existing behavior)

- **Updated Email Notifications**: Modified email templates to use the new property:
  ```python
  display_link = session.get_meeting_link
  ```

### 4. **User Dashboards** (`templates/dashboard/`)

#### Mentee Dashboard (`mentee_dashboard.html`):
- Updated to display meeting link using `session.get_meeting_link`
- Shows the meeting link and "Join Google Meet" button when session is confirmed

#### Mentor Session Detail (`mentor_session_detail.html`):
- Updated to display meeting link using `session.get_meeting_link`

## Workflow

### Admin Perspective:
1. Admin navigates to **Admin Dashboard → Sessions**
2. For a pending session, clicks the **"Confirm with Link"** button
3. A modal dialog appears with an input field
4. Admin pastes the Google Meet link (e.g., `https://meet.google.com/abc-defg-hij`)
5. Clicks **"Confirm & Send Link"**
6. System:
   - Saves the link to `admin_provided_link` field
   - Updates session status to "confirmed"
   - Sends confirmation emails to both mentor and mentee with the meeting link

### Mentee Perspective:
1. After admin confirms the session, mentee receives an email with:
   - Session details (date, time, duration)
   - Google Meet link
2. Mentee can view the confirmed session in **"My Sessions"** dashboard
3. A highlighted section displays:
   - "📹 Meeting Link Available"
   - A blue button: "Join Google Meet" (linked to the meeting)
   - The full meeting link URL

### Mentor Perspective:
1. After admin confirms the session, mentor receives an email with:
   - Session details (date, time, duration)
   - Google Meet link
2. Mentor can view the confirmed session in **Mentor Dashboard**
3. Session detail page displays the meeting link

## Key Features

✅ **Manual Link Input**: Admin can paste any Google Meet link before confirming
✅ **Email Notifications**: Both mentor and mentee receive confirmation emails with the link
✅ **Dashboard Display**: Meeting links are prominently displayed in both dashboards
✅ **Fallback Support**: If no link is provided, auto-generation still works
✅ **User-Friendly Modal**: Clean, simple interface for link submission
✅ **Timestamp Tracking**: System tracks when the link was provided

## Technical Details

### Database Fields:
- `admin_provided_link` (URLField): Stores the manually provided Google Meet link
- `link_provided_at` (DateTimeField): Tracks when the link was provided

### Property:
- `get_meeting_link`: Returns the admin-provided link if available, otherwise the auto-generated link

### Email Template:
Both mentor and mentee receive emails that include:
```
Meeting Link: [link displayed here]
```

## Testing Checklist

- [ ] Create a pending session in admin panel
- [ ] Click "Confirm with Link" button
- [ ] Modal appears with input field
- [ ] Paste a valid Google Meet link
- [ ] Click "Confirm & Send Link"
- [ ] Session status changes to "confirmed"
- [ ] Check emails received by mentor and mentee
- [ ] Verify meeting link appears in mentee dashboard
- [ ] Verify meeting link appears in mentor session detail
- [ ] Test fallback: confirm without providing link (should auto-generate if enabled)

## Backward Compatibility

✅ The implementation maintains backward compatibility:
- Old sessions with `meeting_link` still work
- Auto-generation still works as a fallback
- No breaking changes to existing functionality
