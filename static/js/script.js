document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('prediction-form');
    // const submitBtn = document.getElementById('submit-btn'); // Removed
    const resultSection = document.getElementById('result-section');
    const inputs = form.querySelectorAll('input, select');
    
    // Setup value sync for range sliders
    const rangeInputs = form.querySelectorAll('input[type="range"]');
    rangeInputs.forEach(input => {
        const displayLabel = document.getElementById(`val-${input.id}`);
        if(displayLabel) {
            input.addEventListener('input', (e) => {
                displayLabel.textContent = e.target.value;
            });
        }
    });

    let debounceTimer;
    let radarChart;
    let currentInputData = null;
    let currentResultData = null;

    function updateRadarChart(data) {
        const ctx = document.getElementById('profileRadarChart');
        if (!ctx) return;

        // Normalize data to 0-100 scale for comparison
        const attendance = parseFloat(data.attendance) || 0;
        const prevGrade = parseFloat(data.previous_grade) || 0;
        const studyHours = Math.min((parseFloat(data.study_hours) || 0) / 30 * 100, 100); 
        const sleepScore = Math.min((parseFloat(data.sleep_hours) || 0) / 8 * 100, 100);

        const studentData = [attendance, studyHours, prevGrade, sleepScore];
        const idealData = [95, 66, 90, 100]; // 95% attendance, ~20h study, 90 grade, 8h sleep

        if (radarChart) {
            radarChart.data.datasets[0].data = studentData;
            radarChart.update();
        } else {
            radarChart = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['Attendance', 'Study Hours', 'Prev Grade', 'Sleep Quality'],
                    datasets: [{
                        label: 'Your Profile',
                        data: studentData,
                        backgroundColor: 'rgba(99, 102, 241, 0.2)',
                        borderColor: 'rgba(99, 102, 241, 1)',
                        pointBackgroundColor: 'rgba(99, 102, 241, 1)',
                        borderWidth: 2
                    }, {
                        label: 'Ideal Standard',
                        data: idealData,
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderColor: 'rgba(16, 185, 129, 0.5)',
                        pointBackgroundColor: 'rgba(16, 185, 129, 0.5)',
                        borderWidth: 1,
                        borderDash: [5, 5]
                    }]
                },
                options: {
                    scales: {
                        r: {
                            angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            pointLabels: { color: 'rgba(255, 255, 255, 0.7)', font: { size: 12 } },
                            ticks: { display: false, min: 0, max: 100 }
                        }
                    },
                    plugins: {
                        legend: { labels: { color: 'rgba(255, 255, 255, 0.7)' } }
                    },
                    maintainAspectRatio: false
                }
            });
        }
    }

    function triggerPrediction() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(async () => {
            
            // Gather form data
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // Handle toggles (checkboxes only exist in FormData if checked)
            const toggles = ['internet_access', 'family_support', 'extra_curricular', 'tutoring'];
            toggles.forEach(toggle => {
                data[toggle] = data[toggle] ? 1 : 0;
            });

            // Convert types
            data.age = parseInt(data.age);
            data.study_hours = parseFloat(data.study_hours);
            data.attendance = parseFloat(data.attendance);
            data.previous_grade = parseFloat(data.previous_grade);
            data.sleep_hours = parseFloat(data.sleep_hours);
            
            currentInputData = data;

            try {
                // Send API Request
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data),
                });

                const result = await response.json();

                if (result.success) {
                    currentResultData = result;
                    displayResults(result);
                    updateRadarChart(data);
                } else {
                    console.error('Prediction failed.', result.error);
                }
            } catch (error) {
                console.error('Network error.', error);
            }
        }, 200); // 200ms debounce
    }

    // Attach event listeners to trigger predictions automatically
    inputs.forEach(input => {
        input.addEventListener('change', triggerPrediction);
        if (input.type === 'range') {
            input.addEventListener('input', triggerPrediction);
        }
    });

    // Run initial prediction on load
    triggerPrediction();

    function displayResults(result) {
        const gradeVal = document.getElementById('predicted-grade-val');
        const badge = document.getElementById('category-badge');
        const list = document.getElementById('recommendations-list');
        const progressCircle = document.getElementById('progress-circle');

        // Reset
        list.innerHTML = '';
        
        // Determine category details
        let catClass = '';
        let color = '';
        
        const cat = result.category.toLowerCase();
        if (cat === 'excellent') {
            catClass = 'cat-excellent';
            color = '#10b981';
        } else if (cat === 'good') {
            catClass = 'cat-good';
            color = '#3b82f6';
        } else if (cat === 'average') {
            catClass = 'cat-average';
            color = '#f59e0b';
        } else {
            catClass = 'cat-poor';
            color = '#ef4444';
        }

        // Populate XAI (Feature Impact) if available
        const xaiContainer = document.getElementById('xai-bars');
        if (xaiContainer && result.xai) {
            xaiContainer.innerHTML = ''; // Clear previous
            
            // Loop through keys and display a bar for each
            for (const [feature, impact] of Object.entries(result.xai)) {
                const isPositive = impact > 0;
                const impactClass = isPositive ? 'var(--success)' : 'var(--danger)';
                const icon = isPositive ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down';
                const sign = isPositive ? '+' : '';
                
                // Max impact expected is around 15-25 for our mockup, cap at 100 for width
                const barWidth = Math.min(Math.abs(impact) * 4, 100); 

                const xaiHTML = `
                    <div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 0.8rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem; font-size: 0.9rem;">
                            <span style="color: var(--text-primary);">${feature}</span>
                            <span style="color: ${impactClass}; font-weight: 600;">
                                <i class="fa-solid ${icon}"></i> ${sign}${impact.toFixed(1)} pts
                            </span>
                        </div>
                        <div style="height: 6px; background: var(--background-end); border-radius: 3px; overflow: hidden; position: relative;">
                            <!-- Progress Bar that grows from left for positive, right side logic mock -->
                            <div style="height: 100%; width: ${barWidth}%; background: ${impactClass}; border-radius: 3px; transition: width 0.5s ease-out;"></div>
                        </div>
                    </div>
                `;
                xaiContainer.insertAdjacentHTML('beforeend', xaiHTML);
            }
        }

        // Populate recommendations
        if (result.recommendations && result.recommendations.length > 0) {
            result.recommendations.forEach((recObj, index) => {
                const li = document.createElement('li');
                
                // Assuming backend returns objects like { text: "...", priority: "high" }
                // fallback to string if backend hasn't been updated yet
                const isObj = typeof recObj === 'object';
                const text = isObj ? recObj.text : recObj;
                const priorityClass = isObj && recObj.priority ? `priority-${recObj.priority}` : '';
                
                if(priorityClass) {
                    li.classList.add(priorityClass);
                }

                li.innerHTML = text; 
                li.style.animationDelay = `${index * 0.1}s`;
                li.style.animation = 'fadeInDown 0.5s ease-out forwards';
                li.style.opacity = '0';
                list.appendChild(li);
            });
        } else {
             list.innerHTML = '<li style="color: var(--text-secondary);">Looking good! No immediate action items.</li>';
        }

        // Quick transition for grade value
        gradeVal.textContent = parseFloat(result.grade).toFixed(1);

        // Update circle gradient based on 0-100 scale degrees
        const degrees = result.grade * 3.6;
        progressCircle.style.transition = 'background 0.5s ease';
        progressCircle.style.background = `conic-gradient(${color} ${degrees}deg, rgba(255, 255, 255, 0.1) ${degrees}deg)`;
    }
    
    // PDF Export Logic (Leveraging browser print with dedicated CSS media queries)
    const printBtn = document.getElementById('print-btn');
    if (printBtn) {
        printBtn.addEventListener('click', () => {
             window.print();
        });
    }
    
    // Save Prediction to SQLite DB Logic
    const saveBtn = document.getElementById('save-prediction-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
             if (!currentInputData || !currentResultData) return;
             
             saveBtn.classList.add('loading');
             
             const payload = {
                 ...currentInputData,
                 predicted_grade: currentResultData.grade,
                 category: currentResultData.category,
                 recommendations: currentResultData.recommendations
             };
             
             try {
                 const response = await fetch('/save_prediction', {
                     method: 'POST',
                     headers: { 'Content-Type': 'application/json' },
                     body: JSON.stringify(payload)
                 });
                 const res = await response.json();
                 
                 const statusDiv = document.getElementById('save-status');
                 statusDiv.style.display = 'block';
                 if (res.success) {
                     statusDiv.innerHTML = '<i class="fa-solid fa-circle-check"></i> Profile saved to history!';
                     statusDiv.style.color = 'var(--success)';
                 } else {
                     statusDiv.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> Failed to save: ' + res.error;
                     statusDiv.style.color = 'var(--danger)';
                 }
                 
                 setTimeout(() => {
                     statusDiv.style.display = 'none';
                 }, 4000);
                 
             } catch (e) {
                 console.error(e);
             } finally {
                 saveBtn.classList.remove('loading');
             }
        });
    }
});
