from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Email

class ComposeEmailForm(forms.ModelForm):
    class Meta:
        model = Email
        # We allow the user to type the 'Sender' to simulate different people
        fields = ['sender', 'subject', 'body'] 
        widgets = {
            'sender': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'From (e.g., angry_customer@gmail.com)'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your message here...'}),
        }

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required')
    email = forms.EmailField(max_length=254, required=True, help_text='Required for notifications')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    # This looks complex, but it just adds "class='form-control'" to every field
    # So they look pretty in Bootstrap automatically.
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control mb-2'})