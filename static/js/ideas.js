let userLikes = new Set();

async function loadUserLikes() {
    try {
        const response = await fetch('/api/user_likes');
        if (response.ok) {
            const likedIdeas = await response.json();
            if (Array.isArray(likedIdeas)) {
                userLikes.clear();
                likedIdeas.forEach(ideaId => {
                    userLikes.add(parseInt(ideaId));
                    const likeButton = document.getElementById(`like-btn-${ideaId}`);
                    if (likeButton) {
                        const heart = likeButton.querySelector('.heart');
                        if (heart) {
                            heart.textContent = '❤️';
                            likeButton.classList.add('liked');
                        }
                    }
                });
            }
        }
    } catch (error) {
        console.error('Error loading user likes:', error);
    }
}

async function likeIdea(ideaId) {
    if (!ideaId) {
        showToast('Unable to like: Invalid idea', 'error');
        return;
    }

    try {
        const response = await fetch(`/like_idea/${ideaId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        
        const newLikeCount = data.like_count || 0;
        const likeCountElement = document.getElementById(`like-count-${ideaId}`);
        const likeButton = document.getElementById(`like-btn-${ideaId}`);
        const heart = likeButton ? likeButton.querySelector('.heart') : null;

        if (likeCountElement) likeCountElement.textContent = newLikeCount;

        if (heart && likeButton) {
            if (data.liked) {
                userLikes.add(ideaId);
                heart.textContent = '❤️';
                likeButton.classList.add('liked');
                showToast('Idea liked!', 'success');
            } else {
                userLikes.delete(ideaId);
                heart.textContent = '🤍';
                likeButton.classList.remove('liked');
                showToast('Like removed', 'success');
            }
        }
    } catch (error) {
        console.error('Error liking idea:', error);
        showToast('Failed to like idea. Please try again.', 'error');
    }
}

function showToast(message, type = 'success') {
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) toast.remove();
        }, 300);
    }, 3000);
}

async function incrementViewCount(ideaId) {
    try {
        await fetch(`/api/increment_view/${ideaId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
    } catch (error) {
        console.error('Error incrementing view count:', error);
    }
}

function handleContainerClick(e) {
    const ideaCard = e.target.closest('.idea-card');
    if (ideaCard && !e.target.closest('button') && !e.target.closest('a')) {
        const ideaId = ideaCard.getAttribute('data-idea-id');
        if (ideaId) {
                window.location.href = `/idea/${ideaId}`;

          
        }
        return;
    }

    if (e.target.closest('.like-button')) {
        e.preventDefault();
        e.stopPropagation();
        const likeButton = e.target.closest('.like-button');
        const ideaCard = likeButton.closest('.idea-card');
        const ideaId = ideaCard ? ideaCard.getAttribute('data-idea-id') : null;
        
        if (ideaId) {
            likeIdea(parseInt(ideaId));
        }
        return;
    }

    if (e.target.closest('.comment-button')) {
        e.preventDefault();
        e.stopPropagation();
        const commentButton = e.target.closest('.comment-button');
        const ideaCard = commentButton.closest('.idea-card');
        const ideaId = ideaCard ? ideaCard.getAttribute('data-idea-id') : null;
        
        if (ideaId) {
            incrementViewCount(parseInt(ideaId));
            setTimeout(() => {
                window.location.href = `/idea/${ideaId}#comments-section`;
            }, 100);
        }
        return;
    }
}

function attachEventListeners() {
    const container = document.querySelector('.container');
    if (!container) return;
    
    container.removeEventListener('click', handleContainerClick);
    container.addEventListener('click', handleContainerClick);
}

document.addEventListener('DOMContentLoaded', function() {
    loadUserLikes().then(() => {
        attachEventListeners();
    });
});