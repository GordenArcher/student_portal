class StudentsManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // View student results
        document.addEventListener('click', (e) => {
            if (e.target.closest('.view-results')) {
                const button = e.target.closest('.view-results');
                const studentId = button.dataset.studentId;
                const studentName = button.dataset.studentName;
                this.viewStudentResults(studentId, studentName);
            }
        });

        // Export students list
        const exportBtn = document.getElementById('exportStudents');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportStudents());
        }
    }

    async viewStudentResults(studentId, studentName) {
        const modal = new bootstrap.Modal(document.getElementById('resultsModal'));
        const modalTitle = document.getElementById('resultsModalTitle');
        const modalBody = document.getElementById('resultsModalBody');

        modalTitle.textContent = `Results - ${studentName}`;
        modalBody.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;

        modal.show();

        try {
            const response = await fetch(`/ajax/student/${studentId}/results/`);
            const data = await response.json();

            if (data.success) {
                this.renderStudentResults(modalBody, data.results);
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('Error loading results:', error);
            modalBody.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    Error loading results: ${error.message}
                </div>
            `;
        }
    }

    renderStudentResults(container, results) {
        if (!results || results.length === 0) {
            container.innerHTML = `
                <div class="empty-state small">
                    <i class="bi bi-journal-x"></i>
                    <p>No results found for this student</p>
                </div>
            `;
            return;
        }

        const html = `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Subject</th>
                            <th>Score</th>
                            <th>Grade</th>
                            <th>Term</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map(result => `
                            <tr>
                                <td>
                                    <strong>${this.escapeHtml(result.subject_name)}</strong>
                                    <br><small class="text-muted">${this.escapeHtml(result.subject_code)}</small>
                                </td>
                                <td>
                                    <span class="score-value">${result.score}</span>%
                                </td>
                                <td>
                                    <span class="grade-badge grade-${result.grade.toLowerCase()}">${result.grade}</span>
                                </td>
                                <td>${this.escapeHtml(result.term_name)} ${this.escapeHtml(result.academic_year)}</td>
                                <td>${new Date(result.date_uploaded).toLocaleDateString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            <div class="mt-3">
                <strong>Average Score:</strong> 
                ${(results.reduce((sum, result) => sum + result.score, 0) / results.length).toFixed(1)}%
            </div>
        `;

        container.innerHTML = html;
    }

    exportStudents() {
        // Simple CSV export implementation
        const students = [];
        document.querySelectorAll('.student-card').forEach(card => {
            const name = card.querySelector('h3').textContent.trim();
            const studentId = card.querySelector('.student-id').textContent.trim();
            const className = card.querySelector('.detail-item span').textContent.trim();
            students.push({ name, studentId, className });
        });

        if (students.length === 0) {
            alert('No students to export');
            return;
        }

        const csvContent = [
            ['Name', 'Student ID', 'Class'],
            ...students.map(s => [s.name, s.studentId, s.className])
        ].map(row => row.join(',')).join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `students_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
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

document.addEventListener('DOMContentLoaded', function() {
    window.studentsManager = new StudentsManager();
});