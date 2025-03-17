from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_photo', 'bio', 'phone_number', 'address', 'pincode', 'state']

from django import forms
from .models import Category

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label="Search by product name")
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label="Select Category")
