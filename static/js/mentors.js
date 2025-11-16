       let selectedMentorId = null;
        let selectedMentorName = null;
        let selectedTime = null;

        function openBookingModal(mentorName, mentorId) {
            selectedMentorId = mentorId;
            selectedMentorName = mentorName;
            document.getElementById('modal-mentor-name').textContent = `Book Session with ${mentorName}`;
            document.getElementById('summary-mentor').textContent = mentorName;
            document.getElementById('bookingModal').style.display = 'block';
            document.body.style.overflow = 'hidden';
            
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('session-date').min = today;
        }


        function closeBookingModal() {
            document.getElementById('bookingModal').style.display = 'none';
            document.body.style.overflow = 'auto';
            document.getElementById('successMessage').style.display = 'none';
            document.getElementById('bookingForm').style.display = 'block';
            document.getElementById('bookingForm').reset();
            selectedTime = null;
            updateTimeSlots();
            updateSummary();
        }

        document.addEventListener('DOMContentLoaded', function() {
            const timeSlots = document.querySelectorAll('.time-slot:not(.unavailable)');
            timeSlots.forEach(slot => {
                slot.addEventListener('click', function() {
                    timeSlots.forEach(s => s.classList.remove('selected'));
                    this.classList.add('selected');
                    selectedTime = this.dataset.time;
                    updateSummary();
                });
            });

            document.getElementById('session-date').addEventListener('change', function() {
                updateSummary();
                updateTimeSlots();
            });
        });

        function updateTimeSlots() {
            const timeSlots = document.querySelectorAll('.time-slot');
            timeSlots.forEach((slot, index) => {
                if (Math.random() > 0.7 && index > 2) {
                    slot.classList.add('unavailable');
                    slot.textContent = slot.dataset.time + ' (Booked)';
                } else {
                    slot.classList.remove('unavailable');
                    slot.textContent = slot.dataset.time;
                }
            });
        }

        function updateSummary() {
            const date = document.getElementById('session-date').value;
            document.getElementById('summary-date').textContent = date || '-';
            document.getElementById('summary-time').textContent = selectedTime || '-';
        }

        document.getElementById('bookingForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!selectedTime) {
                alert('Please select a time slot');
                return;
            }

            const formData = {
                mentor_id: selectedMentorId,
                mentor_name: selectedMentorName,
                student_name: document.getElementById('student-name').value,
                student_email: document.getElementById('student-email').value,
                session_date: document.getElementById('session-date').value,
                session_time: selectedTime,
                session_topic: document.getElementById('session-topic').value
            };

            try {
                const response = await fetch('/book_session', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    document.getElementById('bookingForm').style.display = 'none';
                    document.getElementById('successMessage').style.display = 'block';
                    
                    setTimeout(() => {
                        closeBookingModal();
                    }, 3000);
                } else {
                    alert('Booking failed. Please try again.');
                }
            } catch (error) {
                console.error('Booking error:', error);
                alert('Booking failed. Please try again.');
            }
        });

        function viewProfile(mentorId) {
            alert(`Viewing profile for mentor ${mentorId}. Feature coming soon!`);
        }

        function filterMentors() {
    const search = document.getElementById('search').value.toLowerCase();
    const expertise = document.getElementById('expertise').value.toLowerCase();
    
    const cards = document.querySelectorAll('.mentor-card');
    let visibleCount = 0;
    
    cards.forEach(card => {
        const mentorName = card.querySelector('h3').textContent.toLowerCase();
        const expertiseTags = card.querySelectorAll('.expertise-tag');
        let mentorExpertise = '';
        
        expertiseTags.forEach(tag => {
            mentorExpertise += tag.textContent.toLowerCase() + ' ';
        });
        
        let show = true;
        
        if (search && !mentorName.includes(search) && !mentorExpertise.includes(search)) {
            show = false;
        }
        
        if (expertise && expertise !== '') {
            const hasExpertise = mentorExpertise.includes(expertise) || 
                                mentorExpertise.includes(getExpertiseKeyword(expertise));
            if (!hasExpertise) show = false;
        }
        
        if (show) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    const emptyState = document.querySelector('.empty-state');
    const mentorsGrid = document.querySelector('.mentors-grid');
    
    if (visibleCount === 0 && emptyState) {
        emptyState.style.display = 'block';
        mentorsGrid.style.display = 'none';
    } else if (emptyState) {
        emptyState.style.display = 'none';
        mentorsGrid.style.display = 'grid';
    }
}

function getExpertiseKeyword(expertise) {
    const keywords = {
        'tech': 'technology',
        'marketing': 'marketing',
        'finance': 'finance',
        'social': 'social impact'
    };
    return keywords[expertise] || expertise;
}

        window.onclick = function(event) {
            const modal = document.getElementById('bookingModal');
            if (event.target === modal) {
                closeBookingModal();
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.mentor-card');
            cards.forEach((card, index) => {
                setTimeout(() => {
                    card.style.animation = `fadeIn 0.6s ease-out ${index * 0.1}s both`;
                }, index * 50);
            });
        });

        document.getElementById('search').addEventListener('input', filterMentors);
        document.getElementById('expertise').addEventListener('change', filterMentors);
        document.getElementById('availability').addEventListener('change', filterMentors);
