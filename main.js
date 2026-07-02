document.addEventListener('DOMContentLoaded', () => {
    initMobileNav();
    initHeroSlider();
    initScrollReveal();
    initHomePageNav();
    initTimetableFilters();
    initNavbarScroll();
    initContactForm();
    initRecitalCarousel();
});

function initTimetableFilters() {
    document.querySelectorAll('.timetable-filters').forEach(filterBar => {
        const container = filterBar.closest('.schedule-container') || filterBar.parentElement;
        filterBar.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                filterBar.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                container.querySelectorAll('.timetable-view').forEach(v => v.classList.remove('active'));
                btn.classList.add('active');
                const view = container.querySelector('#view-' + btn.dataset.view);
                if (view) view.classList.add('active');
            });
        });
    });
}

function initMobileNav() {
    const toggle = document.querySelector('.nav-toggle');
    const menu = document.querySelector('.nav-menu');
    if (!toggle || !menu) return;

    toggle.addEventListener('click', () => {
        menu.classList.toggle('open');
    });

    document.querySelectorAll('.dropdown > a').forEach(link => {
        link.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                link.parentElement.classList.toggle('open');
            }
        });
    });
}

function initContactForm() {
    const form = document.getElementById('contact-form');
    if (!form) return;

    const nextInput = form.querySelector('#form-next');
    if (nextInput) {
        nextInput.value = `${window.location.origin}${window.location.pathname}?sent=1`;
    }

    form.addEventListener('submit', () => {
        const name = form.querySelector('#name')?.value.trim() || 'Website visitor';
        const topic = form.querySelector('#subject')?.value || 'General Inquiry';
        const subjectInput = form.querySelector('#form-subject');
        if (subjectInput) {
            subjectInput.value = `Dance Dimensions contact: ${topic} — ${name}`;
        }
    });

    const params = new URLSearchParams(window.location.search);
    const successNotice = document.getElementById('contact-form-success');
    if (params.get('sent') === '1' && successNotice) {
        successNotice.hidden = false;
        form.reset();
        successNotice.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        window.history.replaceState({}, '', window.location.pathname);
    }
}

function initHeroSlider() {
    const slides = document.querySelectorAll('.hero-slider .slide');
    const prevBtn = document.querySelector('.slider-arrow.prev');
    const nextBtn = document.querySelector('.slider-arrow.next');
    const dots = document.querySelectorAll('.slider-dot');
    if (!slides.length) return;

    let current = 0;
    let timer;

    function show(index) {
        slides.forEach(s => s.classList.remove('active'));
        dots.forEach(d => d.classList.remove('active'));
        current = (index + slides.length) % slides.length;
        slides[current].classList.add('active');
        if (dots[current]) dots[current].classList.add('active');
    }

    function next() { show(current + 1); resetTimer(); }
    function prev() { show(current - 1); resetTimer(); }

    function resetTimer() {
        clearInterval(timer);
        timer = setInterval(next, 6000);
    }

    if (prevBtn) prevBtn.addEventListener('click', prev);
    if (nextBtn) nextBtn.addEventListener('click', next);
    dots.forEach((dot, i) => dot.addEventListener('click', () => { show(i); resetTimer(); }));

    resetTimer();
}

function initHomePageNav() {
    const slider = document.querySelector('#feature-slider .content-slider');
    const sideNav = document.getElementById('side-navigation');
    const dots = document.querySelectorAll('.side-dot');
    const hero = document.querySelector('.hero-slider');
    if (!slider || !sideNav || !dots.length) return;

    const slides = slider.querySelectorAll('.content-slide');
    const sections = [
        document.getElementById('welcome-section'),
        document.getElementById('modern-dance-section'),
        document.getElementById('feature-slider')
    ].filter(Boolean);

    let currentSlide = 0;
    let slideTimer;
    let activeSection = 'welcome-section';

    function showSlide(index) {
        slides.forEach(s => s.classList.remove('active'));
        currentSlide = (index + slides.length) % slides.length;
        slides[currentSlide].classList.add('active');
        animateFeatureSlide(slides[currentSlide]);
        if (activeSection === 'feature-slider') updateDots();
    }

    function updateDots() {
        dots.forEach(dot => dot.classList.remove('active'));

        const sectionIndex = {
            'welcome-section': 0,
            'modern-dance-section': 1,
            'feature-slider': 2
        };

        const idx = sectionIndex[activeSection];
        if (idx !== undefined) dots[idx]?.classList.add('active');
    }

    function scrollToSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (!section) return;

        activeSection = sectionId;
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
        updateDots();
        resetSlideTimer();
    }

    function resetSlideTimer() {
        clearInterval(slideTimer);
        if (activeSection === 'feature-slider') {
            slideTimer = setInterval(() => showSlide(currentSlide + 1), 7000);
        }
    }

    function getActiveSection() {
        const marker = window.scrollY + window.innerHeight * 0.38;
        let found = sections[0]?.id || 'welcome-section';

        sections.forEach(section => {
            if (marker >= section.offsetTop - 100) {
                found = section.id;
            }
        });

        return found;
    }

    function onScroll() {
        const nextSection = getActiveSection();

        if (nextSection !== activeSection) {
            activeSection = nextSection;
            if (nextSection === 'feature-slider') resetSlideTimer();
            else clearInterval(slideTimer);
        }

        updateDots();

        if (hero) {
            const showNav = window.scrollY > hero.offsetHeight - 120;
            sideNav.classList.toggle('visible', showNav);
            sideNav.setAttribute('aria-hidden', showNav ? 'false' : 'true');
        }
    }

    dots.forEach(dot => {
        dot.addEventListener('click', () => {
            scrollToSection(dot.dataset.section);
        });
    });

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });

    showSlide(0);
    onScroll();
}

