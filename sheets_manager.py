import flask
import json
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class SheetsManager:
    """
    Manages talking to the Google Sheets API and the necessary keys

    This class incorporates a fair amount of code from the Google dev docs
    for the Google Sheets API
        """
    def __init__(self):
        self.token_file = 'token.json'
        self.session_key = 'credentials'
        self.state_key = 'state'
        self.client_secret = 'client_id.json'
        self.callback_url = None

    def auth(self, redir_to):
        try:
            with open(self.token_file) as token_store:
                token = json.load(token_store)
                flask.session[self.session_key] = token
        except FileNotFoundError:
            flow = Flow.from_client_secrets_file(self.client_secret, SCOPES)
            flow.redirect_uri = self.callback_url

            authorization_url, state = flow.authorization_url(
                    access_type='offline',
                    include_granted_scopes='true')

            flask.session[self.state_key] = state
            return flask.redirect(authorization_url)
        return flask.redirect(redir_to)

    def is_authed(self):
        return self.session_key in flask.session

    def credentials_to_dict(credentials):
        """
        Convert a Credentials object to a Dict

        This seems to be the official standard shape of this data.
        Taken directly from
        https://developers.google.com/api-client-library/python/auth/web-app
        """
        return {'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes}

    def api_callback(self, redir):
        state = flask.session[self.state_key]
        flow = Flow.from_client_secrets_file(self.client_secret,
                                             SCOPES, state=state)
        flow.redirect_uri = self.callback_url
        flow.fetch_token(authorization_response=flask.request.url)
        token = SheetsManager.credentials_to_dict(flow.credentials)
        flask.session[self.session_key] = token
        with open(self.token_file, 'w') as token_store:
            json.dump(token, token_store)
        return flask.redirect(redir)

    def get_session_credentials(self):
        credentials = flask.session[self.session_key]
        return Credentials.from_authorized_user_info(credentials)

    def get_api(self):
        credentials = self.get_session_credentials()
        sheets = build('sheets', 'v4', credentials=credentials)
        return sheets
