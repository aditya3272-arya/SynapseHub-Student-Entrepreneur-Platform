        let currentQuestionIndex = 0;
        let selectedAnswer = null;
        let quizQuestions = [];
        let userAnswers = [];
        let quizStartTime = null;
        let correctAnswers = 0;
        let totalPoints = 0;

        document.getElementById('quiz-date').textContent = new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });

        document.addEventListener('DOMContentLoaded', function() {
            loadDailyQuiz();
        });

        async function loadDailyQuiz() {
            try {
                const response = await fetch('/get_daily_quiz');
                if (response.ok) {
                    const data = await response.json();
                    if (data.questions && data.questions.length > 0) {
                        quizQuestions = data.questions;
                        quizStartTime = new Date();
                        displayQuestion(0);
                    } else {
                        showCompletedMessage();
                    }
                } else {
                    showError('Failed to load quiz. Please try again.');
                }
            } catch (error) {
                console.error('Error loading quiz:', error);
                showError('Error loading quiz. Please check your connection.');
            }
        }

        function displayQuestion(index) {
            const container = document.getElementById('quiz-container');
            const question = quizQuestions[index];
            
            container.innerHTML = `
                <div class="quiz-progress">
                    <div class="progress-info">
                        <span>Question ${index + 1} of ${quizQuestions.length}</span>
                        <span>${Math.round(((index) / quizQuestions.length) * 100)}% Complete</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${(index / quizQuestions.length) * 100}%"></div>
                    </div>
                </div>
                <div class="quiz-content">
                    <div class="question-header">
                        <div class="question-number">Question ${index + 1}</div>
                        <div class="question-category">${question.category}</div>
                    </div>
                    <h2 class="question-text">${question.question}</h2>
                    <div class="options-container">
                        ${question.options.map((option, optionIndex) => `
                            <div class="option" onclick="selectOption(${optionIndex}, this)">
                                ${String.fromCharCode(65 + optionIndex)}. ${option}
                            </div>
                        `).join('')}
                    </div>
                    <div class="quiz-actions">
                        ${index > 0 ? `<button class="btn btn-secondary" onclick="previousQuestion()">Previous</button>` : ''}
                        <button class="btn" id="next-btn" onclick="nextQuestion()" disabled>
                            ${index === quizQuestions.length - 1 ? 'Finish Quiz' : 'Next Question'}
                        </button>
                    </div>
                </div>
            `;

            container.classList.add('slide-in-right');
            setTimeout(() => container.classList.remove('slide-in-right'), 500);

            selectedAnswer = null;
        }

        function selectOption(optionIndex, element) {
            document.querySelectorAll('.option').forEach(opt => opt.classList.remove('selected'));
            element.classList.add('selected');
            selectedAnswer = optionIndex;
            document.getElementById('next-btn').disabled = false;
        }

        function previousQuestion() {
            if (currentQuestionIndex > 0) {
                currentQuestionIndex--;
                displayQuestion(currentQuestionIndex);
            }
        }

        async function nextQuestion() {
            if (selectedAnswer === null) return;

            const currentQuestion = quizQuestions[currentQuestionIndex];
            const isCorrect = selectedAnswer === currentQuestion.correct_answer;
            
            userAnswers[currentQuestionIndex] = {
                questionId: currentQuestion.id,
                selectedAnswer: selectedAnswer,
                correct: isCorrect,
                question: currentQuestion.question,
                options: currentQuestion.options,
                correctAnswer: currentQuestion.correct_answer,
                explanation: currentQuestion.explanation
            };

            if (isCorrect) {
                correctAnswers++;
                totalPoints += 10;
            }

            await submitQuizAnswer(currentQuestion.id, selectedAnswer);

            if (currentQuestionIndex === quizQuestions.length - 1) {
                finishQuiz();
            } else {
                currentQuestionIndex++;
                displayQuestion(currentQuestionIndex);
            }
        }

        async function submitQuizAnswer(questionId, selectedAnswer) {
            try {
                await fetch('/submit_quiz_answer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        question_id: questionId,
                        selected_answer: selectedAnswer
                    })
                });
            } catch (error) {
                console.error('Error submitting answer:', error);
            }
        }

        async function finishQuiz() {
            const accuracy = Math.round((correctAnswers / quizQuestions.length) * 100);
            const timeTaken = Math.round((new Date() - quizStartTime) / 1000 / 60); 
            

            try {
                await fetch('/update_quiz_stats', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        questions_answered: quizQuestions.length,
                        correct_answers: correctAnswers,
                        accuracy: accuracy,
                        points_earned: totalPoints,
                        time_taken: timeTaken,
                        quiz_data: userAnswers
                    })
                });
            } catch (error) {
                console.error('Error updating quiz stats:', error);
            }

            displayResults(accuracy, timeTaken);
        }

        function displayResults(accuracy, timeTaken) {
            const container = document.getElementById('quiz-container');
            container.style.display = 'none';

            const resultsContainer = document.getElementById('results-container');
            
            let performanceMessage = '';
            let performanceIcon = '';
            
            if (accuracy >= 90) {
                performanceMessage = 'Outstanding! You\'re a business genius! 🌟';
                performanceIcon = '🏆';
            } else if (accuracy >= 80) {
                performanceMessage = 'Excellent work! Keep it up! 👏';
                performanceIcon = '🎯';
            } else if (accuracy >= 70) {
                performanceMessage = 'Good job! You\'re learning fast! 👍';
                performanceIcon = '📚';
            } else if (accuracy >= 60) {
                performanceMessage = 'Not bad! Keep studying! 💪';
                performanceIcon = '📖';
            } else {
                performanceMessage = 'Keep practicing! You\'ll improve! 🌱';
                performanceIcon = '💡';
            }

            resultsContainer.innerHTML = `
                <div class="results-header">
                    <div class="completion-icon">${performanceIcon}</div>
                    <div class="results-score">${accuracy}%</div>
                    <div class="results-message">${performanceMessage}</div>
                    <div class="completion-subtitle">Quiz completed in ${timeTaken} minute${timeTaken !== 1 ? 's' : ''}</div>
                </div>
                
                <div class="results-stats">
                    <div class="result-stat">
                        <div class="result-stat-number">${correctAnswers}</div>
                        <div class="result-stat-label">Correct</div>
                    </div>
                    <div class="result-stat">
                        <div class="result-stat-number">${quizQuestions.length - correctAnswers}</div>
                        <div class="result-stat-label">Incorrect</div>
                    </div>
                    <div class="result-stat">
                        <div class="result-stat-number">${totalPoints}</div>
                        <div class="result-stat-label">Points Earned</div>
                    </div>
                    <div class="result-stat">
                        <div class="result-stat-number">${timeTaken}m</div>
                        <div class="result-stat-label">Time Taken</div>
                    </div>
                </div>

                <div class="answer-review">
                    <div class="review-header">📋 Answer Review - All Questions</div>
                    <div class="review-content">
                        ${userAnswers.map((answer, index) => `
                            <div class="answer-item">
                                <div class="answer-question">
                                    <strong>Q${index + 1}:</strong> ${answer.question}
                                </div>
                                <div class="answer-details">
                                    <div class="answer-row">
                                        <div class="answer-status ${answer.correct ? 'correct' : 'incorrect'}">
                                            ${answer.correct ? '✓' : '✗'}
                                        </div>
                                        <div class="answer-text">
                                            <strong>Your answer:</strong> ${String.fromCharCode(65 + answer.selectedAnswer)}. ${answer.options[answer.selectedAnswer]}
                                        </div>
                                    </div>
                                    ${!answer.correct ? `
                                        <div class="answer-row">
                                            <div class="answer-status correct">✓</div>
                                            <div class="answer-text">
                                                <strong>Correct answer:</strong> ${String.fromCharCode(65 + answer.correctAnswer)}. ${answer.options[answer.correctAnswer]}
                                            </div>
                                        </div>
                                    ` : ''}
                                </div>
                                <div class="answer-explanation">
                                    💡 <strong>Explanation:</strong> ${answer.explanation}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="quiz-actions" style="margin-top: 2rem;">
                    <a href="/profile" class="btn">View Progress</a>
                    <a href="/dashboard" class="btn btn-secondary">Back to Dashboard</a>
                </div>
            `;

            resultsContainer.style.display = 'block';
            resultsContainer.classList.add('fade-in');

            updateDisplayedStats(accuracy);
        }

        function updateDisplayedStats(newAccuracy) {
            const accuracyStat = document.querySelector('.stats-dashboard .stat-card:nth-child(3) .stat-number');
            if (accuracyStat) {
                accuracyStat.textContent = newAccuracy + '%';
            }
        }

        function showCompletedMessage() {
            const container = document.getElementById('quiz-container');
            container.innerHTML = `
                <div class="quiz-completed">
                    <div class="completion-icon">🎯</div>
                    <h2 class="completion-message">Quiz Already Completed!</h2>
                    <p class="completion-subtitle">You've already taken today's quiz. Come back tomorrow for new challenges!</p>
                    <div class="quiz-actions">
                        <a href="/profile" class="btn">View Your Progress</a>
                        <a href="/dashboard" class="btn btn-secondary">Back to Dashboard</a>
                    </div>
                </div>
            `;
        }

        function showError(message) {
            const container = document.getElementById('quiz-container');
            container.innerHTML = `
                <div class="quiz-completed">
                    <div class="completion-icon">⚠️</div>
                    <h2 class="completion-message">Oops! Something went wrong</h2>
                    <p class="completion-subtitle">${message}</p>
                    <div class="quiz-actions">
                        <button class="btn" onclick="loadDailyQuiz()">Try Again</button>
                        <a href="/dashboard" class="btn btn-secondary">Back to Dashboard</a>
                    </div>
                </div>
            `;
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                const nextBtn = document.getElementById('next-btn');
                if (nextBtn && !nextBtn.disabled) {
                    nextQuestion();
                }
            }
            
            if (e.key >= '1' && e.key <= '4') {
                const optionIndex = parseInt(e.key) - 1;
                const options = document.querySelectorAll('.option');
                if (options[optionIndex]) {
                    selectOption(optionIndex, options[optionIndex]);
                }
            }
        });

        function scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }

        function animateProgress() {
            const progressFill = document.querySelector('.progress-fill');
            if (progressFill) {
                const targetWidth = progressFill.style.width;
                progressFill.style.width = '0%';
                setTimeout(() => {
                    progressFill.style.width = targetWidth;
                }, 100);
            }
        }

        function showConfetti() {
            const confettiColors = ['#667eea', '#764ba2', '#10b981', '#f59e0b', '#ef4444'];
            for (let i = 0; i < 50; i++) {
                setTimeout(() => {
                    const confetti = document.createElement('div');
                    confetti.style.cssText = `
                        position: fixed;
                        top: -10px;
                        left: ${Math.random() * 100}%;
                        width: 10px;
                        height: 10px;
                        background: ${confettiColors[Math.floor(Math.random() * confettiColors.length)]};
                        z-index: 1000;
                        animation: confetti-fall 3s linear forwards;
                        border-radius: 50%;
                    `;
                    document.body.appendChild(confetti);
                    setTimeout(() => confetti.remove(), 3000);
                }, i * 50);
            }
        }

        const style = document.createElement('style');
        style.textContent = `
            @keyframes confetti-fall {
                0% {
                    transform: translateY(-100vh) rotate(0deg);
                    opacity: 1;
                }
                100% {
                    transform: translateY(100vh) rotate(720deg);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);