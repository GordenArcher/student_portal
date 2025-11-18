class ResultsManager {
    constructor() {
        this.uploadUrl = '/teacher/results/upload/';
        this.deleteUrl = '/teacher/results/delete/';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStudentsForSubject();
    }

    setupEventListeners() {
        // Upload form submission
        const uploadForm = document.getElementById('uploadResultForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => this.handleUpload(e));
        }

        // Subject change - load students
        const subjectSelect = document.getElementById('subjectSelect');
        if (subjectSelect) {
            subjectSelect.addEventListener('change', () => this.loadStudentsForSubject());
        }

        // Score input - preview grade
        const scoreInput = document.querySelector('input[name="score"]');
        if (scoreInput) {
            scoreInput.addEventListener('input', () => this.previewGrade());
        }

        // Delete result buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.delete-result')) {
                const resultId = e.target.closest('.delete-result').dataset.resultId;
                this.deleteResult(resultId);
            }
        });

        // Auto-submit filters on change
        const filterSelects = document.querySelectorAll('.filters-form select');
        filterSelects.forEach(select => {
            select.addEventListener('change', () => {
                document.querySelector('.filters-form').submit();
            });
        });
    }

    async loadStudentsForSubject() {
        const subjectSelect = document.getElementById('subjectSelect');
        const studentSelect = document.getElementById('studentSelect');
        const subjectId = subjectSelect.value;

        if (!subjectId) {
            studentSelect.innerHTML = '<option value="">Select Subject First</option>';
            return;
        }

        try {
            studentSelect.innerHTML = '<option value="">Loading students...</option>';
            studentSelect.disabled = true;

            // Get class ID from selected subject
            const selectedOption = subjectSelect.options[subjectSelect.selectedIndex];
            const classId = selectedOption.dataset.classId;

            // Load students for this class
            const response = await fetch(`/ajax/students/?class_id=${classId}`);
            const data = await response.json();

            if (data.students) {
                studentSelect.innerHTML = '<option value="">Select Student</option>';
                data.students.forEach(student => {
                    const option = document.createElement('option');
                    option.value = student.id;
                    option.textContent = `${student.full_name} (${student.student_id})`;
                    studentSelect.appendChild(option);
                });
            } else {
                studentSelect.innerHTML = '<option value="">No students found</option>';
            }
        } catch (error) {
            console.error('Error loading students:', error);
            studentSelect.innerHTML = '<option value="">Error loading students</option>';
        } finally {
            studentSelect.disabled = false;
        }
    }

    previewGrade() {
        const scoreInput = document.querySelector('input[name="score"]');
        const gradePreview = document.getElementById('gradePreview');
        const score = parseFloat(scoreInput.value);

        if (isNaN(score) || score < 0 || score > 100) {
            gradePreview.textContent = '-';
            gradePreview.className = '';
            return;
        }

        const grade = this.calculateGrade(score);
        gradePreview.textContent = grade;
        gradePreview.className = `grade-badge grade-${grade.toLowerCase()}`;
    }

    calculateGrade(score) {
        if (score >= 80) return 'A';
        if (score >= 70) return 'B';
        if (score >= 60) return 'C';
        if (score >= 50) return 'D';
        return 'F';
    }

    async handleUpload(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const uploadButton = document.getElementById('uploadButton');
        
        // Basic validation
        const score = parseFloat(formData.get('score'));
        if (score < 0 || score > 100) {
            this.showNotification('Score must be between 0 and 100', 'error');
            return;
        }

        const uploadData = {
            student_id: formData.get('student_id'),
            subject_id: formData.get('subject_id'),
            score: score,
            academic_year_id: formData.get('academic_year_id'),
            term_id: formData.get('term_id'),
            remarks: formData.get('remarks')
        };

        try {
            uploadButton.disabled = true;
            uploadButton.innerHTML = '<i class="bi bi-hourglass-split"></i> Uploading...';

            const response = await fetch(this.uploadUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify(uploadData),
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Result uploaded successfully!', 'success');
                this.addResultToTable(data.result);
                this.resetUploadForm();
                bootstrap.Modal.getInstance(document.getElementById('uploadModal')).hide();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showNotification('Error uploading result: ' + error.message, 'error');
        } finally {
            uploadButton.disabled = false;
            uploadButton.innerHTML = '<i class="bi bi-cloud-upload"></i> Upload Result';
        }
    }

    async deleteResult(resultId) {
        if (!confirm('Are you sure you want to delete this result? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`${this.deleteUrl}${resultId}/`, {
                method: 'DELETE',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCsrfToken(),
                },
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Result deleted successfully!', 'success');
                this.removeResultFromTable(resultId);
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('Delete error:', error);
            this.showNotification('Error deleting result: ' + error.message, 'error');
        }
    }

    addResultToTable(resultData) {
        const tbody = document.getElementById('results-tbody');
        const emptyState = document.querySelector('.empty-state');
        
        if (emptyState) {
            emptyState.style.display = 'none';
        }

        const newRow = document.createElement('tr');
        newRow.dataset.resultId = resultData.id;
        newRow.innerHTML = `
            <td>
                <div class="student-info">
                    <div class="student-avatar-sm">
                        <i class="bi bi-person-circle"></i>
                    </div>
                    <div class="student-details">
                        <strong>${this.escapeHtml(resultData.student_name)}</strong>
                        <small>Student ID</small>
                    </div>
                </div>
            </td>
            <td>
                <div class="subject-info">
                    <strong>${this.escapeHtml(resultData.subject_name)}</strong>
                    <small>Code</small>
                </div>
            </td>
            <td>
                <span class="class-badge">Class</span>
            </td>
            <td>
                <div class="score-display">
                    <span class="score-value">${resultData.score}</span>
                    <small>%</small>
                </div>
            </td>
            <td>
                <span class="grade-badge grade-${resultData.grade.toLowerCase()}">${resultData.grade}</span>
            </td>
            <td>
                <span class="term-badge">Term Year</span>
            </td>
            <td>
                <span class="upload-date">${resultData.date_uploaded}</span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-outline-danger delete-result" 
                            data-result-id="${resultData.id}"
                            title="Delete Result">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        `;

        tbody.insertBefore(newRow, tbody.firstChild);
    }

    removeResultFromTable(resultId) {
        const row = document.querySelector(`tr[data-result-id="${resultId}"]`);
        if (row) {
            row.remove();
        }

        // Show empty state if no results left
        const tbody = document.getElementById('results-tbody');
        if (tbody.children.length === 0) {
            const emptyState = document.querySelector('.empty-state');
            if (emptyState) {
                emptyState.style.display = 'block';
            }
        }
    }

    resetUploadForm() {
        const form = document.getElementById('uploadResultForm');
        if (form) {
            form.reset();
            document.getElementById('gradePreview').textContent = '-';
            document.getElementById('gradePreview').className = '';
            document.getElementById('studentSelect').innerHTML = '<option value="">Select Subject First</option>';
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.getElementById('notifications');
        if (container) {
            container.appendChild(notification);
        }
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.cookie.match(/csrftoken=([^;]+)/)?.[1];
    }

    escapeHtml(unsafe) {
        if (unsafe === null || unsafe === undefined) return '';
        return unsafe.toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.resultsManager = new ResultsManager();
});