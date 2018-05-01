import csv
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
import predictor
from werkzeug.contrib.cache import SimpleCache
from config_handler import ConfigHandler
from pathlib import Path
from datastore import Datastore, PickledDatastore

config = ConfigHandler()

if config.has('redis') and config.get('redis'):
    cache = Datastore()
    config = ConfigHandler(PickledDatastore(cache))
else:
    cache = SimpleCache()
    config = ConfigHandler(cache)


app = Flask(__name__)

data = {}
if config.has('input', 'ieee'):
    data['ieee'] = pd.read_csv(config.get('input', 'ieee'))

if config.has('input', 'acm'):
    acm_data = pd.read_csv(config.get('input', 'ieee'))
    acm_data['url'] = acm_data['id'].apply(
     "https://dl.acm.org/citation.cfm?id={}&preflayout=flat#abstract".format)
    data['acm'] = acm_data


def read_output(filename):
    _data = pd.read_csv(filename, header=None,
                        names=['paper_id', 'action', 'DOI'])
    _data = _data[_data['paper_id'] != 'paper_id']
    _data['paper_id'] = pd.to_numeric(_data['paper_id'])
    _data = dedup_data(_data)
    return _data


def dedup_data(data):
    return data.groupby('paper_id').last()


# mapping = pd.read_csv('Mapping.csv', skiprows=[1])
# mapping['paper_id'] = mapping.index
users = config.get('users')
mapping = None

def construct_predictor():
    global output, predict
    if config.has('output', 'ieee') and \
            Path(config.get('output', 'ieee')).exists():
        output = read_output(config.get('output', 'ieee'))
        # review_output = read_output('review-output.csv')
        # output = pd.concat((output, review_output))
        output = output.groupby('paper_id').last()
        # mapping['G'] = output['action']

        # unifies = mapping.query('V!=G | V!=A | G!=A | V=="discuss"')
        # reviews = mapping.query('V!=G & V==A & V!="discuss"')

        predict = predictor.Predictor(data['ieee']['Abstract'], output['action'])
    else:
        predict = None

def update_predictor(abstract, label):
    global predict
    if predict:
        predict.update_predictor(abstract, label)

construct_predictor()


def get_output(key):
    action = request.cookies.get('action', 'filter')
    outputfile = config.get('output', key)
    if action != 'filter':
        outputfile = action + '-' + outputfile
    csvfile = open(outputfile, "a")
    output = csv.writer(csvfile)
    return csvfile, output

def get_template(key):
    if key == 'ieee':
        return 'paper.html'
    elif key == 'acm':
        return 'acm.html'

def get_library():
    return request.cookies.get('library', 'ieee')

def style_choice(choice):
    if choice == 'include':
        return 'table-success'
    elif choice == 'exclude':
        return 'table-danger'
    elif choice == 'discuss':
        return 'table-info'

@app.route("/library")
def select_library():
    return render_template('library.html')

@app.route("/library/<libname>")
def set_library(libname):
    if libname == 'ieee':
        resp = make_response(redirect(url_for('go_to_last')))
        resp.set_cookie('library', 'ieee')
    elif libname == 'acm':
        resp = make_response(redirect(url_for('go_to_last')))
        resp.set_cookie('library', 'acm')
    return resp

@app.route('/<int:paper_id>')
def show_paper(paper_id):
    paper_idx = get_paper_idx(paper_id)
    key = get_library()
    template = get_template(key)
    print(template)
    res = data[key].iloc[paper_idx]
    users = config.get('users')
    if not mapping or len(users) == 0:
        current_choices = pd.DataFrame()
    else:
        current_choices = mapping[users].iloc[paper_idx]
    action = request.cookies.get('action', 'filter')
    if action != 'filter':
        action_counts = current_choices.value_counts()
        max_action = action_counts.index[0]
        prediction = [x == max_action for x in ['include', 'exclude', 'discuss']]
        scores = None
    elif 'Abstract' in res and predict:
        scores, prediction = predict.get_prediction(res['Abstract'])
    else:
        scores = None
        prediction = [False, False, False]
    actions = config.get('actions')
    print(actions)
    scores = {a['name']: p for a,p in zip(actions, scores)}
    predicted_action = actions[prediction.index(True)]['id']
    prediction = {a['name']: p for a,p in zip(actions, prediction)}
    print(cache.has('predictions'))
    cache.set('hi', 'hello')
    if cache.has('correct_predictions'):
        correct = cache.getl('correct_predictions', 50)
        count = len(correct)
        correct = map(int, correct)
        average = sum(correct)/count
    else:
        average = None
    print('Prediction', prediction)
    print('Historical prediction accuracy', average)
    return render_template(template, 
            paper_id=paper_id, 
            paper_idx=paper_idx,
            data=res, 
            users=users,
            choices=current_choices,
            styles={user: style_choice(user) for user in users},
            action=action,
            prediction=prediction,
            actions=config.get('actions'),
            questions=config.get('research_questions'),
            criteria=config.get('criteria'),
            predicted_action=predicted_action,
            average=average,
            scores=scores
            )

@app.route("/next")
def go_to_last():
    if output is not None and not output.empty:
        last_id = output.index[-1]
        return redirect('/' + str(last_id+1))
    else:
        return redirect('/0')

@app.route("/highlights")
def highlight_list():
    return jsonify(config.get('highlights'))

def get_paper_idx(paper_id):
    action = request.cookies.get('action', 'filter')
    if action == 'filter':
        return paper_id
    elif action == 'review':
        return reviews.iloc[paper_id]['paper_id']
    elif action == 'unify':
        return unifies.iloc[paper_id]['paper_id']


def get_doi(library, paper_id):
    if library == 'ieee':
        return data[library].iloc[paper_id]['DOI']


def get_abstract(library, paper_id):
    if library == 'ieee':
        return data[library].iloc[paper_id]['Abstract']


def update_stats(action):
    if config.get('redis'):
        predicted_action = request.form['predicted_action']
        if action == predicted_action:
            cache.push('correct_predictions', 1)
        else:
            cache.push('correct_predictions', 0)
        if cache.llen('correct_predictions') > 100:
            cache.pop('correct_predictions')
        cache.incr('predictions')


def process_choice(action):
    paper_idx = request.form['paper_idx']
    csvfile, output = get_output(get_library())
    print(action + "ed " + paper_idx)
    library = get_library()
    doi = get_doi(library, int(paper_idx))
    output.writerow([paper_idx, action, doi])
    csvfile.flush()
    abstract = get_abstract(library, int(paper_idx))
    update_predictor(abstract, action)
    update_stats(action)
    next_paper = str(int(request.form['paper_id'])+1)
    return redirect("/" + str(next_paper))

@app.route("/include", methods=["POST"])
def include_paper():
    return process_choice('include')

@app.route("/exclude", methods=["POST"])
def exclude_paper():
    return process_choice('exclude')

@app.route("/discuss", methods=["POST"])
def discuss_paper():
    return process_choice('discuss')

@app.route("/freeform", methods=["POST"])
def freeform_action():
    return process_choice(request.form['freeform'])

@app.route("/reload")
def reload():
    cache.delete('config')
    construct_predictor()
    return redirect(url_for('go_to_last'))
