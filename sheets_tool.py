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
    if not mgr.is_authed():
        return flask.redirect(flask.url_for('redir_to_auth'))
    return 'This page intentionally left blank'


@app.route("/login")
def redir_to_auth():
    mgr.callback_url = flask.url_for('save_api_key', _external=True)
    return mgr.auth('/')


@app.route("/got_sheets")
def save_api_key():
    return mgr.api_callback('/')


@app.route("/list/<int:rowid>")
def list_sheets(rowid):
    sheets = mgr.get_api()
    sheetid = config.get('sheetid')
    cellrange = config.get('range')
    sheet = config.get('sheet')
    cellrange = "{}!A{}:U{}".format(sheet, rowid, rowid)
    result = sheets.spreadsheets().values().get(
             spreadsheetId=sheetid,
             range=cellrange).execute()
    values = result.get('values', [])[0]

    return flask.render_template("spreadsheet.html", 
            title=values[0],
            url=values[1])


@app.route("/set_values")
def set_sheet_values():
    sheets = mgr.get_api()
    return 'abc'


app.run('localhost', 5000)
