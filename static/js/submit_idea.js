        let currentStep = 1;
        const totalSteps = 4;
        const tags = [];

        function setupCharCounter(inputId, counterId, maxLength) {
            const input = document.getElementById(inputId);
            const counter = document.getElementById(counterId);
            
            input.addEventListener('input', function() {
                const length = this.value.length;
                counter.textContent = `${length}/${maxLength}`;
                
                counter.classList.remove('warning', 'danger');
                if (length > maxLength * 0.8) {
                    counter.classList.add('warning');
                }
                if (length > maxLength * 0.95) {
                    counter.classList.add('danger');
                }
            });
        }

        setupCharCounter('title', 'title-counter', 100);
        setupCharCounter('problem_statement', 'problem-counter', 1000);
        setupCharCounter('solution_description', 'solution-counter', 1000);
        setupCharCounter('target_market', 'market-counter', 500);
        setupCharCounter('team_needs', 'team-counter', 300);
        setupCharCounter('inspiration', 'inspiration-counter', 400);

        const tagInput = document.getElementById('tag-input');
        const tagContainer = document.getElementById('tag-container');
        const tagsHidden = document.getElementById('tags-hidden');

        tagInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                addTag(this.value.trim());
                this.value = '';
            }
        });

        tagInput.addEventListener('blur', function() {
            if (this.value.trim()) {
                addTag(this.value.trim());
                this.value = '';
            }
        });

        function addTag(tagText) {
            if (tagText && tags.length < 8 && !tags.includes(tagText.toLowerCase())) {
                tags.push(tagText.toLowerCase());
                renderTags();
                updateHiddenTags();
            }
        }

        function removeTag(index) {
            tags.splice(index, 1);
            renderTags();
            updateHiddenTags();
        }

        function renderTags() {
            const existingTags = tagContainer.querySelectorAll('.tag');
            existingTags.forEach(tag => tag.remove());

            tags.forEach((tag, index) => {
                const tagElement = document.createElement('div');
                tagElement.className = 'tag';
                tagElement.innerHTML = `
                    ${tag}
                    <button type="button" class="tag-remove" onclick="removeTag(${index})">×</button>
                `;
                tagContainer.insertBefore(tagElement, tagInput);
            });
        }

        function updateHiddenTags() {
            tagsHidden.value = tags.join(',');
        }

        function showStep(step) {
            for (let i = 1; i <= totalSteps; i++) {
                document.getElementById(`step${i}`).classList.remove('active');
                const circle = document.getElementById(`step${i}-circle`);
                circle.classList.remove('active', 'completed');
                
                if (i < step) {
                    circle.classList.add('completed');
                    circle.innerHTML = '✓';
                } else if (i === step) {
                    circle.classList.add('active');
                    circle.innerHTML = i;
                } else {
                    circle.innerHTML = i;
                }
            }

            for (let i = 1; i < totalSteps; i++) {
                const line = document.getElementById(`line${i}`);
                if (i < step) {
                    line.classList.add('active');
                } else {
                    line.classList.remove('active');
                }
            }

            document.getElementById(`step${step}`).classList.add('active');

            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            const submitBtn = document.getElementById('submitBtn');

            prevBtn.style.display = step === 1 ? 'none' : 'inline-flex';
            
            if (step === totalSteps) {
                nextBtn.style.display = 'none';
                submitBtn.style.display = 'inline-flex';
                updatePreview();
            } else {
                nextBtn.style.display = 'inline-flex';
                submitBtn.style.display = 'none';
            }

            currentStep = step;
        }

        function validateStep(step) {
            let isValid = true;
            const validationMessages = document.querySelectorAll('.validation-message');
            validationMessages.forEach(msg => {
                msg.style.display = 'none';
                msg.classList.remove('validation-error', 'validation-success');
            });

            if (step === 1) {
                const title = document.getElementById('title').value.trim();
                const category = document.getElementById('category').value;
                const stage = document.getElementById('stage').value;

                if (!title) {
                    showValidationError('title-validation', 'Title is required');
                    isValid = false;
                } else if (title.length < 5) {
                    showValidationError('title-validation', 'Title must be at least 5 characters');
                    isValid = false;
                }

                if (!category) {
                    isValid = false;
                }

                if (!stage) {
                    isValid = false;
                }
            }

            if (step === 2) {
                const problem = document.getElementById('problem_statement').value.trim();
                const solution = document.getElementById('solution_description').value.trim();

                if (!problem) {
                    showValidationError('problem-validation', 'Problem statement is required');
                    isValid = false;
                } else if (problem.length < 50) {
                    showValidationError('problem-validation', 'Please provide a more detailed problem description (at least 50 characters)');
                    isValid = false;
                }

                if (!solution) {
                    showValidationError('solution-validation', 'Solution description is required');
                    isValid = false;
                } else if (solution.length < 50) {
                    showValidationError('solution-validation', 'Please provide a more detailed solution description (at least 50 characters)');
                    isValid = false;
                }
            }

            return isValid;
        }

        function showValidationError(elementId, message) {
            const element = document.getElementById(elementId);
            element.textContent = message;
            element.classList.add('validation-error');
            element.style.display = 'block';
        }

        document.getElementById('nextBtn').addEventListener('click', function() {
            if (validateStep(currentStep)) {
                if (currentStep < totalSteps) {
                    showStep(currentStep + 1);
                }
            }
        });

        document.getElementById('prevBtn').addEventListener('click', function() {
            if (currentStep > 1) {
                showStep(currentStep - 1);
            }
        });

