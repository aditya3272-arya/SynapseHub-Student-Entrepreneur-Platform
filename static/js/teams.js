       let currentTeamId = null;
        let chatInterval = null;

        // Tab switching functionality
        function switchTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tab buttons
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked button
            event.target.classList.add('active');
        }

        // Application form functionality
        function showApplicationForm(ideaId, ideaTitle) {
            document.getElementById('idea_id').value = ideaId;
            document.querySelector('#applicationModal h2').textContent = `Apply to Join: ${ideaTitle}`;
            document.getElementById('applicationModal').style.display = 'block';
            document.body.style.overflow = 'hidden';
        }

        function closeApplicationModal() {
            document.getElementById('applicationModal').style.display = 'none';
            document.body.style.overflow = 'auto';
            document.getElementById('applicationForm').reset();
        }

        // Team chat functionality
        function openTeamChat(teamId, teamName) {
            currentTeamId = teamId;
            document.getElementById('chat-title').textContent = `${teamName} - Team Chat`;
            document.getElementById('chat-team-name').textContent = teamName;
            document.getElementById('chatModal').style.display = 'block';
            document.body.style.overflow = 'hidden';
            
            // Load chat messages
            loadChatMessages(teamId);
            
            // Start polling for new messages
            chatInterval = setInterval(() => {
                loadChatMessages(teamId);
            }, 3000);
        }

        function closeChatModal() {
            document.getElementById('chatModal').style.display = 'none';
            document.body.style.overflow = 'auto';
            currentTeamId = null;
            
            // Stop polling for messages
            if (chatInterval) {
                clearInterval(chatInterval);
                chatInterval = null;
            }
        }

        async function loadChatMessages(teamId) {
            try {
                const response = await fetch(`/api/team_messages/${teamId}`);
                if (response.ok) {
                    const messages = await response.json();
                    renderChatMessages(messages);
                }
            } catch (error) {
                console.error('Error loading chat messages:', error);
            }
        }

        function renderChatMessages(messages) {
            const chatMessages = document.getElementById('chat-messages');
            const currentUser = document.body.dataset.currentUser || '';
            
            chatMessages.innerHTML = messages.map(message => `
                <div class="message ${message.username === currentUser ? 'own' : 'other'}">
                    ${message.username !== currentUser ? `<div class="message-author">${message.username}</div>` : ''}
                    <div>${message.message}</div>
                    <div style="font-size: 0.7rem; opacity: 0.7; margin-top: 0.25rem;">${message.timestamp}</div>
                </div>
            `).join('');
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function handleChatKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        async function sendMessage() {
            const chatInput = document.getElementById('chat-input');
            const message = chatInput.value.trim();
            
            if (!message || !currentTeamId) return;
            
            try {
                const response = await fetch('/api/send_team_message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        team_id: currentTeamId,
                        message: message
                    })
                });
                
                if (response.ok) {
                    chatInput.value = '';
                    // Reload messages immediately
                    loadChatMessages(currentTeamId);
                } else {
                    showToast('Failed to send message', 'error');
                }
            } catch (error) {
                console.error('Error sending message:', error);
                showToast('Failed to send message', 'error');
            }
        }

        // Leave team functionality
        function confirmLeaveTeam(teamId, teamName) {
            if (confirm(`Are you sure you want to leave the team for "${teamName}"?`)) {
                leaveTeam(teamId);
            }
        }

        async function leaveTeam(teamId) {
            try {
                const response = await fetch(`/leave_team/${teamId}`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    showToast('Successfully left the team', 'success');
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                } else {
                    showToast('Failed to leave team', 'error');
                }
            } catch (error) {
                console.error('Error leaving team:', error);
                showToast('Failed to leave team', 'error');
            }
        }

        // Toast notifications
        function showToast(message, type = 'success') {
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => toast.classList.add('show'), 100);
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }

        // Form submission handling
        document.getElementById('applicationForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            try {
                const response = await fetch('/apply_to_team', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    showToast('Application submitted successfully!', 'success');
                    closeApplicationModal();
                    setTimeout(() => {
                        switchTab('applications');
                    }, 1000);
                } else {
                    const error = await response.text();
                    showToast(error || 'Failed to submit application', 'error');
                }
            } catch (error) {
                console.error('Error submitting application:', error);
                showToast('Failed to submit application', 'error');
            }
        });

        // Close modals when clicking outside
        window.onclick = function(event) {
            const applicationModal = document.getElementById('applicationModal');
            const chatModal = document.getElementById('chatModal');
            
            if (event.target === applicationModal) {
                closeApplicationModal();
            }
            if (event.target === chatModal) {
                closeChatModal();
            }
        };

        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Teams page initialized');
        });