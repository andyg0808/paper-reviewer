import csv
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, make_response
app = Flask(__name__)

data = {}
data['ieee'] = pd.read_csv("IEEE-results--export2018.04.11-15.30.32.csv")
acm_data = pd.read_csv("ACMDL201804116245225.csv")
acm_data['url'] = acm_data['id'].apply("https://dl.acm.org/citation.cfm?id={}&preflayout=flat#abstract".format)
data['acm'] = acm_data


output_files = {
    'acm': 'output-acm.csv',
    'ieee': 'output.csv'
}

def get_output(key):
    outputfile = output_files[key]
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
    key = get_library()
    template = get_template(key)
    print(template)
    res = data[key].iloc[paper_id]
    return render_template(template, paper_id=paper_id, data=res)

def process_choice(action, paper_id):
    csvfile, output = get_output(get_library())
    print(action + "ed " + paper_id)
    output.writerow([paper_id, action])
    csvfile.flush()
    return redirect("/" + str(int(request.form['paper_id']) + 1))

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
