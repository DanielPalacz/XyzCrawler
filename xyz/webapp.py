import flask

# app = flask.Flask(__name__)


def create_app(**kwargs):
    app = flask.Flask(__name__)
    app.config.update(kwargs)

    app.route("/", methods=["GET"])(index)
    app.route("/A", methods=["GET"])(view_a)
    app.route("/B", methods=["GET"])(view_b)
    return app


def index():
    #response = flask.Response('{"helloWorld": 1}', content_type="application/json")
    return str(17)


def view_a():
    return '<a href="/B">B</a>'


def view_b():
    return 'endpoint_B'


# return "str" --> text/html; charset=utf-8
# TypeError
# TypeError: The view function did not return a valid response. The return type must be a string, dict, tuple, Response instance, or WSGI callable, but it was a list.
# TypeError: The view function did not return a valid response tuple. The tuple must have the form (body, status, headers), (body, status), or (body, headers).


if __name__ == "__main__":
    test_app = create_app()
    test_app.run(debug=True, use_reloader=True, port=5678)
    # app.run(debug=True, use_reloader=True, port=5678)
