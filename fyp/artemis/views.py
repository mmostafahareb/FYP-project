from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
import logging
from django.shortcuts import render, redirect
from .serializers import *
from .forms import SoundForm
from django.http import StreamingHttpResponse, Http404
import os
from django.conf import settings
import requests
from django.http import JsonResponse
from .models import process_frame
import cv2
from django.http import StreamingHttpResponse
from PIL import Image
import threading
import time
import io
from django.http import HttpResponse
import wave
import pyaudio


# Initialize VideoCapture with your live stream URL
#cap = cv2.VideoCapture("http://10.1.130.50:8000/stream.mjpg")


def get_frame():
    video_url = "http://10.1.130.50:8000/stream.mjpg"
    cap = cv2.VideoCapture(video_url)
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture frame")
        return None

    cap.release()
    return frame

def baby_detection(request):

    frame = get_frame()
    logger.info(f'frame: {frame}')
    if frame is None:
        return JsonResponse({'error': 'Failed to capture frame'})

    detections = process_frame(frame)
    print(frame)
    babies_detections = detections['babies']
    sleeping_babies_detections = detections['sleeping_babies']

    # Extract the necessary information and return it in the JsonResponse
    response_data = []

    for detection in babies_detections:
        response_data.append({
            'location': detection['bbox'],
            'confidence': detection['confidence'],
            'is_sleeping': any(
                [d['confidence'] > 0.2 for d in sleeping_babies_detections if d['bbox'] == detection['bbox']]
            )
        })

    return JsonResponse(response_data, safe=False)


def cat_detection(request):
    frame = get_frame()
    if frame is None:
        return JsonResponse({'error': 'Failed to capture frame'})

    detections = process_frame(frame)
    cats_detections = detections['cats']

    # Extract the necessary information and return it in the JsonResponse
    response_data = []

    for detection in cats_detections:
        response_data.append({
            'location': detection['bbox'],
            'confidence': detection['confidence'],
        })

    return JsonResponse(response_data, safe=False)


def room_object_detection(request):
    frame = get_frame()
    if frame is None:
        return JsonResponse({'error': 'Failed to capture frame'})

    detections = process_frame(frame)
    room_objects_detections = detections['proofing']

    # Extract the necessary information and return it in the JsonResponse
    response_data = []

    for object_detections in room_objects_detections:
        for detection in object_detections:
            response_data.append({
                'object_type': detection['model_name'],
                'location': detection['bbox'],
                'confidence': detection['confidence'],
                'suggestion': proofing_suggestion(detection['model_name']),
            })

    return JsonResponse(response_data, safe=False)

def proofing_suggestion(model_name):
    proofing_objects = ['windows', 'shelves', 'plugs', 'doors']
    recommendations = ["make sure the windows are closed shut and have mesh and bars", "add doors to the shelves to prevent climbing", "close the plugs to prevent electrocution","make sure the door is shut to prevent escapes"]
    return recommendations[proofing_objects.index(model_name)]
def danger_zone_detection(request):
    frame = get_frame()
    if frame is None:
        return JsonResponse({'error': 'Failed to capture frame'})

    detections = process_frame(frame)
    babies_detections = detections['babies']
    cats_detections = detections['cats']
    room_objects_detections = detections['room_objects']

    # Check if a baby or a cat is near any room object
    in_danger_zone = False
    case = None

    for i, object_detections in enumerate(room_objects_detections):
        for obj_detection in object_detections:
            obj_bbox = obj_detection['bbox']

            for baby_detection in babies_detections:
                baby_bbox = baby_detection['bbox']
                if is_near(obj_bbox, baby_bbox):
                    in_danger_zone = True
                    case = f"Baby detected near room_object_{i}"
                    break

            for cat_detection in cats_detections:
                cat_bbox = cat_detection['bbox']
                if is_near(obj_bbox, cat_bbox):
                    in_danger_zone = True
                    case = f"Cat detected near room_object_{i}"
                    break

            if in_danger_zone:
                break

        if in_danger_zone:
            break

    return JsonResponse({
        'in_danger_zone': in_danger_zone,
        'case': case,})

def is_near(bbox1, bbox2, threshold=20):
    x1, y1, x2, y2 = bbox1
    x1_, y1_, x2_, y2_ = bbox2

    center1 = ((x1 + x2) / 2, (y1 + y2) / 2)
    center2 = ((x1_ + x2_) / 2, (y1_ + y2_) / 2)

    distance = ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5

    return distance <= threshold
class MedicalHistoryView(generics.ListCreateAPIView):
    queryset = Medical_History.objects.all()
    serializer_class = MedicalHistorySerializer


class DependentsView(generics.ListCreateAPIView):
    queryset = Dependents.objects.all()
    serializer_class = DependentsSerializer


class DependentDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dependents.objects.all()
    serializer_class = DependentsSerializer


