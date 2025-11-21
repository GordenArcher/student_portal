import showToast from "/static/scripts/JS/admin_d.js"
import hideLoader from "/static/scripts/JS/admin_d.js"
import showLoader from "/static/scripts/JS/admin_d.js"
import getCsrfToken from "/static/scripts/JS/utility/getCsrfToken.js"

// Store results data
let resultsData = {};
let currentStudents = [];

document.addEventListener('DOMContentLoaded', function() {
    initializeUploadForm();
});

function initializeUploadForm() {
    const academicYearSelect = document.getElementById('academicYearSelect');
    const termSelect = document.getElementById('termSelect');
    const classLevelSelect = document.getElementById('classLevelSelect');
    const subjectSelect = document.getElementById('subjectSelect');
    const loadStudentsBtn = document.getElementById('loadStudentsBtn');
    const calculationModeRadios = document.querySelectorAll('input[name="calculation_mode"]');

    // Load terms when academic year is selected
    academicYearSelect.addEventListener('change', function() {
        const academicYearId = this.value;
        loadTerms(academicYearId);
    });

    [classLevelSelect, subjectSelect].forEach(select => {
        select.addEventListener('change', validateForm);
    });

    loadStudentsBtn.addEventListener('click', loadStudents);

    calculationModeRadios.forEach(radio => {
        radio.addEventListener('change', toggleCalculationMode);
    });

    // Modal event listeners
    initializeModalEvents();

    // Updated form submit to handle batch submission
    document.getElementById('uploadResultsForm').addEventListener('submit', handleFormSubmit);
}

function initializeModalEvents() {
    // Save student result button
    document.getElementById('saveStudentResultBtn').addEventListener('click', saveStudentResult);
    
    // Just validate inputs instead
    document.getElementById('modalClassScore').addEventListener('input', validateScoreInput);
    document.getElementById('modalExamScore').addEventListener('input', validateScoreInput);
    document.getElementById('modalManualScore').addEventListener('input', validateScoreInput);
    
    // Close modal when clicking outside
    document.getElementById('studentResultModal').addEventListener('click', function(e) {
        if (e.target === this) {
            hideStudentModal();
        }
    });
}

function validateScoreInput(e) {
    const value = parseFloat(e.target.value);
    if (value < 0 || value > 100) {
        e.target.setCustomValidity('Score must be between 0 and 100');
    } else {
        e.target.setCustomValidity('');
    }
}

async function loadTerms(academicYearId) {
    const termSelect = document.getElementById('termSelect');

    if (!academicYearId) {
        termSelect.innerHTML = '<option value="">Select an academic year first</option>';
        return;
    }

    try {
        const response = await fetch(`/academics/api/terms/?academic_year=${academicYearId}`);
        const data = await response.json();

        termSelect.innerHTML = '<option value="">Select Term</option>';

        if (!data.success || !data.terms || data.terms.length === 0) {
            termSelect.innerHTML = '<option value="">No terms found for this academic year</option>';
            return;
        }

        data.terms.forEach(term => {
            const option = document.createElement('option');
            option.value = term.id;
            option.textContent = `${term.name} (${term.start_date} - ${term.end_date})`;
            termSelect.appendChild(option);
        });

    } catch (error) {
        console.error('Error loading terms:', error);
        termSelect.innerHTML = '<option value="">Error loading terms</option>';
        showToast('Error loading terms', 'error');
    }
}

function validateForm() {
    const classLevelSelect = document.getElementById('classLevelSelect');
    const subjectSelect = document.getElementById('subjectSelect');
    const termSelect = document.getElementById('termSelect');
    const academicYearSelect = document.getElementById('academicYearSelect');
    const loadStudentsBtn = document.getElementById('loadStudentsBtn');

    const isFormValid = classLevelSelect.value && subjectSelect.value && termSelect.value && academicYearSelect.value;
    
    loadStudentsBtn.disabled = !isFormValid;
    return isFormValid;
}

