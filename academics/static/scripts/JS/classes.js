import showToast from "/static/scripts/JS/admin_d.js"
import hideLoader from "/static/scripts/JS/admin_d.js"
import showLoader from "/static/scripts/JS/admin_d.js"
import getCsrfToken from "/static/scripts/JS/utility/getCsrfToken.js"


document.addEventListener('click', function(e) {
    const dropdownBtn = e.target.closest('.dropdown-toggle');
    if (dropdownBtn) {
        const dropdown = dropdownBtn.closest('.dropdown');
        dropdown.classList.toggle('show');
    } else {
        document.querySelectorAll('.dropdown').forEach(dropdown => {
            dropdown.classList.remove('show');
        });
    }
});


// Get class data
async function getClassData(classId) {
    try {
        const response = await fetch(`/academics/classes/${classId}/data/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        const data = await response.json();

        if (data.success) {
            return data.data;
        } else {
            showToast(data.error || 'Failed to load class data', 'error');
            return null;
        }
    } catch (error) {
        console.error('Error fetching class data:', error);
        showToast('An error occurred while loading class data', 'error');
        return null;
    }
}

// View class function
async function viewClass(classId) {
    try {
        showLoader();
        const classData = await getClassData(classId);
        hideLoader();
        
        if (classData) {
            showViewModal(classData);
        }
    } catch (error) {
        hideLoader();
        console.error('Error viewing class:', error);
    }
}

// Edit class function
async function editClass(classId) {
    try {
        showLoader();
        const classData = await getClassData(classId);
        hideLoader();
        
        if (classData) {
            showEditModal(classData);
        }
    } catch (error) {
        hideLoader();
        console.error('Error editing class:', error);
    }
}

// Show view modal for class
function showViewModal(classData) {
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 700px;">
            <div class="modal-header">
                <h2>🏫 Class Details</h2>
                <button class="modal-close close-modal">✕</button>
            </div>
            <div class="modal-body">
                <div class="class-view-content">
                    <div class="class-basic-info">
                        <div class="class-icon-large" style="background: var(--primary);">
                            <i class="bi bi-building"></i>
                        </div>
                        <div class="class-name-large">${classData.name}</div>
                        <div class="class-code">${classData.code || 'No code'}</div>
                    </div>
                    
                    <div class="info-grid">
                        <div class="info-item">
                            <label>Capacity</label>
                            <span>${classData.capacity} students</span>
                        </div>
                        <div class="info-item">
                            <label>Current Students</label>
                            <span>${classData.current_students_count}</span>
                        </div>
                        <div class="info-item">
                            <label>Available Seats</label>
                            <span>${classData.available_seats}</span>
                        </div>
                        <div class="info-item">
                            <label>Status</label>
                            <span class="status-badge ${classData.is_active ? 'active' : 'inactive'}">
                                ${classData.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                        <div class="info-item">
                            <label>Form Teacher</label>
                            <span>${classData.form_teacher_name || 'Not assigned'}</span>
                        </div>
                        <div class="info-item">
                            <label>Display Order</label>
                            <span>${classData.display_order}</span>
                        </div>
                        <div class="info-item full-width">
                            <label>Description</label>
                            <span>${classData.description || 'No description provided'}</span>
                        </div>
                        <div class="info-item full-width">
                            <label>Subjects (${classData.subjects.length})</label>
                            <div class="subjects-list">
                                ${classData.subjects.map(subject => 
                                    `<span class="subject-tag">${subject.name} (${subject.code})</span>`
                                ).join('') || '<span>No subjects assigned</span>'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary close-modal">Close</button>
                <button type="button" class="btn btn-primary edit-from-view" data-class-id="${classData.id}">
                    <i class="bi bi-pencil-square"></i> Edit Class
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.querySelector('.close-modal').addEventListener('click', () => modal.remove());
    modal.querySelector('.edit-from-view').addEventListener('click', () => {
        modal.remove();
        editClass(classData.id);
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

// Show edit modal for class
function showEditModal(classData) {
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 700px;">
            <div class="modal-header">
                <h2>✏️ Edit Class</h2>
                <button class="modal-close close-modal">✕</button>
            </div>
            <form id="editClassForm" data-class-id="${classData.id}">
                <div class="modal-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Class Name *</label>
                            <input type="text" name="name" class="form-control" value="${classData.name || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>Class Code</label>
                            <input type="text" name="code" class="form-control" value="${classData.code || ''}">
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea name="description" class="form-control" rows="3">${classData.description || ''}</textarea>
                        </div>
                        <div class="form-group">
                            <label>Capacity</label>
                            <input type="number" name="capacity" class="form-control" value="${classData.capacity || 30}" min="1" max="100">
                        </div>
                        <div class="form-group">
                            <label>Display Order</label>
                            <input type="number" name="display_order" class="form-control" value="${classData.display_order || 0}">
                        </div>
                        <div class="form-group">
                            <label>Form Teacher</label>
                            <select name="form_teacher" class="form-control" id="formTeacherSelect">
                                <option value="">Select teacher...</option>
                                <!-- Teachers will be populated dynamically -->
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Subjects</label>
                            <select name="subjects" class="form-control" id="subjectsSelect" multiple style="height: 120px;">
                                <!-- Subjects will be populated dynamically -->
                            </select>
                            <small style="color: var(--text-secondary); font-size: 0.75rem;">Hold Ctrl/Cmd to select multiple</small>
                        </div>
                        <div class="form-group">
                            <label style="display: flex; align-items: center; gap: 8px;">
                                <input type="checkbox" name="is_active" ${classData.is_active ? 'checked' : ''}>
                                <span>Active Class</span>
                            </label>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary close-modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Update Class</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Load teachers and subjects for dropdowns
    loadTeachersAndSubjects(modal, classData);
    
    modal.querySelector('#editClassForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await updateClass(classData.id, new FormData(e.target));
    });
    
    modal.querySelector('.close-modal').addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

// Load teachers and subjects for edit modal
async function loadTeachersAndSubjects(modal, classData) {
    try {
        // Load teachers
        const teachersResponse = await fetch('/academics/api/teachers/');
        const teachersData = await teachersResponse.json();
        
        if (teachersData.success) {
            const teacherSelect = modal.querySelector('#formTeacherSelect');
            teachersData.teachers.forEach(teacher => {
                const option = document.createElement('option');
                option.value = teacher.id;
                option.textContent = `${teacher.first_name} ${teacher.last_name} (${teacher.teacher_profile__employee_id})`;
                option.selected = classData.form_teacher === teacher.id;
                teacherSelect.appendChild(option);
            });
        }
        
        // Load subjects
        const subjectsResponse = await fetch('/academics/api/subjects/');
        const subjectsData = await subjectsResponse.json();
        
        if (subjectsData.success) {
            const subjectsSelect = modal.querySelector('#subjectsSelect');
            subjectsData.subjects.forEach(subject => {
                const option = document.createElement('option');
                option.value = subject.id;
                option.textContent = `${subject.name} (${subject.code})`;
                // Checking if a subject is already assigned to the class
                const isSelected = classData.subjects.some(s => s.id === subject.id);
                option.selected = isSelected;
                subjectsSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading dropdown data:', error);
    }
}

// Update class function
async function updateClass(classId, formData) {
    try {
        const response = await fetch(`/academics/classes/${classId}/update/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
            document.querySelector('.modal.show')?.remove();
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showToast(data.error || 'Failed to update class', 'error');
        }
    } catch (error) {
        console.error('Error updating class:', error);
        showToast('An error occurred while updating class', 'error');
    }
}


