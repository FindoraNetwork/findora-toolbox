import subprocess, re, bleach, secrets, time, jwt
from os import environ
from werkzeug.exceptions import HTTPException
from web.src.shared import findora_env
from findora_toolbox import load_var_file, set_var, ask_yes_no
from flask import (
    Flask,
    flash,
    request,
    redirect,
    url_for,
    session,
    render_template,
    jsonify,
    make_response,
    abort,
)
from flask_bootstrap import Bootstrap
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
)
from requests import HTTPError

load_var_file(findora_env.dotenv_file)

app = Flask(__name__)

Bootstrap(app)

jwt = JWTManager(app)


def handle_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.code
    return response


app.register_error_handler(HTTPException, handle_error)


class TokenExpiredError(HTTPException):
    code = 419
    description = 'Token expired'


class MyClass:
    def __init__(self):
        # Initialize the class
        pass

    @jwt_required
    def my_method(self):
        # This method will only be executed if the request has a valid JWT token in the authorization header
        pass


def updateStats():
    output = (
        subprocess.run(
            ["python3", f"{findora_env.toolbox_location}/src/app.py", "-s"],
            capture_output=True,
        )
        .stdout.decode()
        .replace("\n", "<br>")
        .replace("\x1b[H\x1b[2J\x1b[3J\x1b[35m", "")
        .strip()
    )
    output = re.sub(r"\x1b[^m]*m", "", output)
    return bleach.linkify(output)


@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html")


# Create a route to authenticate your users and set cookies.
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username != environ.get("WEB_USERNAME") or password != environ.get(
        "WEB_PASSWORD"
    ):
        abort(401)
    jwt = create_access_token(identity=username)
    # Set the JWT token in a cookie
    response = make_response(jsonify({"jwt": jwt}), 200)
    response.set_cookie("access_token_cookie", jwt, max_age=86400)
    return response


@app.route("/stats", methods=["GET"])
@jwt_required()
def statsRoute():
    try:
        if not 'access_token_cookie' in request.cookies:
            abort(401)
        output = updateStats()
        return render_template("stats.html", output=output), 200
    except HTTPError as e:
        if e.status_code == 419:
            raise TokenExpiredError
        else:
            return handle_error(e)


@app.route("/logout", methods=["POST"])
def logout():
    # Create a response object and set the cookie to expire
    response = make_response(redirect(url_for("index")))
    response.set_cookie("access_token_cookie", expires=0)
    return response


@app.route("/badlogin")
def badLogin():
    return render_template("badlogin.html")


@app.errorhandler(400)
def handle_bad_request(e):
    return render_template("400.html"), 400


@app.errorhandler(401)
def handle_unauthorized(e):
    return render_template("401.html"), 401


@app.errorhandler(404)
def handle_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(405)
def handle_method_not_allowed(e):
    return render_template("405.html"), 405


@app.errorhandler(TokenExpiredError)
def handle_expired_token(e):
    return render_template("419.html"), 419


@app.errorhandler(500)
def handle_server_error(e):
    return render_template("500.html"), 500


def setupUserAccount():
    if environ.get("WEB_USERNAME") is None:
        username = input("No User Name found, please input a username: ")
        answer = ask_yes_no(f"* You picked {username}, is that correct? (Y/N) ")
        if answer:
            set_var(findora_env.dotenv_file, "WEB_USERNAME", username)
        else:
            raise SystemExit(0)

    if environ.get("WEB_PASSWORD") is None:
        password = input("No password found, please input a password now: ")
        answer = ask_yes_no(f"* You picked {password}, is that correct? (Y/N) ")
        if answer:
            set_var(findora_env.dotenv_file, "WEB_PASSWORD", password)
        else:
            raise SystemExit(0)

    if environ.get("WEB_PORT") is None:
        port = input(
            "* No port found, please input your desired port (don't forget to update your firewall): "
        )
        answer = ask_yes_no(f"* You picked {port}, is that correct? (Y/N) ")
        if answer:
            set_var(findora_env.dotenv_file, "WEB_PORT", port)
        else:
            print("* No port, no server, goodbye!")
            raise SystemExit(0)


if __name__ == "__main__":
    app.config["SECRET_KEY"] = secrets.token_hex(32)
    app.config["JWT_SECRET_KEY"] = secrets.token_hex(32)
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    setupUserAccount()
    app.run(host="0.0.0.0", port=environ.get("WEB_PORT"))