function toggleCalculationMode() {
    const calculationMode = document.querySelector('input[name="calculation_mode"]:checked').value;
    
    if (calculationMode === 'system') {
        document.getElementById('systemScoreInputs').style.display = 'block';
        document.getElementById('manualScoreInputs').style.display = 'none';
    } else {
        document.getElementById('systemScoreInputs').style.display = 'none';
        document.getElementById('manualScoreInputs').style.display = 'block';
    }
}

async function loadStudents() {
    if (!validateForm()) {
        showToast('Please fill all required fields', 'warning');
        return;
    }

    const classLevelId = document.getElementById('classLevelSelect').value;
    const academicYearId = document.getElementById('academicYearSelect').value;
    const studentsContainer = document.getElementById('studentsContainer');
    const loadStudentsBtn = document.getElementById('loadStudentsBtn');

    try {
        loadStudentsBtn.innerHTML = '<span class="loading-spinner"></span> Loading...';
        loadStudentsBtn.disabled = true;

        const response = await fetch(`/academics/api/results/students/?class_level_id=${classLevelId}&academic_year_id=${academicYearId}`);
        const data = await response.json();

        if (data.success) {
            currentStudents = data.students;
            displayStudents(data.students);
            loadExistingResults();
        } else {
            showToast(data.error || 'Error loading students', 'error');
        }
    } catch (error) {
        console.error('Error loading students:', error);
        showToast('Error loading students', 'error');
    } finally {
        loadStudentsBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Load Students';
        loadStudentsBtn.disabled = false;
    }
}

