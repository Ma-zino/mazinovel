# novels/models.py

from django.db import models
from django.contrib.auth.models import User # To link novels/chapters to authors
from django.utils.text import slugify # To create URL slugs
from django.urls import reverse # To generate URLs for models

# Create your models here.

class Novel(models.Model):
    """Represents a single novel."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('dropped', 'Dropped'),
    ]

    title = models.CharField(max_length=255)
    # Link to the user who wrote this novel.
    # on_delete=models.CASCADE means if the User is deleted, their Novels are also deleted.
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='novels')
    synopsis = models.TextField(blank=True) # Optional synopsis
    # Requires Pillow to be installed: pip install Pillow
    # 'upload_to' specifies a subdirectory within your MEDIA_ROOT
    cover_image = models.ImageField(upload_to='novel_covers/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    # A slug is a URL-friendly version of the title (e.g., "the-dark-tower")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True) # Automatically set when created
    updated_at = models.DateTimeField(auto_now=True)     # Automatically set when saved

    def __str__(self):
        """String representation of the Novel object."""
        return self.title

    def save(self, *args, **kwargs):
        """Override save method to auto-generate slug if blank."""
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug uniqueness if multiple novels have similar titles
            original_slug = self.slug
            counter = 1
            while Novel.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs) # Call the original save method

    def get_absolute_url(self):
        """Returns the URL to access a particular novel instance."""
        # We will define the URL pattern named 'novel_detail' later
        return reverse('novel_detail', kwargs={'slug': self.slug})


class Chapter(models.Model):
    """Represents a single chapter within a Novel."""

    # Link this chapter back to its Novel.
    # related_name allows accessing chapters from a novel object (e.g., my_novel.chapters.all())
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    chapter_number = models.PositiveIntegerField()
    content = models.TextField()
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure chapter numbers are unique within the same novel
        unique_together = ('novel', 'chapter_number')
        # Default ordering for chapters when queried
        ordering = ['novel', 'chapter_number']

    def __str__(self):
        """String representation of the Chapter object."""
        return f'{self.novel.title} - Chapter {self.chapter_number}: {self.title}'

    
    def get_absolute_url(self):
        """Returns the URL to access a particular chapter instance."""
        # Add the 'novels:' namespace here:
        return reverse('novels:chapter_detail', kwargs={'novel_slug': self.novel.slug, 'chapter_number': self.chapter_number})