import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config.database import db
from constants.http_status_codes_constant import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
import services.question_preprocess_service
from routes.auth_routes import auth
from routes.module_routes import module
from routes.assignment_routes import assignment
from routes.diagram_routes import diagram
from routes.submission_routes import submission

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

OUTPUTS_GENERATED_DOT_FILES_PATH = os.path.join('outputs', 'generated_dot_files')
OUTPUTS_GENERATED_USE_CASE_DIAGRAMS_PATH = os.path.join('outputs', 'generated_use_case_diagrams')
OUTPUTS_GENERATED_CLASS_DIAGRAMS_PATH = os.path.join('outputs', 'generated_class_diagrams')
OUTPUTS_GENERATED_CLASS_FILES_PATH = os.path.join('outputs', 'generated_class_files')
OUTPUTS_FOLDER = os.path.join(APP_ROOT, 'outputs')
UML_GENERATOR_UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
SUBMISSION_PATH = os.path.join(APP_ROOT, 'submissions/use_case')
SUBMISSION_PATH_CLASS = os.path.join(APP_ROOT, 'submissions/class')

USE_CASE_SAVED_MODEL_PATH = os.path.join(APP_ROOT, 'tensorflow_models/use_case/model')
USE_CASE_SAVED_LABEL_PATH = os.path.join(APP_ROOT, 'tensorflow_models/use_case/label')
CLASS_SAVED_MODEL_PATH = os.path.join(APP_ROOT, 'tensorflow_models/class/model')
CLASS_SAVED_LABEL_PATH = os.path.join(APP_ROOT, 'tensorflow_models/class/label/label_map.pbtxt')
CLASS_COMP_SAVED_MODEL_PATH = os.path.join(APP_ROOT, 'tensorflow_models/class_component/model')
CLASS_COMP_SAVED_LABEL_PATH = os.path.join(APP_ROOT, 'tensorflow_models/class_component/label/label_map.pbtxt')
app = Flask(__name__, static_folder='outputs')
CORS(app)

app.config.from_mapping(SECRET_KEY=os.environ.get('SECRET_KEY'),
                        SQLALCHEMY_DATABASE_URI='sqlite:///database.db',
                        SQLALCHEMY_TRACK_MODIFICATIONS=False, JWT_SECRET_KEY='JWT_SECRET_KEY')
app.config['UML_GENERATOR_UPLOAD_FOLDER'] = UML_GENERATOR_UPLOAD_FOLDER

db.app = app
db.init_app(app)

JWTManager(app)

app.register_blueprint(auth)
app.register_blueprint(module)
app.register_blueprint(assignment)
app.register_blueprint(diagram)
app.register_blueprint(submission)


@app.before_first_request
def create_tables():
    db.create_all()


@app.get('/api/v1/')
def index():
    return 'UML Diagram Plagiarism Detection Tool API'


@app.errorhandler(HTTP_404_NOT_FOUND)
def handle_404(error):
    print(error)
    return {'err': 'Not found'}, HTTP_404_NOT_FOUND


@app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
def handle_500(error):
    print(error)
    return {'err': 'Something went wrong'}, HTTP_500_INTERNAL_SERVER_ERROR


if __name__ == '__main__':
    app.run(debug=True)
