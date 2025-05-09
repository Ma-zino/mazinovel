// mazinovel/novels/static/novels/js/novel_detail_review.js
document.addEventListener('DOMContentLoaded', function() {
    // --- Modal Functionality ---
    const reviewModal = document.getElementById('review-modal');
    const openModalBtn = document.querySelector('[data-modal-target="#review-modal"]');
    const closeModalBtns = document.querySelectorAll('[data-modal-close]');

    function openModal() {
        if (reviewModal) {
            reviewModal.style.display = 'flex';
            reviewModal.setAttribute('aria-hidden', 'false');
            initializeStarRatingsInModal(); // Initialize stars WHEN modal opens
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        }
    }

    function closeModal() {
         if (reviewModal) {
            reviewModal.style.display = 'none';
            reviewModal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = ''; // Restore background scrolling
        }
    }

    if (openModalBtn) { openModalBtn.addEventListener('click', openModal); }
    closeModalBtns.forEach(btn => { btn.addEventListener('click', closeModal); });

    // Close modal if clicking overlay (background)
     if (reviewModal) {
        const modalOverlay = reviewModal.querySelector('.modal-overlay');
         if (modalOverlay) {
            modalOverlay.addEventListener('click', closeModal);
         }
     }

    // --- Tab Functionality (Review Section Like/Newest) ---
    const reviewTabButtons = document.querySelectorAll('.reviews-section .review-tabs .tab-btn');
    if (reviewTabButtons.length > 0) {
        reviewTabButtons.forEach(button => {
            button.addEventListener('click', function() {
                 reviewTabButtons.forEach(btn => btn.classList.remove('active'));
                 this.classList.add('active');
                 const tabType = this.getAttribute('data-tab');
                 console.log(`TODO: Fetch/display reviews for tab: ${tabType}`);
                 // Add AJAX call here later
            });
        });
    }

    // --- Interactive Star Rating Input within Modal ---
    function initializeStarRatingsInModal() {
        const modalRatingWidgets = reviewModal?.querySelectorAll('.star-rating-widget');

        if (modalRatingWidgets) {
            modalRatingWidgets.forEach(widget => {
                const stars = widget.querySelectorAll('.visible-stars .star-input');
                const fieldName = widget.dataset.fieldName;
                const hiddenRadios = widget.querySelectorAll(`.hidden-radio-group input[name="${fieldName}"]`);
                let currentRating = 0;

                 // Find initially checked value from hidden radios
                hiddenRadios.forEach(radio => { if (radio.checked) { currentRating = parseInt(radio.value || 0); } });

                 // Set initial visible stars appearance
                updateVisibleStars(widget.querySelector('.visible-stars'), currentRating); // Pass visible stars container

                stars.forEach(star => {
                    const starValue = parseInt(star.dataset.value);

                    star.addEventListener('mouseover', () => {
                         updateVisibleStars(widget.querySelector('.visible-stars'), starValue, true); // Hover preview
                    });
                     star.addEventListener('mouseleave', () => {
                          updateVisibleStars(widget.querySelector('.visible-stars'), currentRating); // Revert to selected
                    });
                     star.addEventListener('click', () => {
                          currentRating = starValue; // Update the rating value
                          // Check the corresponding hidden radio
                          hiddenRadios.forEach(radio => { radio.checked = (parseInt(radio.value) === currentRating); });
                          updateVisibleStars(widget.querySelector('.visible-stars'), currentRating); // Update visuals
                          updateTotalScoreInModal(); // Recalculate overall
                      });
                 });
            });
             updateTotalScoreInModal(); // Initial calculation
        }
    } // End initializeStarRatingsInModal

     // Helper to update the visible stars' classes based on rating value
     function updateVisibleStars(visibleStarsContainer, rating, isHover = false) {
         const stars = visibleStarsContainer?.querySelectorAll('.star-input');
         if (!stars) return;
         stars.forEach(star => {
              const starValue = parseInt(star.dataset.value);
              star.classList.remove('selected', 'hover');
              if (starValue <= rating) {
                  star.classList.add(isHover ? 'hover' : 'selected');
              }
          });
      }

    // Calculate and Update Total Score Display in Modal
    function updateTotalScoreInModal() {
         let totalScoreSum = 0;
         let ratingCount = 0;
         const scoreDisplayValueEl = reviewModal?.querySelector('#total-score-val');
         const scoreDisplayStarsContainer = reviewModal?.querySelector('.total-score-display .stars-display.total-stars');

         if (!scoreDisplayValueEl || !scoreDisplayStarsContainer) return;

         const checkedInputs = reviewModal?.querySelectorAll('.review-criteria-ratings .star-rating-widget input[type="radio"]:checked');

         if (checkedInputs) {
             checkedInputs.forEach(input => {
                 const rating = parseInt(input.value);
                 if (rating > 0) {
                     totalScoreSum += rating;
                     ratingCount++;
                 }
             });
         }

         const finalAvgScore = ratingCount > 0 ? (totalScoreSum / ratingCount) : 0.0;
         scoreDisplayValueEl.textContent = finalAvgScore.toFixed(1);

         // Update total score visual stars
         const averageForStars = parseFloat(finalAvgScore);
         const avgFloor = Math.floor(averageForStars);
         const avgDiff = averageForStars - avgFloor;

         scoreDisplayStarsContainer.innerHTML = ''; // Clear old stars/spans
          for (let i = 1; i <= 5; i++) {
             const starSpan = document.createElement('span'); // Using span for simplicity
             starSpan.classList.add('star');
             starSpan.innerHTML = '★'; // Simple text star, easier than SVG manipulation here maybe

             if (i <= avgFloor) { starSpan.classList.add('filled'); }
             // Add half-star logic if desired with CSS or different char
             scoreDisplayStarsContainer.appendChild(starSpan);
         }
     }

     // Could be called initially if modal is built on page load and data is present
     // initializeStarRatingsInModal(); // Maybe call once if form exists, not just on open?

}); // End DOMContentLoaded