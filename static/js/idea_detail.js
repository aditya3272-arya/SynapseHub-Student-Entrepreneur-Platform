let ideaId = null;
let isLiked = false;

function getIdeaIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    const idIndex = pathParts.indexOf('idea') + 1;
    if (idIndex > 0 && idIndex < pathParts.length) {
        return parseInt(pathParts[idIndex]);
    }
    return null;
}

ideaId = getIdeaIdFromUrl();

if (!ideaId) {
    console.error('Could not extract idea ID from URL');
}

async function toggleLike() {
    if (!ideaId) {
        showToast('Error: Invalid idea ID', 'error');
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
            throw new Error('Failed to toggle like');
        }

        const data = await response.json();
        
        const heartIcon = document.getElementById('heart-icon');
        const likeCount = document.getElementById('like-count');
        const likeBtn = document.getElementById('like-btn');

        if (data.liked) {
            heartIcon.textContent = '❤️';
            likeBtn.classList.add('active');
            showToast('Idea liked! ❤️', 'success');
        } else {
            heartIcon.textContent = '🤍';
            likeBtn.classList.remove('active');
            showToast('Like removed', 'success');
        }

        likeCount.textContent = data.like_count;
        isLiked = data.liked;
        
    } catch (error) {
        console.error('Error toggling like:', error);
        showToast('Failed to update like. Please try again.', 'error');
    }
}

async function submitComment() {
    if (!ideaId) {
        showToast('Error: Invalid idea ID', 'error');
        return;
    }

    const commentInput = document.getElementById('comment-text');
    const commentText = commentInput.value.trim();

    if (!commentText) {
        showToast('Please enter a comment', 'error');
        return;
    }

    try {
        const response = await fetch('/api/comments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                idea_id: ideaId,
                text: commentText
            })
        });

        if (!response.ok) {
            throw new Error('Failed to post comment');
        }

        const newComment = await response.json();
        
        const commentsList = document.getElementById('comments-list');
        const emptyComments = commentsList.querySelector('.empty-comments');
        if (emptyComments) {
            emptyComments.remove();
        }

        const commentHtml = `
            <div class="comment">
                <div class="comment-header">
                    <div class="comment-avatar">${newComment.author[0].toUpperCase()}</div>
                    <div class="comment-meta">
                        <div class="comment-author">${newComment.author}</div>
                        <div class="comment-date">${newComment.date}</div>
                    </div>
                </div>
                <div class="comment-text">${escapeHtml(newComment.text)}</div>
            </div>
        `;

        commentsList.insertAdjacentHTML('afterbegin', commentHtml);

        const currentCount = parseInt(document.getElementById('comment-count').textContent);
        document.getElementById('comment-count').textContent = currentCount + 1;
        
        const commentsHeader = document.querySelector('.comments-header span');
        if (commentsHeader) {
            commentsHeader.textContent = `${currentCount + 1} comment${currentCount + 1 !== 1 ? 's' : ''}`;
        }

        commentInput.value = '';
        showToast('Comment posted successfully! 💬', 'success');
        
    } catch (error) {
        console.error('Error posting comment:', error);
        showToast('Failed to post comment. Please try again.', 'error');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function scrollToComments() {
    const commentsSection = document.getElementById('comments-section');
    if (commentsSection) {
        commentsSection.scrollIntoView({
            behavior: 'smooth'
        });
        setTimeout(() => {
            const commentInput = document.getElementById('comment-text');
            if (commentInput) {
                commentInput.focus();
            }
        }, 500);
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

async function loadUserLikes() {
    if (!ideaId) return;

    try {
        const response = await fetch('/api/user_likes');
        if (response.ok) {
            const likedIdeas = await response.json();
            if (likedIdeas.includes(ideaId)) {
                const heartIcon = document.getElementById('heart-icon');
                const likeBtn = document.getElementById('like-btn');
                if (heartIcon) heartIcon.textContent = '❤️';
                if (likeBtn) likeBtn.classList.add('active');
                isLiked = true;
            }
        }
    } catch (error) {
        console.error('Error loading user likes:', error);
    }
}

async function incrementViewCount() {
    if (!ideaId) return;

    try {
        const response = await fetch(`/api/increment_view/${ideaId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            const data = await response.json();
            const viewCount = document.getElementById('view-count');
            if (viewCount && data.views) {
                viewCount.textContent = data.views;
            }
        }
    } catch (error) {
        console.error('Error incrementing view count:', error);
    }
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.ctrlKey && e.target.id === 'comment-text') {
        submitComment();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    console.log('Idea detail page loaded. Idea ID:', ideaId);
    
    if (ideaId) {
        loadUserLikes();
        incrementViewCount();
    } else {
        console.error('Failed to initialize: Invalid idea ID');
    }

    if (window.location.hash === '#comments-section') {
        setTimeout(() => {
            scrollToComments();
        }, 500);
    }
});