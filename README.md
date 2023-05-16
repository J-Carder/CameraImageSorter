This is a simple GUI program made with Python and TKinter that sorts a single folder of images into year (ie. 2023) and year-month-day (ie. 2023-05-15) folders.

# Usage

Download cameraImageSorter.exe and data.csv (will get created automatically if not found, data.csv just saves your settings so you don't have to re-enter them each time) to a directory on your PC.

Make a temporary folder to store images straight out of the camera.

Run cameraImageSorter.exe.

In CameraImageSorter fill out the temporary path "Import from:" and the destination path "Copy to:". 

## Options

### import
To import files (copy from one temp to dest) select the "import" checkbox.

### clean 
Selecting the "clean" checkbox will DELETE all files in the temporary folder ("Import from:") after copying them.

## Run!

Once ready click run and your images will be copied over and sorted!

# Folder Structure

CameraImageSorter currently supports only one folder structure which is as follows:

Year*\
|\
Year-Month-Day*\
|\
P100000.jpg

\* = folders

# Other

CameraImageSorter won't duplicate images or folders if they already exist.

The latest image date is shown in the bottom right.