function showDeleteConfirmation(classId, className) {
    const modal = document.createElement('div');
    modal.className = 'confirmation-modal show';
    modal.innerHTML = `
        <div class="confirmation-content">
            <div class="confirmation-icon">
                <i class="bi bi-exclamation-triangle"></i>
            </div>
            <h3 class="confirmation-title">Delete Class</h3>
            <p class="confirmation-message">
                Are you sure you want to delete <strong>${className}</strong>? 
                This action cannot be undone and all associated data will be permanently removed.
            </p>
            <div class="confirmation-actions">
                <button class="btn btn-outline btn-cancel" style="padding: 10px 20px;">Cancel</button>
                <button class="btn btn-danger btn-confirm-delete" style="padding: 10px 20px;" data-class-id="${classId}">
                    <i class="bi bi-trash"></i> Delete Class
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.querySelector('.btn-cancel').addEventListener('click', () => {
        modal.remove();
    });
    
    modal.querySelector('.btn-confirm-delete').addEventListener('click', function() {
        const classId = this.getAttribute('data-class-id');
        deleteClass(classId);
        modal.remove();
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Delete class function
async function deleteClass(classId) {
    try {
        const response = await fetch(`/academics/classes/${classId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
            const classCard = document.querySelector(`[data-class-id="${classId}"]`).closest('.class-card');
            if (classCard) {
                classCard.remove();
            }
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showToast(data.error || 'Failed to delete class', 'error');
        }
    } catch (error) {
        console.error('Error deleting class:', error);
        showToast('An error occurred while deleting class', 'error');
    }
}

