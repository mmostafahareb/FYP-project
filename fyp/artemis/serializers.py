from rest_framework import serializers
from .models import *


class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Medical_History
        fields = ['event_id', 'dependent_id', 'date', 'description']


class DependentsSerializer(serializers.ModelSerializer):


    class Meta:
        model = Dependents
        fields = ['dependent_id', 'name', 'age', 'is_cat', 'breed', 'user_id']



class UsersSerializer(serializers.ModelSerializer):
    dependents = DependentsSerializer(many=True, read_only=True)

    class Meta:
        model = Users
        fields = ['user_id', 'name', 'email', 'phone', 'dependents']

class FeedingScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feeding_Schedule
        fields = ['cron_schedule', 'is_currently_used']


class SavedSoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Saved_Sounds
        fields = ['sound_id', 'sound_name', 'sound_size', 'sound_length', 'sound_location']


class PotentialEmergencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Potential_Emergencies
        fields = ['emer_id', 'description', 'occurrence', 'is_true']

class SensorDataSerializer(serializers.ModelSerializer):
    dependents = DependentsSerializer(many=True, read_only=True)

    class Meta:
        model = Sensor_Data
        fields = ['timestamp_id', 'sound_sensor', 'thermal_sensor', 'is_asleep', 'dependent_id', 'dependents']
