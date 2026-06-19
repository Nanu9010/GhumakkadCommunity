document.addEventListener('DOMContentLoaded', function() {
    initNavbarScroll();
    initFadeInAnimations();
    initSmoothScroll();
    initStarRating();
    initImageGallery();
    initPriceSlider();
});

function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

function initFadeInAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });
    document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
}

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

function initStarRating() {
    document.querySelectorAll('.star-rating-input').forEach(container => {
        const stars = container.querySelectorAll('i');
        const input = container.querySelector('input[type="hidden"]');
        stars.forEach(star => {
            star.addEventListener('click', function() {
                const value = this.dataset.value;
                input.value = value;
                stars.forEach(s => {
                    s.classList.remove('bi-star-fill');
                    s.classList.add('bi-star');
                    if (parseInt(s.dataset.value) <= parseInt(value)) {
                        s.classList.remove('bi-star');
                        s.classList.add('bi-star-fill');
                    }
                });
            });
            star.addEventListener('mouseenter', function() {
                const value = this.dataset.value;
                stars.forEach(s => {
                    s.classList.remove('bi-star-fill');
                    s.classList.add('bi-star');
                    if (parseInt(s.dataset.value) <= parseInt(value)) {
                        s.classList.remove('bi-star');
                        s.classList.add('bi-star-fill');
                    }
                });
            });
            container.addEventListener('mouseleave', function() {
                const selected = input.value;
                stars.forEach(s => {
                    s.classList.remove('bi-star-fill');
                    s.classList.add('bi-star');
                    if (parseInt(s.dataset.value) <= parseInt(selected)) {
                        s.classList.remove('bi-star');
                        s.classList.add('bi-star-fill');
                    }
                });
            });
        });
    });
}

function initImageGallery() {
    const mainImg = document.querySelector('.gallery-main img');
    const thumbs = document.querySelectorAll('.thumb-grid img');
    if (!mainImg || !thumbs.length) return;
    thumbs.forEach(thumb => {
        thumb.addEventListener('click', function() {
            mainImg.src = this.src;
            thumbs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function initPriceSlider() {
    const slider = document.querySelector('.price-slider');
    const output = document.querySelector('.price-output');
    if (!slider || !output) return;
    output.textContent = '₹' + slider.value;
    slider.addEventListener('input', function() {
        output.textContent = '₹' + this.value;
    });
}

function addToWishlist(url) {
    fetch(url, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    }).then(response => {
        if (response.ok) { location.reload(); }
    }).catch(err => console.error(err));
}

function applyCoupon() {
    const code = document.getElementById('couponInput')?.value;
    if (!code) return;
    const form = document.getElementById('couponForm');
    if (form) form.submit();
}

function confirmDelete(url) {
    if (confirm('Are you sure you want to delete this?')) {
        window.location.href = url;
    }
}

function updateBookingTotal() {
    const price = parseFloat(document.getElementById('tourPrice')?.dataset?.price || 0);
    const travelers = parseInt(document.getElementById('id_travelers')?.value || 1);
    const total = price * travelers;
    const totalEl = document.getElementById('bookingTotal');
    if (totalEl) {
        totalEl.textContent = '₹' + total.toLocaleString();
    }
}

function initNotificationAutoDismiss() {
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
}

window.addEventListener('load', initNotificationAutoDismiss);

function loadSlots(dateUrl) {
    fetch(dateUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById('slotContainer');
            if (!container) return;
            container.innerHTML = '';
            data.slots.forEach(slot => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'btn btn-outline-custom m-1 slot-btn';
                btn.dataset.slotId = slot.id;
                btn.dataset.available = slot.available;
                btn.innerHTML = `${slot.start_time} - ${slot.end_time} <small>(${slot.available} spots)</small>`;
                if (slot.available < 1) { btn.disabled = true; btn.classList.add('disabled'); }
                btn.addEventListener('click', function() {
                    document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    document.getElementById('selectedSlot')?.setAttribute('value', slot.id);
                });
                container.appendChild(btn);
            });
        });
}

function initTourBooking() {
    const dateInput = document.getElementById('id_travel_date');
    if (!dateInput) return;
    dateInput.addEventListener('change', function() {
        const tourId = this.dataset.tourId;
        if (this.value && tourId) {
            loadSlots(`/tours/api/slots/${tourId}/${this.value}/`);
        }
    });
    const travelersInput = document.getElementById('id_travelers');
    if (travelersInput) {
        travelersInput.addEventListener('change', updateBookingTotal);
    }
}
