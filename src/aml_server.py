import os, sys
from tasks import aml
from redis import Redis
from flask import Flask, request
from werkzeug.utils import secure_filename
app = Flask(__name__)
import json
err = lambda d: (json.dumps(dict(status='err', msg=d)), 500)
ok = lambda d: json.dumps(dict(status='ok', data=d))
pending = lambda: json.dumps(dict(status='pending'))
tracker = Redis()
AMLSUB = '/tmp/aml-sub'

@app.route('/sub/<anon>', methods=['POST'])
def submit(anon):
    if 'file' in request.files:
        transfer_in = request.files['file']
        if os.path.splitext(transfer_in.filename)[1]=='.tgz':
            transfer_in.save(os.path.join(AMLSUB, secure_filename(transfer_in.filename)))
    task = aml.delay(dict(playbook='/tmp/aml-sub/{}/aml.yml'.format(anon)))
    tracker.set(anon, task.id)
    return ok('Job submitted.')

@app.route('/r/<anon>')
def get_result(anon):
    task_id = tracker.get(anon)
    if task_id:
        r = aml.AsyncResult(task_id)
        if r.state == 'SUCCESS':
            return ok(r.get())
        elif r.state == 'FAILURE':
            return err('ERR Check server log for debugging')
        else:
            return pending()
