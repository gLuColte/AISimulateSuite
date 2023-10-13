##########################################################
####################### Libraries ########################
##########################################################
from ultralytics import YOLO
import numpy as np
import subprocess
import cv2
import math
import os
import time

##########################################################
###################### Parameters ########################
##########################################################


##########################################################
####################### Functions ########################
##########################################################

def open_ffmpeg_stream_process(stream_path, input_height, input_width):
    args = (
        "ffmpeg -re -f rawvideo -pix_fmt "
        f"rgb24 -s {input_height}x{input_width} -i pipe:0 -pix_fmt rgb24 -fflags nobuffer "
        f"-f rtsp {stream_path}"
    ).split()
    return subprocess.Popen(args, stdin=subprocess.PIPE)

##########################################################
######################### Main ###########################
##########################################################
if __name__ == "__main__":
    # Initialize Model
    model_path=os.environ['MODEL_PATH']
    model = YOLO(model_path)
    
    # RUN
    input_stream=os.environ['RTSP_INPUT']
    output_stream=os.environ['RTSP_OUTPUT']
    visualization=bool(int(os.environ['VISUALIZATION']))
    capture = cv2.VideoCapture(input_stream)
    
    # Reading first frame to prepare 
    success, img = capture.read()
    width, height, channels = img.shape
    print(f"Frame Height = {height}, Frame Width = {width}")

    # Setup output
    ffmpeg_process = open_ffmpeg_stream_process(output_stream, height, width)
          
    while True:
        success, img = capture.read()
        if not success:
            print("Failed to grab")
            time.sleep(1)
            continue
        results = model(img, stream=True)
        if visualization:
            # coordinates
            for r in results:
                img = r.plot()
                
                
                
        ffmpeg_process.stdin.write(img.astype(np.uint8).tobytes())
        
    capture.release()
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()