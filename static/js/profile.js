        let ideaToDelete = null;

        function triggerFileInput() {
            document.getElementById('profile-pic-input').click();
        }

        async function uploadProfilePic() {
            const fileInput = document.getElementById('profile-pic-input');
            const file = fileInput.files[0];
            
            if (!file) return;
            
            const formData = new FormData();
            formData.append('profile_pic', file);
            
            try {
                const response = await fetch('/upload_profile_pic', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    showMessage('Profile picture updated successfully! 📷', 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showMessage('Failed to upload profile picture. Please try again.', 'error');
                }
            } catch (error) {
                console.error('Error uploading profile picture:', error);
                showMessage('Error uploading profile picture.', 'error');
            }
        }

        function openEditProfileModal() {
            document.getElementById('editProfileModal').style.display = 'block';
            document.body.style.overflow = 'hidden';
        }

        function closeEditProfileModal() {
            document.getElementById('editProfileModal').style.display = 'none';
            document.body.style.overflow = 'auto';
        }

        function confirmDeleteIdea(ideaId, ideaTitle) {
            ideaToDelete = ideaId;
            document.getElementById('idea-to-delete-title').textContent = ideaTitle;
            document.getElementById('deleteConfirmModal').style.display = 'block';
            document.body.style.overflow = 'hidden';
        }

        function closeDeleteConfirmModal() {
            document.getElementById('deleteConfirmModal').style.display = 'none';
            document.body.style.overflow = 'auto';
            ideaToDelete = null;
        }

        async function saveProfile() {
            const profileData = {
                username: document.getElementById('edit-username').value,
                email: document.getElementById('edit-email').value,
                age: document.getElementById('edit-age').value,
                skills: document.getElementById('edit-skills').value,
                interests: document.getElementById('edit-interests').value,
                bio: document.getElementById('edit-bio').value
            };

            try {
                const response = await fetch('/update_profile', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(profileData)
                });

                if (response.ok) {
                    showMessage('Profile updated successfully! ✅', 'success');
                    closeEditProfileModal();
                    setTimeout(() => location.reload(), 1500);
                } else {
                    const errorData = await response.json();
                    showMessage(errorData.message || 'Failed to update profile.', 'error');
                }
            } catch (error) {
                console.error('Error updating profile:', error);
                showMessage('Error updating profile. Please try again.', 'error');
            }
        }

        async function deleteIdea() {
            if (!ideaToDelete) return;

            try {
                const response = await fetch(`/delete_idea/${ideaToDelete}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    showMessage('Idea deleted successfully! 🗑️', 'success');
                    closeDeleteConfirmModal();
                    setTimeout(() => location.reload(), 1500);
                } else {
                    const errorData = await response.json();
                    showMessage(errorData.message || 'Failed to delete idea.', 'error');
                }
            } catch (error) {
                console.error('Error deleting idea:', error);
                showMessage('Error deleting idea. Please try again.', 'error');
            }
        }

       

        function showMessage(message, type) {
            const messageContainer = document.getElementById('message-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type} fade-in`;
            messageDiv.textContent = message;
            
            messageContainer.appendChild(messageDiv);
            
            setTimeout(() => {
                messageDiv.style.opacity = '0';
                setTimeout(() => messageDiv.remove(), 300);
            }, 4000);
        }

        window.onclick = function(event) {
            const editModal = document.getElementById('editProfileModal');
            const deleteModal = document.getElementById('deleteConfirmModal');
            
            if (event.target === editModal) {
                closeEditProfileModal();
            }
            if (event.target === deleteModal) {
                closeDeleteConfirmModal();
            }
        };

        document.addEventListener('DOMContentLoaded', function() {
            loadQuizAnalytics();
            
            const ideaCards = document.querySelectorAll('.idea-item');
            ideaCards.forEach((card, index) => {
                setTimeout(() => {
                    card.style.animation = `slideIn 0.5s ease-out ${index * 0.1}s both`;
                }, index * 100);
            });
        });

        async function loadQuizAnalytics() {
            try {
                const response = await fetch('/get_quiz_analytics');
                if (response.ok) {
                    const analytics = await response.json();
                    
                    document.getElementById('total-quizzes').textContent = analytics.total_quizzes || 0;
                    document.getElementById('avg-accuracy').textContent = `${analytics.avg_accuracy || 0}%`;
                    document.getElementById('best-category').textContent = analytics.best_category || 'N/A';
                    document.getElementById('improvement-rate').textContent = `${analytics.improvement_rate || 0}%`;
                    
                    document.getElementById('accuracy-display').textContent = `${analytics.avg_accuracy || 0}%`;
                    
                    if (analytics.recent_scores && analytics.recent_scores.length > 0) {
                        generatePerformanceChart(analytics.recent_scores);
                    }
                }
            } catch (error) {
                console.error('Error loading quiz analytics:', error);
            }
        }

        function generatePerformanceChart(scores) {
    const chartContainer = document.getElementById('performance-chart-container');
    
    if (scores.length === 0) {
        chartContainer.innerHTML = '<div style="text-align: center; color: #6b7280; padding: 2rem;">No quiz data available yet. Take some quizzes to see your progress!</div>';
        return;
    }
    
    let chartHTML = '<div style="display: flex; align-items: end; height: 120px; gap: 8px; justify-content: center; margin-bottom: 1rem;">';
    
    scores.forEach((score, index) => {
        const height = Math.max(20, (score / 100) * 100);
        const color = score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444';
        const isLatest = index === 0;
        
        chartHTML += `
            <div style="display: flex; flex-direction: column; align-items: center; gap: 5px;">
                <div style="width: ${isLatest ? '30px' : '25px'}; height: ${height}px; background: ${color}; 
                           border-radius: 4px 4px 0 0; opacity: ${isLatest ? '1' : '0.8'}; 
                           transition: all 0.3s; border: ${isLatest ? '2px solid #667eea' : 'none'};" 
                     onmouseover="this.style.opacity='1'; this.style.transform='scale(1.1)'" 
                     onmouseout="this.style.opacity='${isLatest ? '1' : '0.8'}'; this.style.transform='scale(1)'"></div>
                <small style="font-size: 0.7rem; color: #6b7280; font-weight: ${isLatest ? 'bold' : 'normal'};">${score}%</small>
            </div>
        `;
    });
    
    chartHTML += '</div>';
    chartHTML += '<div style="text-align: center; margin-top: 1rem; color: #6b7280; font-size: 0.8rem;">Last ' + scores.length + ' quiz performances (latest highlighted)</div>';
    chartHTML += '<div style="display: flex; justify-content: center; gap: 1rem; margin-top: 0.5rem; font-size: 0.7rem;">';
    chartHTML += '<div><span style="background: #10b981; width: 12px; height: 12px; display: inline-block; margin-right: 4px; border-radius: 2px;"></span>Excellent (80%+)</div>';
    chartHTML += '<div><span style="background: #f59e0b; width: 12px; height: 12px; display: inline-block; margin-right: 4px; border-radius: 2px;"></span>Good (60-79%)</div>';
    chartHTML += '<div><span style="background: #ef4444; width: 12px; height: 12px; display: inline-block; margin-right: 4px; border-radius: 2px;"></span>Needs Work (< 60%)</div>';
    chartHTML += '</div>';
    
    chartContainer.innerHTML = chartHTML;
}


let currentEvaluationIdeaId = null;

async function evaluateIdea(ideaId, ideaTitle) {
    console.log(`Starting evaluation for idea ${ideaId}: ${ideaTitle}`);
    
    currentEvaluationIdeaId = ideaId;
    document.getElementById('evaluation-idea-title').textContent = `"${ideaTitle}"`;
    
    document.getElementById('evaluationModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    const contentDiv = document.getElementById('evaluation-content');
    contentDiv.innerHTML = `
        <div style="text-align: center; padding: 3rem;">
            <div class="loading-spinner"></div>
            <p style="margin-top: 1rem; font-weight: bold;">Analyzing your idea with AI...</p>
            <p style="color: #6b7280; font-size: 0.9rem;">This may take a few moments</p>
            <div style="margin-top: 1rem;">
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
            </div>
        </div>
    `;
    
    try {
        console.log(`Making API call to /evaluate_idea/${ideaId}`);
        
        const response = await fetch(`/evaluate_idea/${ideaId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        console.log(`API response status: ${response.status}`);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Evaluation data received:', data);
            
            if (data.success && data.evaluation) {
                displayEvaluation(data.evaluation);
            } else {
                throw new Error(data.message || 'Invalid response format');
            }
        } else {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `Server error: ${response.status}`);
        }
        
    } catch (error) {
        console.error('Evaluation error:', error);
        contentDiv.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
                <h3>Evaluation Failed</h3>
                <p style="color: #6b7280; margin-bottom: 1rem;">${error.message || 'Unable to evaluate idea at this time.'}</p>
                <button class="btn btn-secondary" onclick="closeEvaluationModal()">Close</button>
                <button class="btn" onclick="evaluateIdea(${ideaId}, '${ideaTitle.replace(/'/g, "\\'")}')">Try Again</button>
            </div>
        `;
    }
}

function displayEvaluation(evaluation) {
    console.log('Displaying evaluation:', evaluation);
    
    const contentDiv = document.getElementById('evaluation-content');
    
    function getScoreClass(score) {
        if (score >= 8) return 'score-excellent';
        if (score >= 6) return 'score-good';
        if (score >= 4) return 'score-fair';
        return 'score-poor';
    }
    
    function getScoreColor(score) {
        if (score >= 8) return '#10b981'; 
        if (score >= 6) return '#f59e0b'; 
        if (score >= 4) return '#f97316'; 
        return '#ef4444'; // Red
    }
    
    const overallRating = evaluation.overall_rating || 5;
    const overallFeedback = evaluation.overall_feedback || 'Evaluation completed.';
    const detailedAnalysis = evaluation.detailed_analysis || {};
    const improvements = evaluation.improvements || [];
    const strengths = evaluation.strengths || [];
    const challenges = evaluation.challenges || [];
    const nextSteps = evaluation.next_steps || [];
    
    const html = `
        <div class="evaluation-results">
            <!-- Overall Rating -->
            <div class="overall-rating">
                <div class="score-circle ${getScoreClass(overallRating)}" 
                     style="background: ${getScoreColor(overallRating)}; color: white; font-weight: bold;">
                    ${overallRating}/10
                </div>
                <h3>Overall Rating</h3>
                <p>${overallFeedback}</p>
            </div>
            
            <!-- Detailed Analysis Grid -->
            <div class="analysis-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                ${Object.entries(detailedAnalysis).map(([category, data]) => `
                    <div class="evaluation-section">
                        <div class="score-display" style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                            <div class="score-circle ${getScoreClass(data.score || 5)}"
                                 style="width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                                        background: ${getScoreColor(data.score || 5)}; color: white; font-weight: bold; font-size: 0.9rem;">
                                ${data.score || 5}/10
                            </div>
                            <h4 style="margin: 0; text-transform: capitalize;">
                                ${category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </h4>
                        </div>
                    <p>${data.feedback}</p>
                </div>
            `).join('')}
        </div>
        
        <div class="evaluation-section">
            <h4>💡 Key Strengths</h4>
            <ul class="evaluation-list">
                ${evaluation.strengths.map(strength => `<li>• ${strength}</li>`).join('')}
            </ul>
        </div>
        
        <div class="evaluation-section">
            <h4>⚠️ Main Challenges</h4>
            <ul class="evaluation-list">
                ${evaluation.challenges.map(challenge => `<li>• ${challenge}</li>`).join('')}
            </ul>
        </div>
        
        <div class="evaluation-section">
            <h4>🚀 Improvement Suggestions</h4>
            <ul class="evaluation-list">
                ${evaluation.improvements.map(improvement => `<li>• ${improvement}</li>`).join('')}
            </ul>
        </div>
        
        <div class="evaluation-section">
            <h4>📋 Next Steps</h4>
            <ul class="evaluation-list">
                ${evaluation.next_steps.map(step => `<li>• ${step}</li>`).join('')}
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 2rem; padding: 1rem; background: #f0f9ff; border-radius: 10px;">
            <p style="color: #0369a1; font-size: 0.9rem;">
                Evaluation completed on ${new Date(evaluation.evaluation_date).toLocaleDateString()}
            </p>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}

function closeEvaluationModal() {
    document.getElementById('evaluationModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    currentEvaluationIdeaId = null;
}

window.onclick = function(event) {
    const editModal = document.getElementById('editProfileModal');
    const deleteModal = document.getElementById('deleteConfirmModal');
    const evaluationModal = document.getElementById('evaluationModal');
    
    if (event.target === editModal) {
        closeEditProfileModal();
    }
    if (event.target === deleteModal) {
        closeDeleteConfirmModal();
    }
    if (event.target === evaluationModal) {
        closeEvaluationModal();
    }
};