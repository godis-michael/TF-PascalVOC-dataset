from PIL import Image
from bs4 import BeautifulSoup
import progressbar
import os
import errno
import shutil
import glob
import re


bar = progressbar.ProgressBar()


def create_tree(path):
    for folder in ('VOCdevkit', 'VOCdevkit/VOC2012', 'VOCdevkit/VOC2012/Annotations', 'VOCdevkit/VOC2012/ImageSets',
                   'VOCdevkit/VOC2012/JPEGImages', 'VOCdevkit/VOC2012/SegmentationClass',
                   'VOCdevkit/VOC2012/SegmentationObject', 'VOCdevkit/VOC2012/ImageSets/Action',
                   'VOCdevkit/VOC2012/ImageSets/Layout', 'VOCdevkit/VOC2012/ImageSets/Main',
                   'VOCdevkit/VOC2012/ImageSets/Segmentation'):
        try:
            os.makedirs(path + folder)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
            else:
                delete_prompt = input('Directories structure already exist. Do you want to delete it? [y/n]: ')
                if delete_prompt == 'y':
                    shutil.rmtree(path + folder)
                    os.makedirs(path+folder)
                elif delete_prompt == 'n':
                    break
                else:
                    raise ValueError('Possible choices are yes-\'y\' or no-\'n\'')
                    break

# create_tree('')


def prepare_images_and_create_train_and_val_sets(path):
    JPEGImages, ImageSets = path + 'VOCdevkit/VOC2012/JPEGImages/', path + 'VOCdevkit/VOC2012/ImageSets/'

    for model_class in next(os.walk(JPEGImages))[1]:
        if model_class != 'negatives':
            class_name = re.sub(r'\s', '_', model_class)
            index = 1
            images_dir = JPEGImages + '/' + model_class + '/'
            amount = len(os.listdir(images_dir))
            for image in os.listdir(images_dir):
                image_name = class_name + '-' + str(index)
                os.rename(images_dir + image, JPEGImages + image_name + '.jpg')
                if index <= round(amount/2, 0):
                    with open(ImageSets + 'Main/' + model_class + '_train.txt', 'a') as f:
                        f.write(image_name + ' 1\n')
                    with open(ImageSets + 'Main/' + 'train.txt', 'a') as f:
                        f.write(image_name + '\n')
                else:
                    with open(ImageSets + 'Main/' + model_class + '_val.txt', 'a') as f:
                        f.write(image_name + ' 1\n')
                    with open(ImageSets + 'Main/' + 'val.txt', 'a') as f:
                        f.write(image_name + '\n')
                index += 1
            os.removedirs(JPEGImages + model_class)

# prepare_images_and_create_train_and_val_sets('')


def add_negatives(path):
    JPEGImages, ImageSetsMain  = path + 'VOCdevkit/VOC2012/JPEGImages/', 'VOCdevkit/VOC2012/ImageSets/Main/',
    negatives_dir = JPEGImages + 'negatives/'
    train, val = glob.glob(ImageSetsMain + '*_train.txt'), glob.glob(ImageSetsMain + '*_val.txt')
    amount = len(os.listdir(negatives_dir))
    index = 1

    for image in os.listdir(negatives_dir):
        image_name = 'negative-' + str(index)
        # basewidth = 500
        # img = Image.open(negatives_dir + image)
        # wpercent = (basewidth / float(img.size[0]))
        # hsize = int((float(img.size[1]) * float(wpercent)))
        # img = img.resize((basewidth, hsize), Image.ANTIALIAS)
        # img.save(JPEGImages + image_name + '.jpg')
        os.rename(negatives_dir + image,  JPEGImages + image_name + '.jpg')
        if index <= round(amount / 2, 0):
            for file in train:
                with open(file, 'a') as f:
                    f.write(image_name + ' -1\n')
                if file == train[0]:
                    with open(ImageSetsMain + 'train.txt', 'a') as f:
                        f.write(image_name + '\n')
        else:
            for file in val:
                with open(file, 'a') as f:
                    f.write(image_name + ' -1\n')
                if file == val[0]:
                    with open(ImageSetsMain + 'val.txt', 'a') as f:
                        f.write(image_name + '\n')
        index += 1
    shutil.rmtree(negatives_dir)

# add_negatives('')


def change_folder_in_xml(path):
    anotations_path = path + 'VOCdevkit/VOC2012/Annotations/'
    files = glob.glob(anotations_path + '*.xml')

    for file in bar(files):
        with open(file, 'r+') as f:
            soup = BeautifulSoup(f, 'xml')
            folder, database = soup.folder, soup.database
            folder.string, database.string = 'VOC2012', 'The VOC2012 Database'
            soup.path.decompose()
            f.seek(0)
            f.truncate()
            f.write(str(soup))

change_folder_in_xml('')