function initScrollReveal() {
    initAutoReveal();

    const sections = document.querySelectorAll('.reveal');
    const featureSlider = document.getElementById('feature-slider');

    sections.forEach(section => {
        if (section.id === 'feature-slider') return;
        if (!section.dataset.revealPrepared) prepareRevealSection(section);
    });

    if (featureSlider && !featureSlider.dataset.revealPrepared) {
        prepareFeatureSliderReveal(featureSlider);
    }

    if (!sections.length && !featureSlider) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;

            entry.target.classList.add('revealed');

            if (entry.target.id === 'feature-slider') {
                animateFeatureSlide(entry.target.querySelector('.content-slide.active'));
            }

            observer.unobserve(entry.target);
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -5% 0px' });

    sections.forEach(section => observer.observe(section));
    if (featureSlider) observer.observe(featureSlider);

    document.querySelectorAll('.reveal--instant').forEach(section => {
        requestAnimationFrame(() => section.classList.add('revealed'));
    });
}

function initAutoReveal() {
    document.querySelectorAll('.page-header').forEach(preparePageHeader);
    document.querySelectorAll('.recital-banner').forEach(prepareRecitalBanner);
    document.querySelectorAll('.recital-announcement').forEach(prepareAnnouncementBar);

    document.querySelectorAll([
        'section.philosophy-section',
        'section.testimonials-section',
        'section.current-classes',
        'section.groups-section',
        'section.classes-content',
        'section.schedule-section',
        'section.recital-content',
        'section.troupe-content',
        'section.dress-code-content',
        'section.gallery-content',
        'section.contact-content'
    ].join(',')).forEach(prepareGenericRevealSection);
}

function preparePageHeader(header) {
    if (header.dataset.revealPrepared === 'true') return;
    header.dataset.revealPrepared = 'true';
    header.classList.add('reveal', 'reveal--instant');

    header.querySelectorAll('.page-header-subtitle, h1, p').forEach((el, index) => {
        tagRevealChild(el, index, {
            fade: el.classList.contains('page-header-subtitle'),
            title: el.tagName === 'H1',
            blur: el.tagName === 'P'
        });
    });
}

function prepareRecitalBanner(banner) {
    if (banner.dataset.revealPrepared === 'true') return;
    banner.dataset.revealPrepared = 'true';
    banner.classList.add('reveal');

    const photo = banner.querySelector('img');
    if (photo) {
        photo.classList.add('reveal-child', 'reveal-photo', 'reveal-photo--from-right');
        photo.style.setProperty('--reveal-i', 0);
    }
}

function prepareAnnouncementBar(bar) {
    if (bar.dataset.revealPrepared === 'true') return;
    bar.dataset.revealPrepared = 'true';
    bar.classList.add('reveal');

    bar.querySelectorAll('.recital-announcement-label, p').forEach((el, index) => {
        tagRevealChild(el, index, {
            label: el.classList.contains('recital-announcement-label'),
            blur: el.tagName === 'P'
        });
    });
}

function prepareGenericRevealSection(section) {
    if (section.dataset.revealPrepared === 'true') return;
    if (section.querySelector('.content-slide-content')) return;

    section.dataset.revealPrepared = 'true';
    section.classList.add('reveal');

    collectRevealBlocks(section).forEach((block, index) => {
        applyRevealBlock(block, index);
    });
}

