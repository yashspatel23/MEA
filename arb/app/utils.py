from collections import OrderedDict
from functools import wraps
import json
import traceback

from flask.wrappers import Response

from arb import logger


def add_error_wrapper(f):
    """
    The decorated function must return a dict

    i.e. f(*args, **kwargs) is of type dict
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = OrderedDict()
        try:
            resp = f(*args, **kwargs)
            # validation
            if not isinstance(resp, dict):
                resp = OrderedDict()
                raise Exception('Incorrect usage of decorator: add_error_wrapper')
        except Exception as e:
            store_error_info(resp, e)
        return jsonify_dict(resp)

    return decorated_function


def jsonify_dict(data):
    return Response(json.dumps(data, indent=2), mimetype='application/json')


def bool_param(s):
    """
    'True' --> True; 'False' --> False

    Default is False
    """
    if isinstance(s, bool):
        result = s
    elif not isinstance(s, str):
        result = False
    elif s.lower() == 'true' or s.lower() == 'yes':
        result = True
    else:
        result = False

    return result


def store_error_info(obj, exception):
        """
        Parameters
        ----------
        file_path: str
            A string representing the file path

        Returns
        -------
        core.models.Concept

        """
        traceback_stack_msg = traceback.format_exc()
        logger.info(traceback_stack_msg)

        obj['error_type'] = type(exception).__name__
        obj['error_msg'] = exception.message
        obj['error_traceback_list'] = traceback_stack_msg.split('\n')


