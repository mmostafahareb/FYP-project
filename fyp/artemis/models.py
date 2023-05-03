
from django.db import models

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