class UsersView(generics.ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer


class UserDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer


class FeedingScheduleView(generics.ListCreateAPIView):
    queryset = Feeding_Schedule.objects.all()
    serializer_class = FeedingScheduleSerializer


def upload_sound(request):
    if request.method == 'POST':
        form = SoundForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            # Save file locally
            file = form.cleaned_data['sound_file']
            filename = file.name
            with open('media/' + filename, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Upload file to Flask app
            url = 'http://10.1.130.50:6500/upload_sound'
            files = {'file': (filename, open('media/' + filename, 'rb'))}

            try:
                response = requests.post(url, files=files, timeout=30000)
                if response.status_code == 200:
                    return redirect('success')
                else:
                    form.add_error(None, 'File upload failed')
            except requests.exceptions.RequestException as e:
                form.add_error(None, str(e))
        else:
            return render(request, 'upload.html', {'form': form})
    else:
        form = SoundForm()
        return render(request, 'upload.html', {'form': form})


class PotentialEmergencyView(generics.ListCreateAPIView):
    queryset = Potential_Emergencies.objects.all()
    serializer_class = PotentialEmergencySerializer


class SensorDataView(generics.ListCreateAPIView):
    queryset = Sensor_Data.objects.all()
    serializer_class = SensorDataSerializer

def success(request):
    return render(request, 'success.html')

def download_sound(request, sound_id):
    try:
        sound = Saved_Sounds.objects.get(sound_id=sound_id)
        file_path = os.path.join(settings.MEDIA_ROOT, sound.sound_file.path)
    except Saved_Sounds.DoesNotExist:
        raise Http404("Sound not found")

    if os.path.exists(file_path):
        def file_iterator(file_path, chunk_size=8192):
            with open(file_path, 'rb') as file:
                while True:
                    data = file.read(chunk_size)
                    if not data:
                        break
                    yield data

        response = StreamingHttpResponse(file_iterator(file_path))
        response['Content-Type'] = 'audio/mpeg'
        response['Content-Disposition'] = f'attachment; filename="{sound.sound_name}"'
        return response
    else:
        raise Http404("File not found")


def mjpeg_frame_generator():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to JPEG format
        img = Image.fromarray(frame)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        jpeg_frame = buffer.getvalue()

        # Yield a multipart HTTP response with the JPEG frame
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + jpeg_frame + b'\r\n'
        )

def video_stream(request):
    response = StreamingHttpResponse(
        mjpeg_frame_generator(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )
    return response
# Define the function to monitor detections and control the servo
def servo_control():
    state = 1
    last_seen_direction = None
    urls = [
        "http://10.1.130.50:6500/move-servo-right",
        "http://10.1.130.50:6500/move-servo-center",
        "http://10.1.130.50:6500/move-servo-left",
    ]

    while True:
        frame = get_frame()
        if frame is None:
            time.sleep(10)
            continue

        detections = process_frame(frame)
        babies_detections = detections['babies']
        cats_detections = detections['cats']

        # Check if a baby or a cat is detected
        if len(babies_detections) == 0 and len(cats_detections) == 0:
            if last_seen_direction == "right":
                state -= 1
            elif last_seen_direction == "left":
                state += 1

            if state < 0 or state > 2:
                state = 1

            requests.get(urls[state])

        # Update last_seen_direction based on the detected objects
        if len(babies_detections) > 0 or len(cats_detections) > 0:
            last_object = babies_detections[-1] if len(babies_detections) > 0 else cats_detections[-1]
            x_center = (last_object['bbox'][0] + last_object['bbox'][2]) / 2
            frame_center = frame.shape[1] / 2
            last_seen_direction = "right" if x_center > frame_center else "left"

        time.sleep(10)


def play_audio(request):
    audio_url = "http://10.1.130.50:6500/record"
    response = requests.get(audio_url, stream=True)

    if response.status_code == 200:
        audio_data = io.BytesIO(response.content)
        audio = wave.open(audio_data, 'rb')

        # Initialize PyAudio object
        p = pyaudio.PyAudio()

        # Open audio stream
        stream = p.open(format=p.get_format_from_width(audio.getsampwidth()),
                        channels=audio.getnchannels(),
                        rate=audio.getframerate(),
                        output=True)

        # Read and play audio in chunks
        chunk_size = 1024
        data = audio.readframes(chunk_size)
        while data:
            stream.write(data)
            data = audio.readframes(chunk_size)

        # Stop and close the audio stream
        stream.stop_stream()
        stream.close()

        # Terminate the PyAudio object
        p.terminate()

        # Delete any temporary files created by wave
        audio.close()

        return HttpResponse("Audio played successfully.")
    else:
        return HttpResponse("Failed to play audio. Could not fetch audio stream.", status=400)

# Start the servo_control function in a separate thread
servo_control_thread = threading.Thread(target=servo_control)
servo_control_thread.daemon = True
servo_control_thread.start()