function displayStudents(students) {
    const studentsContainer = document.getElementById('studentsContainer');
    const submitBtn = document.getElementById('submitBtn');

    if (students.length === 0) {
        studentsContainer.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-people"></i>
                <h4>No Students Found</h4>
                <p>No active students found in the selected class</p>
            </div>
        `;
        submitBtn.disabled = true;
        return;
    }

    let html = `
        <div class="students-list">
            <div class="students-header">
                <div class="student-info">Student Information</div>
                <div class="student-status">Result Status</div>
                <div class="student-actions">Actions</div>
            </div>
    `;

    students.forEach(student => {
        const hasResult = resultsData[student.id];
        const statusClass = hasResult ? 'status-completed' : 'status-pending';
        const statusText = hasResult ? 'Result Entered' : 'Pending';
        
        html += `
            <div class="student-item" data-student-id="${student.id}">
                <div class="student-info">
                    <div class="student-avatar">
                        <i class="bi bi-person-circle"></i>
                    </div>
                    <div class="student-details">
                        <div class="student-name">${student.first_name} ${student.last_name}</div>
                        <div class="student-id">${student.student_profile__student_id || student.username}</div>
                    </div>
                </div>
                <div class="student-status">
                    <span class="status-badge ${statusClass}">${statusText}</span>
                    ${hasResult ? `<div class="score-preview">Class: ${resultsData[student.id].class_score || 'N/A'}, Exam: ${resultsData[student.id].exam_score || 'N/A'}</div>` : ''}
                </div>
                <div class="student-actions">
                    <button class="btn btn-sm btn-primary enter-result-btn" data-student-id="${student.id}">
                        <i class="bi bi-pencil-square"></i> ${hasResult ? 'Edit Result' : 'Enter Result'}
                    </button>
                </div>
            </div>
        `;
    });

    html += '</div>';
    studentsContainer.innerHTML = html;
    submitBtn.disabled = false;

    // Add event listeners to student items
    attachStudentEventListeners();
}

function attachStudentEventListeners() {
    // Enter result buttons
    document.querySelectorAll('.enter-result-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const studentId = this.getAttribute('data-student-id');
            openStudentModal(studentId);
        });
    });

    // Make entire student item clickable (optional)
    document.querySelectorAll('.student-item').forEach(item => {
        item.addEventListener('click', function(e) {
            if (!e.target.closest('.student-actions')) {
                const studentId = this.getAttribute('data-student-id');
                openStudentModal(studentId);
            }
        });
    });
}

function openStudentModal(studentId) {
    const student = currentStudents.find(s => s.id == studentId);
    if (!student) return;

    // Populate modal with student info
    document.getElementById('modalStudentName').textContent = `Enter Results for ${student.first_name} ${student.last_name}`;
    document.getElementById('modalStudentId').value = studentId;
    document.getElementById('modalStudentIdDisplay').textContent = student.student_profile__student_id || student.username;
    
    const classLevelName = document.getElementById('classLevelSelect').options[document.getElementById('classLevelSelect').selectedIndex].text;
    document.getElementById('modalStudentClass').textContent = classLevelName;

    // Load existing result data if any
    const existingResult = resultsData[studentId];
    if (existingResult) {
        document.getElementById('modalClassScore').value = existingResult.class_score || '';
        document.getElementById('modalExamScore').value = existingResult.exam_score || '';
        document.getElementById('modalManualScore').value = existingResult.score || '';
        document.getElementById('modalRemarks').value = existingResult.remarks || '';
        
        // Set calculation mode
        const calcMode = existingResult.calculation_mode || 'system';
        document.querySelector(`input[name="calculation_mode"][value="${calcMode}"]`).checked = true;
        toggleCalculationMode();
    } else {
        // Clear form
        document.getElementById('studentResultForm').reset();
        document.querySelector('input[name="calculation_mode"][value="system"]').checked = true;
        toggleCalculationMode();
    }

    // Show modal
    document.getElementById('studentResultModal').style.display = 'flex';
    
    // Focus on first input
    setTimeout(() => {
        const firstInput = document.querySelector('#studentResultForm input:not([type="hidden"]):not([type="radio"])');
        if (firstInput) firstInput.focus();
    }, 100);
}

function hideStudentModal() {
    document.getElementById('studentResultModal').style.display = 'none';
}

function saveStudentResult() {
    const studentId = document.getElementById('modalStudentId').value;
    const calculationMode = document.querySelector('input[name="calculation_mode"]:checked').value;
    
    let resultData = {
        student_id: studentId,
        remarks: document.getElementById('modalRemarks').value,
        calculation_mode: calculationMode
    };

    // Validate based on calculation mode
    if (calculationMode === 'system') {
        const classScore = document.getElementById('modalClassScore').value;
        const examScore = document.getElementById('modalExamScore').value;
        
        if (!classScore || !examScore) {
            showToast('Please enter both class score and exam score', 'error');
            return;
        }
        
        const classScoreVal = parseFloat(classScore);
        const examScoreVal = parseFloat(examScore);
        
        if (classScoreVal < 0 || classScoreVal > 100 || examScoreVal < 0 || examScoreVal > 100) {
            showToast('Scores must be between 0 and 100', 'error');
            return;
        }
        
        resultData.class_score = classScoreVal;
        resultData.exam_score = examScoreVal;
    } else {
        const manualScore = document.getElementById('modalManualScore').value;
        
        if (!manualScore) {
            showToast('Please enter the total score', 'error');
            return;
        }
        
        const manualScoreVal = parseFloat(manualScore);
        
        if (manualScoreVal < 0 || manualScoreVal > 100) {
            showToast('Score must be between 0 and 100', 'error');
            return;
        }
        
        resultData.score = manualScoreVal;
        resultData.class_score = 0;
        resultData.exam_score = 0;
    }

    // Save to results data
    resultsData[studentId] = resultData;
    
    // Update UI
    updateStudentStatus(studentId);
    
    showToast('Result saved successfully. Click "Upload Results" to submit.', 'success');
    hideStudentModal();
    
    // Enable submit button if we have at least one result
    document.getElementById('submitBtn').disabled = Object.keys(resultsData).length === 0;
}

function updateStudentStatus(studentId) {
    const studentItem = document.querySelector(`.student-item[data-student-id="${studentId}"]`);
    if (!studentItem) return;

    const statusElement = studentItem.querySelector('.student-status');
    const result = resultsData[studentId];
    
    if (result) {
        const scoreDisplay = result.calculation_mode === 'system' 
            ? `Class: ${result.class_score || 'N/A'}, Exam: ${result.exam_score || 'N/A'}`
            : `Total: ${result.score || 'N/A'}`;
            
        statusElement.innerHTML = `
            <span class="status-badge status-completed">Result Entered</span>
            <div class="score-preview">${scoreDisplay}</div>
        `;
        
        // Update button text
        const actionsElement = studentItem.querySelector('.student-actions');
        const button = actionsElement.querySelector('.enter-result-btn');
        button.innerHTML = '<i class="bi bi-pencil"></i> Edit Result';
    }
}

async function loadExistingResults() {
    const classLevelId = document.getElementById('classLevelSelect').value;
    const subjectId = document.getElementById('subjectSelect').value;
    const termId = document.getElementById('termSelect').value;

    if (!classLevelId || !subjectId || !termId) return;

    try {
        const response = await fetch(`/academics/api/results/existing/?class_level_id=${classLevelId}&subject_id=${subjectId}&term_id=${termId}`);
        const data = await response.json();

        if (data.success && data.results) {
            resultsData = data.results;
            
            // Update UI for students with existing results
            Object.keys(resultsData).forEach(studentId => {
                updateStudentStatus(studentId);
            });
            
            // Enable submit button if we have results
            document.getElementById('submitBtn').disabled = Object.keys(resultsData).length === 0;
        }
    } catch (error) {
        console.error('Error loading existing results:', error);
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (Object.keys(resultsData).length === 0) {
        showToast('Please enter results for at least one student', 'error');
        return;
    }

    // Get form data
    const classLevelId = document.getElementById('classLevelSelect').value;
    const subjectId = document.getElementById('subjectSelect').value;
    const termId = document.getElementById('termSelect').value;
    const academicYearId = document.getElementById('academicYearSelect').value;
    const isPublished = document.getElementById('isPublished').checked;

    // Show loading modal
    const loadingModal = document.getElementById('loadingModal');
    loadingModal.style.display = 'flex';

    let successCount = 0;
    let errorCount = 0;
    const errors = [];

    // Submit each student's result individually
    for (const [studentId, resultData] of Object.entries(resultsData)) {
        try {
            const formData = new FormData();
            formData.append('student', studentId);
            formData.append('class_level', classLevelId);
            formData.append('subject', subjectId);
            formData.append('term', termId);
            formData.append('academic_year', academicYearId);
            formData.append('calculation_mode', resultData.calculation_mode);
            formData.append('remarks', resultData.remarks || '');
            
            if (isPublished) {
                formData.append('is_published', 'on');
            }

            if (resultData.calculation_mode === 'system') {
                formData.append('class_score', resultData.class_score);
                formData.append('exam_score', resultData.exam_score);
            } else {
                formData.append('score', resultData.score);
                formData.append('class_score', resultData.class_score || 0);
                formData.append('exam_score', resultData.exam_score || 0);
            }

            const response = await fetch('/academics/results/upload/result/new/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });

            if (response.ok) {
                successCount++;
            } else {
                errorCount++;
                const student = currentStudents.find(s => s.id == studentId);
                errors.push(`${student.first_name} ${student.last_name}`);
            }
        } catch (error) {
            errorCount++;
            const student = currentStudents.find(s => s.id == studentId);
            errors.push(`${student.first_name} ${student.last_name}`);
            console.error(`Error submitting result for student ${studentId}:`, error);
        }
    }

    // Hide loading modal
    loadingModal.style.display = 'none';

    // Show results
    if (successCount > 0) {
        showToast(`Successfully uploaded ${successCount} result(s)`, 'success');
    }
    
    if (errorCount > 0) {
        showToast(`Failed to upload ${errorCount} result(s): ${errors.join(', ')}`, 'error');
    }

    // If all succeeded, redirect
    // if (errorCount === 0 && successCount > 0) {
    //     setTimeout(() => {
    //         window.location.href = '/academics/upload-results/';
    //     }, 2000);
    // } else {
    //     // Reload the page to show updated results
    //     setTimeout(() => {
    //         window.location.reload();
    //     }, 3000);
    // }
}