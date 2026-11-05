<template>
  <!-- Overlay only exists on mobile while the drawer is open -->
  <div v-if="mobileOpen" class="sidebar-overlay" aria-hidden="true" @click="closeMobile"></div>

  <div
    id="app-sidebar"
    ref="panel"
    class="sidebar"
    :class="{ 'is-collapsed': collapsed, 'is-mobile-open': mobileOpen }"
  >
    <div class="sidebar-brand">
      <div class="brand-mark" aria-hidden="true">{{ brandInitial }}</div>
      <div class="brand-text">
        <span class="brand-name">{{ t('nav.companyName') }}</span>
        <span class="brand-sub">{{ t('nav.subtitle') }}</span>
      </div>
    </div>

    <nav class="sidebar-nav" :aria-label="t('nav.mainNavigation')">
      <template v-for="group in navGroups" :key="group.id">
        <div v-if="group.label" class="nav-section-label">{{ t(group.label) }}</div>
        <router-link
          v-for="item in group.items"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          :data-label="t(item.label)"
          @click="closeMobile"
        >
          <!-- Icons are trusted, hardcoded path data from navigation.js. Never feed user input into v-html. -->
          <svg
            class="nav-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.75"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
            v-html="item.icon"
          ></svg>
          <span class="nav-label">{{ t(item.label) }}</span>
        </router-link>
      </template>
    </nav>

    <div class="sidebar-footer">
      <slot name="footer"></slot>
      <!-- Hidden on tablet (rail is forced there by CSS) and mobile (drawer) -->
      <button
        type="button"
        class="collapse-toggle"
        :data-label="collapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
        :aria-pressed="collapsed"
        :aria-label="collapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
        @click="toggleCollapsed"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path :d="collapsed ? 'M9 6l6 6-6 6' : 'M15 6l-6 6 6 6'" />
        </svg>
        <span class="nav-label">{{ collapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar') }}</span>
      </button>
    </div>
  </div>
</template>

<script>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from '../composables/useI18n'
import { useSidebar } from '../composables/useSidebar'
import { navGroups } from '../navigation'

export default {
  name: 'AppSidebar',
  setup() {
    const { t } = useI18n()
    const route = useRoute()
    const { collapsed, mobileOpen, toggleCollapsed, closeMobile } = useSidebar()
    const panel = ref(null)

    const brandInitial = computed(() => (t('nav.companyName') || '?').charAt(0))

    // Close the drawer whenever navigation happens, including back/forward.
    watch(() => route.fullPath, closeMobile)

    // Element that opened the drawer, so focus can return to it on close.
    let previouslyFocused = null

    const focusableIn = () =>
      Array.from(panel.value?.querySelectorAll('a[href], button:not([disabled])') || [])
        .filter((el) => el.offsetParent !== null)

    // While the mobile drawer is open: Esc closes, and Tab wraps inside the drawer
    // because the rest of the page is dimmed and should not be reachable.
    const onKeydown = (e) => {
      if (e.key === 'Escape') {
        closeMobile()
        return
      }
      if (e.key !== 'Tab') return
      const items = focusableIn()
      if (!items.length) return
      const first = items[0]
      const last = items[items.length - 1]
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }

    // While the mobile drawer is open: lock body scroll, move focus in, restore focus on close.
    watch(mobileOpen, async (open) => {
      document.body.style.overflow = open ? 'hidden' : ''
      if (open) {
        previouslyFocused = document.activeElement
        document.addEventListener('keydown', onKeydown)
        await nextTick()
        focusableIn()[0]?.focus()
      } else {
        document.removeEventListener('keydown', onKeydown)
        previouslyFocused?.focus?.()
        previouslyFocused = null
      }
    })

    onBeforeUnmount(() => {
      document.removeEventListener('keydown', onKeydown)
      document.body.style.overflow = ''
    })

    return {
      t,
      navGroups,
      brandInitial,
      panel,
      collapsed,
      mobileOpen,
      toggleCollapsed,
      closeMobile
    }
  }
}
</script>

<style scoped>
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  z-index: var(--z-sidebar);
  overflow: hidden;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: var(--topbar-h);
  flex: none;
  padding: 0 var(--space-4);
  border-bottom: 1px solid var(--sidebar-border);
}

.brand-mark {
  flex: none;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  display: grid;
  place-items: center;
  background: var(--sidebar-accent);
  color: #fff;
  font-weight: var(--weight-bold);
}

.brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-name {
  color: var(--sidebar-item-active-text);
  font-weight: var(--weight-semibold);
  font-size: var(--text-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.brand-sub {
  color: var(--sidebar-text);
  font-size: var(--text-xs);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-2) var(--space-3);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-section-label {
  margin: var(--space-4) var(--space-3) var(--space-1);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  letter-spacing: var(--tracking-wide);
  text-transform: uppercase;
  color: var(--sidebar-section-label);
}

.nav-item,
.collapse-toggle {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: 36px;
  padding: 0 var(--space-3);
  border-radius: var(--radius-md);
  color: var(--sidebar-text);
  text-decoration: none;
  font-family: inherit;
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  transition: background var(--duration-fast), color var(--duration-fast);
}

.nav-item:hover,
.collapse-toggle:hover {
  background: var(--sidebar-item-hover);
  color: var(--sidebar-text-hover);
}

/* Exact-active only: the "/" route is an ancestor of every path, so router-link-active would highlight Overview everywhere. */
.nav-item.router-link-exact-active {
  background: var(--sidebar-item-active-bg);
  color: var(--sidebar-item-active-text);
}

.nav-item.router-link-exact-active::before {
  content: '';
  position: absolute;
  left: calc(-1 * var(--space-3));
  top: 8px;
  bottom: 8px;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: var(--sidebar-accent);
}

/* The sidebar background is dark, so the default blue ring needs a lighter tone to stay visible. */
.nav-item:focus-visible,
.collapse-toggle:focus-visible {
  outline-color: var(--sidebar-focus-ring);
}

.nav-icon {
  flex: none;
  width: 18px;
  height: 18px;
}

.collapse-toggle svg {
  flex: none;
  width: 18px;
  height: 18px;
}

.nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-footer {
  flex: none;
  padding: var(--space-3);
  border-top: 1px solid var(--sidebar-border);
}

.collapse-toggle {
  width: 100%;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
}

/*
 * Icons-only rail. Two triggers share one set of rules, duplicated because plain CSS cannot
 * OR a class with a media query:
 *   1. the user's collapse toggle (.is-collapsed), on viewports >= 768px
 *   2. tablet widths (768-1023px), forced by CSS so the saved desktop preference is never overwritten
 * Labels are hidden visually (clip), not display:none, so each link keeps its accessible name.
 * Tooltips read data-label. overflow must be visible (on the sidebar and on .sidebar-nav, which
 * would otherwise compute overflow-x to auto) so the tooltip can escape the 68px column.
 * Below 768px neither block applies, so the drawer always shows full labels.
 */
@media (min-width: 768px) {
.sidebar.is-collapsed { overflow: visible; }
.sidebar.is-collapsed .sidebar-nav { overflow: visible; }
.sidebar.is-collapsed .nav-label {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}
.sidebar.is-collapsed .brand-text,
.sidebar.is-collapsed .nav-section-label {
  display: none;
}
.sidebar.is-collapsed .nav-section-label + .nav-item {
  margin-top: var(--space-3);
}
.sidebar.is-collapsed .nav-item,
.sidebar.is-collapsed .collapse-toggle,
.sidebar.is-collapsed .sidebar-brand {
  justify-content: center;
  padding-left: 0;
  padding-right: 0;
}
.sidebar.is-collapsed .nav-item::after,
.sidebar.is-collapsed .collapse-toggle::after {
  content: attr(data-label);
  /* Empty alt text keeps the tooltip out of the accessible name (otherwise links read as "Overview Overview") */
  content: attr(data-label) / '';
  position: absolute;
  left: calc(100% + var(--space-3));
  top: 50%;
  transform: translateY(-50%);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  background: var(--color-text);
  color: var(--color-surface);
  font-size: var(--text-xs);
  white-space: nowrap;
  box-shadow: var(--shadow-md);
  pointer-events: none;
  opacity: 0;
  transition: opacity var(--duration-fast);
  z-index: var(--z-dropdown);
}
.sidebar.is-collapsed .nav-item:hover::after,
.sidebar.is-collapsed .nav-item:focus-visible::after,
.sidebar.is-collapsed .collapse-toggle:hover::after,
.sidebar.is-collapsed .collapse-toggle:focus-visible::after {
  opacity: 1;
}
}

@media (min-width: 768px) and (max-width: 1023px) {
.sidebar { overflow: visible; }
.sidebar .sidebar-nav { overflow: visible; }
.sidebar .nav-label {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}
.sidebar .brand-text,
.sidebar .nav-section-label {
  display: none;
}
.sidebar .nav-section-label + .nav-item {
  margin-top: var(--space-3);
}
.sidebar .nav-item,
.sidebar .collapse-toggle,
.sidebar .sidebar-brand {
  justify-content: center;
  padding-left: 0;
  padding-right: 0;
}
.sidebar .nav-item::after,
.sidebar .collapse-toggle::after {
  content: attr(data-label);
  /* Empty alt text keeps the tooltip out of the accessible name (otherwise links read as "Overview Overview") */
  content: attr(data-label) / '';
  position: absolute;
  left: calc(100% + var(--space-3));
  top: 50%;
  transform: translateY(-50%);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  background: var(--color-text);
  color: var(--color-surface);
  font-size: var(--text-xs);
  white-space: nowrap;
  box-shadow: var(--shadow-md);
  pointer-events: none;
  opacity: 0;
  transition: opacity var(--duration-fast);
  z-index: var(--z-dropdown);
}
.sidebar .nav-item:hover::after,
.sidebar .nav-item:focus-visible::after,
.sidebar .collapse-toggle:hover::after,
.sidebar .collapse-toggle:focus-visible::after {
  opacity: 1;
}

  /* The rail is forced here, so a toggle would do nothing */
  .collapse-toggle {
    display: none;
  }
}

/* Mobile: off-canvas drawer */
@media (max-width: 767px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: min(280px, 85vw);
    z-index: var(--z-drawer);
    transform: translateX(-100%);
    /* visibility keeps the off-screen links out of the tab order while the drawer is closed */
    visibility: hidden;
    transition: transform var(--duration) var(--ease), visibility 0s linear var(--duration);
    box-shadow: var(--shadow-lg);
  }

  .sidebar.is-mobile-open {
    transform: translateX(0);
    visibility: visible;
    transition-delay: 0s;
  }

  .collapse-toggle {
    display: none;
  }

  .sidebar-overlay {
    position: fixed;
    inset: 0;
    background: rgb(15 23 42 / 0.5);
    z-index: var(--z-overlay);
  }
}
</style>
