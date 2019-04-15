import cntk as ct
import numpy as np
import time
from loadData import *

#https://stackoverflow.com/questions/48582311/cntk-cloning-a-single-layer
#https://cntk.ai/pythondocs/CNTK_301_Image_Recognition_with_Deep_Transfer_Learning.html?highlight=freeze

learning_rate = 0.005
num_classes = 8
height = 64
width = 64

# Creates the network model for transfer learning
def clone_model(model_path,input_var): 

    # Load the pretrained classification net and find nodes
    base_model = ct.load_model(model_path)
    
    #last_node = ct.logging.find_by_name(base_model,'output')
    
    cloned_model = base_model.clone(ct.CloneMethod.clone)
    """
    # CHECK IF CORRECTLY CLONED:
    node_outputs = ct.logging.get_node_outputs(cloned_model)
    for l in node_outputs: 
        print("  {0} {1}".format(l.name, l.shape))
    """

    z = cloned_model (input_var)

    return z

def getData(folder,path_to_label_csv):
    trainingParams = Parameters(num_classes,height,width, False, True)
    print("generating training image data")
    trainingValues = ImageData(folder,"",path_to_label_csv,trainingParams)

    return trainingValues
        
def fineTuneModel(folder_with_data,path_to_label_csv="label.csv",
    original_model_path="../vgg13.model",max_epochs=10):

    trainingValues = getData(folder_with_data,path_to_label_csv)

    input_var =ct.input((1,height,width),np.float32)
    label_var = ct.input((num_classes), np.float32)
    print("cloning old model")
    z = clone_model(original_model_path,input_var)
    loss = ct.cross_entropy_with_softmax(z, label_var)
    metric = ct.classification_error(z, label_var) 

    minibatch_size = 32
    epoch_size = trainingValues.getLengthOfData()

    lr_per_minibatch = [learning_rate]*10+[learning_rate/2.0]
    mm_time_constant = -minibatch_size/np.log(0.9)
    lr_schedule = ct.learning_rate_schedule(lr_per_minibatch,
        unit=ct.UnitType.minibatch, epoch_size=epoch_size)
    mm_schedule = ct.momentum_as_time_constant_schedule(mm_time_constant)

    learner = ct.momentum_sgd(z.parameters, lr_schedule, mm_schedule)
    trainer = ct.Trainer(z, (loss, metric), learner)
    print("created trainer and learner")

    print("training started")
    while epoch < max_epochs :

        trainingValues.reset() 
        # Training 
        start_time = time.time()
        training_loss = 0
        training_accuracy = 0

        #mini-batch learning
        while trainingValues.hasMoreMinibatches():
            #while there is data for a mini batch:
            x,y,currBatchSize = trainingValues.getNextMinibatch(minibatch_size)
            # x - images y - labels/emotions
            trainer.train_minibatch({ input_var : x, label_var: y})

            #maintain stats:
            training_loss += trainer.previous_minibatch_loss_average *    currBatchSize
            training_accuracy += trainer.previous_minibatch_evaluation_average * currBatchSize
            
        training_accuracy /= trainingValues.getLengthOfData()
        training_accuracy = 1.0 - training_accuracy

        print("Epoch took:", time.time() - start_time, "seconds")
        print("training accuracy:\t\t{:.2f}%".format(training_accuracy*100))

        epoch +=1

    #SAVE MODEL
    z.save("../vgg13.model")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", 
                        "--base_folder", 
                        type = str, 
                        help = "Base folder containing the training images and label.csv, 
                        required = True)
    args = parser.parse_args()    
    fineTuneModel(args.base_folder)
    #LABEL.CSV MUST BE IN THE FOLDER!!!!!