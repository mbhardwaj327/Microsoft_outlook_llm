from decouple import config as env
import requests
import logging
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:
    from pytz import timezone as ZoneInfo  # Fallback for older versions
from datetime import datetime, timedelta
    

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MicrosoftGraphAPI:
    """
    A class to interact with Microsoft Graph API for managing calendar events.
    """

    def __init__(self):
        """
        Initializes the MicrosoftGraphAPI class with client credentials and sets up API endpoints.

        :param client_id: Client ID for Microsoft Graph API
        :param client_secret: Client Secret for Microsoft Graph API
        :param redirect_uri: Redirect URI for OAuth flow
        """
        self.client_id = env('Microsoft_CientID')
        self.client_secret = env('Microsoft_SecretValue')
        self.redirect_uri = env('Microsoft_REDIRECT_URI')
        self.user_profile_url = 'https://graph.microsoft.com/v1.0/me'
        self.base_url = 'https://graph.microsoft.com/v1.0/me/events'
        self.token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        self.calendar_view_url = 'https://graph.microsoft.com/v1.0/me/calendarview'
        
    def get_user_details(self, access_token):
        # Headers for the Graph API request including the access token
        graph_headers = {
            'Authorization': f'Bearer {access_token}'
        }
        return self._send_request('get', self.user_profile_url, graph_headers)

    def generate_access_token(self, code):
        """
        Generates an access token using an authorization code from OAuth flow.

        :param code: Authorization code
        :return: JSON response containing access token
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'client_id': self.client_id,
            'scope': 'User.Read Calendars.Read',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code',
            'client_secret': self.client_secret
        }
        return self._send_request('post', self.token_url, headers, data)

    def refresh_access_token(self, refresh_token):
        """
        Refreshes the access token using a refresh token.

        :param refresh_token: Refresh token
        :return: JSON response containing new access token
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'client_id': self.client_id,
            'scope': 'User.Read Calendars.Read',
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
            'client_secret': self.client_secret
        }
        # Send the POST request
        response = requests.post(self.token_url, headers=headers, data=data)
        return response.json() if response.text else None

    def get_all_calendar_events(self, refresh_token):
        """
        Retrieves all calendar events for the authenticated user.

        :param access_token: Access token
        :return: JSON response containing calendar events
        """
        response = self.refresh_access_token(refresh_token)
        if response:
            access_token = response['access_token']
            headers = {"Authorization": f"Bearer {access_token}"}
            return self._send_request('get', self.base_url, headers)
        return None
    
    def create_calendar_event(self, access_token, event_data):
        """
        Creates a new calendar event.
        :param access_token: Access token
        :param event_data: Dictionary containing details of the event to be created
        :return: JSON response of the newly created event
        """
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        return self._send_request('post', self.base_url, headers, event_data)

    def update_calendar_event(self, event_id, access_token, update_data):
        """
        Updates a specific calendar event.

        :param event_id: Event ID of the calendar event to update
        :param access_token: Access token
        :param update_data: Dictionary containing update fields for the event
        :return: JSON response of the updated event
        """
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        url = f"{self.base_url}/{event_id}"
        return self._send_request('patch', url, headers, update_data)

    def delete_calendar_event(self, event_id, access_token):
        """
        Deletes a specific calendar event.

        :param event_id: Event ID of the calendar event to delete
        :param access_token: Access token
        :return: None on success, logs error if failed
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{self.base_url}/{event_id}"
        return self._send_request('delete', url, headers)

    def _send_request(self, method, url, headers, data=None):
        """
        Sends a request to the Microsoft Graph API and handles errors.

        :param method: HTTP method ('get', 'post', 'patch', 'delete')
        :param url: URL for the request
        :param headers: Headers to include in the request
        :param data: Data to send in the request, if any (for 'post' and 'patch')
        :return: JSON response data or None if an error occurs
        """
        try:
            if method in ['get', 'delete']:
                response = requests.request(method, url, headers=headers)
            else:  # 'post' or 'patch'
                response = requests.request(method, url, headers=headers, json=data)
            response.raise_for_status()
            return response.json() if response.text else None
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}, Status Code: {response.status_code}, Response: {response.text}")
            return None
        
    def get_todays_calendar_events(self, refresh_token):
        """
        Retrieves today's calendar events for the authenticated user in the Eastern Standard Time (EST).

        :param refresh_token: Refresh token to get access token
        :return: List of events happening today
        """
        # Refresh access token
        response = self.refresh_access_token(refresh_token)
        if not response:
            return None

        access_token = response.get('access_token')
        if not access_token:
            return None

        # Define EST timezone
        est_tz = ZoneInfo('America/New_York')
        # Get the current date in EST
        now_est = datetime.now(est_tz)
        today_start = datetime(now_est.year, now_est.month, now_est.day, 0, 0, 0, tzinfo=est_tz)
        today_end = today_start + timedelta(days=1)

        # Convert start and end times to ISO 8601 format
        start_datetime = today_start.isoformat()
        end_datetime = today_end.isoformat()

        # Build the request URL with start and end times
        url = f"{self.calendar_view_url}?startDateTime={start_datetime}&endDateTime={end_datetime}"

        # Set the headers, including the authorization and timezone
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Prefer": 'outlook.timezone="Central European Standard Time"'
        }
        # Send the request to fetch events
        events_response = self._send_request('get', url, headers)
        if not events_response:
            return None

        events = events_response.get('value', [])
        return events
