

import os
import subprocess
from fastapi import FastAPI, UploadFile, File

app = FastAPI()

IMAGES_FOLDER = 'resources'
RESULTS_FILE = 'runs/detect/detections.txt'

# @app.on_event("startup")
# async def startup_event():
#     clear_resources_directory()


def clear_resources_directory():
    # Get the list of files in the resources directory
    file_list = os.listdir(IMAGES_FOLDER)

    # Iterate over the files and remove them
    for file_name in file_list:
        file_path = os.path.join(IMAGES_FOLDER, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

@app.get("/")
def hello():
    return "Hello, World!"


@app.post("/image")
async def receive_image(file: UploadFile = File(...)):
    # Save the received image
    file_path = f"{IMAGES_FOLDER}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Run the command to execute detect.py
    command = f"python3 detect.py --weights best-4.pt --source {IMAGES_FOLDER} --save-txt --conf-thres 0.60"
    subprocess.run(command, shell=True)

    if os.path.isfile(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            detections = f.readlines()
        detections_cleaned = [detection.strip() for detection in detections]
    else:
        detections_cleaned = ["NULL"]

    # Check if the first two elements are the same
    if len(detections_cleaned) >= 2 and detections_cleaned[0] == detections_cleaned[1]:
        detected_value = detections_cleaned[0]
    # Check if the last two elements are the same
    elif len(detections_cleaned) >= 2 and detections_cleaned[-1] == detections_cleaned[-2]:
        detected_value = detections_cleaned[-1]
    else:
        detected_value = detections_cleaned[-1]

    # Send the detected value back as a response
    return {"status": 200, "remarks": "file uploaded successfully", "detected_value": detected_value}
