# novels/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg, Count, F # Import F and Count

class ReviewCategory(models.Model):
    """Categories for review ratings (Writing Quality, Character Design, etc.)"""
    name = models.CharField(max_length=100, unique=True) # Ensure names are unique
    order = models.PositiveIntegerField(default=0) # To control display order

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Review Categories"

    def __str__(self):
        return self.name

class Novel(models.Model):
    """Represents a single novel."""
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published'), ('completed', 'Completed'), ('on_hold', 'On Hold'), ('dropped', 'Dropped'),]
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='novels')
    synopsis = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='novel_covers/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0, editable=False)
    # Add genre field later if needed:
    # genres = models.ManyToManyField(Genre, related_name='novels', blank=True)

    def __str__(self): return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug; counter = 1
            while Novel.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'; counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('novels:novel_detail', kwargs={'slug': self.slug})

    # --- Review/Rating Calculation Methods ---
    def rating_count(self):
        """Returns the total number of Reviews for this novel."""
        return self.reviews.count() # 'reviews' is the related_name from Review model

    def average_rating(self):
        """Calculates average of the overall_rating field from Reviews."""
        # Ensure 'overall_rating' exists on the Review model
        avg = self.reviews.aggregate(Avg('overall_rating'))['overall_rating__avg']
        return round(avg, 1) if avg is not None else 0.0

    def average_rating_per_category(self):
        """ Returns a dictionary with average rating for each category. """
        category_averages = {}
        categories = ReviewCategory.objects.all() # Get all defined categories
        for category in categories:
             # Filter CategoryRating related to reviews of this novel AND for this specific category
             avg = CategoryRating.objects.filter(
                 review__novel=self,
                 category=category
             ).aggregate(Avg('rating'))['rating__avg']
             category_averages[category.name] = round(avg, 1) if avg is not None else 0.0
        return category_averages
    # -----------------------------------------


class Chapter(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    chapter_number = models.PositiveIntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('novel', 'chapter_number'); ordering = ['novel', 'chapter_number']
    def __str__(self): return f'{self.novel.title} - Ch. {self.chapter_number}: {self.title}'
    def get_absolute_url(self):
        return reverse('novels:chapter_detail', kwargs={'novel_slug': self.novel.slug, 'chapter_number': self.chapter_number})

class Review(models.Model):
    """Main review model, linking user, novel, text content, and overall rating."""
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='novel_reviews')
    content = models.TextField()
    # Overall rating might be calculated automatically or submitted (decide strategy)
    overall_rating = models.DecimalField(
        max_digits=2, decimal_places=1, # e.g., 4.5
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        null=True, blank=True # Make nullable if calculated after CategoryRatings saved
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'novel') # One review per user per novel
        ordering = ['-created_at']

    def __str__(self): return f"Review by {self.user.username} for {self.novel.title}"

    # If calculating overall after category ratings are saved:
    def calculate_and_save_overall(self):
        if self.pk: # Ensure review object exists
             ratings = self.category_ratings.all() # Use related_name
             if ratings.exists():
                 avg = ratings.aggregate(Avg('rating'))['rating__avg']
                 self.overall_rating = round(avg, 1) if avg else 0.0
                 self.save(update_fields=['overall_rating']) # Save efficiently
        return self.overall_rating


class CategoryRating(models.Model):
    """Stores the rating for a specific category within a specific Review."""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='category_ratings')
    category = models.ForeignKey(ReviewCategory, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        unique_together = ('review', 'category') # One rating per category per review

    def __str__(self): return f"{self.review}: {self.category.name} - {self.rating}"