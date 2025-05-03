# novels/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Novel, Chapter, Rating # Import Rating
# Import your forms
from .forms import CustomUserCreationForm, RatingForm
from django.http import Http404
from collections import OrderedDict
from django.core.paginator import Paginator
from django.db.models import F
# Import decorators and messages
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Need reverse for login redirect with next parameter
from django.urls import reverse

def novel_list(request):
    # Featured Novel
    featured_novel = Novel.objects.filter(status='published').order_by('-updated_at').first()
    # Popular Novels
    popular_novels = Novel.objects.filter(status='published').order_by('title')[:6]
    # Newly Added
    newly_added = Novel.objects.filter(status='published').order_by('-created_at')[:6]
    # Top Completed Novels
    completed_novels = Novel.objects.filter(status='completed').order_by('-updated_at')[:6]

    # --- Latest Chapter Updates with Pagination ---
    latest_chapters = Chapter.objects.filter(
        novel__status__in=['published', 'completed']
    ).select_related('novel', 'novel__author').order_by('-created_at')[:100]
    updates_by_novel = OrderedDict()
    for chapter in latest_chapters:
        novel = chapter.novel
        if novel.id not in updates_by_novel:
             updates_by_novel[novel.id] = {'novel': novel, 'chapters': []}
        if len(updates_by_novel[novel.id]['chapters']) < 3:
             updates_by_novel[novel.id]['chapters'].append(chapter)
    all_latest_updates_list = list(updates_by_novel.values())
    paginator = Paginator(all_latest_updates_list, 32)
    page_number = request.GET.get('page')
    latest_updates_page_obj = paginator.get_page(page_number)

    context = {
        'featured_novel': featured_novel,
        'popular_novels': popular_novels,
        'latest_updates_page_obj': latest_updates_page_obj,
        'newly_added': newly_added,
        'completed_novels': completed_novels,
    }
    return render(request, 'novels/novel_list.html', context)


# --- Corrected novel_detail view ---
def novel_detail(request, slug):
    novel = get_object_or_404(Novel.objects.select_related('author'), slug=slug)
    chapters = novel.chapters.all().order_by('chapter_number')
    user_rating = None
    rating_form_instance = RatingForm() # Default form instance

    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(novel=novel, user=request.user).first()

    if request.method == 'POST':
        # Ensure user is logged in to submit rating
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to rate novels.")
            login_url = reverse('login') + '?next=' + request.path # Construct login URL
            return redirect(login_url)

        # Use form instance bound to POST data
        rating_form_post = RatingForm(request.POST)
        if rating_form_post.is_valid():
            rating_obj, created = Rating.objects.update_or_create(
                novel=novel,
                user=request.user,
                defaults={'rating': rating_form_post.cleaned_data['rating']}
            )
            # Refresh novel to potentially update average rating (if denormalized later)
            # novel.refresh_from_db() # Maybe not strictly necessary unless caching heavily

            if created: messages.success(request, "Your rating has been submitted.")
            else: messages.success(request, "Your rating has been updated.")
            return redirect(novel.get_absolute_url()) # Redirect after successful POST
        else:
             # Form is invalid, pass THIS invalid form instance back to template
             rating_form_instance = rating_form_post
             messages.error(request, "There was an error submitting your rating. Please check the form.")

    # --- Increment View Count only on GET requests ---
    if request.method == 'GET':
        novel.view_count = F('view_count') + 1
        novel.save(update_fields=['view_count'])
        novel.refresh_from_db() # Crucial to get updated count for display

    # --- Prepare REVERSED rating choices for template loop ---
    rating_choices = list(rating_form_instance.fields['rating'].choices)
    rating_choices.reverse()
    # --- END REVERSE ---

    context = {
        'novel': novel,
        'chapters': chapters,
        'rating_form': rating_form_instance, # Pass form instance (may have errors on POST failure)
        'rating_choices': rating_choices,   # Pass reversed choices
        'user_rating': user_rating,
    }
    return render(request, 'novels/novel_detail.html', context)


# --- chapter_detail view ---
def chapter_detail(request, novel_slug, chapter_number):
    chapter = get_object_or_404(Chapter.objects.select_related('novel'), novel__slug=novel_slug, chapter_number=chapter_number)
    novel = chapter.novel
    previous_chapter = Chapter.objects.filter( novel=novel, chapter_number__lt=chapter.chapter_number ).order_by('-chapter_number').first()
    next_chapter = Chapter.objects.filter( novel=novel, chapter_number__gt=chapter.chapter_number ).order_by('chapter_number').first()

    context = {
        'novel': novel, 'chapter': chapter,
        'previous_chapter': previous_chapter, 'next_chapter': next_chapter,
    }
    return render(request, 'novels/chapter_detail.html', context)

# --- signup view ---
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'registration/signup.html', context)