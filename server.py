"""
Dead-simple mock response server for TalentIQ and FullContact
Run the app:
    FLASK_APP=server.py flask run
Ping the app:
    GET 127.0.0.1:5000/$SERVICE
  where $SERVICE={'talent_iq', 'full_contact'}
  add `delay=$MSS` query param to delay response for $MSS miliseconds
  query parameters starting with `X-Ratelimit` (case-insensitive) will be
    echoed back as response headers
"""
import json
from time import sleep

from flask import abort, Flask, Response, request

FULL_CONTACT = 'full_contact'
TALENTIQ = 'talent_iq'


def config_app(to_config):
    """
    Config the app by reading dummy responses into memory
    :param to_config: app instance to configure
    :type config: flask.app.Flask
    :return: None
    """
    cfg = {}
    for svc in (FULL_CONTACT, TALENTIQ):
        with open('{}_response.json'.format(svc)) as resp_json:
            cfg[svc] = json.load(resp_json)
    to_config.config.from_object(__name__)
    to_config.config.update(cfg)


def get_relevant_params(dct, prefix='x-ratelimit'):
    """
    Helper function to pull out relevant query parameters
    :param dct: query param dict to extract from
    :type dct: werkzeug.datastructures.MultiDict (or probably any collections.Mapping)
    :param prefix: prefix to filter key/value pairs by
    :type prefix: str
    :return: dict
    """
    return {key.lower(): val for key, val in dct.iteritems()
            if key.lower().startswith(prefix)}


APP = Flask(__name__)
config_app(APP)


@APP.route('/<service>')
def serve(service):
    """
    Server function
    :param service: name of service to return mock data for
    :type service: str
    :return: None
    """
    delay = request.args.get('delay', 0)
    headers = get_relevant_params(request.args)
    sleep(float(delay))
    try:
        payload = APP.config[service]
    except KeyError:
        abort(404)
    else:
        resp = Response(response=json.dumps(payload), headers=headers,
                        mimetype='application/json')
        return resp
