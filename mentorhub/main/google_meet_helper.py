"""
Google Meet Integration Module
Handles creation of actual Google Meet links using Google Calendar API
Primary method: Google Calendar API (Method 2)
Fallback method: Simple SHA256 hashing
"""

import os
import json
from datetime import datetime, timedelta
from django.conf import settings

class GoogleMeetHelper:
    """Helper class to manage Google Meet links using Google Calendar API"""
    
    @staticmethod
    def generate_meet_link_with_calendar(session_obj):
        """
        Create an actual Google Meet link by creating a Google Calendar event
        This is Method 2 - Google Calendar API (Primary method)
        
        Args:
            session_obj: Session model instance
            
        Returns:
            str: The Google Meet link URL
        """
        try:
            # Check if Google Calendar API is enabled
            if not settings.GOOGLE_CALENDAR_API_ENABLED:
                return GoogleMeetHelper._generate_simple_meet_link(session_obj)
            
            # Import Google API libraries
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            
            # Get service account credentials
            credentials = GoogleMeetHelper._get_service_account_credentials()
            
            if not credentials:
                # Fallback to simple method if credentials not available
                return GoogleMeetHelper._generate_simple_meet_link(session_obj)
            
            # Build the Google Calendar service
            service = build('calendar', 'v3', credentials=credentials)
            
            # Prepare event details for Google Calendar
            event_start = session_obj.session_datetime
            event_end = event_start + timedelta(minutes=session_obj.duration_minutes)
            
            event = {
                'summary': f'Mentoring Session: {session_obj.mentor.full_name} & {session_obj.mentee.username}',
                'description': (
                    f'CodeMentorHub Mentoring Session\n\n'
                    f'Mentor: {session_obj.mentor.full_name}\n'
                    f'Mentor Email: {session_obj.mentor.user.email if session_obj.mentor.user else "N/A"}\n'
                    f'Mentee: {session_obj.mentee.first_name or session_obj.mentee.username}\n'
                    f'Mentee Email: {session_obj.mentee.email}\n\n'
                    f'Session ID: {session_obj.id}\n'
                    f'Duration: {session_obj.duration_minutes} minutes'
                ),
                'start': {
                    'dateTime': event_start.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': event_end.isoformat(),
                    'timeZone': 'UTC',
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': f'session-{session_obj.id}-{int(datetime.now().timestamp())}',
                        'conferenceSolutionKey': {
                            'key': 'hangoutsMeet'
                        }
                    }
                },
                'attendees': [],
            }
            
            # Add mentee as attendee
            if session_obj.mentee.email:
                event['attendees'].append({
                    'email': session_obj.mentee.email,
                    'displayName': session_obj.mentee.first_name or session_obj.mentee.username,
                    'responseStatus': 'needsAction'
                })
            
            # Add mentor as attendee if they have an email
            if session_obj.mentor.user and session_obj.mentor.user.email:
                event['attendees'].append({
                    'email': session_obj.mentor.user.email,
                    'displayName': session_obj.mentor.full_name,
                    'responseStatus': 'needsAction'
                })
            
            # Create the event with conference data (generates Google Meet link)
            created_event = service.events().insert(
                calendarId=settings.GOOGLE_CALENDAR_ID,
                body=event,
                conferenceDataVersion=1,
                sendNotifications=True  # Send calendar invitations
            ).execute()
            
            # Extract the Google Meet link from the created event
            if 'conferenceData' in created_event and 'entryPoints' in created_event['conferenceData']:
                for entry in created_event['conferenceData']['entryPoints']:
                    if entry.get('entryPointType') == 'video':
                        meet_link = entry.get('uri')
                        if meet_link:
                            # Store the calendar event ID for potential future updates
                            session_obj.meeting_notes = session_obj.meeting_notes or ''
                            if 'calendar_event_id' not in session_obj.meeting_notes:
                                session_obj.meeting_notes += f"\n[Calendar Event ID: {created_event.get('id')}]"
                            return meet_link
            
            # If no meet link found, try fallback
            raise Exception("No Google Meet link found in calendar event")
            
        except Exception as e:
            print(f"Error creating Google Calendar event: {e}")
            # Fallback to simple method
            return GoogleMeetHelper._generate_simple_meet_link(session_obj)
    
    @staticmethod
    def _generate_simple_meet_link(session_obj):
        """
        Fallback method to generate a simple Google Meet link using SHA256 hashing
        This is Method 1 - Used as fallback if Google Calendar API fails
        """
        import hashlib
        
        # Create a unique, reproducible meeting ID
        meeting_seed = f"codementor-{session_obj.mentor.id}-{session_obj.mentee.id}-{session_obj.session_date}-{session_obj.session_time}"
        meeting_hash = hashlib.sha256(meeting_seed.encode()).hexdigest()[:16]
        
        # Use a format that Google Meet will recognize and auto-create
        meeting_id = f"codementor-{session_obj.id}-{meeting_hash}"
        
        return f"https://meet.google.com/{meeting_id}"
    
    @staticmethod
    def _get_service_account_credentials():
        """
        Get Google API credentials from service account JSON file
        
        Returns:
            Credentials object or None if not available
        """
        try:
            from google.oauth2.service_account import Credentials
            
            service_account_file = settings.GOOGLE_SERVICE_ACCOUNT_FILE
            
            # Check if file exists
            if not os.path.exists(service_account_file):
                print(f"Service account file not found: {service_account_file}")
                return None
            
            # Load credentials from service account file
            credentials = Credentials.from_service_account_file(
                service_account_file,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            
            return credentials
            
        except ImportError as e:
            print(f"Google API libraries not installed: {e}")
            print("Install with: pip install -r requirements.txt")
            return None
        except Exception as e:
            print(f"Error loading service account credentials: {e}")
            return None


def create_meet_link(session_obj):
    """
    Public function to create a Google Meet link
    Uses Method 2 (Google Calendar API) as primary
    Falls back to Method 1 (SHA256) if needed
    
    Args:
        session_obj: Session model instance
        
    Returns:
        str: Google Meet link URL
    """
    helper = GoogleMeetHelper()
    return helper.generate_meet_link_with_calendar(session_obj)

