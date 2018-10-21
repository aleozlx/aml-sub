import os, sys, logging
logger = logging.getLogger('docker-playbook')
whitelist = ['hello', 'nvidia_smi', 'm4_exercise',
    'm6_cleanup', 'm6_exercise', 'm6_archive']

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

def step_m6_cleanup(ctx):
    os.system('rm -f TransferLearning.py')
    os.system('jupyter nbconvert --to python TransferLearning.ipynb')
    # delete comments / empty lines
    os.system(r"sed -i -e '/^\s*#/d' -e '/^$/d' TransferLearning.py")
    # delete automation / magic
    #os.system(r"sed -i -e '/dsa_automation\.ui_amljob/,$d' -e '/get_ipython/d' -e '/import tf_threads/,+5d'  TransferLearning.py")
    os.system(r"sed -i -e '/dsa_automation\.ui_amljob/,$d' -e '/get_ipython/d' TransferLearning.py")
    # delete plotting
    os.system(r"sed -i -e '/\bplt\b/d' -e '/\bimshow\b/d' TransferLearning.py")
    # increase epochs
    os.system(r"sed -i -e 's/\bepochs=1/epochs=50/g'  -e 's/steps_per_epoch = 10/steps_per_epoch = 570/g' -e 's/validation_steps = 5/validation_steps = 100/g'  -e 's/\bsteps = 5/steps = 100/g' TransferLearning.py")
    #os.system("tail -n 30 TransferLearning.py")

def step_m6_exercise(ctx):
    os.system('python3 TransferLearning.py')

def step_m6_archive(ctx):
    os.system('tar czf results.tgz TransferLearning.py weights_food100.h5 evaluation.json')
