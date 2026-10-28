'use strict';

(() => {
  const root = document.documentElement;
  const themeButton = document.querySelector('.theme-toggle');
  const systemTheme = matchMedia('(prefers-color-scheme: dark)');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const themeColor = document.querySelector('meta[name="theme-color"]');
  const updateThemeControl = () => {
    const dark = root.dataset.theme === 'dark';
    themeButton.setAttribute('aria-label', `Activer le thème ${dark ? 'clair' : 'sombre'}`);
    themeButton.title = `Activer le thème ${dark ? 'clair' : 'sombre'}`;
    themeColor.content = dark ? '#111113' : '#f8f8fa';
  };
  themeButton.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('portfolio-theme', root.dataset.theme); } catch (_) {}
    updateThemeControl();
  });
  systemTheme.addEventListener('change', (event) => {
    let saved;
    try { saved = localStorage.getItem('portfolio-theme'); } catch (_) {}
    if (saved !== 'dark' && saved !== 'light') {
      root.dataset.theme = event.matches ? 'dark' : 'light';
      updateThemeControl();
    }
  });
  updateThemeControl();

  const menuButton = document.querySelector('.menu-toggle');
  const menu = document.querySelector('.nav-links');
  const closeMenu = () => {
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-label', 'Ouvrir le menu');
    menu.classList.remove('is-open');
  };
  menuButton.addEventListener('click', () => {
    const open = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
    menu.classList.toggle('is-open', open);
  });
  menu.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.navigation')) closeMenu();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
      closeMenu();
      menuButton.focus();
    }
  });
  matchMedia('(min-width: 601px)').addEventListener('change', closeMenu);

  // Only draw while the scene is nearby, at most once per animation frame.
  const workspace = document.querySelector('.workspace');
  const stage = workspace.querySelector('.workspace-stage');
  let sceneVisible = false;
  let framePending = false;
  const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));
  const drawScene = () => {
    framePending = false;
    if (reducedMotion.matches) return;
    const bounds = workspace.getBoundingClientRect();
    const stickyTop = parseFloat(getComputedStyle(stage).top) || 0;
    const distance = bounds.height - stage.offsetHeight;
    const progress = clamp((stickyTop - bounds.top) / Math.max(1, distance));
    const zoomProgress = clamp(progress / 0.85);
    const ease = zoomProgress * zoomProgress * (3 - 2 * zoomProgress);
    const endScale = innerWidth <= 600 ? Math.max(2.6, innerHeight / 160) : Math.max(3.4, innerHeight / 230);
    workspace.style.setProperty('--zoom', (1 + ease * (endScale - 1)).toFixed(4));
    workspace.style.setProperty('--caption-opacity', String(1 - clamp(progress / 0.2)));
    workspace.style.setProperty('--desk-opacity', String(1 - clamp((progress - 0.68) / 0.24)));
    const message = clamp((progress - 0.7) / 0.25);
    workspace.style.setProperty('--message-opacity', String(message));
    workspace.style.setProperty('--message-y', `${24 * (1 - message)}px`);
  };
  const requestScene = () => {
    if (!sceneVisible || framePending || reducedMotion.matches) return;
    framePending = true;
    requestAnimationFrame(drawScene);
  };
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => {
      sceneVisible = entry.isIntersecting;
      if (sceneVisible) requestScene();
    }, { rootMargin: '100px' }).observe(workspace);
    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    if (!reducedMotion.matches) {
      document.querySelectorAll('.section-heading, .expertise-item, .about-copy, .portrait-wrap').forEach((element) => {
        if (element.getBoundingClientRect().top > innerHeight) {
          element.classList.add('reveal-ready');
          revealObserver.observe(element);
        }
      });
    }
    const navObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const link = menu.querySelector(`a[href="#${entry.target.id}"]`);
        if (!link) return;
        if (entry.isIntersecting) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }, { rootMargin: '-20% 0px -50% 0px' });
    document.querySelectorAll('#projets, #expertise, #parcours, #apropos').forEach((section) => navObserver.observe(section));
  } else {
    sceneVisible = true;
    requestScene();
  }
  window.addEventListener('scroll', requestScene, { passive: true });
  window.addEventListener('resize', requestScene, { passive: true });
  reducedMotion.addEventListener('change', requestScene);

  const cards = [...document.querySelectorAll('.project-card')];
  const filters = [...document.querySelectorAll('.filter')];
  filters.forEach((button) => button.addEventListener('click', () => {
    filters.forEach((filter) => {
      const active = filter === button;
      filter.classList.toggle('is-active', active);
      filter.setAttribute('aria-pressed', String(active));
    });
    let visible = 0;
    cards.forEach((card) => {
      card.hidden = button.dataset.filter !== 'all' && card.dataset.category !== button.dataset.filter;
      if (!card.hidden) visible++;
    });
    document.querySelector('.project-count').textContent = `${String(visible).padStart(2, '0')} projet${visible > 1 ? 's' : ''}`;
  }));

  const projects = {
    robotics: {
      eyebrow: 'POLLEN ROBOTICS / 2025', title: 'Voir. Comprendre. Agir.',
      intro: 'Une vision réactive pour aider les prothèses robotiques à comprendre leur environnement.',
      stat: '12 ms', statLabel: 'par image pour la segmentation, selon les résultats du projet.',
      sections: [
        ['Le défi', 'Segmenter des objets en temps réel pour un usage en robotique, où chaque milliseconde compte. Produire des masques précis tout en limitant la latence.'],
        ['Mon approche', 'Développement d’un module de segmentation et intégration d’un mécanisme d’attention dans Fast SAM. L’attention se concentre sur la génération d’un masque dans une bounding box pour cibler l’objet utile.'],
        ['Le résultat', 'Une segmentation réalisée en 12 ms par image, permettant un fonctionnement fluide dans les conditions du projet.']
      ], tags: ['Fast SAM', 'Attention', 'Segmentation', 'Robotique']
    },
    rag: {
      eyebrow: 'STACKEASY / 2025', title: 'La bonne information. Au bon moment.',
      intro: 'Transformer une base de connaissances en réponses utiles, explicables et reliées à leurs sources.',
      stat: 'RAG', statLabel: 'hybride : recherche vectorielle et symbolique, avec orchestration multi-agents.',
      sections: [
        ['Le défi', 'Améliorer la pertinence des réponses et faciliter le traitement de l’information sans perdre le lien avec les documents d’origine.'],
        ['Mon approche', 'Conception d’un système combinant recherche vectorielle et symbolique. Orchestration d’agents spécialisés intégrant des LLM pour automatiser le traitement et la synthèse d’information.'],
        ['Une réponse explicable', 'Implémentation d’une restitution avec citations automatiques des documents issus de la base vectorielle, pour permettre de retrouver les sources des réponses.']
      ], tags: ['RAG hybride', 'LLM', 'Multi-agents', 'Recherche vectorielle']
    },
    archeology: {
      eyebrow: 'ARCHÉOVISION / 2024', title: 'Un nouveau regard sur le passé.',
      intro: 'Aider l’analyse archéologique à retrouver les traces de pigments bleus sur des pierres antiques.',
      stat: '+30 %', statLabel: 'de précision par rapport au POC initial, selon les résultats du projet.',
      sections: [
        ['Le contexte', 'Développement d’une application de segmentation pour la reconnaissance de pigments bleus sur les pierres du temple d’Apollon à Delphes.'],
        ['Mon approche', 'Utilisation d’un réseau U-Net et de la Dice Loss pour segmenter les zones d’intérêt dans les images et faciliter leur identification.'],
        ['Le résultat', 'Une amélioration de la précision de 30 % par rapport au POC initial, pour faciliter le travail d’analyse archéologique.']
      ], tags: ['U-Net', 'Dice Loss', 'Segmentation', 'Patrimoine']
    }
  };
  const dialog = document.querySelector('.project-dialog');
  let projectTrigger;
  document.querySelectorAll('[data-project]').forEach((button) => button.addEventListener('click', () => {
    const project = projects[button.dataset.project];
    projectTrigger = button;
    document.querySelector('#dialog-eyebrow').textContent = project.eyebrow;
    document.querySelector('#dialog-title').textContent = project.title;
    document.querySelector('#dialog-intro').textContent = project.intro;
    document.querySelector('#dialog-stat-value').textContent = project.stat;
    document.querySelector('#dialog-stat-label').textContent = project.statLabel;
    const sections = document.querySelector('#dialog-sections');
    sections.replaceChildren();
    project.sections.forEach(([title, copy]) => {
      const section = document.createElement('section');
      const heading = document.createElement('h3');
      const paragraph = document.createElement('p');
      heading.textContent = title;
      paragraph.textContent = copy;
      section.append(heading, paragraph);
      sections.append(section);
    });
    const tags = document.querySelector('#dialog-tags');
    tags.replaceChildren(...project.tags.map((tag) => {
      const item = document.createElement('li');
      item.textContent = tag;
      return item;
    }));
    dialog.showModal();
    dialog.scrollTop = 0;
    document.body.classList.add('modal-open');
  }));
  document.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (event) => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.classList.remove('modal-open');
    projectTrigger?.focus({ preventScroll: true });
  });

  let feedbackTimeout;
  document.querySelector('.copy-email').addEventListener('click', async () => {
    const feedback = document.querySelector('.copy-feedback');
    clearTimeout(feedbackTimeout);
    try {
      await navigator.clipboard.writeText('garnieranatole@gmail.com');
      feedback.textContent = 'Adresse e-mail copiée.';
    } catch (_) {
      feedback.textContent = 'Adresse à copier : garnieranatole@gmail.com';
    }
    feedbackTimeout = setTimeout(() => { feedback.textContent = ''; }, 5000);
  });
  document.querySelector('#copyright-year').textContent = new Date().getFullYear();
})();
