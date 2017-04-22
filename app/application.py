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


def fibonacci(n):
    if n <= 2:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)
@application.route('/computefibonacci')
def httpfibonacci():
    try:
        n = int(request.args['n'])
    except:
        return 'Wrong arugments', 404
    return 'Fibonacci(' + str(n) + ') = ' + str(fibonacci(n))

if __name__=='__main__':
    application.secret_key='cenas lixadas'
    app.run(host='127.0.0.1',port=8000)
