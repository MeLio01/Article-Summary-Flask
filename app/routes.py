from app import app
from flask import redirect, render_template, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask import request, jsonify, Response
import os
#import pickle
#from joblib import dump, load

import numpy as np
import nltk
import re
from newspaper import fulltext
import requests

def model(url):
    news = fulltext(requests.get(url).text)
    def casefolding(sentence):
        return sentence.lower()
    def cleaning(sentence):
        return re.sub(r'[^a-z]', ' ', re.sub("’", '', sentence))
    def tokenization(sentence):
        return sentence.split()
    def sentence_split(paragraph):
        return nltk.sent_tokenize(paragraph)
    def word_freq(data):
        w = []
        for sentence in data:
            for words in sentence:
                w.append(words)
        bag = list(set(w))
        res = {}
        for word in bag:
            res[word] = w.count(word)
        return res
    def sentence_rank(data):
        weights = []
        for words in data:
            temp = 0
            wordfreq = word_freq(data)
            for word in words:
                temp += wordfreq[word]
            weights.append(temp)
        return weights
    sentence_list = sentence_split(news)

    data = []
    for sentence in sentence_list:
        data.append(tokenization(cleaning(casefolding(sentence))))
    data = (list(filter(None, data)))
        
    rank = sentence_rank(data)

    n = 3
    result = ''
    sort_list = np.argsort(rank)[::-1][:n]
    for i in range(n):
        result += '{} '.format(sentence_list[sort_list[i]])
    return result

#model = pickle.load(open('model.pkl', 'rb'))
#model = load('model.joblib')

class Form(FlaskForm):
    url = StringField('Enter the url', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = Form()

    if request.method == 'POST':
        result = model(form.url.data)
        flash('Sucess')
        return render_template('index.html', form=form, text=result)
    return render_template('index.html', form=form)

@app.route('/api', methods=['POST'])
def get_summary():
    header = request.headers.get("Authorization")
    if header != os.environ.get('AUTH_PASSWORD'):
        return Response("Invalid password", 400)
    req = request.json
    try:
        url = req['url']
        result = model(url)
        return jsonify({'result': result})
    except Exception as e:
        return Response("Error", 400)