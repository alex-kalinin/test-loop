import imageio
import redisgears
import base64
import redisAI
import numpy as np
import cv2

MAX_IMAGES = 1000 #

def softmax(p):
    t = np.exp(p)
    s = t.sum()
    return t / s

labels = ['healthy', 'multiple_diseases', 'rust', 'scab']

def addToGraphRunner(x):
    try:
        xlog('addToGraphRunner:', 'count=', x['count'])

        # converting the image to matrix of colors
        data = io.BytesIO(x['img'])
        dataM = imageio.imread(data).astype(dtype='float32')
        
        newImg = (cv2.resize(dataM, (224, 224)) / 128) - 1

        l = np.asarray(newImg, dtype=np.float32)
        img_ba = bytearray(l.tobytes())

        # converting the matrix color to Tensor
        v1 = redisAI.createTensorFromBlob('FLOAT', [1, 224, 224, 3], img_ba)

        # creating the graph runner, 'g1' is the key in redis on which the graph is located
        graphRunner = redisAI.createModelRunner('mobilenet:model')
        redisAI.modelRunnerAddInput(graphRunner, 'input', v1)
        redisAI.modelRunnerAddOutput(graphRunner, 'MobilenetV2/Predictions/Reshape_1')

        # run the graph and translate the result to python list
        res = redisAI.tensorToFlatList(redisAI.modelRunnerRun(graphRunner)[0])
        res_np = np.array(res)
        
        proba = softmax(res_np)
        result = ''
        
        for i, name in enumerate(labels):
            result += "{:.0f}% {}\n".format(100 * i, name)

        # extract the animal name
        return (result, x['img'])
    except:
        xlog('addToGraphRunner: error:', sys.exc_info()[0])


def addToStream(x):
    # save animal name into a new stream
    try:
        redisgears.executeCommand('xadd', 'cats', 'MAXLEN', '~', str(MAX_IMAGES), '*', 'image', 'data:image/jpeg;base64,' + base64.b64encode(x[1]).decode('utf8'))
    except:
        xlog('addToStream: error:', sys.exc_info()[0])


gearsCtx('StreamReader').\
    map(addToGraphRunner).\
    register('input:0')
