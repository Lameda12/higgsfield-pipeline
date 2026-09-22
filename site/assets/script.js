(() => {
  "use strict";

  // Footer year
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Copy-to-clipboard buttons
  document.querySelectorAll(".copy-btn[data-copy-target]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const target = document.getElementById(btn.dataset.copyTarget);
      if (!target) return;

      const text = target.innerText;
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        const range = document.createRange();
        range.selectNode(target);
        window.getSelection()?.removeAllRanges();
        window.getSelection()?.addRange(range);
        document.execCommand("copy");
        window.getSelection()?.removeAllRanges();
      }

      const original = btn.textContent;
      btn.textContent = "Copied!";
      btn.classList.add("copied");
      setTimeout(() => {
        btn.textContent = original;
        btn.classList.remove("copied");
      }, 1500);
    });
  });

  // Smooth scroll for in-page nav links + collapse mobile menu after click
  const navCollapseEl = document.getElementById("navMenu");
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener("click", (e) => {
      const id = link.getAttribute("href");
      if (!id || id === "#") return;
      const el = document.querySelector(id);
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ behavior: "smooth", block: "start" });

      if (navCollapseEl?.classList.contains("show")) {
        // Close the mobile menu via Bootstrap's collapse API if available
        const bsCollapse = window.bootstrap?.Collapse.getOrCreateInstance(navCollapseEl);
        bsCollapse?.hide();
      }
    });
  });

  // Active nav-link highlighting on scroll
  const sections = [...document.querySelectorAll("section[id], header[id]")];
  const navLinks = [...document.querySelectorAll("#navMenu .nav-link")];

  const setActive = () => {
    const scrollPos = window.scrollY + 120;
    let currentId = sections[0]?.id;
    for (const section of sections) {
      if (section.offsetTop <= scrollPos) currentId = section.id;
    }
    navLinks.forEach((link) => {
      link.classList.toggle("active", link.getAttribute("href") === `#${currentId}`);
    });
  };

  window.addEventListener("scroll", setActive, { passive: true });
  setActive();
})();
