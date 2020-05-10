import imageio
import redisgears
import base64
import redisAI
import numpy as np
import cv2
import urllib.request
import traceback
import PIL.Image

def softmax(p):
    t = np.exp(p)
    s = t.sum()
    return t / s

labels = ['healthy', 'multiple_diseases', 'rust', 'scab']

def log(msg):
    key_name = 'log:0'
    if msg is None:
        redisgears.executeCommand('SET', key_name, '')
    else:
        prev = redisgears.executeCommand('GET', key_name)
        prev += ('\n' + msg)
        redisgears.executeCommand('SET', key_name, prev)

def addToGraphRunner(x):
    try:
        redisgears.executeCommand('DEL', 'result')
        log(None)
        log('Starting')
        log(str(x.keys()))
        log(str(x['value']))
        
        url = x['value']['url']

        log(url)
        data = io.BytesIO(urllib.request.urlopen(url).read())
        log('Downloaded image')

        dataM = imageio.imread(data).astype(dtype='float32')
        log('Converted to numpy')

        log('Shape: ' + str(dataM.shape))

        newImg = cv2.resize(dataM, (224, 224))
        log('Shape: ' + str(newImg.shape))

        l = np.asarray(newImg, dtype=np.float32)
        log('Shape: ' + str(l.shape))

        img_ba = bytearray(l.tobytes())

        # converting the matrix color to Tensor
        # img_t = redisAI.createTensorFromBlob('FLOAT', [1, 224, 224, 3], img_ba)
        # graphRunner = redisAI.createModelRunner('plant')
        # redisAI.modelRunnerAddInput(graphRunner, 'input', img_t)
        # redisAI.modelRunnerAddOutput(graphRunner, 'fc')

        # # run the graph and translate the result to python list
        # res = redisAI.tensorToFlatList(redisAI.modelRunnerRun(graphRunner)[0])
        # res_np = np.array(res)
        
        # proba = softmax(res_np)
        
        # for i, name in enumerate(labels):
        #     result += "{:.0f}% {}\n".format(100 * i, name)

        # redisgears.executeCommand('SET', 'result', result)
            
        # return (result, '')
        # x['value']['result'] = 'test'
        return x
    except:
        err = traceback.format_exc()
        log('addToGraphRunner: error:' + str(err))

def addToStream(x):
    try:
        redisgears.executeCommand(
            'xadd',
            'output:1', '*',
            'result', x['value']['result'])
    except:
        err = traceback.format_exc()
        log('addToGraphRunner: error:' + str(err))

gearsCtx('StreamReader').\
    map(addToGraphRunner).\
    foreach(addToStream). \
    register('input:0')
