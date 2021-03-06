from __future__ import print_function
from PIL import Image
import os
import os.path
import errno
import numpy as np
import sys
if sys.version_info[0] == 2:
    import cPickle as pickle
else:
    import pickle

import torch.utils.data as data
from .utils import download_url, check_integrity


class SEMEION(data.Dataset):
    """`SEMEION <http://archive.ics.uci.edu/ml/datasets/semeion+handwritten+digit>`_ Dataset.
    
    Args:
        root (string):  数据集存放的主目录, ``semeion.py``存在.
        transform (callable, optional): 一个 transform 函数, 它输入 PIL image 并且返回 
        transformed 版本. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): 一个 transform 函数,输入 target 并且
            转换它.
        download (bool, optional): 如果 true, 就从网上下载数据集并且放到 root 目录下. 
        如果数据集已经下载,那么不会再次下载.

    """
    url = "http://archive.ics.uci.edu/ml/machine-learning-databases/semeion/semeion.data"
    filename = "semeion.data"
    md5_checksum = 'cb545d371d2ce14ec121470795a77432'

    def __init__(self, root, transform=None, target_transform=None, download=True):
        self.root = os.path.expanduser(root)
        self.transform = transform
        self.target_transform = target_transform

        if download:
            self.download()

        if not self._check_integrity():
            raise RuntimeError('Dataset not found or corrupted.' +
                               ' You can use download=True to download it')

        self.data = []
        self.labels = []
        fp = os.path.join(root, self.filename)
        data = np.loadtxt(fp)
        # convert value to 8 bit unsigned integer
        # color (white #255) the pixels
        self.data = (data[:, :256] * 255).astype('uint8')
        self.data = np.reshape(self.data, (-1, 16, 16))
        self.labels = np.nonzero(data[:, 256:])[1]

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is index of the target class.
        """
        img, target = self.data[index], self.labels[index]

        # doing this so that it is consistent with all other datasets
        # to return a PIL Image
        img = Image.fromarray(img, mode='L')

        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target

    def __len__(self):
        return len(self.data)

    def _check_integrity(self):
        root = self.root
        fpath = os.path.join(root, self.filename)
        if not check_integrity(fpath, self.md5_checksum):
            return False
        return True

    def download(self):
        if self._check_integrity():
            print('Files already downloaded and verified')
            return

        root = self.root
        download_url(self.url, root, self.filename, self.md5_checksum)
