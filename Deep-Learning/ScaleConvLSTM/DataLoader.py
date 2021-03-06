# --------------------------------------------------------
# ScaleConvLSTM
# Copyright (c) 2018 Fudan-VTS
# Licensed under The MIT License [see LICENSE for details]
# Written by liwenxi
# --------------------------------------------------------
import numpy as np
from scipy.io import loadmat
from scipy.io import savemat
import cv2
import torch
from torch.utils.data import Dataset
from skimage import io, color
import math, os


def gaussian_kernel(image, points):
    image_density = np.zeros(image.shape)
    h, w = image_density.shape

    if len(points) == 0:
        return image_density

    if len(points) == 1:
        x1 = np.max(0, np.min(w, round(points[0, 0])))
        y1 = np.max(0, np.min(h, round(points[0, 1])))
        image_density[y1, x1] = 255
        return image_density

    for j in range(len(points)):
        f_sz = 15
        sigma = 4.0
        kx = cv2.getGaussianKernel(f_sz, sigma=sigma)
        ky = cv2.getGaussianKernel(f_sz, sigma=sigma)
        H = np.multiply(kx, ky.T)
        # convert x, y to int
        x = min(w, max(0, abs(int(math.floor(points[j, 0])))))
        y = min(h, max(0, abs(int(math.floor(points[j, 1])))))
        if x > w or y > h:
            continue
        gap = int(math.floor(f_sz / 2))
        x1 = x - gap if x - gap > 0 else 0
        x2 = x + gap if x + gap < w else w - 1
        y1 = y - gap if y - gap > 0 else 0
        y2 = y + gap if y + gap < h else h - 1
        # generate 2d gaussian kernel
        kx = cv2.getGaussianKernel(y2 - y1 + 1, sigma=sigma)
        ky = cv2.getGaussianKernel(x2 - x1 + 1, sigma=sigma)
        gaussian = np.multiply(kx, ky.T)

        image_density[y1:y2 + 1, x1:x2 + 1] = image_density[y1:y2 + 1, x1:x2 + 1] + gaussian

    return image_density


class MallDataset(Dataset):
    def __init__(self, img_path, point_path):
        self.img_path = img_path
        self.point_path = point_path
        ground_truth__dict = loadmat(point_path)
        self.point = ground_truth__dict['frame'][0]

    def __len__(self):
        # print("len", self.point.shape[0]-39)
        return int((self.point.shape[0]-4))
        # return 60

    def __getitem__(self, idx):
        image_list = []
        density_list = []
        for i in range(0, 5):
            image = io.imread(self.img_path + 'seq_00' + str(idx+i+1).zfill(4) + '.jpg')
            gray = color.rgb2gray(image)
            density = gaussian_kernel(gray, self.point[idx+i]['loc'][0][0])
            image_list.append(gray)
            density_list.append(density)
        # print("11", len(image_list))
        image_list = torch.tensor(image_list, dtype = torch.double)
        density_list = torch.tensor(density_list, dtype = torch.double)
        image_list = torch.unsqueeze(image_list, 1)
        density_list = torch.unsqueeze(density_list, 1)
        # print("________")
        # print(image_list.size())
        # print(density_list.size())
        # print("________")
        return image_list, density_list

class MallDatasetTest(Dataset):
    def __init__(self, img_path, point_path):
        self.img_path = img_path
        self.point_path = point_path
        ground_truth__dict = loadmat(point_path)
        self.count = ground_truth__dict['count']

    def __len__(self):
        # print("len", self.point.shape[0]-39)
        return self.count.shape[0]-4

    def __getitem__(self, idx):
        image_list = []
        count_list = []
        for i in range(0, 5):
            image = io.imread(self.img_path + 'seq_00' + str(idx+i+1).zfill(4) + '.jpg')
            gray = color.rgb2gray(image)
            count = self.count[idx+i]
            image_list.append(gray)
            count_list.append(count)
        # print("11", len(image_list))
        image_list = torch.tensor(image_list, dtype = torch.double)
        count_list = torch.tensor(count_list, dtype = torch.double)
        image_list = torch.unsqueeze(image_list, 1)
        # count_list = torch.unsqueeze(density_list, 1)
        return image_list, count_list