// Assign teacher to class
async function assignTeacher(classId) {
    try {
        showLoader();
        const classData = await getClassData(classId);
        const teachersResponse = await fetch('/academics/api/teachers/');
        const teachersData = await teachersResponse.json();
        hideLoader();

        if (classData && teachersData.success) {
            showAssignTeacherModal(classData, teachersData.teachers);
        }
    } catch (error) {
        hideLoader();
        console.error('Error loading data for teacher assignment:', error);
        showToast('An error occurred while loading data', 'error');
    }
}

// Show assign teacher modal
function showAssignTeacherModal(classData, teachers) {
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h2>👨‍🏫 Assign Teacher</h2>
                <button class="modal-close close-modal">✕</button>
            </div>
            <form id="assignTeacherForm" data-class-id="${classData.id}">
                <div class="modal-body">
                    <div class="class-info">
                        <div class="class-avatar">${classData.name.charAt(0)}</div>
                        <div class="class-details">
                            <div class="class-name">${classData.name}</div>
                            <div class="class-code">${classData.code || 'No code'}</div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Select Form Teacher *</label>
                        <select name="form_teacher" class="form-control" required>
                            <option value="">Select a teacher...</option>
                            ${teachers.map(teacher => `
                                <option value="${teacher.id}" ${classData.form_teacher === teacher.id ? 'selected' : ''}>
                                    ${teacher.first_name} ${teacher.last_name} - ${teacher.teacher_profile__employee_id}
                                </option>
                            `).join('')}
                        </select>
                    </div>
                    
                    <div class="current-teacher" style="margin-top: 16px; padding: 12px; background: var(--bg-main); border-radius: 8px;">
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 4px;">Current Teacher:</div>
                        <div style="font-weight: 600; color: var(--text-primary);">
                            ${classData.form_teacher_name || 'Not assigned'}
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary close-modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Assign Teacher</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.querySelector('#assignTeacherForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await updateClassTeacher(classData.id, new FormData(e.target));
    });
    
    modal.querySelector('.close-modal').addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

// Manage subjects for class
async function manageSubjects(classId) {
    try {
        showLoader();
        const classData = await getClassData(classId);
        const subjectsResponse = await fetch('/academics/api/subjects/');
        const subjectsData = await subjectsResponse.json();
        const academicYears = await loadAcademicYears();
        hideLoader();

        if (classData && subjectsData.success) {
            showManageSubjectsModal(classData, subjectsData.subjects, academicYears.academic_years
);
        }
    } catch (error) {
        hideLoader();
        console.error('Error loading data for subject management:', error);
        showToast('An error occurred while loading data', 'error');
    }
}

