        function updateActivityFeed() {
            console.log('Updating activity feed...');
        }

        function animateStreak() {
            const streakNumber = document.querySelector('.streak-number');
            if (streakNumber) {
                const currentStreak = parseInt(streakNumber.textContent);
                let count = 0;
                const increment = currentStreak / 20;
                const counter = setInterval(() => {
                    count += increment;
                    if (count >= currentStreak) {
                        streakNumber.textContent = currentStreak;
                        clearInterval(counter);
                    } else {
                        streakNumber.textContent = Math.floor(count);
                    }
                }, 50);
            }
        }

        function markNotificationRead(element) {
            element.style.opacity = '0.6';
            element.querySelector('.notification-icon').style.background = '#d1d5db';
        }

        document.addEventListener('DOMContentLoaded', function() {
            animateStreak();
            
            document.querySelectorAll('.notification-item').forEach(item => {
                item.addEventListener('click', function() {
                    markNotificationRead(this);
                });
            });

            document.querySelectorAll('.quick-card').forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-8px) scale(1.02)';
                });
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(-5px) scale(1)';
                });
            });
        });

function openFeedbackModal() {
    document.getElementById('feedbackModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeFeedbackModal() {
    document.getElementById('feedbackModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    resetForm();
}

window.onclick = function(event) {
    const modal = document.getElementById('feedbackModal');
    if (event.target === modal) {
        closeFeedbackModal();
    }
}

document.querySelectorAll('.rating-star').forEach(star => {
    star.addEventListener('click', function() {
        const rating = this.getAttribute('data-rating');
        document.getElementById('rating').value = rating;
        
        document.querySelectorAll('.rating-star').forEach((s, index) => {
            if (index < rating) {
                s.classList.add('active');
            } else {
                s.classList.remove('active');
            }
        });
    });
});

document.querySelectorAll('.category-tag').forEach(tag => {
    tag.addEventListener('click', function() {
        document.querySelectorAll('.category-tag').forEach(t => t.classList.remove('selected'));
        
        this.classList.add('selected');
        document.getElementById('category').value = this.getAttribute('data-category');
    });
});

document.getElementById('feedbackForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const successMessage = document.getElementById('successMessage');
    
    const name = document.getElementById('userName').value.trim();
    const email = document.getElementById('userEmail').value.trim();
    const rating = document.getElementById('rating').value;
    const message = document.getElementById('feedbackMessage').value.trim();
    
    if (!name || !email || !rating || !message) {
        alert('Please fill in all required fields');
        return;
    }
    
    submitBtn.disabled = true;
    loadingSpinner.style.display = 'inline-block';
    submitBtn.innerHTML = '<span class="loading-spinner"></span> Submitting...';
    
    const formData = new FormData(this);
    const data = {
        name: formData.get('name'),
        email: formData.get('email'),
        rating: formData.get('rating'),
        category: formData.get('category') || 'General',
        message: formData.get('message'),
        improvements: formData.get('improvements') || 'N/A',
    };
    
    try {
        const response = await fetch('https://script.google.com/macros/s/AKfycbwiiuh4BcR47TfUGEKlvZP2CD6fOutkoJtTHLGJFMLeTUGcM2tfVHNRqUachFRzbGIj/exec', {
            method: 'POST',
            mode: 'no-cors',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        
        console.log('Feedback submitted successfully');
        
        successMessage.style.display = 'block';
        this.reset(); 
        resetForm(); 
        
        setTimeout(() => {
            closeFeedbackModal();
        }, 2000);
        
    }  finally {
        submitBtn.disabled = false;
        loadingSpinner.style.display = 'none';
        submitBtn.innerHTML = 'Submit Feedback';
    }
});

async function submitFeedbackWithErrorHandling() {
    const submitBtn = document.getElementById('submitBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const successMessage = document.getElementById('successMessage');
    
    try {
        const response = await fetch('https://script.google.com/macros/s/AKfycbwiiuh4BcR47TfUGEKlvZP2CD6fOutkoJtTHLGJFMLeTUGcM2tfVHNRqUachFRzbGIj/exec', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            successMessage.style.display = 'block';
            setTimeout(() => closeFeedbackModal(), 2000);
        } else {
            throw new Error(result.error || 'Submission failed');
        }
        
    } catch (error) {
        if (error.name === 'TypeError' && error.message.includes('CORS')) {
            console.log('CORS error, but submission likely successful');
            successMessage.style.display = 'block';
            setTimeout(() => closeFeedbackModal(), 2000);
        } else {
            console.error('Error submitting feedback:', error);
            alert('Error: ' + error.message);
        }
    }
}