# Emotional Recognition

The AI Deep Learner recognizes the following 8 emotions-

* neutral, 
* happiness,
* surprise, 
* sadness, 
* anger, 
* disgust, 
* fear and
* contempt

with the help of the FER+ dataset( see citation below)
My implementation uses PLD training mode (Probabilistic Label Drawing) described in https://arxiv.org/abs/1608.01041.

I have included my trained model (vgg13.model) in the parent directory. So you can start playing around right away. 
However do look at the "To Train" section

## Contents
* Installing Prerequisities
* To Train
* To Test
* To fine tune
* Datasets and CSVs
* Citation

## Install Prerequisities
```$ pip install -r requirements.txt```

## To Train

### Step 1 - Get Image Dataset

Obtain fer2013.csv from (Kaggle here)
[https://www.kaggle.com/c/challenges-in-representation-learning-facial-expression-recognition-challenge/data]
Save the file in the parent directory (where the fer2013new.csv file is stored)

### Step 2 - Generate Images from Dataset
The fer2013.csv has pixel values for each image. The images must first be generated from this. To do this:
```
cd src
python getImages.py -d ../data -fer '../fer2013.csv' -ferplus '../fer2013new.csv'
``` 
(Generates 28 thousand training, 3.5 thousand validation and testing images each and stores it in the [data](data) folder)

###  Step 3 - Train (finally!)
```
cd src
python -W ignore train.py -d ../data -maxe 100
```
Trains the images in the FER2013Train Folder within [Data](data) for 100 epochs

#### Training with Checkpoints
In case you can't train all at one go, I have also used checkpoints (i.e. train till an epoch x and continue from it later on!)

if you trained till epoch number 10 (11 epochs), you will see model_10 in [models](data/models) directory
So to resume training from epoch 11:
```
cd src
python -W ignore train.py -d ../data -ckp ../data/models/model_10 -e 11
```

**NOTE - ** At the end of the training, code generates `vgg13.model` file in the parent directory. I have included mine!

**SO YOU DON'T HAVE TO TRAIN TO USE MY MODEL.**

## To Test

IMAGES SENT CAN BE PNG OR JPEG and coloured!
For good output, please ensure that there is only one person in the image.

To test a single image 
```
cd src
python -W ignore EmotionDetector.py -t 1 -m ../vgg13.model -d <path of the image>
```
OR test several images at once:
```
cd src
python -W ignore EmotionDetector.py -t 2 -m ../vgg13.model -d <path with all the images e.g. ../data/FER2013Test >
```

## To Fine Tune
To know more about fine tuning click [here](https://flyyufelix.github.io/2016/10/03/fine-tuning-in-keras-part1.html)

With regular fine tuning, my model works better with more use. Furthermore fine tuning can be used to personalize the AI 
to your face/emotions!
(to personalize the ai, make sure that the images for training are just images of you!)

Apart from the images you will also need to create a "label.csv" file (refer next section)

```
cd src
python -W ignore fine_tuning_1.py - d <folder with the training images and label.csv file>```

## Datasets and CSVs:

**_fer2013new.csv_** - usage (train,test or validation),image name, emotion confidence values for 8+2 emotions
(neutral,happiness,surprise,sadness,anger,disgust,fear,contempt,unknown,Non-Face)

**_fer2013.csv_** - main emotion,image name, pixel value
The pixels must be converted to images and stored in the right sub-folders within [data](data)

### Layout for Training
There is a folder named data that has the following layout:
```
/data
  /FER2013Test
    label.csv
  /FER2013Train
    label.csv
  /FER2013Valid
    label.csv
```
*label.csv* in each folder contains the the image name is in the following format: ferXXXXXXXX.png, where XXXXXXXX is 
the row index of the original FER csv file. So here the names of the first few images:
```
fer0000000.png
fer0000001.png
fer0000002.png
```
It also contains the scale of each emotion from 1-10 in order of neutral, happiness,	surprise, sadness, anger, disgust, 
fear, contempt, unknown, NF (no face). 


## Citation
I have the used the FER+ and FER dataset here.

**@inproceedings{BarsoumICMI2016,  
&nbsp;&nbsp;&nbsp;&nbsp;title={Training Deep Networks for Facial Expression Recognition with Crowd-Sourced Label Distribution},  
&nbsp;&nbsp;&nbsp;&nbsp;author={Barsoum, Emad and Zhang, Cha and Canton Ferrer, Cristian and Zhang, Zhengyou},  
&nbsp;&nbsp;&nbsp;&nbsp;booktitle={ACM International Conference on Multimodal Interaction (ICMI)},  
&nbsp;&nbsp;&nbsp;&nbsp;year={2016}  
}**

@MISC{Goodfeli-et-al-2013,
       author = {Goodfellow, Ian and Erhan, Dumitru and Carrier, Pierre-Luc and Courville, Aaron and Mirza, Mehdi and Hamner, Ben and Cukierski, Will and Tang, Yichuan and Thaler, David and Lee, Dong-Hyun and Zhou, Yingbo and Ramaiah, Chetan and Feng, Fangxiang and Li, Ruifan and Wang, Xiaojie and Athanasakis, Dimitris and Shawe-Taylor, John and Milakov, Maxim and Park, John and Ionescu, Radu and Popescu, Marius and Grozea, Cristian and Bergstra, James and Xie, Jingjing and Romaszko, Lukasz and Xu, Bing and Chuang, Zhang and Bengio, Yoshua},
     keywords = {competition, dataset, representation learning},
        title = {Challenges in Representation Learning: A report on three machine learning contests},
         year = {2013},
  institution = {Unicer},
          url = {http://arxiv.org/abs/1307.0414},
     abstract = {The ICML 2013 Workshop on Challenges in Representation
Learning focused on three challenges: the black box learning challenge,
the facial expression recognition challenge, and the multimodal learn-
ing challenge. We describe the datasets created for these challenges and
summarize the results of the competitions. We provide suggestions for or-
ganizers of future challenges and some comments on what kind of knowl-
edge can be gained from machine learning competitions.

http://deeplearning.net/icml2013-workshop-competition}
}