function collectRevealBlocks(section) {
    const selector = [
        '.container > *:not(.philosophy-features):not(.testimonials-grid):not(.current-images):not(.recital-hub-grid):not(.sponsors-grid):not(.video-grid)',
        '.schedule-container > *',
        '.philosophy-features > *',
        '.testimonials-grid > *',
        'section.testimonials-section > .testimonials-label',
        'section.testimonials-section > .testimonials-title',
        '.current-images > *',
        '.recital-hub-grid > *',
        '.sponsors-grid > *',
        '.gallery-grid > *',
        '.video-grid > *',
        '.gallery-category',
        '.gallery-intro',
        '.dress-intro',
        '.dress-note',
        '.groups-grid > *',
        '.contact-grid > *',
        '.classes-content .class-strip',
        '.dress-code-content .class-strip',
        '.info-block',
        '.dress-shop-cta',
        '.recital-flyer',
        '.recital-hub-intro',
        '.recital-back',
        '.recital-event-card',
        '.sponsors-section'
    ].join(',');

    const blocks = [];
    section.querySelectorAll(selector).forEach(block => {
        if (blocks.some(existing => existing.contains(block) && existing !== block)) return;
        const childIndex = blocks.findIndex(existing => block.contains(existing));
        if (childIndex !== -1) blocks.splice(childIndex, 1);
        blocks.push(block);
    });

    return blocks;
}

function applyRevealBlock(block, index) {
    if (block.classList.contains('reveal-child')) return;

    block.classList.add('reveal-child');
    block.style.setProperty('--reveal-i', Math.min(index, 8));

    if (block.matches('h1, h2, h3, .philosophy-title, .current-title, .schedule-title, .testimonials-title, .sponsors-title')) {
        block.classList.add('reveal-child--title');
    } else if (block.matches('[class*="label"], [class*="badge"], [class*="subtitle"], .class-age, .philosophy-label, .testimonials-label, .schedule-label, .current-badge, .recital-announcement-label')) {
        block.classList.add('reveal-child--label');
    } else if (block.matches('.class-strip, .philosophy-feature, .testimonial-item, .group-card, .gallery-item, .video-card, .contact-info, .contact-form, .info-block, .current-img, .gallery-category')) {
        block.classList.add('reveal-child--rise');
        setupStripPhoto(block);
    } else if (block.matches('.recital-hub-link, .register-btn, a.register-btn')) {
        block.classList.add('reveal-child--pop');
    } else if (block.matches('p, .philosophy-intro, .current-intro, .recital-hub-intro, .philosophy-subtext, ul, ol, .timetable-view, .timetable-filters, .recital-event-card, .current-images, .current-register, .dress-shop-cta, .recital-flyer')) {
        block.classList.add('reveal-child--blur');
    } else {
        block.classList.add('reveal-child--rise');
    }
}

function setupStripPhoto(block) {
    if (!block.classList.contains('class-strip')) return;

    const photo = block.querySelector('.class-strip-img');
    if (!photo) return;

    photo.classList.add('reveal-photo');
    photo.classList.add(block.classList.contains('reverse') ? 'reveal-photo--from-right' : 'reveal-photo--from-left');
}

function tagRevealChild(el, index, hints = {}) {
    el.classList.add('reveal-child');
    el.style.setProperty('--reveal-i', index);

    if (hints.title) el.classList.add('reveal-child--title');
    else if (hints.fade) el.classList.add('reveal-child--fade');
    else if (hints.label) el.classList.add('reveal-child--label');
    else if (hints.blur) el.classList.add('reveal-child--blur');
    else el.classList.add('reveal-child--rise');
}

