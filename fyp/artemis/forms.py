from django import forms
from .models import Saved_Sounds

class SoundForm(forms.ModelForm):
    class Meta:
        model = Saved_Sounds
        fields = ('sound_file','sound_id','sound_size','sound_name','sound_length')
