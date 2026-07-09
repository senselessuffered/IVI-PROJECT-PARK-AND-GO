from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:   
        model = get_user_model()
        fiels = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data['email']

        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует.')
        
        return email
    pass
