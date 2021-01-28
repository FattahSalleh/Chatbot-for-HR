### PREPROCESSING ###

#===================== Imports =====================#

import nltk
from nltk.stem.lancaster import LancasterStemmer # Reduce words to their root version (LancasterStemmer is one of the stemmer available)
stemmer = LancasterStemmer()

from flask import Flask, escape, request, render_template, redirect, flash
import flask
from jinja2 import Template
import cgi, cgitb 
cgitb.enable() 

import numpy
import tflearn
import tensorflow
import random
import json
import pickle # Serializes objects so they can be saved to a file, and loaded in a program again later on.

import mysql.connector #Connect to mySQL database
from mysql.connector import Error

import csv

#===================== Declare Flask =====================#

app = Flask(__name__)

#Global Var
globalEmpName = ""
globalEmpID = 0

#===================== Try to connect to mysql database =====================#

app.config['SECRET_KEY'] = "thisissosecret"

connection = mysql.connector.connect(host='FatNye', 
                                    database = 'fatnye_staff', 
                                    user='fatnye_redha', 
                                    password='userredha123')
try:
    
    if connection.is_connected():
        db_info = connection.get_server_info()
        print("Connected to MySQL Server Version ", db_info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

except Error as e:
    print("Error while connecting to MySQL", e)

#===================== Define app route and functions =====================#
@app.route('/') #Render HTML template file
def homePage():
    return render_template("index.html")

@app.route('/login') #Render Login Page
def loginPage():
    return render_template("login.html")

@app.route('/login', methods=['POST']) #Handle Login Information
def login():
    loginID = request.form['userID']
    loginPass = request.form['userPass']

    sqlQuery = "SELECT * FROM employee WHERE empID = '" + loginID + "' and empPass = '" + loginPass + "'" #Search for matching empID and empPass in database
    cursor = connection.cursor()
    cursor.execute(sqlQuery)
    loginData = cursor.fetchone() 

    if loginData is None:
        return redirect("http://127.0.0.1:5000/login")
    else:
        global globalEmpID
        globalEmpID = loginID

        sqlQuery = "SELECT empName FROM employee WHERE empID = '"+loginID+"'"
        cursor = connection.cursor()
        cursor.execute(sqlQuery)
        theEmpName = cursor.fetchone() 

        global globalEmpName
        globalEmpName = theEmpName

        print (globalEmpID) #Check ID
        print (globalEmpName) #Check Name

        return redirect("http://127.0.0.1:5000/logged")


@app.route('/logged', methods=['GET', 'POST']) #Render Page After Logged In
def loggedPage():
    return render_template("logged.html")

@app.route('/get') #Get User Input from Widget
def get_bot_response():    

    print(globalEmpID) #Check ID
    userText = request.args.get('ui') #Get input from JS

    with open('inputLog.csv','a') as result_file:
        wr = csv.writer(result_file, dialect='excel')
        wr.writerow([userText])

    return str(predict(userText)) #Send to predict() function


if __name__ == '__main__':
    app.run(debug=True)


#===================== Import File  =====================#

with open("intents.json") as file:
    data = json.load(file)

#===================== Open pickled data OR pickle the data =====================#

try: # rb = read bytes
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    words = []
    labels = []
    docs_x = [] # List of all different patterns
    docs_y = [] # Words and tags for those pattern

    # Stem => Change words into their root words. Ex: Whats = What, there? = there
    # Tokenize => Get all words in patterns, splitting it by space
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w not in "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)

    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)



#===================== Create or load Deep Neural Network Model (Tensorflow) =====================#

# Tensorflow AI stuff
tensorflow.reset_default_graph()

# Model layer
net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

# Train model
model = tflearn.DNN(net)

# No need to train model if we have a model that exist
try:
    model.load("model.tflearn") ## After delete model. Comment and place any letter ex: 'x' below, to load new model!
    #x
except:
    model.fit(training, output, n_epoch=450, batch_size=8, show_metric=True)     # Pass all training data into model
    model.save("model.tflearn")     # epoch = number of times it's gonna see the same data (The many times the better it is at classifying data)



#===================== Take user input and return in required format =====================#

# Take the bag of words, convert into numpy array and return wherever we need it
def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)


#===================== Give response to Python logic for processing =====================#
def predict(input):
    results = model.predict([bag_of_words(input, words)])[0]
    results_index = numpy.argmax(results)
    tag = labels[results_index]

    if results[results_index] > 0.7:
        for tg in data["intents"]:
            if tg['tag'] == tag:
                responses = tg['responses']
                sql = tg['sql']

        response = random.choice(responses)            
        sqlVar = sql[0]

        with open('tagLog.csv','a') as result_file:
            wr = csv.writer(result_file, dialect='excel')
            wr.writerow([tag])

        if sqlVar == "":
            return response
        else:
            sqlQuery = "SELECT {} FROM employee WHERE empID = {}".format(sqlVar, globalEmpID) #response
            cursor = connection.cursor()
            cursor.execute(sqlQuery)
            record = cursor.fetchone()

            responseList = [] #array [,]
            responseList.append(response)
            responseList.append(record[0])

            return ''.join(str(x) for x in responseList) 
    else:
        with open('tagLog.csv','a') as result_file:
            wr = csv.writer(result_file, dialect='excel')
            wr.writerow("X")
        return "I'm sorry but I don't understand, please try again."


