import flask

app = flask.Flask(__name__)

# adding routing


@app.route("/", methods=["GET"])
def index():
    #response = flask.Response('{"helloWorld": 1}', content_type="application/json")
    return str(17)


@app.route("/A", methods=["GET"])
def view_a():
    return '<a href="/B">B</a>'


@app.route("/B", methods=["GET"])
def view_b():
    return 'endpoint_B'


# return "str" --> text/html; charset=utf-8
# TypeError
# TypeError: The view function did not return a valid response. The return type must be a string, dict, tuple, Response instance, or WSGI callable, but it was a list.
# TypeError: The view function did not return a valid response tuple. The tuple must have the form (body, status, headers), (body, status), or (body, headers).


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, port=5678)
