import flask
from werkzeug.contrib.cache import SimpleCache
from googleapiclient.discovery import build
from sheets_manager import SheetsManager
from config_handler import ConfigHandler

cache = SimpleCache()
config = ConfigHandler()
mgr = SheetsManager()

app = flask.Flask(__name__)
app.secret_key = config.get('secret_key')


@app.route("/")
def homepage():
    return 'This page intentionally left blank'


@app.route("/login")
def redir_to_auth():
    return mgr.auth('/')


@app.route("/got_sheets")
def save_api_key():
    return mgr.api_callback('/')


@app.route("/list")
def list_sheets():
    credentials = mgr.get_session_credentials()
    sheets = build('sheets', 'v4', credentials=credentials)
    sheetid = config.get('sheetid')
    cellrange = config.get('range')
    result = sheets.spreadsheets().values().get(
             spreadsheetId=sheetid,
             range=cellrange).execute()
    values = result.get('values', [])
    return str(values)


app.run('localhost', 5000)
