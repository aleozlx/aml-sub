import os, sys, subprocess, uuid
import datetime
import sqlite3
import pandas as pd
import requests
from ipywidgets import Button, HBox
import IPython.display
from IPython.display import Javascript, HTML, display, clear_output

scary_template = 'IPython.notebook.kernel.execute("{}");'
localdb = sqlite3.connect('local.db')

def scary(code):
    return Javascript(scary_template.format(code))

def scarier(code):
    return Javascript(scary_template.replace('"', "`").format(code))

display(scarier("__notebook_path='${IPython.notebook.notebook_path}'; scary_stuff.notebook_path=__notebook_path"))

def inside_docker():
    docker_flag = os.system("grep -q docker /proc/1/cgroup")==0
    return docker_flag

def nbid():
    subprocess.Popen(
        ['/dsa/data/scripts/nbid', notebook_path],
        stdout=subprocess.PIPE
    ).stdout.read().decode('ascii')
    
def aml_list(path, excludes = ['.ipynb_checkpoints', '__pycache__', 'local.db'], exclude_exts = ['.ipynb', '.tgz']):
    return [fname for fname in set(os.listdir(path)) - set(excludes) if os.path.splitext(fname)[1] not in exclude_exts]

def aml_archive(fnames):
    track_id = uuid.uuid1()
    os.system('tar cvzf {}.tgz {}'.format(track_id, '\x20'.join(fnames)))
    return track_id
    
def aml_submit():
    nbid()
    files = aml_list('.')
    track_id = aml_archive(files)
    fname_sub = '{}.tgz'.format(track_id)
    res = requests.post('http://128.206.117.147:5000/sub/{}'.format(track_id),
        files= {'file': (fname_sub, open(fname_sub, 'rb'))}, timeout=5).json()
    return track_id, files, res

def aml_onsubmit(btn=None):
    track_id, files, res = aml_submit()
    # print(res)
    localdb.execute('INSERT INTO my_submissions VALUES (?, ?, "unknown", ?);',
        (str(track_id), str(files), datetime.datetime.now()))
    localdb.commit()
    aml_onrefresh()

def aml_onrefresh(btn=None):
    ret = localdb.execute("SELECT track_id FROM my_submissions WHERE state='unknown';").fetchone()
    if ret:
        (track_id, ) = ret
    else: return
    res = requests.get('http://128.206.117.147:5000/r/{}'.format(track_id), timeout=5).json()
    if res['status'] in {'ok', 'err'}:
        localdb.execute("UPDATE my_submissions SET state=?;", (res['status'], ))
        localdb.commit()
        clear_output()
        aml_jobUI(False)
        if res['status']=='ok':
            os.system('wget http://128.206.117.147:5000/f/{} -O {}'.format(track_id, res['data']))
    
def aml_jobUI(init=True):
    if init:
        btnSubmit = Button(description='New submission', button_style='info')
        btnSubmit.on_click(aml_onsubmit)
        btnRefresh = Button(description='Refresh', button_style='info')
        btnRefresh.on_click(aml_onrefresh)
        localdb.execute("""CREATE TABLE IF NOT EXISTS my_submissions (
            track_id text,
            files text,
            state text,
            ts timestamp
        );""")
        display(HBox([btnSubmit, btnRefresh]))
    submissions = pd.DataFrame(localdb.execute("SELECT track_id, ts, state FROM my_submissions;").fetchall(),
        columns=['id', 'time', 'state'])
    display(HTML(submissions.to_html()))

