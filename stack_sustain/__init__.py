import os

import requests

from flask import Flask, g, render_template, request


sites = ["stackoverflow", "superuser",  "serverfault"]
#tags = open("stack_sustain/tags.txt", "r").readlines()
with open("stack_sustain/tags.txt") as f:
    tags = f.read().splitlines()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
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

    sus_questions_so = get_sustainability_questions("stackoverflow") 
    sus_questions_su = get_sustainability_questions("superuser") 
    sus_questions_sf = get_sustainability_questions("serverfault") 
    

    @app.route('/', methods=['GET', 'POST'])
    def home():
        if request.method == 'POST':
            username_so = request.form['username_so']
            username_su = request.form['username_su']
            username_sf = request.form['username_sf']

            try:
                g.user_id_so = username_so
                g.user_id_su = username_su
                g.user_id_sf = username_sf

                g.questions_so = get_questions_by_user_id(g.user_id_so, 'stackoverflow') if g.user_id_so else []
                g.questions_su = get_questions_by_user_id(g.user_id_su, 'superuser') if g.user_id_su else []
                g.questions_sf = get_questions_by_user_id(g.user_id_sf, 'serverfault') if g.user_id_sf else []

                g.answers_so = get_questions_answered_by_user_id(g.user_id_so, 'stackoverflow') if g.user_id_so else []
                g.answers_su = get_questions_answered_by_user_id(g.user_id_su, 'superuser') if g.user_id_su else []
                g.answers_sf = get_questions_answered_by_user_id(g.user_id_sf, 'serverfault') if g.user_id_sf else []
                len_questions = len( g.questions_so) + len(g.questions_su) + len(g.questions_sf)
                len_answers = len( g.answers_so) + len(g.answers_su) + len(g.answers_sf)

                #g.answers = get_answers_by_user_id(g.user_id)
                g.user_score = len_questions + len_answers
            except IndexError:
                print("User not found")
        g.tags = ', '.join(tags)
        return render_template('home.html', so_questions = sus_questions_so, su_questions = sus_questions_su, sf_questions =sus_questions_sf)
    

    
    return app

def get_sustainability_questions(site: str):
    """
    Gets all questions related to sustainability for a specific site.

    args:
        site (str): Site

    returns:
        list of questions.
    """
    questions = []
    try:
        for tag in tags:
            questions_tag_site= get_sustainability_questions_by_tag(tag, site)
            questions += questions_tag_site
    except:
        return []
    return questions
    
def get_sustainability_questions_by_tag(tag:str, site:str):
    """
    Gets all questions which has a given tag.

    args:
        tag (str): Tag
        site (str): Site

    returns:
        list of questions.
    """
    r = requests.get(f"https://api.stackexchange.com//2.3/questions?order=desc&sort=activity&tagged={tag}&site={site}&pagesize=100&key=g6OAYkAkdJGs5mF)Y5RanA((")
    data = r.json()
    questions = []
    try:
        for item in data["items"]:
            questions.append(item)
    except:
        raise IndexError() 
    return questions

def get_questions_by_user_id(user_id: str, site:str):
    """
    Gets all questions asked by a given user id on a site.

    args:
        user_id (str): User id
        site (str): Site
    
    returns:
        list of questions asked.
    """
    r = requests.get(f"https://api.stackexchange.com/2.3/users/{user_id}/questions?order=desc&sort=activity&site={site}&pagesize=100&key=g6OAYkAkdJGs5mF)Y5RanA((")
    data = r.json()
    questions = []
    try:
        for question in data["items"]:
            if len([item for item in tags if item in question["tags"]]):
                questions.append(question)
    except:
        questions =  []
    return questions


def get_question_by_question_ids(ids: list[str], site:str):
    """
    Gets all questions with the given list of ids.

    args:
        ids (list[str]): question ids.
        site (str): Site
    
    returns:
        list of questions asked.
    """
    ids = ';'.join(ids)
    r = requests.get(f"https://api.stackexchange.com/2.3/questions/{ids}?order=desc&sort=activity&site={site}&pagesize=100&key=g6OAYkAkdJGs5mF)Y5RanA((")
    data = r.json()
    questions = []
    try:
        for question in data["items"]:
            if len([item for item in tags if item in question["tags"]]):
                questions.append(question)
    except Exception as e:
        print(e)
        questions =  []
    return questions
    
def get_questions_answered_by_user_id(user_id: str, site:str):
    r = requests.get(f"https://api.stackexchange.com/2.3/users/{user_id}/answers?order=desc&sort=activity&site={site}&pagesize=100&key=g6OAYkAkdJGs5mF)Y5RanA((")
    data = r.json()
    result = []


    try:
        question_ids = []
        for answer in data["items"]:
                question_ids.append(str(answer["question_id"]))
        result = get_question_by_question_ids(question_ids, site)
    except:
        result =  []
    return result

def get_stack_exhange_user_by_name(display_name: str, site:str):
    r = requests.get(f"https://api.stackexchange.com/2.3/users?site={site}&inname={display_name}&pagesize=100&key=g6OAYkAkdJGs5mF)Y5RanA((")
    data = r.json()
    try:
        # 5924096
        user_id = data['items'][0]['user_id']
    except:
        return None

    return user_id

