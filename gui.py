import csv
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, make_response
app = Flask(__name__)

data = {}
data['ieee'] = pd.read_csv("IEEE-results--export2018.04.11-15.30.32.csv")
acm_data = pd.read_csv("ACMDL201804116245225.csv")
acm_data['url'] = acm_data['id'].apply("https://dl.acm.org/citation.cfm?id={}&preflayout=flat#abstract".format)
data['acm'] = acm_data

mapping = pd.read_csv('Mapping.csv', skiprows=[1])
mapping['paper_id'] = [x+1 for x in mapping.index]
mapping.index = mapping['paper_id']
output = pd.read_csv('output.csv')
output = output.groupby('paper_id').last()
mapping['G'] = output['action']
def run_unify(thing):
    v,g,a = thing[['V', 'G', 'A']]
    return v!=g or v!=a or g!=a
mapping['unify'] = mapping.apply(run_unify, axis=1)
def run_review(thing):
    v,g,a = thing[['V', 'G', 'A']]
    return v!=a or g!=a
mapping['review'] = mapping.apply(run_review, axis=1)


output_files = {
    'acm': 'output-acm.csv',
    'ieee': 'output.csv'
}

def get_output(key):
    action = request.cookies.get('action', 'filter')
    outputfile = output_files[key]
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
        resp = make_response("Library set to IEEE")
        resp.set_cookie('library', 'ieee')
    elif libname == 'acm':
        resp = make_response("Library set to ACM")
        resp.set_cookie('library', 'acm')
    return resp

@app.route('/<int:paper_id>')
def show_paper(paper_id):
    paper_id = get_next_paper(paper_id)
    key = get_library()
    template = get_template(key)
    print(template)
    res = data[key].iloc[paper_id]
    current_choices = mapping[['V', 'G', 'A']].iloc[paper_id]
    return render_template(template, 
            paper_id=paper_id, 
            data=res, 
            choices=current_choices,
            v_style=style_choice(current_choices['V']),
            g_style=style_choice(current_choices['G']),
            a_style=style_choice(current_choices['A']),
            action=request.cookies.get('action', 'filter')
            )

def get_next_paper(paper_id):
    action = request.cookies.get('action', 'filter')
    if action == 'filter':
        return paper_id
    elif action == 'review':
        return mapping[mapping['review']].iloc[paper_id:].iloc[0]['paper_id']
    elif action == 'unify':
        return mapping[mapping['unify']].iloc[paper_id:].iloc[0]['paper_id']

def process_choice(action, paper_id):
    csvfile, output = get_output(get_library())
    print(action + "ed " + paper_id)
    output.writerow([paper_id, action])
    csvfile.flush()
    next_paper = str(int(request.form['paper_id'])+1)
    return redirect("/" + str(next_paper))

@app.route("/include", methods=["POST"])
def include_paper():
    return process_choice('include', request.form['paper_id'])

@app.route("/exclude", methods=["POST"])
def exclude_paper():
    return process_choice('exclude', request.form['paper_id'])

@app.route("/discuss", methods=["POST"])
def discuss_paper():
    return process_choice('discuss', request.form['paper_id'])

@app.route("/freeform", methods=["POST"])
def freeform_action():
    return process_choice(request.form['freeform'], request.form['paper_id'])
