import os, sys, subprocess
from celery import Celery

config = dict(
    CELERY_ACCEPT_CONTENT = ['json'],
    CELERY_TASK_SERIALIZER = 'json',
    CELERY_RESULT_SERIALIZER = 'json',
    CELERY_IGNORE_RESULT = False,
    CELERYD_CONCURRENCY = 2,
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
    os.chdir(ctx['workspace'])
    playbook_script = os.path.join(os.path.dirname(__file__), 'playbook.py')
    subprocess.call(['python3', playbook_script, '--relocate', '/home/developer/workspace', '--container-name', 'aml-{}'.format(ctx['anon'][:ctx['anon'].index('-')]), ctx['playbook']])
