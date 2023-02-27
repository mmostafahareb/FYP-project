from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.response import Response
from .models import *
from .serializers import *
import croniter

class DependentViewSet(viewsets.ModelViewSet):
    queryset = Dependents.objects.all()
    serializer_class = DependentsSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        dependent_id = instance.dependent_id
        # Remove row from Users_dependents table
        Users_dependents.objects.filter(dependent_id=dependent_id).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        medical_history = Medical_History.objects.filter(dependent_id=instance.dependent_id)
        medical_history_serializer = MedicalHistorySerializer(medical_history, many=True)
        data = serializer.data
        data['medical_history'] = medical_history_serializer.data
        return Response(data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_id = instance.user_id
        # Delete all dependents for this user
        Dependents.objects.filter(users_dependents__user_id=user_id).delete()
        # Remove all rows from Users_dependents table for this user
        Users_dependents.objects.filter(user_id=user_id).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class LullabyAPIView(APIView):
    def post(self, request, format=None):
        serializer = LullabySerializer(data=request.data)
        if serializer.is_valid():
            sound = SavedSound(name=serializer.validated_data['name'],
                               sound_file=request.FILES['sound_file'])
            sound.save()
            # code to send lullaby to baby
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FeedingScheduleAPIView(APIView):
    def post(self, request, format=None):
        serializer = FeedingScheduleSerializer(data=request.data)
        if serializer.is_valid():
            schedule = FeedingSchedule.objects.first()
            if schedule:
                schedule.cron_schedule = serializer.validated_data['cron_schedule']
                schedule.is_currently_used = serializer.validated_data['is_currently_used']
                # validate the cron job
                try:
                    croniter.croniter(schedule.cron_schedule)
                except ValueError:
                    return Response({'message': 'invalid cron job'}, status=status.HTTP_400_BAD_REQUEST)
                schedule.save()
            else:
                FeedingSchedule.objects.create(cron_schedule=serializer.validated_data['cron_schedule'],
                                                is_currently_used=serializer.validated_data['is_currently_used'])
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        class FeedingScheduleAPIView(APIView):
            def get(self, request):
                # code for getting feeding schedule
                pass

            def post(self, request):
                # code for updating feeding schedule


                # code for updating the feeding schedule
                pass
    def get(self, request, format=None):
        schedule = FeedingSchedule.objects.first()
        if schedule:
            serializer = FeedingScheduleSerializer(schedule)
            return Response(serializer.data)
        return Response({'detail': 'Feeding schedule not found'}, status=status.HTTP_404_NOT_FOUND)

class FeedingStatusAPIView(APIView):
    def get(self, request, format=None):
        # code to get feeding status
        return Response({'feeding_status': 'OK'})

class DangerZoneAPIView(APIView):
    def get(self, request, format=None):
        zones = DangerZone.objects.all()
        serializer = DangerZoneSerializer(zones, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = DangerZoneSerializer(data=request.data)
        if serializer.is_valid():
            try:
                DangerZone.objects.get(file_location=serializer.validated_data['file_location'])
                return Response({'detail': 'Danger zone already exists'}, status=status.HTTP_400_BAD_REQUEST)
            except DangerZone.DoesNotExist:
                zone = DangerZone(description=serializer.validated_data['description'],
                                  file_location=serializer.validated_data['file_location'])
                zone.save()
                # code to use the danger zone file
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'detail': e.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
