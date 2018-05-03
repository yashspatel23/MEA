from arb import FLASK_SERVER_PORT, FLASK_DEBUG_MODE
from arb.app.routes import application


if __name__ == '__main__':
    # ----------------------------
    # web server
    # ----------------------------
    application.config.update(
        DEBUG=FLASK_DEBUG_MODE
    )
    application.run(host='0.0.0.0', port=FLASK_SERVER_PORT)



