from tasks import aml

from flask import Flask, request
app = Flask(__name__)
import json
err = lambda d: (json.dumps(dict(status='err', msg=d)), 500)
ok = lambda d: json.dumps(dict(status='ok', data=d))

@app.route('/sub/<anon>', methods=['POST'])
def submit(anon):
    aml.delay(dict(playbook='/tmp/aml-sub/{}/aml.yml'.format(anon)))
    return ok('Job submitted.')
