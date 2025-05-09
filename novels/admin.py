# novels/admin.py
from django.contrib import admin
from .models import Novel, Chapter, ReviewCategory, Review, CategoryRating # Import new models

@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'updated_at', 'view_count')
    list_filter = ('status', 'author')
    search_fields = ('title', 'synopsis')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'novel', 'chapter_number', 'created_at')
    list_filter = ('novel',)
    search_fields = ('title', 'content', 'novel__title')

@admin.register(ReviewCategory)
class ReviewCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',) # Allow changing order in admin list

class CategoryRatingInline(admin.TabularInline): # Inline form for admin
    model = CategoryRating
    extra = 0 # Don't show extra empty forms

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('novel', 'user', 'overall_rating', 'created_at', 'updated_at')
    list_filter = ('novel', 'user', 'created_at')
    search_fields = ('content', 'novel__title', 'user__username')
    readonly_fields = ('created_at', 'updated_at') # Automatically set
    inlines = [CategoryRatingInline] # Allow editing category ratings within review admin

@admin.register(CategoryRating)
class CategoryRatingAdmin(admin.ModelAdmin):
     list_display = ('review', 'category', 'rating')
     list_filter = ('category', 'rating')
     search_fields = ('review__novel__title', 'review__user__username', 'category__name')