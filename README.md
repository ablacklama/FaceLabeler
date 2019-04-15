# FaceLabeler
This is a lightweight desktop tool for capturing and labeling face images.

##### Disclaimer: if multiple faces are detected, only the bigger one will be kept.
# Usage
**`Get Image`** button will grab the current image of your face and desplay it in the top right. It will also show if no face was found. 

**`Save`** Will then save the image to you image directory, and save the current label (selected on the dropdown menu) to your labels csv file. 

**`Capture and Save`** is just a one way to get the image and save it. 

**`Enable Cap/Save Shortcut`** When enabled, you can simply press space to capture and save the image. This provides a fast way to capture many images.

**`GrayScale`** Toggles whether the image will be saved as single channel black and white.

**`Show Face Detection Box`** Toggles whether you can see the detected faces in real time.

Below the video stream is list of the labels with the number of images matching each label in the database.

You can also configure the face detection algorithm to run slower or faster in the settings. A value closer to 0.1 or 0 is recommended for snappy performace, but it can eat a lot of cpu. So pick whatever works for you. Keep in mind, if you set a .5 second delay, you will only be able to save a maximum of 2 pictures a second.

# Setup
The list of labels is read from a csv file (default: `labelConfig.csv`). To customize your labels, you need to change this csv file to include the labels of your choice. Each row should have two colums with and integer `index` and a `label` (example `0,Happy`). There is no hard limit on how many labels you can have.

You also need a csv file for your labels to be stored in. This should be empty until you start to gather images. Labels are stored as `filename,Label`.

Finally, you need a directory where the images will be saved to.

All of these can be configured in settings.


