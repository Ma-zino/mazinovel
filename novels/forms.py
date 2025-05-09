# novels/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ReviewCategory, Review


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


# class RatingForm(forms.ModelForm):
#     """Form for users to submit a rating."""
#     # Use RadioSelect for star-like choices initially
#     rating = forms.ChoiceField(
#         choices=Rating.RATING_CHOICES,
#         widget=forms.RadioSelect,
#         label="Your Rating" # Optional label override
#     )

#     class Meta:
#         model = Rating
#         fields = ['rating'] # Only expose the rating field to the user

class ReviewForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Type your review here...'}),
        min_length=10, # Optional
        required=True
    )
    # No longer define category fields here directly, use __init__

    def __init__(self, *args, **kwargs):
        review_instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        self.review_instance = review_instance

        categories = ReviewCategory.objects.all()
        self.category_fields = [] # Store category field names

        initial_category_ratings = {}
        if review_instance:
             self.fields['content'].initial = review_instance.content
             for cat_rating in review_instance.category_ratings.all():
                 initial_category_ratings[cat_rating.category_id] = cat_rating.rating

        for category in categories:
             field_name = f'category_{category.id}'
             self.fields[field_name] = forms.ChoiceField(
                choices=[('', '---')] + [(i, str(i)) for i in range(1, 6)], # Add empty choice
                widget=forms.RadioSelect, # CSS/JS will style this later
                required=True, # Or False if you allow partial reviews
                label=category.name, # Keep the label for accessibility
                initial=initial_category_ratings.get(category.id),
                # Use specific classes for easier CSS/JS targeting maybe?
                # widget=forms.RadioSelect(attrs={'class': 'star-rating-radio-group'})
             )
             self.category_fields.append(field_name) # Keep track of these fields

    def category_rating_fields(self):
        """Helper method to yield only category rating fields for looping in template."""
        for name in self.category_fields:
            yield self[name] # Yield the BoundField object

    def save(self, novel, user):
        """Creates or updates the Review and related CategoryRatings."""
        content = self.cleaned_data['content']

        # Use update_or_create for the main Review
        review_obj, created = Review.objects.update_or_create(
            novel=novel,
            user=user,
            # Defaults are used if CREATING, update fields are used if UPDATING
            defaults={'content': content}
        )

        # Create/Update CategoryRating objects
        total_rating_sum = 0
        rating_count = 0
        categories = ReviewCategory.objects.all()
        for category in categories:
            field_name = f'category_{category.id}'
            rating_value = self.cleaned_data.get(field_name)
            if rating_value: # If user submitted a rating for this category
                 rating_value = int(rating_value)
                 CategoryRating.objects.update_or_create(
                     review=review_obj,
                     category=category,
                     defaults={'rating': rating_value}
                 )
                 total_rating_sum += rating_value
                 rating_count += 1

        # Calculate and save overall rating on the Review object
        if rating_count > 0:
            overall = round(total_rating_sum / rating_count, 1)
            review_obj.overall_rating = overall
            review_obj.save(update_fields=['overall_rating', 'content', 'updated_at']) # Ensure all updated fields are saved
        else:
            review_obj.overall_rating = None # Or 0.0 if no categories rated
            review_obj.save(update_fields=['overall_rating', 'content', 'updated_at'])

        return review_obj