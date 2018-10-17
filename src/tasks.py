import os, sys, subprocess
from celery import Celery

config = dict(
    CELERY_ACCEPT_CONTENT = ['json'],
    CELERY_TASK_SERIALIZER = 'json',
    CELERY_RESULT_SERIALIZER = 'json',
    CELERY_IGNORE_RESULT = False,
    CELERYD_CONCURRENCY = 40,
    CELERY_TRACK_STARTED = True
)

app = Celery('tasks', backend='redis://', broker='redis://')
app.conf.update(config)

@app.task
def aml(ctx):
    ctx['workspace'] = os.path.dirname(ctx['playbook'])
    #print('WS', ctx['workspace'], ctx['archive'])
    os.system('mkdir -pv {workspace}'.format(**ctx))
    os.system('tar xvf {archive} -C {workspace}'.format(**ctx))
    os.system("""sed -i 's/\/tmp\/aml-sub\/workspace/\/tmp\/aml-sub\/{anon}/g' {workspace}/submit.yml""".format(**ctx))
    # Using subprocess for module dependency isolation
    subprocess.call(['python3', '-m', 'playbook', '--relocate', '/home/developer/workspace', ctx['playbook']])