async function loadAcademicYears() {
    try {
        const response = await fetch('/academics/academic-years/', {
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest',
            },
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error loading academic years:', error);
        return [];
    }
}

// Show manage subjects modal
function showManageSubjectsModal(classData, allSubjects, academicYears) {

    const modal = document.createElement('div');
    
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <h2>📚 Manage Subjects - ${classData.name}</h2>
                <button class="modal-close close-modal">✕</button>
            </div>
            <div class="modal-body">
                <div class="class-info">
                    <div class="class-avatar">${classData.name.charAt(0)}</div>
                    <div class="class-details">
                        <div class="class-name">${classData.name}</div>
                        <div class="class-students">${classData.current_students_count} students</div>
                    </div>
                </div>
                
                <div class="subjects-management">
                    ${academicYears && academicYears.length > 0 ? `
                        <div class="form-group">
                            <label for="academic_year">Academic Year</label>
                            <select name="academic_year" id="academic_year" class="form-control" required>
                                <option value="">Select Academic Year</option>
                                ${academicYears.map(year => `
                                    <option value="${year.id}" ${year.is_current ? 'selected' : ''}>
                                        ${year.name} ${year.is_current ? '(Current)' : ''}
                                    </option>
                                `).join('')}
                            </select>
                        </div>
                    ` : `
                        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 12px 16px; border-radius: 6px; display: flex; align-items: center; gap: 8px;">
                            <i class="bi bi-exclamation-triangle" style="color: #f39c12; font-size: 16px;"></i>
                            <span>
                                No academic years available. Please ${" "}
                                <a href="/academics/academic-years/create/" style="color: #856404; text-decoration: underline; font-weight: 500;">
                                    create an academic year
                                </a> 
                                first.
                            </span>
                        </div>
                    `}

                    <div class="form-group">
                        <label>Available Subjects</label>
                        <div class="subjects-selection">
                            <div class="subjects-list-container">
                                ${allSubjects.map(subject => {
                                    const isSelected = classData.subjects.some(s => s.id === subject.id);
                                    return `
                                        <div class="subject-item ${isSelected ? 'selected' : ''}" data-subject-id="${subject.id}">
                                            <div class="subject-check">
                                                <input name="subjects" type="checkbox" value="${subject.id}" ${isSelected ? 'checked' : ''}>
                                            </div>
                                            <div class="subject-info">
                                                <div class="subject-name">${subject.name}</div>
                                                <div class="subject-code">${subject.code}</div>
                                            </div>
                                            <div class="subject-category">
                                                <span class="category-badge ${subject.category === 'core' ? 'core' : 'elective'}">
                                                    ${subject.category === 'core' ? 'Core' : 'Elective'}
                                                </span>
                                            </div>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                        </div>
                        <small style="color: var(--text-secondary); font-size: 0.75rem;">
                            Select the subjects to be taught in this class
                        </small>
                    </div>
                    
                    <div class="selection-summary">
                        <div class="summary-item">
                            <span>Total Selected:</span>
                            <span id="selectedCount">${classData.subjects.length}</span>
                        </div>
                        <div class="summary-item">
                            <span>Core Subjects:</span>
                            <span id="coreCount">${classData.subjects.filter(s => s.category === 'core').length}</span>
                        </div>
                        <div class="summary-item">
                            <span>Elective Subjects:</span>
                            <span id="electiveCount">${classData.subjects.filter(s => s.category === 'elective').length}</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary close-modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="saveSubjectsBtn">
                    <i class="bi bi-check-lg"></i> Save Changes
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Update selection counts
    function updateSelectionCounts() {
        const selectedItems = modal.querySelectorAll('.subject-item.selected');
        const selectedCount = selectedItems.length;
        const coreCount = Array.from(selectedItems).filter(item => {
            return item.querySelector('.category-badge').textContent === 'Core';
        }).length;
        const electiveCount = selectedCount - coreCount;
        
        modal.querySelector('#selectedCount').textContent = selectedCount;
        modal.querySelector('#coreCount').textContent = coreCount;
        modal.querySelector('#electiveCount').textContent = electiveCount;
    }
    
    // Handle subject item clicks
    const subjectItems = modal.querySelectorAll('.subject-item');
    subjectItems.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        
        item.addEventListener('click', (e) => {
            if (e.target.type !== 'checkbox') {
                checkbox.checked = !checkbox.checked;
            }
            
            if (checkbox.checked) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
            
            updateSelectionCounts();
        });
        
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
            updateSelectionCounts();
        });
    });
    
    modal.querySelector('#saveSubjectsBtn').addEventListener('click', async () => {
        await updateClassSubjects(classData.id);
    });
    
    modal.querySelector('.close-modal').addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
    
    updateSelectionCounts();
}

// Update class teacher
async function updateClassTeacher(classId, formData) {
    try {
        const response = await fetch(`/academics/classes/${classId}/assign-teacher/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
            document.querySelector('.modal.show')?.remove();
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showToast(data.error || 'Failed to assign teacher', 'error');
        }
    } catch (error) {
        console.error('Error assigning teacher:', error);
        showToast('An error occurred while assigning teacher', 'error');
    }
}

// Update class subjects
async function updateClassSubjects(classId, formData) {
    try {
        console.log('Starting updateClassSubjects for class:', classId);
        
        // Wait a bit if content was dynamically loaded
        await new Promise(resolve => setTimeout(resolve, 50));

        const academicYearSelect = document.querySelector('select[name="academic_year"]');
        const academicYearId = academicYearSelect ? academicYearSelect.value : null;
        
        if (!academicYearId) {
            showToast('Please select an academic year', 'error');
            return;
        }
        
        const subjectCheckboxes = document.querySelectorAll('input[name="subjects"]:checked');
        console.log('Found checkboxes:', subjectCheckboxes.length);
        
        // Debug each checkbox
        subjectCheckboxes.forEach((checkbox, index) => {
            console.log(`Checkbox ${index}:`, {
                value: checkbox.value,
                id: checkbox.id,
                dataset: checkbox.dataset
            });
        });
        
        const subjectIds = Array.from(subjectCheckboxes)
            .map(checkbox => {
                // Try different ways to get the ID
                return checkbox.value || 
                       checkbox.getAttribute('data-subject-id') || 
                       checkbox.id.replace('subject_', '');
            })
            .filter(id => id && id !== ''); // Remove empty values
        
        console.log('Final subjectIds:', subjectIds);
        
        if (subjectIds.length === 0) {
            showToast('Please select at least one subject', 'error');
            return;
        }
        
        const submitData = new FormData();
        submitData.append("academic_year", academicYearId)
        subjectIds.forEach(id => {
            submitData.append('subjects', id);
        });

        const response = await fetch(`/academics/classes/${classId}/assign-subjects/`, {
            method: 'POST',
            body: submitData,
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        const data = await response.json();
        console.log('Server response:', data);

        if (data.success) {
            showToast(data.message, 'success');
            document.querySelector('.modal.show')?.remove();
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showToast(data.error || 'Failed to update subjects', 'error');
        }
    } catch (error) {
        console.error('Error updating subjects:', error);
        showToast('An error occurred while updating subjects', 'error');
    }
}

// Event listeners for action buttons
document.addEventListener('click', function(e) {
    if (e.target.closest('.delete-btn')) {
        const btn = e.target.closest('.delete-btn');
        const classId = btn.getAttribute('data-class-id');
        const className = btn.closest('.class-card').querySelector('.class-name').textContent;
        showDeleteConfirmation(classId, className);
    }
    
    if (e.target.closest('.view-btn')) {
        const btn = e.target.closest('.view-btn');
        const classId = btn.getAttribute('data-class-id');
        viewClass(classId);
    }
    
    if (e.target.closest('.edit-btn')) {
        const btn = e.target.closest('.edit-btn');
        const classId = btn.getAttribute('data-class-id');
        editClass(classId);
    }
    
    if (e.target.closest('.assign-teacher-btn')) {
        const btn = e.target.closest('.assign-teacher-btn');
        const classId = btn.getAttribute('data-class-id');
        assignTeacher(classId);
    }
    
    if (e.target.closest('.manage-subjects-btn')) {
        const btn = e.target.closest('.manage-subjects-btn');
        const classId = btn.getAttribute('data-class-id');
        manageSubjects(classId);
    }
});


document.addEventListener('DOMContentLoaded', function() {
    const classForm = document.getElementById('classForm');
    if (classForm) {
        classForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            try {
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Creating...';
                submitBtn.disabled = true;
                
                const response = await fetch(this.getAttribute('data-url'), {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                });

                const data = await response.json();

                if (data.success) {
                    showToast(data.message, 'success');
                    setTimeout(() => {
                        const modal = document.getElementById('classModal');
                        if (modal) modal.style.display = 'none';
                        window.location.reload();
                    }, 1500);
                } else {
                    showToast(data.error || 'Failed to create class', 'error');
                }
            } catch (error) {
                console.error('Error creating class:', error);
                showToast('An error occurred while creating class', 'error');
            } finally {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // Modal functionality
    const openModalBtn = document.getElementById('openClassModal');
    const modal = document.getElementById('classModal');
    const closeModalBtns = document.querySelectorAll('.closeModal');

    if (openModalBtn && modal) {
        openModalBtn.addEventListener('click', () => {
            modal.style.display = 'flex';
        });
    }

    if (closeModalBtns) {
        closeModalBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                if (modal) modal.style.display = 'none';
            });
        });
    }

    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
});