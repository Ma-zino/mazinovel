# novels/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    # --- Define fields inherited from UserCreationForm with desired widgets ---
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}) # Add placeholder
    )
    password1 = forms.CharField(
        label="Password", # Keep label if needed internally
        widget=forms.PasswordInput(attrs={'placeholder': 'Create password'}) # Add placeholder
    )
    password2 = forms.CharField(
        label="Confirm Password", # Keep label if needed internally
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}) # Add placeholder
    )

    # --- Keep your custom fields ---
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'First Name (Optional)'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name (Optional)'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Ensure all desired fields are listed correctly
        # The order here might influence default rendering if using {{ form.as_p }} etc.
        # but doesn't affect manual rendering in the template.
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2') # Removed the UserCreationForm.Meta.fields + ... to avoid duplication

    def clean_email(self):
        """
        Ensure the email address is unique.
        """
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists(): # Use iexact for case-insensitive check
            raise forms.ValidationError("An account with this email address already exists.")
        return email