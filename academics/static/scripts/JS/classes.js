import showToast from "/static/scripts/JS/admin_d.js"

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
        // Implement view functionality
        console.log('View class:', classId);
    }
    
    if (e.target.closest('.edit-btn')) {
        const btn = e.target.closest('.edit-btn');
        const classId = btn.getAttribute('data-class-id');
        // Implement edit functionality
        console.log('Edit class:', classId);
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


function getCsrfToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}