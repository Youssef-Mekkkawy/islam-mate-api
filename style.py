css = open('docs/.vitepress/theme/custom.css', 'r', encoding='utf-8').read()

fix = """
/* ===== NAVBAR ICONS - WHITE ON TEAL ===== */

/* GitHub icon */
.VPNavBarExtra .vpi-social-github,
.VPSocialLink[href*="github"] .vpi-social-github {
  color: white !important;
  fill: white !important;
}

/* All social icons in navbar */
.VPNavBar .VPSocialLinks .vpi-social-github,
.VPNavBar .VPSocialLinks svg {
  fill: white !important;
  color: white !important;
}

/* Search button */
.VPNavBarSearch .VPLocalSearchBox,
.VPNavBarSearch button {
  color: white !important;
}

.VPNavBarSearch .DocSearch-Button-Placeholder {
  color: rgba(255,255,255,0.8) !important;
}

/* Search icon */
.VPNavBarSearch svg,
.VPNavBarSearch .vpi-search {
  fill: white !important;
  color: white !important;
}

/* Search text "Search" + "Ctrl K" */
.VPNavBarSearch .search-button-text {
  color: rgba(255,255,255,0.85) !important;
}

.VPNavBarSearch .search-button kbd {
  color: rgba(255,255,255,0.6) !important;
  border-color: rgba(255,255,255,0.3) !important;
  background: rgba(255,255,255,0.1) !important;
}

/* Dark/Light toggle icon */
.VPNavBarAppearance button svg {
  fill: white !important;
  color: white !important;
}

/* Language switcher */
.VPNavBarTranslations button svg,
.VPNavBarTranslations .vpi-languages {
  fill: white !important;
  color: white !important;
}

.VPNavBarTranslations .text {
  color: rgba(255,255,255,0.85) !important;
}
"""

with open('docs/.vitepress/theme/custom.css', 'w', encoding='utf-8') as f:
    f.write(css + fix)

print('Done!')