import os

import requests

from flask import Flask, g, render_template, request


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

    # a simple page that says hello
    @app.route('/', methods=['GET', 'POST'])
    def home():
        if request.method == 'POST':
            username = request.form['username']

            try:
                g.user_id = get_stack_exhange_user_by_name(username)
                g.questions = get_questions_by_user_id(g.user_id)
                #g.answers = get_answers_by_user_id(g.user_id)
                g.user_score = len(g.questions)
            except IndexError:
                print("User not found")
        return render_template('home.html')
    
    """
    @app.add_template_global
    def get_answers_by_user_id(user_id: str):
        r = requests.get(f"https://api.stackexchange.com/2.3/users/{user_id}/answers?order=desc&sort=activity&site=stackoverflow")
        data = r.json()

        try:
            answers = data["items"]
            for answer in answers:
                question_id = answer["question_id"]

        except:
            raise IndexError()

        return answers
    """

    @app.add_template_global
    def get_sustainability_questions():
        print(os.getcwd())
        tags = open("stack_sustain/tags.txt", "r").readlines()
        tags_str = ";".join(tags)
        r = requests.get(f"https://api.stackexchange.com//2.3/questions?order=desc&sort=activity&tagged={tags_str}&site=stackoverflow")
        data = r.json()

        try:
            questions = data["items"]
        except:
            raise IndexError()

        return questions
    
    return app




def get_questions_by_user_id(user_id: str):
    r = requests.get(f"https://api.stackexchange.com/2.3/users/{user_id}/questions?order=desc&sort=activity&site=stackoverflow")
    data = r.json()

    try:
        questions = data["items"]
    except:
        raise IndexError()

    return questions

def get_stack_exhange_user_by_name(display_name: str):
    r = requests.get(f"https://api.stackexchange.com/2.3/users?site=stackoverflow&inname={display_name}")
    data = r.json()

    try:
        # 5924096
        user_id = data['items'][0]['user_id']
    except:
        raise IndexError()

    return user_id

