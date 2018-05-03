from flask import Flask


application = Flask(__name__)


# ================================================
# Testing Routes
# ================================================


@application.route('/ping', methods=['GET'])
def ping():
    return "pong\n"


# ================================================
# version 1
# ================================================
api_prefix_v1 = '/api/v1'



