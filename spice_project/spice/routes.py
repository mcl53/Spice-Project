from flask import render_template, flash, url_for, redirect, request, send_file
from spice import app
from spice.forms import EnterData
import os
import pandas as pd
from spice.results import generate_results, mean_and_sd

# Variables in global application context
filepath = None
filename = None


def save_file(fingerprint_data_csv):
    fingerprint_data_fn = fingerprint_data_csv.filename
    file_path = os.path.join(
        app.root_path, 'Fingerprints', fingerprint_data_fn)
    fingerprint_data_csv.save(file_path)
    global filepath
    filepath = str(file_path)
    global filename
    filename = str(fingerprint_data_fn)
    print(filepath, filename)


'''App routes'''


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    form = EnterData()
    if form.validate_on_submit():
        global filepath, filename
        filepath = None
        filename = None
        fingerprint_data_csv = form.file.data
        save_file(fingerprint_data_csv)
        flash('Successfully submitted fingerprint data.', 'success')
        return redirect(url_for('result', file_name=filename))
    return render_template('home.html', title='Home', form=form)


@app.route("/result/<file_name>", methods=['GET', 'POST'])
def result(file_name):
    global filepath
    results_data = generate_results(filepath)
    is_spice = mean_and_sd(results_data)
    if is_spice:
        print("spicy boi")
        spice = "Spice"
    else:
        print("calm")
        spice = "Not Spice"
    return render_template('result.html', title='Results', file_name=file_name, is_spice=spice)


@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html', title='About')


@app.route("/how_to_use", methods=['GET'])
def how_to_use():
    return render_template('how_to_use.html', title='How to use application')


@app.route("/fingerprints/<file_name>")
def fingerprints(file_name):
    path_to_file = os.path.join(app.root_path, "Fingerprints", file_name)
    print(file_name)
    return send_file(path_to_file, attachment_filename=file_name)
