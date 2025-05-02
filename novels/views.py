# novels/views.py
from django.shortcuts import render, get_object_or_404, redirect 
from .models import Novel, Chapter
from django.views import generic # Can use generic view later if preferred
from .forms import CustomUserCreationForm
from django.http import Http404 # For 404 error handling 
from collections import OrderedDict # For ordered dictionary to maintain order of updates
from django.core.paginator import Paginator # Import Paginator



def novel_list(request):
    # Featured Novel
    featured_novel = Novel.objects.filter(status='published').order_by('-updated_at').first()

    # Popular Novels (Placeholder ordering)
    popular_novels = Novel.objects.filter(status='published').order_by('title')[:6] # Fetch 6

    # Newly Added
    newly_added = Novel.objects.filter(status='published').order_by('-created_at')[:6] # Fetch 6

    # Top Completed Novels
    completed_novels = Novel.objects.filter(status='completed').order_by('-updated_at')[:6]

    # --- REVISED LOGIC for Latest Chapter Updates with Pagination ---
    # Fetch recent chapters across published/completed novels
    latest_chapters = Chapter.objects.filter(
        novel__status__in=['published', 'completed']
    ).select_related('novel', 'novel__author').order_by('-created_at')[:100] # Fetch a larger initial pool (e.g., 100 chapters)

    # Process to group by novel, keeping track of latest 3 per novel
    updates_by_novel = OrderedDict()
    for chapter in latest_chapters:
        novel = chapter.novel
        if novel.id not in updates_by_novel:
             updates_by_novel[novel.id] = {'novel': novel, 'chapters': []}
        if len(updates_by_novel[novel.id]['chapters']) < 3:
             updates_by_novel[novel.id]['chapters'].append(chapter)

    # Convert the dictionary values to a list (this contains ALL novels with recent updates)
    all_latest_updates_list = list(updates_by_novel.values())

    # --- Implement Pagination ---
    items_per_page = 32 # 4 columns * 8 rows
    paginator = Paginator(all_latest_updates_list, items_per_page)
    page_number = request.GET.get('page') # Get page number from URL (?page=...)
    latest_updates_page_obj = paginator.get_page(page_number) # Get the Page object

    context = {
        'featured_novel': featured_novel,
        'popular_novels': popular_novels,
        'latest_updates_page_obj': latest_updates_page_obj, # Pass the paginated page object
        'newly_added': newly_added,
        'completed_novels': completed_novels,
    }
    return render(request, 'novels/novel_list.html', context)

# --- novel_detail view remains the same ---
def novel_detail(request, slug):
    novel = get_object_or_404(Novel, slug=slug)
    chapters = novel.chapters.all() # Ordering is handled by Chapter.Meta
    context = {
        'novel': novel,
        'chapters': chapters,
    }
    return render(request, 'novels/novel_detail.html', context)


# ADD THIS FUNCTION:
def chapter_detail(request, novel_slug, chapter_number):
    """View function for displaying a single chapter's content."""
    # Get the specific chapter, ensuring it matches the novel slug and chapter number
    # Using filter() first and then get() is one way, or nested lookups
    chapter = get_object_or_404(Chapter, novel__slug=novel_slug, chapter_number=chapter_number)
    novel = chapter.novel # Get the parent novel easily

    # Find previous and next chapters (if they exist)
    # We rely on the default ordering defined in Chapter.Meta
    previous_chapter = Chapter.objects.filter(
        novel=novel,
        chapter_number__lt=chapter.chapter_number
    ).order_by('-chapter_number').first() # Get the highest chapter number less than current

    next_chapter = Chapter.objects.filter(
        novel=novel,
        chapter_number__gt=chapter.chapter_number
    ).order_by('chapter_number').first() # Get the lowest chapter number greater than current

    context = {
        'novel': novel,
        'chapter': chapter,
        'previous_chapter': previous_chapter,
        'next_chapter': next_chapter,
    }
    return render(request, 'novels/chapter_detail.html', context)

def signup(request):
    if request.method == 'POST':
        # Use the custom form
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Optional: Add a success message here using django.contrib.messages
            return redirect('login') # Redirect to login after successful registration
    else:
        # Use the custom form
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'registration/signup.html', context)