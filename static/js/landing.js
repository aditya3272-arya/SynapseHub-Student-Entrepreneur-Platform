        function showLoginModal() {
            document.getElementById('loginModal').style.display = 'block';
        }
        function showSignupModal() {
            document.getElementById('signupModal').style.display = 'block';
        }
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        window.onclick = function(event) {
            const loginModal = document.getElementById('loginModal');
            const signupModal = document.getElementById('signupModal');
            if (event.target == loginModal) {
                loginModal.style.display = 'none';
            }
            if (event.target == signupModal) {
                signupModal.style.display = 'none';
            }
        }

        let selectedOption = null;
        const correctAnswer = 1; 
        
        function selectQuizOption(element) {
            document.querySelectorAll('.quiz-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            element.classList.add('selected');
            selectedOption = Array.from(element.parentNode.children).indexOf(element);
        }
        
        function checkQuizAnswer() {
            if (selectedOption === null) {
                alert('Please select an answer first!');
                return;
            }
            
            const resultDiv = document.getElementById('quiz-result');
            const isCorrect = selectedOption === correctAnswer;
            
            if (isCorrect) {
                resultDiv.innerHTML = `
                    <div style="color: #059669; font-weight: bold;">✅ Correct!</div>
                    <p style="margin-top: 0.5rem;">Validating your idea with potential customers is crucial before investing time and money. This helps you understand if people actually want your solution!</p>
                `;
                resultDiv.style.background = '#f0fdf4';
            } else {
                resultDiv.innerHTML = `
                    <div style="color: #dc2626; font-weight: bold;">❌ Not quite right</div>
                    <p style="margin-top: 0.5rem;">The correct answer is "Validate your idea with potential customers". Understanding if people actually want your solution is crucial before investing time and money!</p>
                `;
                resultDiv.style.background = '#fef2f2';
            }
            
            resultDiv.style.display = 'block';
            
            setTimeout(() => {
                const signupPrompt = document.createElement('div');
                signupPrompt.innerHTML = `
                    <div style="text-align: center; margin-top: 1rem; padding: 1rem; background: #eff6ff; border-radius: 8px;">
                        <p style="margin-bottom: 1rem;">Want to test your knowledge daily and learn more?</p>
                        <button class="btn btn-primary" onclick="showSignupModal()">Join Kidpreneur Now!</button>
                    </div>
                `;
                resultDiv.appendChild(signupPrompt.firstElementChild);
            }, 2000);
        }

        function handleScrollAnimations() {
            const elements = document.querySelectorAll('.animate-on-scroll');
            elements.forEach(element => {
                const elementTop = element.getBoundingClientRect().top;
                const elementVisible = 150;
                if (elementTop < window.innerHeight - elementVisible) {
                    element.classList.add('visible');
                }
            });
        }

        document.addEventListener('DOMContentLoaded', function() {
            handleScrollAnimations();
            window.addEventListener('scroll', handleScrollAnimations);
            
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth'
                        });
                    }
                });
            });

            const statNumbers = document.querySelectorAll('.stat-number');
            statNumbers.forEach(stat => {
                const finalValue = parseInt(stat.textContent.replace(/[^\d]/g, ''));
                let currentValue = 0;
                const increment = finalValue / 50;
                const counter = setInterval(() => {
                    currentValue += increment;
                    if (currentValue >= finalValue) {
                        stat.textContent = stat.textContent; 
                        clearInterval(counter);
                    } else {
                        const suffix = stat.textContent.match(/[^\d]/g)?.join('') || '';
                        stat.textContent = Math.floor(currentValue) + suffix;
                    }
                }, 50);
            });
        });