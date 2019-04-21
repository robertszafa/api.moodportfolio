import argparse
import cntk as ct
import numpy as np
from PIL import Image
import pandas as pd
import io

from .img_preprocess import distort_img,compute_norm_mat,preproc_img
from .rect_util import Rect
from .loadData import Parameters


emotion_table = {0 : 'neutral'  , 
                 1 : 'happiness', 
                 2 : 'surprise' , 
                 3 : 'sadness'  , 
                 4 : 'anger'    , 
                 5 : 'disgust'  , 
                 6 : 'fear'     , 
                 7 :'contempt'  }

def test_SingleInstance(saved_model_path,imgData):
    
	emotionAndConfidence={} #empty dictionary

	testingParams = Parameters(8,64,64, True, False)
	img = preprocessTestImage(imgData,testingParams)

	model = ct.load_model(saved_model_path)
	out = ct.softmax(model)
	pred_probs = out.eval({out.arguments[0]:img})
	#convert pred_probs to a dictionary
	for i in range(pred_probs[0].shape[0]):
		emotionAndConfidence[emotion_table[i]] = pred_probs[0][i]
	emotion = np.argmax(pred_probs)
	print(emotion_table[emotion])
	return emotionAndConfidence

def testSeveralInstances(saved_model_path,path_with_data):#,img_paths):
    model = ct.load_model(saved_model_path)
    out = ct.softmax(model)
    
    testingParams = Parameters(8,64,64, True, False)
    path = path_with_data
    """
    df = pd.read_csv(path + "label.csv")
    imageNames = df.iloc[:,0].values 
    box = df.iloc[:,1].values
    y = list(map(np.argmax,df.iloc[:,2:].values))
    """
    pred = []

    for name in imageNames : 
        img = preprocessTestImage(path+name,testingParams)
        pred_probs = out.eval({out.arguments[0]:img})
        emotion = np.argmax(pred_probs)
        pred.append(emotion_table[emotion])

    print(pred)
    

def preprocessTestImage(imgData,testingParams):
    
	image_data = Image.open(io.BytesIO(imgData)).convert('L') #grayscale
	image_data.load()  
	img_box = [0,0,48,48]
	# face rectangle #(48,48)
	face_rc = Rect(img_box)

	distorted_image = distort_img(image_data, face_rc, 
											testingParams.width, 
											testingParams.height, 
											testingParams.max_shift, 
											testingParams.max_scale, 
											testingParams.max_angle, 
											testingParams.max_skew, 
											testingParams.do_flip)
	A, A_pinv = compute_norm_mat(testingParams.width,
		testingParams.height)
	final_image = preproc_img(distorted_image, A=A, A_pinv=A_pinv)
	final_image = np.expand_dims(final_image, axis=0)

	return final_image

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t",
                        "--test_instances", 
                        type = int,
                        help = "1 to test just 1 instance. Any other number to test several.",
                        required = True)
    parser.add_argument("-m", 
                        "--saved_model", 
                        type = str,
                        help = "Specify the path where .dnn file is stored",
                        required = True)
    parser.add_argument("-p", 
                        "--img_path", 
                        type = str, 
                        help = "Location for the 1 image for testing. OR path with the folder of all images for testing.",
                        required = True)
    
    args = parser.parse_args()  

    if args.test_instances == 1:
        test_SingleInstance(args.saved_model, args.img_path)
    else:
        testSeveralInstances(args.saved_model, args.img_path)

# python -W ignore EmotionDetector.py -t 1 -m ai/vgg13.model -p fer0032220.png

# python -W ignore EmotionDetector.py -t 2 -m ../vgg13.model -p ../data/FER2013Test