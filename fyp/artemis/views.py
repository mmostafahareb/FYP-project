from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from django.shortcuts import render, redirect
from .serializers import *
from .forms import SoundForm
from django.http import StreamingHttpResponse, Http404
import os
from django.conf import settings
import requests

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
            url = 'http://192.168.1.125:6400/upload_sound'
            files = {'file': (filename, open('media/' + filename, 'rb'))}

            try:
                response = requests.post(url, files=files, timeout=3000)
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