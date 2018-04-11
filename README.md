
1. Put the CSV from the shared directory into this directory.
2. Run `FLASK_APP=gui.py flask run` from this directory. You'll need the pip
   packages for Pandas and flask installed.
3. Go to the url it prints out and add `/1` to it. That's the first document (page_id 1).
   The page_id is the row number in the CSV file.

Clicking the buttons or pressing the shortcut keys will write the result to a
file called `output.csv`. This will not be overwritten if it exists, but will
be added to. It has two columns: the page_id and the decision.

It should be easy enough to combine a finished `output.csv` file with the
actual data in Pandas; I've not tried yet.

Untested code:
~~~
data = pd.read_csv("IEEE....")
output = pd.read_csv("output.csv")
data['decisions'] = output['action']
~~~


All code MIT licensed.
