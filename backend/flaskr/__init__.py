from calendar import c
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,PUT,POST,DELETE,OPTIONS')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()
        data ={}
        if len(categories) == 0:
            abort(404)
        for categorie in categories:
            if categorie.id and categorie.type:
                data[str(categorie.id)]=categorie.type
                    
        return jsonify(
                {
                    'categories':data
                }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = Question.query.all()
        formatted_question = [question.format() for question in questions]
        categories = Category.query.order_by(Category.id).all()
        data ={}
        for categorie in categories:
            if categorie.id and categorie.type:
                data[str(categorie.id)]=categorie.type
        return jsonify({
            'questions': formatted_question[start:end],
            'totalQuestions' : len(formatted_question),
            'categories'   : data
        })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:questions_id>', methods=['DELETE'])
    def delete_question(questions_id):
        try:
            question = Question.query.filter_by(id=questions_id).one_or_none()

            if question is None:
                abort(404)
            else:
                question.delete()
                return jsonify({
                    'success': True,
                    'deleted': questions_id
                })
        except:
             abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_questions():
        body = request.get_json()
        new_question = body.get('question', None)
        new_reponse = body.get('answer', None)
        new_difficulte = body.get('difficulty', None)
        new_categorie = body.get('category', None)
        try:   
            if new_question is None or new_reponse is None or new_difficulte is None or new_categorie is None :
                abort(400)
            question = Question(question=new_question, answer=new_reponse,
                        category=new_categorie, difficulty = new_difficulte )
            question.insert()
            return jsonify({
                'success': True
            })
        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search = body.get('searchTerm', None)
        if search:
            questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search))).all()
            formatted_question = [question.format() for question in questions]
            return jsonify({
                'questions': formatted_question,
                'totalQuestion': len(questions)
            })
        else:
            abort(422)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions')
    def get_specific_categorie(id):
        questions = Question.query.filter(Question.id == id).one_or_none()    
        if questions is None:
            abort(404)
        else:
            return jsonify({
                'questions': questions.format()
            })

          
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():
        body = request.get_json()
        array = []
        array = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)
        categories = Category.query.filter(Category.type==quiz_category['type']).first()
        categories = categories.format()
        categories_id= str(categories["id"])
        try:   
            questions = Question.query.filter(Question.category == categories_id)
            data =[]
            for q in questions:
                if not q.id in array:
                    data.append(q)
            question = random.choice(data)
            formatted_question = question.format()
            return jsonify({
                'question': formatted_question
            })
        except:
            abort(404)
            
        
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (jsonify({'success': False, 'error': 404,
                'message': '404 Not found'}), 404)

    @app.errorhandler(422)
    def unprocessable(error):
        return (jsonify({'success': False, 'error': 422,
                'message': 'unprocessable'}), 422)

    @app.errorhandler(400)
    def error_client(error):
        return (jsonify({'success': False, 'error': 400,
                'message': 'Bad request'}), 400)

    @app.errorhandler(500)
    def server_error(error):
        return (jsonify({'success': False, 'error': 500,
                'message': 'internal server error'}), 500)

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (jsonify({'success': False, 'error': 405,
                'message': 'method not allowed'}), 405)
        
    @app.errorhandler(505)
    def version_http(error):
        return (jsonify({'success': False, 'error': 505,
                'message': 'Http version not supported'}), 505)
    return app

