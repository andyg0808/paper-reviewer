import csv
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

data = pd.read_csv("IEEE-results--export2018.04.11-15.30.32.csv")

csvfile = open("output.csv", "a")
output = csv.writer(csvfile)
output.writerow(['paper_id', 'action'])

@app.route('/<int:paper_id>')
def show_paper(paper_id):
    res = data.iloc[paper_id]
    return render_template("paper.html", paper_id=paper_id, data=res)

def process_choice(action, paper_id):
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
