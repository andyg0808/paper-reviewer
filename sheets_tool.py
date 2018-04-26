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


def get_available_values(typeid):
    sheets = mgr.get_api()
    sheetid = config.get('sheetid')
    cellrange = config.get('type_filters')[typeid]
    result = sheets.spreadsheets().values().get(
            spreadsheetId=sheetid,
            range=cellrange,
            majorDimension='COLUMNS'
            ).execute()
    return result.get('values', [])[0]


def get_row_value(rowid):
    sheets = mgr.get_api()
    sheetid = config.get('sheetid')
    sheet = config.get('sheet')
    cellrange = "{}!A{}:U{}".format(sheet, rowid, rowid)
    result = sheets.spreadsheets().values().get(
             spreadsheetId=sheetid,
             range=cellrange).execute()
    return result.get('values', [])[0]


@app.route("/list/<int:rowid>")
def list_sheets(rowid):
    values = get_row_value(rowid)

    paper_types = get_available_values('paper_types')
    res_types = get_available_values('research_types')
    tools = get_available_values('tools')
    models = get_available_values('models')
    measurements = get_available_values('measurements')

    return flask.render_template("spreadsheet.html", 
            rowid=rowid,
            title=values[0],
            url=values[1],
            paper_types=paper_types,
            res_types=res_types,
            tools=tools,
            models=models,
            measurements=measurements)


@app.route("/set_values", methods=['POST'])
def set_sheet_values():
    rowid = int(flask.request.form['rowid'])
    sheets = mgr.get_api()
    values = get_row_value(rowid)
    print(values)
    return flask.redirect(flask.url_for('list_sheets', rowid=rowid+1))


app.run('localhost', 5000)
