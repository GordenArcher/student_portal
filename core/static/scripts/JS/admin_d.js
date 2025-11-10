
export function showToast(message, type = "success", duration = 3000) {
    const toast = document.getElementById("toast");
    if (!toast) return;

    toast.textContent = message;
    toast.className = `toast ${type} show bounce`;

    setTimeout(() => {
        toast.className = `toast ${type}`;
    }, duration);
}


document.addEventListener("DOMContentLoaded", function() {
    const navLinks = document.querySelectorAll(".nav-links li a");
    const currentPath = window.location.pathname.replace(/\/$/, "");

    navLinks.forEach(link => {
        if (!link.href || link.getAttribute("href") === "#") return;

        const linkPath = new URL(link.href, window.location.origin)
            .pathname.replace(/\/$/, "");

        if (linkPath === currentPath) {
            link.classList.add("active");
        } else {
            link.classList.remove("active");
        }

        link.addEventListener("click", () => {
            navLinks.forEach(l => l.classList.remove("active"));
            link.classList.add("active");
        });
    });
});