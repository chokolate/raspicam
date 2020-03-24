#! /usr/local/bin/python3

from imutils.video import VideoStream
import cv2
import time
import datetime
import imutils
import os
import boto3
import asyncio
import pdb
from time import sleep

  
class Camera:
      
## instance method 1
  async def record(self):
    vs = VideoStream().start()
    time.sleep(2.0)
    firstFrame = None
    #pdb.set_trace()
    while True:
      frame = vs.read()
      text = "Unoccupied"
      
      if frame is None:
        break
      frame = imutils.resize(frame, width=500)
      gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      gray = cv2.GaussianBlur(gray, (21, 21), 0)
      
      if firstFrame is None:
        firstFrame = gray
        continue
      frameDelta = cv2.absdiff(firstFrame, gray)
      thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
      thresh = cv2.dilate(thresh, None, iterations=2)
      cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      cnts = imutils.grab_contours(cnts)      
      
      for c in cnts:
        if cv2.contourArea(c)<500:
          continue
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        text = "Occupied"
        await self.saveFrame(frame);
      cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
      cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I :%M:%S%p"),(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

      cv2.imshow("Security Feed", frame)
      key = cv2.waitKey(1) & 0xFF
      if key == ord("q"):
        break

    vs.stop()
    cv2.destroyAllWindows()

## instance method 2
  async def saveFrame(self, frame):
    session = boto3.Session(
    aws_access_key_id='AKIAWZXAQBR336CGYA5A',
    aws_secret_access_key='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',
    )
    s3 = session.resource('s3')
    bucket_name = 'webcamfotos'
    save_as = datetime.datetime.now().strftime("%-H.%-M.%S")
    filename = (f"{save_as}.png")
    ##file_path = '/Users/choka/Desktop/editorfiles/webcamAlbum'
    cv2.imwrite(filename, frame)
    object = s3.Object(bucket_name, filename)
    object.put(Body=open(filename, 'rb'))
    
    client = boto3.client('rekognition', region_name='us-west-2', aws_access_key_id='AKIAWZXAQBR336CGYA5A', aws_secret_access_key='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' )
    
    with open(filename, 'rb') as image:
        response = client.detect_labels(Image={'Bytes': image.read()})
        for label in response['Labels']:
          print (label['Name'] + ' : ' + str(label['Confidence']))

    os.remove(filename)
   

async def main():
  webcam = Camera();
  await webcam.record();

if __name__ == "__main__":
  print("calling main...")
  asyncio.run(main())


  
