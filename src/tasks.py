import os, sys, subprocess
from celery import Celery

app = Celery('tasks', backend='rpc://', broker='pyamqp://guest@localhost//')

@app.task
def add(x, y):
    return x + y

@app.task
def aml(ctx):
    # Using subprocess for module dependency isolation
    subprocess.call(['python3', '-m', 'playbook', '--relocate', '/home/developer/workspace', ctx['playbook']])