function prepareRevealSection(section) {
    if (section.dataset.revealPrepared === 'true') return;
    section.dataset.revealPrepared = 'true';

    const photo = section.querySelector('.content-slide-image .framed-image--photo');
    if (photo) {
        photo.classList.add('reveal-photo');
        photo.classList.add(
            section.id === 'modern-dance-section' ? 'reveal-photo--from-left' : 'reveal-photo--from-right'
        );
    }

    let contentIndex = 0;
    section.querySelectorAll('.content-slide-content > .reveal-child').forEach(el => {
        if (el.classList.contains('content-slide-actions')) {
            el.classList.remove('reveal-child');
            el.querySelectorAll('.content-slide-btn').forEach((btn, btnIndex) => {
                btn.classList.add('reveal-child', 'reveal-child--pop');
                btn.style.setProperty('--reveal-i', btnIndex);
            });
            return;
        }

        if (el.classList.contains('content-slide-title')) el.classList.add('reveal-child--title');
        if (el.classList.contains('content-slide-label')) el.classList.add('reveal-child--label');
        if (el.classList.contains('content-slide-text')) el.classList.add('reveal-child--blur');
        if (el.classList.contains('framed-image--logo')) el.classList.add('reveal-child--scale');
        if (el.classList.contains('content-slide-location')) el.classList.add('reveal-child--fade');

        el.style.setProperty('--reveal-i', contentIndex);
        contentIndex += 1;
    });

    section.querySelectorAll('.affiliation-item.reveal-child').forEach((item, index) => {
        item.classList.add('reveal-child--rise');
        item.style.setProperty('--reveal-i', index);
    });
}

function prepareFeatureSliderReveal(featureSlider) {
    featureSlider.dataset.revealPrepared = 'true';
    featureSlider.classList.add('reveal');

    featureSlider.querySelectorAll('.content-slide').forEach(slide => {
        const photo = slide.querySelector('.content-slide-image .framed-image--photo');
        if (photo) {
            photo.classList.add('reveal-photo', 'reveal-photo--from-right');
        }

        slide.querySelectorAll('.content-slide-label, .content-slide-title, .content-slide-text, .content-slide-btn').forEach((el, index) => {
            el.classList.add('feature-reveal-item');
            el.style.setProperty('--reveal-i', index);
        });
    });
}

function animateFeatureSlide(slide) {
    if (!slide) return;

    const featureSlider = document.getElementById('feature-slider');
    if (!featureSlider?.classList.contains('revealed')) return;

    featureSlider.querySelectorAll('.content-slide.is-animating').forEach(activeSlide => {
        activeSlide.classList.remove('is-animating');
    });

    slide.classList.remove('is-animating');
    void slide.offsetWidth;
    slide.classList.add('is-animating');
}

function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    const onScroll = () => {
        navbar.classList.toggle('scrolled', window.scrollY > 40);
    };

    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
}

function initRecitalCarousel() {
    const carousel = document.getElementById('recital-carousel');
    if (!carousel) return;

    const slides = carousel.querySelectorAll('.recital-carousel-slide');
    const captions = carousel.querySelectorAll('.recital-carousel-caption');
    const prevBtn = carousel.querySelector('.recital-carousel-arrow.prev');
    const nextBtn = carousel.querySelector('.recital-carousel-arrow.next');
    const dotsContainer = carousel.querySelector('.recital-carousel-dots');
    if (!slides.length || !dotsContainer) return;

    let current = 0;
    let timer;

    slides.forEach((slide, index) => {
        const dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'recital-carousel-dot' + (index === 0 ? ' active' : '');
        dot.setAttribute('role', 'tab');
        dot.setAttribute('aria-label', `Show photo ${index + 1} of ${slides.length}`);
        dot.setAttribute('aria-selected', index === 0 ? 'true' : 'false');
        dot.addEventListener('click', () => show(index));
        dotsContainer.appendChild(dot);
    });

    const dots = dotsContainer.querySelectorAll('.recital-carousel-dot');

    function show(index) {
        slides.forEach(slide => {
            slide.classList.remove('active');
            slide.setAttribute('aria-hidden', 'true');
        });
        dots.forEach(dot => {
            dot.classList.remove('active');
            dot.setAttribute('aria-selected', 'false');
        });
        captions.forEach(caption => caption.classList.remove('active'));

        current = (index + slides.length) % slides.length;
        slides[current].classList.add('active');
        slides[current].setAttribute('aria-hidden', 'false');
        dots[current].classList.add('active');
        dots[current].setAttribute('aria-selected', 'true');
        if (captions[current]) captions[current].classList.add('active');
    }

    function next() {
        show(current + 1);
        resetTimer();
    }

    function prev() {
        show(current - 1);
        resetTimer();
    }

    function resetTimer() {
        clearInterval(timer);
        timer = setInterval(next, 7000);
    }

    if (prevBtn) prevBtn.addEventListener('click', prev);
    if (nextBtn) nextBtn.addEventListener('click', next);

    carousel.addEventListener('mouseenter', () => clearInterval(timer));
    carousel.addEventListener('mouseleave', resetTimer);
    carousel.addEventListener('focusin', () => clearInterval(timer));
    carousel.addEventListener('focusout', resetTimer);

    resetTimer();
}
