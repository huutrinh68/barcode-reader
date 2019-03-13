from pyzbar.pyzbar import decode
from PIL import Image
import cv2
import numpy as np
import time
import datetime
import pandas as pd
import platform

# camera number
camera_id = 0
window_name = "frame"
max_freq = [0]
sum_freq = [0]

def beep(freq, dur=100):
    """
        @param freq frequent
        @param dur  duration（ms）
    """
    if platform.system() == "Windows":
        import winsound
        winsound.Beep(freq, dur)
    elif platform.system() == "Linux":
        import os
        os.system("beep -f " + str(freq) + " -l 50")
    else:
        import os
        os.system('play -n synth %s sin %s' % (dur/1000, freq))
        
def gettime():
    return str(datetime.datetime.now())

def refesh(barcode_dict, max_freq, sum_freq):
    max_freq[0] = 0 
    sum_freq[0] = 0
    barcode_dict = {}
    
def make_dict(dict_result, key, max_freq, sum_freq):
    sum_freq[0] += 1
    key = str(key)
    
    if key not in dict_result.keys():
        dict_result[key] = 1
    else:
        dict_result[key] += 1
        if dict_result[key] > max_freq[0]:
            max_freq[0] = dict_result[key]
            percent = max_freq[0]/sum_freq[0]
            print(percent)
            
            if percent >= 0.9 and sum_freq[0] > 10:
                print("It is enough!")
                beep(2000, 500)
                time.sleep(2)
                return True, key        
            
    return False, ''
    
def edit_contrast(image, gamma):
    look_up_table = [np.uint8(255.0 / (1 + np.exp(-gamma * (i - 128.) / 255.)))
        for i in range(256)]
 
    result_image = np.array([look_up_table[value]
                             for value in image.flat], dtype=np.uint8)
    result_image = result_image.reshape(image.shape)
    return result_image

def barcode_read():
    # return list of barcode
    listBarcode  = []
    listTime     = []
    
    # storge barcode by dictionary
    barcode_dict = {}
    
    # capture video from camera
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        sys.exit()

    while True:
        ret, frame = cap.read()
        if ret:
            gray_scale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            image = edit_contrast(gray_scale, 15)
            data = decode(frame)
            if data:
                # show barcode content
                barcode = data[0][0].decode('utf-8', 'ignore')
                print(barcode)

                # push barcode into dictionary
                flag, key = make_dict(barcode_dict, barcode, max_freq, sum_freq)
                
                if flag == True:
                    listBarcode.append(key)
                    listTime.append(gettime())
                    
                    refesh(barcode_dict, max_freq, sum_freq)
                    
            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        else:
            continue

    cv2.destroyWindow(window_name)
    
    return listTime, listBarcode

    
if __name__=="__main__":
    listTime, listBarcode = barcode_read()
    print('list các code:', listBarcode)
    
    df = pd.DataFrame({'Time':listTime, 'Barcode':listBarcode})
    df.to_csv(datetime.datetime.today().strftime('%Y-%m-%d')+'.csv', mode='a', header=False)
