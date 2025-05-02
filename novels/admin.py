# novels/admin.py
from django.contrib import admin
from .models import Novel, Chapter # Import your models

# Register your models here.

# Simple registration (we can customize this later)
admin.site.register(Novel) 
admin.site.register(Chapter)

# # --- Optional: Customize Admin Display ---
# # Example of customizing the Novel admin:
# class NovelAdmin(admin.ModelAdmin):
#     list_display = ('title', 'author', 'status', 'created_at', 'updated_at') # Columns to show in list view
#     list_filter = ('status', 'author') # Filters in the sidebar
#     search_fields = ('title', 'synopsis') # Fields to search
#     prepopulated_fields = {'slug': ('title',)} # Auto-fill slug from title (requires JS)
#     date_hierarchy = 'created_at' # Adds date navigation
# #
# admin.site.unregister(Novel) # Unregister the simple version first if you used it
# admin.site.register(Novel, NovelAdmin) # Register with the custom class

# # Example of customizing the Chapter admin:
# class ChapterAdmin(admin.ModelAdmin):
#     list_display = ('title', 'novel', 'chapter_number', 'updated_at')
#     list_filter = ('novel',)
#     search_fields = ('title', 'content')
#     ordering = ('novel', 'chapter_number') # Default sort order

# admin.site.unregister(Chapter) # Unregister the simple version first
# admin.site.register(Chapter, ChapterAdmin) # Register with the custom class