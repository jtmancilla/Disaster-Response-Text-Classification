# Disaster-Response-Text-Classification
Web app to classify texts from disaster response times into a fixed set of categories.

<br>This uses the disaster response dataset from [Figure 8]( https://www.figure-eight.com/dataset/combined-disaster-response-data/)

<br>This was done as part of the Udacity Data Scientist nanodegree

<br>I have hosted this app on Heroku. It can be accessed [here](https://vijkar-figure8-disastertextclf.herokuapp.com/)

# Project structure

The project structure is as follows:

- app
<br>Contains the web app, template html etc.
    - templates        
        - master.html
            <br>Template for the landing page
        - go.html
            <br>Templates for the text classification page. Extends master.html
    - run.py
        <br>Script that brings up the Flask App
- data
<br>Contains the source data and script to process the data        
    - messages.csv
        Input messages
    - categories.csv
        <br>Category labels for the above messages
    - DisasterResponse.db
        SQLite database file. Contains 2 tables:
        1. messages
            <br>Messages with their corresponding categories from the above 2 files
        2. word_count
            <br>Counts and frequencies of all the words in the repository
    
    <br>There is a note below on why the sqlite database binary has been checked in to the repository
- models
<br>Contains the machine learning model that can predict the categories for a given disaster text. The model is stored as a pickle file.
<br>There is a note below on why the model file has been checked in
- utils
<br>Contains functions that are used in multiple places. The tokenizer that splits a given text message into tokens after cleaning is used both at training time and in the web app. Hence abstracted it out to a different script.
- LICENSE
<br>License file. This project is under the Apache 2.0 license.
- Procfile
<br>Herkoku procfile, that tells Heroku how to boot the web app
- nltk.txt
<br>List of nltk datasets to download. This file enables heroku to download and install the right nltk datasets before spinning up the app.
<br>Downloading and installing these datasets can be time consuming. Given Heroku only gives 60 seconds for the app to come up and bind to the port, this feature saves time and makes the downloading of datasets a setup step.
- requirements.txt
<br>Standard python venv requirements.txt listing required packages for this project
- runtime.txt
<br>Specifies the python runtime required in Heroku
- train_classifier.py
<br> Script that trains the model. Details on runtime parameters below

# Run instructions

Note: If you are cloning this repo and have setup your python environment using the requirements.txt then you can skip to step 3

All the steps below assume you are the root directory of the repository

1. Processing the source data
```
python data/process_data.py data/messages.csv data/categories.csv data/DisasterResponse.db
```
2. Training the machine learning model
<br>`python train_classifier.py data/DisasterResponse.db models/classifier.pkl`
3. Spinning up the web app
You have 2 options:

    1. Using gunicorn
    <br>Install gunicorn (part of requirements.txt) and then
    <br>`gunicorn --chdir app run:app`  
    2. Using Heroku CLI
    <br>Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) and then
    <br>`heroku local`


## Why binary files are checked in to the repository

Heroku has a requirement that the web app needs to spin up and bind to the assigned port within 60 seconds of initiation. In other words the flask app we are using here should be ready to serve requests within 60 seconds.

Reading the CSV files and writing to the SQLite database takes about 10 + 10 seconds in the Heroku cloud in the free tier. 10 seconds for merging the messages and categories and another 10 seconds for computing the word counts and frequencies.

Training the model and saving the pickle file takes about 50 seconds in the Heroku cloud in the free tier

I tried initially to only check in the csv's into the repository and have the flask app process the data and buld the model at runtime.

With data process and model building taking ~60 seconds, I was on the edge of time and heroku would time out and kill my application.

I tried 2 different approaches to overcome the 60 second limitation:

1. Using a [release phase](https://devcenter.heroku.com/articles/release-phase)
<br>The release phase is a setup step that allows one to setup a few things before spinning up ones web application. Unfortunately this step is done in a different machine and the local disk is not carried over to the deploy stage([Ref](https://devcenter.heroku.com/articles/release-phase#design-considerations)).
Hence even though I could do all data preprocessing and model building in the release phase, at deploy time those models and sqlite databases wouldn't be available to my application

2. Asynchronous computation
<br>Heroku allows [worker tasks](https://devcenter.heroku.com/articles/procfile#procfile-format) to run outside the wb application. These would be for performing large  computations asynchronously so that web app wouldnt get choked.
<br>I tried to put in file checks and sleeps in my flask app to wait for the worker to finish data pre-processing and model building. I still ran into the timout issue
<br>Worker tasks have a particular format. Using a simple python script doesnt do the job. When the worker dies, Heroku seems to assume the web app should also die. This also caused issues
<br>With a bunch of refactoring I could use the worker approach and get this to work. Another approach was to use a nonSQLite database hosted by Heroku like Redis. However, I was constrained on time and had to submit this assignment for the Udacity nanodegree. Hence I decided to pause here and check in the binaries of the sqlite database and model pickle file.
<br>My understanding of the Heroku platform is limited. There could be other ways to overcome the 60 second timeout. If you are reading this and have suggestions, I am keen to hear them. Please drop me a note.