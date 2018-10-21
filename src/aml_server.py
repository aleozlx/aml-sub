import os, sys
from tasks import aml
from redis import Redis
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
app = Flask(__name__)
import json
import yaml
err = lambda d: (json.dumps(dict(status='err', msg=d)), 500)
ok = lambda d: json.dumps(dict(status='ok', data=d))
pending = lambda d: json.dumps(dict(status='pending', msg=d))
tracker = Redis()
AMLSUB = '/tmp/aml-sub'

@app.route('/sub/<anon>', methods=['POST'])
def submit(anon):
    if 'file' in request.files:
        transfer_in = request.files['file']
        if os.path.splitext(transfer_in.filename)[1]=='.tgz':
            transfer_in.save(os.path.join(AMLSUB, secure_filename(transfer_in.filename)))
    task = aml.delay(dict(
        anon=anon,
        archive='/tmp/aml-sub/{}.tgz'.format(anon),
        playbook='/tmp/aml-sub/{}/submit.yml'.format(anon)))
    tracker.set(anon, task.id)
    return ok('Job submitted.')

@app.route('/del/<anon>', methods=['POST'])
def revoke(anon):
    container_name = 'aml-{}'.format(anon[:anon.index('-')])
    os.system('docker stop {}'.format(container_name))
    return ok('Task revoked.')

@app.route('/r/<anon>')
def query(anon):
    task_id = tracker.get(anon)
    if task_id:
        r = aml.AsyncResult(task_id)
        if r.state == 'SUCCESS':
            playbook = '/tmp/aml-sub/{}/submit.yml'.format(anon)
            with open(playbook, 'r') as f:
                playbook_content = yaml.load(f)
            if 'transfer_back' in playbook_content:
                output_file = '/tmp/aml-sub/{}/{}'.format(anon, playbook_content['transfer_back'])
                if os.path.exists(output_file):
                    return ok(playbook_content['transfer_back'])
                else:
                    return err('Job has completed without generating the output file as specified.')
            else:
                return err('No transfer_back specified')
        elif r.state == 'FAILURE':
            return err('Some error has occurred.')
        elif r.state == 'STARTED':
            return pending('started')
        else:
            return pending('queued')

@app.route('/f/<anon>')
def fetch(anon):
    task_id = tracker.get(anon)
    playbook = '/tmp/aml-sub/{}/submit.yml'.format(anon)
    with open(playbook, 'r') as f:
        playbook_content = yaml.load(f)
    output_file = '/tmp/aml-sub/{}/{}'.format(anon, playbook_content['transfer_back'])
    return send_file(output_file)
