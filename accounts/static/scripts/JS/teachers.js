import showToast from "../../../../core/static/scripts/JS/admin_d.js"

document.getElementById("openModal").onclick = openModal
document.querySelector(".closeModal").onclick = closeModal

function openModal() {
    document.getElementById('teacherModal').classList.add('show');
}

function closeModal() {
    document.getElementById('teacherModal').classList.remove('show');
}

document.getElementById('teacherModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

const colors = ['#2563eb', '#10b981', '#8b5cf6', '#f59e0b', '#06b6d4', '#ec4899', '#ef4444'];
document.querySelectorAll('.teacher-avatar').forEach((avatar, index) => {
    avatar.style.background = colors[index % colors.length];
});


document.addEventListener('DOMContentLoaded', () => {
    const teacherForm = document.getElementById('teacherForm');
    if (!teacherForm) return;

    teacherForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(teacherForm);
        const url = teacherForm.dataset.url;
        const csrf = teacherForm.dataset.csrf;

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrf,
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: formData
            });

            const data = await response.json();

            if (data.status === "success") {
                showToast(data.message, "success");
                closeModal();
                setTimeout(() => location.reload(), 1500);
            } else {
                showToast(data.message || "Error creating user", "error");
            }

        } catch (err) {
            showToast("Something went wrong. Try again.", "error");
            console.error(err);
        }
    });
});
