import cv2
import numpy as np
import math
import config, load_model

blue = (255,0,0)
green = (0,255,0)
red = (0,0,255)
yellow = (0,255,255)
white = (255,255,255)
orange = (0,165,255)

# Load video
videosrc = "TownCentre.mp4"
video = cv2.VideoCapture(videosrc)

#config for different datasets
if videosrc == 'TownCentre.mp4':
    configuration = config.towncentre
    distance = configuration.get('distance')
    h = configuration.get('height')
    w = configuration.get('width')

if videosrc == 'PETS2009.mp4':
    configuration = config.pets2009
    distance = configuration.get('distance')
    h = configuration.get('height')
    w = configuration.get('width')

if videosrc == 'VIRAT.mp4':
    configuration = config.virat
    distance = configuration.get('distance')
    h = configuration.get('height')
    w = configuration.get('width')

# Load Yolo
net, output_layers, classes = load_model.loading_dependencies()

def calculateCentroid(xmin,ymin,xmax,ymax):

    xmid = ((xmax+xmin)/2)
    ymid = ((ymax+ymin)/2)
    centroid = (xmid,ymid)

    return xmid,ymid,centroid

def get_distance(x1,x2,y1,y2):
  distance = math.sqrt((x1-x2)**2 + (y1-y2)**2)
  return distance

def main():

    while True:

        centroids = []
        box_colors = []
        detectedBox = []
        ret, frame = video.read() 

        if ret:
            frame_resized = cv2.resize(frame, (416,416)) # resize frame for prediction       
        else:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.IMREAD_COLOR)
        height, width, channels = frame.shape

        # Detecting objects
        blob = cv2.dnn.blobFromImage(frame_resized, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

        net.setInput(blob)
        outs = net.forward(output_layers)

        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]

                xmin = x
                ymin = y
                xmax = (x + w)
                ymax = (y + h)

                label = str(classes[class_ids[i]])
                if label == 'person':
                    #calculate centroid point for bounding boxes
                    xmid, ymid, centroid = calculateCentroid(xmin,ymin,xmax,ymax)
                    detectedBox.append([xmin,ymin,xmax,ymax,centroid])

                    my_color = 0
                    for k in range (len(centroids)):
                        c = centroids[k]
                        
                        if get_distance(c[0],centroid[0],c[1],centroid[1]) <= distance:
                            box_colors[k] = 1
                            my_color = 1
                            cv2.line(frame, (int(c[0]),int(c[1])), (int(centroid[0]),int(centroid[1])), yellow, 1,cv2.LINE_AA)
                            cv2.circle(frame, (int(c[0]),int(c[1])), 3, orange, -1,cv2.LINE_AA)
                            cv2.circle(frame, (int(centroid[0]),int(centroid[1])), 3, orange, -1,cv2.LINE_AA)
                            break
                    centroids.append(centroid)
                    box_colors.append(my_color)        

        for i in range (len(detectedBox)):
            x1 = detectedBox[i][0]
            y1 = detectedBox[i][1]
            x2 = detectedBox[i][2]
            y2 = detectedBox[i][3]
            
            #for ellipse output
            xc = ((x2+x1)/2)
            yc = y2-5
            centroide = (int(xc),int(yc))

            if box_colors[i] == 0:
                cv2.rectangle(frame,(x1,y1),(x2,y2), white, 2,cv2.LINE_AA)
                label = "safe"
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)

                y1label = max(y1, labelSize[1])
                cv2.rectangle(frame, (x1, y1label - labelSize[1]),(x1 + labelSize[0], y1 + baseLine), (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, label, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, green, 1,cv2.LINE_AA)
            else:
                cv2.rectangle(frame,(x1,y1),(x2,y2), red, 2)
                # cv2.ellipse(frame, centroide, (35, 19), 0.0, 0.0, 360.0, red, 2)

                label = "unsafe"
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)

                y1label = max(y1, labelSize[1])
                cv2.rectangle(frame, (x1, y1label - labelSize[1]),(x1 + labelSize[0], y1 + baseLine), (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, label, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, orange, 1,cv2.LINE_AA)

        cv2.imshow("Social Distance System", frame)

        if cv2.waitKey(1) >= 0:  
            break

    video.release()

if __name__ == '__main__':
    main()
    cv2.destroyAllWindows()