function updatePreview() {
    const previewContainer = document.getElementById('preview-container');
    const title = document.getElementById('title').value || 'Untitled Idea';
    const category = document.getElementById('category').value || 'Uncategorized';
    const stage = document.getElementById('stage').value || 'Not specified';
    const problem = document.getElementById('problem_statement').value || 'No problem statement provided';
    const solution = document.getElementById('solution_description').value || 'No solution description provided';
    const market = document.getElementById('target_market').value || 'Not specified';
    const budget = document.getElementById('budget_range').value || 'Not specified';
    const timeline = document.getElementById('timeline').value || 'Not specified';
    const teamNeeds = document.getElementById('team_needs').value || 'Not specified';
    const inspiration = document.getElementById('inspiration').value || 'Not provided';
    const collaborationChecked = document.getElementById('collaboration-checkbox').checked;

    previewContainer.innerHTML = `
        <div class="preview-title">${title}</div>
        <div class="preview-section">
            <div class="preview-label">Category</div>
            <div class="preview-content">${category}</div>
        </div>
        <div class="preview-section">
            <div class="preview-label">Development Stage</div>
            <div class="preview-content">${stage}</div>
        </div>
        <div class="preview-section">
            <div class="preview-label">Tags</div>
            <div class="preview-content">${tags.length > 0 ? tags.join(', ') : 'No tags added'}</div>
        </div>
        <div class="preview-section">
            <div class="preview-label">Problem Statement</div>
            <div class="preview-content">${problem}</div>
        </div>
        <div class="preview-section">
            <div class="preview-label">Solution</div>
            <div class="preview-content">${solution}</div>
        </div>
        <div class="preview-section">
            <div class="preview-label">Target Market</div>
            <div class="preview-content">${market}</div>
        </div>
        <div class="preview-section">
            <div class="preview-label">Budget Range</div>
            <div class="preview-content">${budget}</div>
        </div>
        <div class="preview-section">
            <div class="preview-label">Timeline</div>
            <div class="preview-content">${timeline}</div>
        </div>
        <div class="preview-section">
            <div class="preview-label">Team Collaboration</div>
            <div class="preview-content">${collaborationChecked ? 'Open for collaboration' : 'Not looking for collaborators'}</div>
        </div>
        ${collaborationChecked ? `
        <div class="preview-section">
            <div class="preview-label">Team Needs</div>
            <div class="preview-content">${teamNeeds}</div>
        </div>
        ` : ''}
        <div class="preview-section">
            <div class="preview-label">Inspiration</div>
            <div class="preview-content">${inspiration}</div>
        </div>
    `;
}

document.getElementById('ideaForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    if (!validateStep(1) || !validateStep(2) || !validateStep(3)) {
        showToast('Please fix the errors before submitting', 'error');
        return;
    }
    
    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '🚀 Sharing Your Idea...';
    submitBtn.disabled = true;

    updateHiddenTags(); 
    
    setTimeout(() => {
        this.submit();
    }, 1000);
});

