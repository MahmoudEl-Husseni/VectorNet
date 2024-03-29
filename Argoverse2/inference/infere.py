import sys
sys.path.append('/content/VectorNet/Argoverse2')

import numpy as np

import torch
from torch.utils.data import DataLoader

from Vectornet import VectorNet
from config import N_TRAJ, N_FUTURE, VAL_BS

import os 
if __name__=='__main__':
    scene_name = os.environ['scene_name']
    data_dir = os.environ['data_path']
    best_models_path = os.environ['best_models_path']
    save_path = os.environ['save_path']
    EXPERIMENT_NAME = os.environ['EXPERIMENT_NAME']

    debug=False
    if debug: 
        print('scene_name: ', scene_name)
        print('data dir: ', data_dir)
        print('best_models_path: ', best_models_path)
        print('save_path: ', save_path)


    if EXPERIMENT_NAME=='Argo-avg': 
        from dataset_argoavg import Vectorset, custom_collate
    elif EXPERIMENT_NAME=='Argo-1' or EXPERIMENT_NAME=='Argo-Normalized' or EXPERIMENT_NAME=='Argo-GNN-GNN' or EXPERIMENT_NAME=='Argo-pad':
        from dataset import Vectorset, custom_collate

    from dataset import SingleScene



    # load model

    model = VectorNet(EXPERIMENT_NAME)

    model_ckpt_path = f'{best_models_path}/{EXPERIMENT_NAME.lower()}-best_model.pth'


    checkpoint = torch.load(model_ckpt_path, map_location='cpu')

    # Extract the model state dictionary from the checkpoint
    model_state_dict = checkpoint['state_dict']
    model.load_state_dict(model_state_dict)
    model.eval()


    # load scene


    if EXPERIMENT_NAME=='Argo-1' :
        dataset = SingleScene(data_dir, EXPERIMENT_NAME, normalize=False)
    else :
        dataset = SingleScene(data_dir, EXPERIMENT_NAME, normalize=True)

    from metrics.fde import compute_fde

    record = dataset[[scene_name]]

    scene_in = custom_collate([record, record])
    
    out = model(scene_in)[0]
    pred, conf = out[:-6], out[-6:]
    pred = pred.view(-1, 6, 50, 2)

    np.save(f'{save_path}/{scene_name}_pred_{EXPERIMENT_NAME}.npy', out.detach().numpy())
