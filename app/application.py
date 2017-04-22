from app import *

logging.basicConfig(level=logging.INFO)
dbsession=crud.get_session()

app = connexion.App(__name__, specification_dir='swagger/')
app.add_api('swagger.yaml')

application=app.app


@application.before_request
def make_session_permanent():
    session.permanent = True
    application.permanent_session_lifetime = timedelta(minutes=1)

if __name__=='__main__':
    application.secret_key='cenas lixadas'
    app.run(host='127.0.0.1',port=8000)
