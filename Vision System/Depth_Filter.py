import pyrealsense2 as rs
import numpy as np
import cv2
import math

def clamp(input, min, max):
    if input < min:
        return min
    elif input > max:
        return max
    else :
        return input

def label(text,image):
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)
    cv2.rectangle(image, (0, 445), ((text_size[0])[0] + 20, 480), (0, 0, 0), -1)
    cv2.putText(image, text, (10, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)


# Create a pipeline
pipeline = rs.pipeline()

# Create a config and configure the pipeline to stream
# different resolutions of color and depth streams
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)

if device_product_line == 'L500':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 15)
else:
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)

# Start streaming
profile = pipeline.start(config)

# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
#print("Depth Scale is: " , depth_scale)

# Create an align object
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames.
align_to = rs.stream.color
align = rs.align(align_to)

#set bgr limits for the chroma key filter
lower_HSV = np.array([20,50,50])
upper_HSV = np.array([40,255,255])
wh_coef = 1
percentage = 0
# Streaming loop
try:
    while True:
        # Get frameset of color and depth
        frames = pipeline.wait_for_frames()
        # frames.get_depth_frame() is a 640x360 depth image

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        # Validate that both frames are valid
        if not aligned_depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Find closest pixel and set clipping distance 200mm behind it
        #closest_pixel = np.amin(depth_image[np.nonzero(depth_image)])
        closest_pixel = 600
        clipping_distance_in_meters = closest_pixel + 200
        clipping_distance = clipping_distance_in_meters / depth_scale /1000

        # Remove background - Set pixels further than clipping_distance to grey
        grey_color = 0
        depth_image_3d = np.dstack((depth_image,depth_image,depth_image)) #depth image is 1 channel, color is 3 channels
        bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)

        # Render images:
        #   depth align to color on left
        #   depth on right
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        images = np.hstack((bg_removed, depth_colormap))

        # Creates a chroma key mask using the predefined bgr limits and sets
        # all other pixels to black
        HSV = cv2.cvtColor(bg_removed,cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(HSV , lower_HSV, upper_HSV)
        masked_image = np.copy(bg_removed)
        masked_image[mask == 0] = [0, 0, 0]

        ## creates a contour around the image and then draws a rectangle around the objects ##
        # convets image to grey
        imgray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
        # adds a blur to the image
        imgblur = cv2.GaussianBlur(imgray, (5, 5), 1)
        # draws the contours around the object
        ret, thresh = cv2.threshold(imgblur,30, 255, 0)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        percentages = []
        coords = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            objCor = len(approx)
            x, y, w, h = cv2.boundingRect(approx)
            # adds a filter to remove any contours that have an area that's too small
            if area > 1200:
                if objCor > 7:
                    #cv2.drawContours(color_image, cnt, -1, (255, 0, 0), 3)
                    # draws a rectangle around the contour based on the coordinates found above
                    cv2.rectangle(color_image, (x, y), (x + (w), y + (h)), (0, 255, 0), 2)

                    # finds the centre of the supposed grape and finds the depth at that point
                    xcentre = clamp((int(x + (w / 2))),0,479)
                    ycentre = clamp((int(y + (h / 4))),0,639)
                    ystalk = y - 10
                    cv2.circle(color_image,(xcentre, ystalk),2,(0,0,255),2,1)
                    depth = depth_image[xcentre, ycentre]
                    exp_area = 183285 * math.exp(-0.006*depth)
                    area_coef = 1 - (abs(1-(area/exp_area)))
                    if (w * 3) < h or h > (w*6):
                        wh_coef = 0.5
                    else : wh_coef = 1
                    if depth != 0 and depth < 1000:
                        percentage = clamp((round((100 * area_coef * wh_coef), 0)),0,100)
                        if (percentage is not None):
                            percentages.append(percentage)
                    if (xcentre is not None) and (ystalk is not None):
                        coords.append([xcentre,ycentre]) #change to stalk for submission
                    cv2.putText(color_image,'Certainty : ' + str(percentage) + '%',(x,y + h + 20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,0),2)
                    #cv2.putText(color_image,str(depth), (x, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (255, 0, 0), 2)

        ## Display the final image ##
        # Change names of images
        Image1 = bg_removed
        Image2 = HSV
        Image3 = masked_image
        Image4 = color_image
        #Add title for each image (label function at start of code)
        label('Remove Background', Image1)
        label('HSV', Image2)
        label('Chroma-key filter', Image3)
        label('Grape Centainty', Image4)
        if coords:
            cv2.putText(color_image, 'Pick Location X : ' + str((coords[0])[0]) + ' Y : ' + str((coords[0])[1]) + ' D : ' + str(depth_image[(coords[0])[0],(coords[0])[1]]), (0, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)
        #Add all images to one screen
        img_concate_hori_1 = np.concatenate((Image1,Image2), axis=1)
        img_concate_hori_2 = np.concatenate((Image3, Image4), axis=1)
        img_concate_vert = np.concatenate((img_concate_hori_1,img_concate_hori_2), axis=0)
        #Display the final images
        cv2.imshow('Grape Detection',img_concate_vert)
        key = cv2.waitKey(1)
        # Press esc or 'q' to close the image window
        if key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            break
finally:
    pipeline.stop()