function validateStep(step) {
    let isValid = true;
    const validationMessages = document.querySelectorAll('.validation-message');
    validationMessages.forEach(msg => {
        msg.style.display = 'none';
        msg.classList.remove('validation-error', 'validation-success');
    });

    if (step === 1) {
        const title = document.getElementById('title').value.trim();
        const category = document.getElementById('category').value;
        const stage = document.getElementById('stage').value;

        if (!title) {
            showValidationError('title-validation', 'Title is required');
            isValid = false;
        } else if (title.length < 5) {
            showValidationError('title-validation', 'Title must be at least 5 characters');
            isValid = false;
        } else if (title.length > 100) {
            showValidationError('title-validation', 'Title must be less than 100 characters');
            isValid = false;
        }

        if (!category) {
            isValid = false;
        }

        if (!stage) {
            isValid = false;
        }
    }

    if (step === 2) {
        const problem = document.getElementById('problem_statement').value.trim();
        const solution = document.getElementById('solution_description').value.trim();

        if (!problem) {
            showValidationError('problem-validation', 'Problem statement is required');
            isValid = false;
        } else if (problem.length < 50) {
            showValidationError('problem-validation', 'Please provide a more detailed problem description (at least 50 characters)');
            isValid = false;
        } else if (problem.length > 1000) {
            showValidationError('problem-validation', 'Problem statement is too long (maximum 1000 characters)');
            isValid = false;
        }

        if (!solution) {
            showValidationError('solution-validation', 'Solution description is required');
            isValid = false;
        } else if (solution.length < 50) {
            showValidationError('solution-validation', 'Please provide a more detailed solution description (at least 50 characters)');
            isValid = false;
        } else if (solution.length > 1000) {
            showValidationError('solution-validation', 'Solution description is too long (maximum 1000 characters)');
            isValid = false;
        }
    }

    if (step === 3) {
        const collaborationCheckbox = document.getElementById('collaboration-checkbox');
        const teamNeeds = document.getElementById('team_needs');
        
        if (collaborationCheckbox && collaborationCheckbox.checked && teamNeeds) {
            const teamNeedsValue = teamNeeds.value.trim();
            if (!teamNeedsValue) {
                showValidationError('team-validation', 'Please describe the team members you need');
                isValid = false;
            } else if (teamNeedsValue.length < 20) {
                showValidationError('team-validation', 'Please provide more details about your team needs (at least 20 characters)');
                isValid = false;
            } else if (teamNeedsValue.length > 300) {
                showValidationError('team-validation', 'Team needs description is too long (maximum 300 characters)');
                isValid = false;
            }
        }

        const targetMarket = document.getElementById('target_market').value.trim();
        if (targetMarket && targetMarket.length > 500) {
            showValidationError('market-validation', 'Target market description is too long (maximum 500 characters)');
            isValid = false;
        }

        const inspiration = document.getElementById('inspiration').value.trim();
        if (inspiration && inspiration.length > 400) {
            showValidationError('inspiration-validation', 'Inspiration description is too long (maximum 400 characters)');
            isValid = false;
        }
    }

    return isValid;
}

function showValidationError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.classList.add('validation-error');
        element.style.display = 'block';
    }
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.padding = '1rem 1.5rem';
    toast.style.borderRadius = '12px';
    toast.style.zIndex = '9999';
    toast.style.transform = 'translateX(400px)';
    toast.style.transition = 'transform 0.3s ease';
    
    if (type === 'success') {
        toast.style.background = '#10b981';
        toast.style.color = 'white';
    } else {
        toast.style.background = '#ef4444';
        toast.style.color = 'white';
    }
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        toast.style.transform = 'translateX(400px)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

        
        document.addEventListener('DOMContentLoaded', function() {
            showStep(1);
        });

        document.addEventListener('DOMContentLoaded', function() {
    const collaborationCheckbox = document.getElementById('collaboration-checkbox');
    const teamNeedsSection = document.getElementById('team-needs-section');
    const teamNeedsInput = document.getElementById('team_needs');

    if (collaborationCheckbox && teamNeedsSection) {
        collaborationCheckbox.addEventListener('change', function() {
            if (this.checked) {
                teamNeedsSection.style.display = 'block';
                teamNeedsInput.setAttribute('required', 'required');
                teamNeedsSection.style.opacity = '0';
                teamNeedsSection.style.transform = 'translateY(-10px)';
                setTimeout(() => {
                    teamNeedsSection.style.transition = 'all 0.3s ease';
                    teamNeedsSection.style.opacity = '1';
                    teamNeedsSection.style.transform = 'translateY(0)';
                }, 50);
            } else {
                teamNeedsSection.style.display = 'none';
                teamNeedsInput.removeAttribute('required');
                teamNeedsInput.value = '';
                updateCharCounter('team_needs', 'team-counter', 300);
            }
        });
    }

    function validateCollaborationStep() {
        const checkbox = document.getElementById('collaboration-checkbox');
        const teamNeeds = document.getElementById('team_needs');
        
        if (checkbox && checkbox.checked) {
            const teamNeedsValue = teamNeeds.value.trim();
            if (!teamNeedsValue) {
                showValidationError('team-validation', 'Please describe the team members you need');
                return false;
            }
            if (teamNeedsValue.length < 20) {
                showValidationError('team-validation', 'Please provide more details about your team needs (at least 20 characters)');
                return false;
            }
        }
        return true;
    }

    const originalValidateStep = validateStep;
    validateStep = function(step) {
        let isValid = originalValidateStep(step);
        
        if (step === 3) { 
            isValid = validateCollaborationStep() && isValid;
        }
        
        return isValid;
    };
});


function updateCharCounter(inputId, counterId, maxLength) {
    const input = document.getElementById(inputId);
    const counter = document.getElementById(counterId);
    
    if (input && counter) {
        const length = input.value.length;
        counter.textContent = `${length}/${maxLength}`;
        
        counter.classList.remove('warning', 'danger');
        if (length > maxLength * 0.8) {
            counter.classList.add('warning');
        }
        if (length > maxLength * 0.95) {
            counter.classList.add('danger');
        }
    }
}


document.addEventListener('DOMContentLoaded', function() {
    const teamNeedsInput = document.getElementById('team_needs');
    if (teamNeedsInput) {
        teamNeedsInput.addEventListener('input', function() {
            updateCharCounter('team_needs', 'team-counter', 300);
        });
    }
});
