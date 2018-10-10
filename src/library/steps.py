import os, sys, logging
logger = logging.getLogger('docker-playbook')
whitelist = ['hello', 'nvidia_smi']

def resolve(step_name):
    if step_name in whitelist:
        return globals()['step_{}'.format(step_name)]

def step_nvidia_smi(ctx):
    os.system('nvidia-smi')

def step_hello(ctx):
    print('Hello World!')
