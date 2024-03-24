import os

import requests

from flask import Flask, g, render_template, request

from flask_caching import Cache

sites = ["stackoverflow", "superuser", "serverfault"]
tags = open("stack_sustain/tags.txt", "r").readlines()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    

    @app.route('/', methods=['GET', 'POST'])
    def home():
        if request.method == 'POST':
            username_so = request.form['username_so']
            username_su = request.form['username_su']
            username_sf = request.form['username_sf']

            try:
                g.user_id_so = get_stack_exhange_user_by_name(username_so, 'stackoverflow')
                g.user_id_su = get_stack_exhange_user_by_name(username_sf, 'superuser')
                g.user_id_sf = get_stack_exhange_user_by_name(username_su, 'serverfault')

                g.questions_so = get_questions_by_user_id(g.user_id_so, 'stackoverflow') if g.user_id_so else []
                g.questions_su = get_questions_by_user_id(g.user_id_su, 'superuser') if g.user_id_su else []
                g.questions_sf = get_questions_by_user_id(g.user_id_sf, 'serverfault') if g.user_id_sf else []
                print(len(g.questions_so), len(g.questions_su), len(g.questions_sf ))
                #g.answers = get_answers_by_user_id(g.user_id)
                g.user_score = len(g.questions_so) + len(g.questions_su) + len(g.questions_sf)
            except IndexError:
                print("User not found")
        else:
            print("hey")
            g.sus_questions_so = get_sustainability_questions("stackoverflow") 
            g.sus_questions_su = get_sustainability_questions("superuser") 
            g.sus_questions_sf = get_sustainability_questions("serverfault") 
        g.tags = ','.join(tags)
        return render_template('home.html')
    
    @cache.memoize(timeout=120) 
    def get_sustainability_questions(site: str):
        questions = []
        try:
            for tag in tags:
                questions_tag_site= get_sustainability_questions_by_tag(tag, site)
                questions += questions_tag_site
        except:
            return []
        return questions
    
    return app


def get_sustainability_questions_by_tag(tag:str, site:str):
    r = requests.get(f"https://api.stackexchange.com//2.3/questions?order=desc&sort=activity&tagged={tag}&site={site}&key=g6OAYkAkdJGs5mF)Y5RanA((")
    data = r.json()
    questions = []
    try:
        for item in data["items"]:
            questions.append(item)
    except:
        raise IndexError()
    print(questions)    
    return questions

def get_questions_by_user_id(user_id: str, site:str):
    r = requests.get(f"https://api.stackexchange.com/2.3/users/{user_id}/questions?order=desc&sort=activity&site={site}&key=g6OAYkAkdJGs5mF)Y5RanA((")
    data = r.json()
    print(data)
    try:
        questions = data["items"]
    except:
        questions =  []
    return questions

def get_stack_exhange_user_by_name(display_name: str, site:str):
    r = requests.get(f"https://api.stackexchange.com/2.3/users?site={site}&inname={display_name}&key=g6OAYkAkdJGs5mF)Y5RanA((")
    data = r.json()
    print(data)
    try:
        # 5924096
        user_id = data['items'][0]['user_id']
    except:
        return None

    return user_id

