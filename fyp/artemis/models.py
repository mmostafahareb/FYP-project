from django.db import models
import cv2
import torch
from ultralytics import YOLO
proofing_objects = ['windows', 'shelves', 'plugs', 'doors']
url = 'C:\\Users\\Mohamad MostafaHAREB\\PycharmProjects\\pythonProject2\\fyp\\artemis\\ml_models'
# Load your YOLO models from .pt files
yolo_babies = YOLO(f"{url}/baby.pt")
yolo_cats = YOLO(f"{url}/cat.pt")
yolo_sleeping_babies = YOLO(f"{url}/baby_sleep.pt")
yolo_room_objects = [
    YOLO(f"{url}/{i}.pt") for i in proofing_objects
]


# Define a function to process the live stream and detect objects
def process_frame(frame):
    # Convert the frame to a PyTorch tensor and normalize it
    frame_tensor = torch.from_numpy(frame).permute(2, 0, 1).float() / 255.0

    # Perform object detection using your YOLO models
    with torch.no_grad():
        babies_detections = yolo_babies(frame_tensor.unsqueeze(0))[0]
        cats_detections = yolo_cats(frame_tensor.unsqueeze(0))[0]
        sleeping_babies_detections = yolo_sleeping_babies(frame_tensor.unsqueeze(0))[0]
        room_objects_detections = [
            model(frame_tensor.unsqueeze(0))[0] for model in yolo_room_objects
        ]

    # Filter detections based on confidence threshold (e.g., 0.2)
    confidence_threshold = 0.2
    babies_detections = [d for d in babies_detections if d['confidence'] > confidence_threshold]
    cats_detections = [d for d in cats_detections if d['confidence'] > confidence_threshold]
    sleeping_babies_detections = [d for d in sleeping_babies_detections if d['confidence'] > confidence_threshold]
    room_objects_detections = []
    for i, model in enumerate(yolo_room_objects):
        detections = model(frame)
        for detection in detections:
            detection_list = [detection, proofing_objects[i]]
        room_objects_detections.append(detection_list)

    # Return the detection results
    return {
        'babies': babies_detections,
        'cats': cats_detections,
        'sleeping_babies': sleeping_babies_detections,
        'proofing': room_objects_detections,
    }

class Users(models.Model):
    user_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
class Dependents(models.Model):
    dependent_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    is_cat = models.BooleanField()
    breed = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
class Medical_History(models.Model):
    event_id = models.IntegerField(primary_key=True)
    dependent_id = models.ForeignKey(Dependents, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=255)






class Feeding_Schedule(models.Model):
    cron_schedule = models.CharField(primary_key=True, max_length=255)
    is_currently_used = models.BooleanField()

class Saved_Sounds(models.Model):
    sound_id = models.IntegerField(primary_key=True)
    sound_name = models.CharField(max_length=255)
    sound_size = models.IntegerField()
    sound_length = models.IntegerField()
    sound_location = models.CharField(max_length=255,default='documents/')
    sound_file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Potential_Emergencies(models.Model):
    emer_id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=255)
    occurrence = models.DateTimeField()
    is_true = models.BooleanField()

class Sensor_Data(models.Model):
    timestamp_id = models.DateTimeField(primary_key=True)
    sound_sensor = models.IntegerField()
    thermal_sensor = models.IntegerField()
    is_asleep = models.BooleanField()
    dependent_id = models.ForeignKey(Dependents, on_delete=models.CASCADE)

class Danger_Zones(models.Model):
    zone_id = models.IntegerField(primary_key=True)
    file_location = models.CharField(max_length=255)