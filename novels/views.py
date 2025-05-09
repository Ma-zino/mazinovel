# novels/views.py
from django.shortcuts import render, get_object_or_404, redirect, reverse # Add reverse
from .models import Novel, Chapter, Review, ReviewCategory, CategoryRating
from .forms import CustomUserCreationForm, ReviewForm # Use ReviewForm
from django.http import Http404, HttpResponseForbidden # Add HttpResponseForbidden
from collections import OrderedDict
from django.core.paginator import Paginator
from django.db.models import F, Avg, Count # Add Avg, Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction # For atomic review saving

# novel_list view (KEEP AS IS for now)
def novel_list(request):
     # ... (existing novel_list logic remains the same) ...
    featured_novel = Novel.objects.filter(status='published').order_by('-updated_at').first()
    popular_novels = Novel.objects.filter(status='published').order_by('title')[:6]
    newly_added = Novel.objects.filter(status='published').order_by('-created_at')[:6]
    completed_novels = Novel.objects.filter(status='completed').order_by('-updated_at')[:6]
    latest_chapters = Chapter.objects.filter(novel__status__in=['published', 'completed']).select_related('novel', 'novel__author').order_by('-created_at')[:100]
    updates_by_novel = OrderedDict()
    for chapter in latest_chapters:
        novel = chapter.novel
        if novel.id not in updates_by_novel: updates_by_novel[novel.id] = {'novel': novel, 'chapters': []}
        if len(updates_by_novel[novel.id]['chapters']) < 3: updates_by_novel[novel.id]['chapters'].append(chapter)
    all_latest_updates_list = list(updates_by_novel.values())
    paginator = Paginator(all_latest_updates_list, 32)
    page_number = request.GET.get('page')
    latest_updates_page_obj = paginator.get_page(page_number)
    context = { 'featured_novel': featured_novel, 'popular_novels': popular_novels, 'latest_updates_page_obj': latest_updates_page_obj, 'newly_added': newly_added, 'completed_novels': completed_novels }
    return render(request, 'novels/novel_list.html', context)


# --- UPDATED novel_detail view for Reviews ---
def novel_detail(request, slug):
    novel = get_object_or_404(Novel.objects.select_related('author'), slug=slug)
    chapters = novel.chapters.all().order_by('chapter_number')

    # Fetch existing reviews for this novel
    reviews = Review.objects.filter(novel=novel).select_related('user') # Add prefetch_related('category_ratings') if needed frequently
    # Calculate overall average and count (using model methods)
    average_rating = novel.average_rating()
    rating_count = novel.rating_count()
    # Get average rating PER category (using model method)
    category_averages = novel.average_rating_per_category()

    user_review = None # The logged-in user's existing review, if any
    review_form = None # Initialize form to None

    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first() # Check if user already reviewed

        if request.method == 'POST':
            # User is submitting or updating a review
            # Pass instance=user_review if updating, None if creating
            form_instance = user_review if user_review else None
            review_form = ReviewForm(request.POST, instance=form_instance)

            if review_form.is_valid():
                try:
                    # Use transaction to ensure Review and CategoryRatings save together
                    with transaction.atomic():
                        saved_review = review_form.save(novel=novel, user=request.user)
                         # Ensure overall rating is recalculated if necessary
                         # saved_review.calculate_and_save_overall() # Uncomment if auto-calculation isn't reliable via signals/overrides
                except Exception as e:
                     messages.error(request, f"An error occurred saving your review: {e}")
                else:
                     messages.success(request, "Your review has been submitted/updated successfully.")
                     return redirect(novel.get_absolute_url()) # Redirect to prevent re-POST

            else: # Form is invalid
                messages.error(request, "Please correct the errors in your review.")
                 # The invalid form (review_form) will be passed to the template

        else: # GET request
             # Prepare form for display in modal (prefilled if user_review exists)
             review_form = ReviewForm(instance=user_review)

    # --- View Count ---
    if request.method == 'GET':
        novel.view_count = F('view_count') + 1
        novel.save(update_fields=['view_count'])
        novel.refresh_from_db()

    # Get categories for displaying in the modal form (even if not logged in?)
    review_categories = ReviewCategory.objects.all()

    context = {
        'novel': novel,
        'chapters': chapters,
        'average_rating': average_rating, # Pass calculated average
        'rating_count': rating_count, # Pass calculated count
        'category_averages': category_averages, # Pass averages per category
        'reviews': reviews, # Pass the list of existing reviews
        'user_review': user_review, # Pass user's existing review or None
        'review_form': review_form, # Pass the ReviewForm instance (bound or unbound)
        'review_categories': review_categories # Pass categories for the form/display
    }
    return render(request, 'novels/novel_detail.html', context)

# --- chapter_detail view (Unchanged) ---
def chapter_detail(request, novel_slug, chapter_number):
    # ... (existing chapter_detail logic) ...
    chapter = get_object_or_404(Chapter.objects.select_related('novel'), novel__slug=novel_slug, chapter_number=chapter_number)
    novel = chapter.novel
    previous_chapter = Chapter.objects.filter( novel=novel, chapter_number__lt=chapter.chapter_number ).order_by('-chapter_number').first()
    next_chapter = Chapter.objects.filter( novel=novel, chapter_number__gt=chapter.chapter_number ).order_by('chapter_number').first()
    context = { 'novel': novel, 'chapter': chapter, 'previous_chapter': previous_chapter, 'next_chapter': next_chapter, }
    return render(request, 'novels/chapter_detail.html', context)

# --- signup view (Unchanged) ---
def signup(request):
    # ... (existing signup logic) ...
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid(): form.save(); messages.success(request, 'Registration successful. Please log in.'); return redirect('login')
    else: form = CustomUserCreationForm()
    context = {'form': form}; return render(request, 'registration/signup.html', context)