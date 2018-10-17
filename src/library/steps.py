import os, sys, logging
logger = logging.getLogger('docker-playbook')
whitelist = ['hello', 'nvidia_smi', 'm4_exercise']

def resolve(step_name):
    if step_name in whitelist:
        return globals()['step_{}'.format(step_name)]

def step_nvidia_smi(ctx):
    os.system('nvidia-smi')

def step_hello(ctx):
    print('Hello World!')

def step_m4_exercise(ctx):
    logging.getLogger().setLevel(logging.CRITICAL)
    import pandas as pd
    import numpy as np
    from sklearn.externals import joblib
    logging.getLogger().setLevel(logging.INFO)
    classifier = joblib.load('my_module_4_model.pkl')
    DATASET = '/dsa/data/all_datasets/autoMPG-1.txt'
    assert os.path.exists(DATASET)
    dataset = pd.read_csv(DATASET, index_col=0)
    X = np.array(dataset.iloc[:60,1:8])
    y = np.array(dataset.iloc[:60,0])
    with open('output.txt', 'w') as f:
        f.write('{}\n'.format(classifier.score(X, y)))
