import os
import sys
import shutil
import argparse
from datetime import datetime
from yacs.config import CfgNode as CN

_C = CN()

# SOLVER related parameters
_C.SOLVER = CN()
_C.SOLVER.alias           = 'time'     # The experiment alias
_C.SOLVER.gpu             = (0,)       # The gpu ids
_C.SOLVER.logdir          = 'logs'     # Directory where to write event logs
_C.SOLVER.ckpt            = ''         # Restore weights from checkpoint file
_C.SOLVER.run             = 'train'    # Choose from train or test
_C.SOLVER.type            = 'sgd'      # Choose from sgd or adam
_C.SOLVER.max_epoch       = 300        # Maximum training iterations
_C.SOLVER.test_every_epoch= 10         # Test model every n training epochs
_C.SOLVER.lr_type         = 'step'     # Learning rate type: step or cos
_C.SOLVER.lr              = 0.1        # Initial learning rate
_C.SOLVER.gamma           = 0.1        # Learning rate step-wise decay
_C.SOLVER.step_size       = (120,60,)  # Learning rate step size.
_C.SOLVER.ckpt_num        = 10         # The number of checkpoint kept
_C.SOLVER.dist_url        = 'tcp://localhost:10001'
_C.SOLVER.verbose         = False    

# DATA related parameters
_C.DATA = CN()
_C.DATA.train = CN()
_C.DATA.train.name       = ''          # The name of the dataset

_C.DATA.train.depth      = 5           # The octree depth
_C.DATA.train.full_depth = 2           # The full depth
_C.DATA.train.node_dis   = False       # Save the node displacement
_C.DATA.train.split_label= False       # Save the split label
_C.DATA.train.adaptive   = False       # Build the adaptive octree
_C.DATA.train.node_feat  = False       # Calculate the node feature

_C.DATA.train.distort    = False       # Whether to apply data augmentation
_C.DATA.train.offset     = 0.016       # Offset used to displace the points
_C.DATA.train.scale      = 0.0         # Scale the points
_C.DATA.train.uniform    = False       # Generate uniform scales
_C.DATA.train.jitter     = 0.0         # Jitter the points
_C.DATA.train.normal_axis= ''          # Used to re-orient normal directions
_C.DATA.train.interval   = (1, 1, 1)   # Use interval&angle to generate random angle
_C.DATA.train.angle      = (180, 180, 180)

_C.DATA.train.location   = ''          # The data location
_C.DATA.train.filelist   = ''          # The data filelist
_C.DATA.train.batch_size = 32          # Training data batch size
_C.DATA.train.num_workers= 8           # Number of workers to load the data


_C.DATA.test = _C.DATA.train.clone()


# MODEL related parameters
_C.MODEL = CN()
_C.MODEL.name            = ''          # The name of the model
_C.MODEL.depth           = 5           # The input octree depth
_C.MODEL.depth_out       = 5           # The output feature depth
_C.MODEL.channel         = 3           # The input feature channel
_C.MODEL.factor          = 1           # The factor used to widen the network
_C.MODEL.nout            = 40          # The output feature channel
_C.MODEL.resblock_num    = 3           # The resblock number
_C.MODEL.bottleneck      = 4           # The bottleneck factor of one resblock
_C.MODEL.dropout         = (0.0,)      # The dropout ratio
_C.MODEL.upsample        = 'nearest'   # The method used for upsampling
_C.MODEL.nempty          = False


# loss related parameters
_C.LOSS = CN()
_C.LOSS.num_class        = 40          # The class number for the cross-entropy loss
_C.LOSS.weight_decay     = 0.0005      # The weight decay on model weights
_C.LOSS.weights          = (1.0, 1.0)  # The weight factors for different losses
_C.LOSS.label_smoothing  = 0.0         # The factor of label smoothing


# backup the commands
_C.SYS = CN()
_C.SYS.cmds              = ''          # Used to backup the commands

FLAGS = _C


def _update_config(FLAGS, args):
  FLAGS.defrost()
  if args.config:
    FLAGS.merge_from_file(args.config)  
  if args.opts:
    FLAGS.merge_from_list(args.opts)  
  FLAGS.SYS.cmds = ' '.join(sys.argv)  
  # update logdir
  alias = FLAGS.SOLVER.alias.lower()
  if 'time' in alias:
    alias = alias.replace('time', datetime.now().strftime('%m%d%H%M')) #%S
  FLAGS.SOLVER.logdir += '_' + alias
  FLAGS.freeze()


def _backup_config(FLAGS, args):
  logdir = FLAGS.SOLVER.logdir
  if not os.path.exists(logdir):
    os.makedirs(logdir)
  # copy the file to logdir
  if args.config:
    shutil.copy2(args.config, logdir)
  # dump all configs
  filename = os.path.join(logdir, 'all_configs.yaml')
  with open(filename, 'w') as fid:
    fid.write(FLAGS.dump())


def _set_env_var(FLAGS):
  gpus = ','.join([str(a) for a in FLAGS.SOLVER.gpu])
  os.environ['CUDA_VISIBLE_DEVICES'] = gpus


def get_config():
  return FLAGS

def parse_args(backup=True):
  parser = argparse.ArgumentParser(description='The configs')
  parser.add_argument('--config', type=str,
                      help='experiment configure file name')
  parser.add_argument('opts', nargs=argparse.REMAINDER,
                      help="Modify config options using the command-line")

  args = parser.parse_args()
  _update_config(FLAGS, args)
  if backup:
    _backup_config(FLAGS, args)
  _set_env_var(FLAGS)
  return FLAGS


if __name__ == '__main__':
  flags = parse_args(backup=False)
  print(flags)
