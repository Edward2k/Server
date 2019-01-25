###############################################################################
# Web Technology at VU University Amsterdam
# Assignment 3
#
# The assignment description is available on Canvas.
# This is a template for you to quickly get started with Assignment 3.
# Read through the code and try to understand it.
#
# Have you looked at the documentation of bottle.py?
# http://bottle.readthedocs.org/en/stable/index.html
#
# Once you are familiar with bottle.py and the assignment, start implementing
# an API according to your design by adding routes.
###############################################################################

# Include more methods/decorators as you use them
# See http://bottle.readthedocs.org/en/stable/api.html#bottle.Bottle.route

from bottle import response, error, get, post, request, route, delete, put
import json
from random import randint


###############################################################################
# Routes

@post('/create') #NOT IDEMPOTENT since it will not always return the same value. Safe to use as it works as intended
def submitForm(db):

    origin = request.forms.get('origin')
    best_before_date = request.forms.get('best_before_date')
    product = request.forms.get('product')
    amount = request.forms.get('amount')
    image = request.forms.get('image')

    db.execute(""" INSERT INTO supermarket (product, origin, amount, image, best_before_date)
                VALUES (?, ?, ?, ?, ?)""",
                (product, origin, amount, image,  best_before_date))

@get('/getAll') #will return all sqllite data in JSON format. It is Idempotent as 2 consescutive calls result in same response
def getStocklist(db):
    db.execute("SELECT * FROM supermarket")
    response = db.fetchall()
    return json.dumps(response)

@get('/reset') #will reset data base so that it is empty. A hard reset but will keep table construct so new data can be inserted
def resetStockList(db):
    db.execute("DELETE FROM supermarket")
    return 'Reset database'

@delete ('/delete/<id>') #(RESTful) This is idempotent as first call will delte the ID and the decond will will not because the item is not existant
def deleteItem(db, id):
    db.execute("""SELECT id, product, origin, amount, image, best_before_date
                    FROM supermarket WHERE id=?""", (id,))
    answer = db.fetchall()
    if answer == []:
        return 'Element with ID ' + id + ' is not in database'
        answer.status=404 #response code

    else:
        db.execute("DELETE FROM supermarket WHERE id=?", (id,))
        answer.status=200 #response code
        return 'Item was deleted'

@get ('/getSpecific/<id>') #(RESTful) Idempotent as will always retireve the same value for same ID
def getItem(db, id):
    db.execute("""SELECT id, product, origin, amount, image, best_before_date
                    FROM supermarket WHERE id=?""", (id,))
    answer = db.fetchall()
    if id.isalpha():
        return 'Element wrong input, id must be integer'
        answer.status=400
    elif answer == []:
        return 'Element with ID ' + id + ' is not in database'
        answer.status=404 #response code
    else:
        return json.dumps(answer)
        answer.status=200 #response code

@put ('/update/<id>') #(RESTful) Idempotent as repeat requests will result in same result
def updateItem(db, id):

    db.execute("""SELECT id, product, origin, amount, image, best_before_date
                        FROM supermarket WHERE id=?""", (id,))
    responses = db.fetchall()
    if responses == []:
        return 'Error 404: Element with ID ' + id + ' is not in database'
        response.status=404 #response code
    else:

        origin = request.forms.get('origin')
        best_before_date = request.forms.get('best_before_date')
        product = request.forms.get('product')
        amount = request.forms.get('amount')
        image = request.forms.get('image')

        db.execute("""UPDATE supermarket
                        SET product=?, origin=?, amount=?, image=?,
                        best_before_date=? WHERE id=?""",
                        (product, origin, amount, image, best_before_date, id))
        response.status=201 #response code
        return 'Item was updated'

###############################################################################
# Error handling
# TODO (optional):

@error(404) #Page not found
def error404(error):
    return 'Nothing here, sorry'

@error(500) #Server Error
def error500(error):
    return 'Sorry, server error :/ *Import dinaosaur*'

@error(403) #Unauthorized access
def error403(error):
    return 'Halt, authorized personal only >:)'

@error(503) #Server not responding
def error503(error):
    return 'service unavailable: server in maintanance. Try again later :))'

@error(504) #Gateway timeout
def error504(error):
    return 'Gateway timeout, lolz'
###############################################################################


###############################################################################
# This starts the server
#
# Access it at http://localhost:8080
###############################################################################

if __name__ == "__main__":
    from bottle import install, run
    from wtplugin import WtDbPlugin, WtCorsPlugin

    install(WtDbPlugin())
    install(WtCorsPlugin())
    run(host='localhost', port=8080, reloader=True, debug=False, autojson=False)
