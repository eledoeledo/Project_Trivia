import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
        'postgres', 'root', 'localhost:5432', self.database_name)
        #"postgres://{}/{}".format('localhost:5432', self.database_name)

        self.new_question = {
             "question":"toto",
              "answer" : "toto",
              "difficulty":1,
               "category":3
        }
        self.new_question_search = {
             "searchTerm":"What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
        }
        
        self.new_question_search_vide = {
             "searchTerm":""
        }
        
        self.question_prev = {
              "previous_questions":[],
               "quiz_category":"History"
        }
        
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_categories(self):
        res = self.client().get('/categories')
        # ici on récupère les données provenant de la Response
        data = json.loads(res.data)
        self.assertTrue(data['categories'])
    # route n'existe pas
    def test_404_not_found(self):
        res = self.client().get("/toto")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "404 Not found")

    def test_get_all_questions(self):
        res = self.client().get('/questions')
        # ici on récupère les données provenant de la Response
        data = json.loads(res.data)
        self.assertTrue(data['questions'])    
        self.assertTrue(data['totalQuestions'])    
        self.assertTrue(data['categories'])    

    #Delete a different question 
    def test_delete_questions(self):
        res = self.client().delete("/questions/10")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 10).one_or_none()

        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 10)

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")  


    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(data["success"], True)
     

    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post("/questions/1000", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_requesting_select_on_categorie(self):
        res=self.client().get('/categories/6/questions')
        data = json.loads(res.data)
        print(data)
        self.assertTrue(data['questions'])  

    def test_404_requesting_select_on_categorie(self):
        res=self.client().get('/categories/189999/questions')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], '404 Not found')

    def test_search_question(self):
        res = self.client().post("/questions/search", json=self.new_question_search)
        data = json.loads(res.data)
        print(data)

        self.assertTrue(data['questions'])  
        self.assertTrue(data['totalQuestion'])  

    def test_422_search_question_does_not_exist(self):
        res = self.client().post("/questions/search", json=self.new_question_search_vide)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_quizzes(self):
        res = self.client().post("/quizzes", json=self.question_prev)
        data = json.loads(res.data)

        self.assertTrue(data['question'])  
    
     
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()