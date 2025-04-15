// Quiz Timer
class QuizTimer {
    constructor(duration, displayElement, onComplete) {
        this.duration = duration;
        this.display = displayElement;
        this.onComplete = onComplete;
        this.timeLeft = duration * 60; // Convert to seconds
        this.timerId = null;
    }

    start() {
        this.timerId = setInterval(() => {
            this.timeLeft--;
            this.updateDisplay();
            
            if (this.timeLeft <= 0) {
                this.stop();
                if (this.onComplete) this.onComplete();
            }
        }, 1000);
    }

    stop() {
        if (this.timerId) {
            clearInterval(this.timerId);
            this.timerId = null;
        }
    }

    updateDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        this.display.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    getTimeSpent() {
        const timeSpent = (this.duration * 60) - this.timeLeft;
        const minutes = Math.floor(timeSpent / 60);
        const seconds = timeSpent % 60;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

// Initialize Quiz Timer
document.addEventListener('DOMContentLoaded', function() {
    const timerElement = document.getElementById('quiz-timer');
    const quizForm = document.getElementById('quiz-form');
    
    if (timerElement && quizForm) {
        const duration = parseInt(timerElement.dataset.duration || '30');
        const timer = new QuizTimer(duration, timerElement, () => {
            quizForm.submit();
        });
        timer.start();

        // Add time taken to form submission
        quizForm.addEventListener('submit', function(e) {
            const timeInput = document.createElement('input');
            timeInput.type = 'hidden';
            timeInput.name = 'time_taken';
            timeInput.value = timer.getTimeSpent();
            this.appendChild(timeInput);
        });
    }
});

// Chart.js Initialization for Dashboard
function initializeCharts() {
    const performanceChart = document.getElementById('performanceChart');
    if (performanceChart) {
        fetch('/api/user/performance')
            .then(response => response.json())
            .then(data => {
                const scores = data.recent_scores.reverse();
                new Chart(performanceChart, {
                    type: 'line',
                    data: {
                        labels: scores.map(score => score.quiz_name),
                        datasets: [{
                            label: 'Score Percentage',
                            data: scores.map(score => score.percentage),
                            borderColor: '#4e73df',
                            tension: 0.3,
                            fill: false
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
            });
    }
}

// Initialize Charts
document.addEventListener('DOMContentLoaded', initializeCharts);

// Form Validation
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Add form validation to all forms
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
});

// Animate elements on scroll
function animateOnScroll() {
    const elements = document.querySelectorAll('.fade-in');
    elements.forEach(element => {
        const position = element.getBoundingClientRect();
        if (position.top < window.innerHeight) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
}

window.addEventListener('scroll', animateOnScroll);
document.addEventListener('DOMContentLoaded', animateOnScroll); 