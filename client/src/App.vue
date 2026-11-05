<template>
  <div class="app-shell" :class="{ 'is-collapsed': collapsed }">
    <a class="skip-link" href="#main-content">{{ t('nav.skipToContent') }}</a>

    <AppSidebar />

    <div class="app-main">
      <header class="topbar">
        <button
          type="button"
          class="icon-btn menu-btn"
          :aria-label="t('nav.openMenu')"
          :aria-expanded="mobileOpen"
          aria-controls="app-sidebar"
          @click="openMobile"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" aria-hidden="true">
            <path d="M4 7h16M4 12h16M4 17h16" />
          </svg>
        </button>
        <div class="topbar-title">{{ pageTitle }}</div>
        <div class="topbar-actions">
          <LanguageSwitcher />
          <ProfileMenu
            @show-profile-details="showProfileDetails = true"
            @show-tasks="showTasks = true"
          />
        </div>
      </header>
      <FilterBar />
      <main id="main-content" class="app-content" tabindex="-1">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import { useSidebar } from './composables/useSidebar'
import { navItems } from './navigation'
import AppSidebar from './components/AppSidebar.vue'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

export default {
  name: 'App',
  components: {
    AppSidebar,
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const route = useRoute()
    const { collapsed, mobileOpen, openMobile } = useSidebar()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // Top bar title comes from the same nav array as the sidebar (single source of truth).
    const pageTitle = computed(() => {
      const item = navItems.find((i) => i.to === route.path)
      return item ? t(item.label) : ''
    })

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      pageTitle,
      collapsed,
      mobileOpen,
      openMobile,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
/*
 * Design tokens. Palette derives from the original app (slate neutrals, blue primary);
 * status colors follow the project design system (green / blue / yellow / red).
 * Consume these instead of raw values.
 */
:root {
  /* Spacing: 4px base scale */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;

  /* Typography (CJK fallbacks added because the app ships a Japanese locale) */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Hiragino Sans', 'Noto Sans JP', sans-serif;
  --text-xs: 0.75rem;
  --text-sm: 0.8125rem;
  --text-base: 0.875rem;
  --text-md: 1rem;
  --text-lg: 1.25rem;
  --text-xl: 1.5rem;
  --text-2xl: 1.875rem;
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --weight-regular: 400;
  --weight-medium: 500;
  --weight-semibold: 600;
  --weight-bold: 700;
  --tracking-tight: -0.015em;
  --tracking-wide: 0.04em;

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* Elevation */
  --shadow-xs: 0 1px 2px rgb(15 23 42 / 0.04);
  --shadow-sm: 0 1px 3px rgb(15 23 42 / 0.06), 0 1px 2px rgb(15 23 42 / 0.04);
  --shadow-md: 0 4px 12px rgb(15 23 42 / 0.08), 0 2px 4px rgb(15 23 42 / 0.04);
  --shadow-lg: 0 16px 40px rgb(15 23 42 / 0.16), 0 4px 12px rgb(15 23 42 / 0.08);

  /* Neutrals */
  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-surface-muted: #f1f5f9;
  --color-border: #e2e8f0;
  --color-border-strong: #cbd5e1;
  --color-text: #0f172a;
  --color-text-secondary: #475569;
  --color-text-muted: #64748b;

  /* Primary */
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-primary-soft: #eff6ff;
  --color-primary-text: #1d4ed8;
  --color-focus-ring: rgb(37 99 235 / 0.35);

  /* Status */
  --color-success: #16a34a;
  --color-success-soft: #dcfce7;
  --color-success-text: #166534;
  --color-warning: #d97706;
  --color-warning-soft: #fef3c7;
  --color-warning-text: #92400e;
  --color-danger: #dc2626;
  --color-danger-soft: #fee2e2;
  --color-danger-text: #991b1b;
  --color-info: #2563eb;
  --color-info-soft: #dbeafe;
  --color-info-text: #1e40af;

  /* Sidebar. Section label is lighter than the template's #64748b, which is only ~3.7:1 on #0f172a. */
  --sidebar-bg: #0f172a;
  --sidebar-border: #1e293b;
  --sidebar-text: #94a3b8;
  --sidebar-text-hover: #e2e8f0;
  --sidebar-item-hover: #1e293b;
  --sidebar-item-active-bg: #1e293b;
  --sidebar-item-active-text: #ffffff;
  --sidebar-accent: #3b82f6;
  --sidebar-section-label: #8a99ae;
  --sidebar-focus-ring: #93c5fd;

  /* Layout */
  --sidebar-w: 240px;
  --sidebar-w-collapsed: 68px;
  --topbar-h: 60px;
  --content-max: 1440px;
  --page-padding: var(--space-8);

  /* Motion */
  --ease: cubic-bezier(0.2, 0, 0, 1);
  --duration-fast: 120ms;
  --duration: 200ms;

  /*
   * Layering. Existing modals use z-index 1000-2000 and menus 1000 (component-scoped),
   * so --z-modal is raised above the template default to stay consistent with them.
   * The top bar must sit above the filter row, otherwise its dropdowns would be painted
   * under the filter selects (the sticky top bar forms its own stacking context).
   */
  --z-filterbar: 15;
  --z-sticky: 20;
  --z-sidebar: 30;
  --z-overlay: 40;
  --z-drawer: 50;
  --z-dropdown: 60;
  --z-modal: 2000;
}

@media (max-width: 767px) {
  :root {
    --page-padding: var(--space-4);
  }
}

/* Base */
*,
*::before,
*::after {
  box-sizing: border-box;
}

* {
  margin: 0;
  padding: 0;
}

body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  background: var(--color-bg);
  color: var(--color-text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Numbers in tables should not jitter when values change */
table td {
  font-variant-numeric: tabular-nums;
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
  }
}

/* App shell: sidebar column + main column. minmax(0, 1fr) stops wide tables blowing out the grid. */
.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-w) minmax(0, 1fr);
  min-height: 100vh;
  transition: grid-template-columns var(--duration) var(--ease);
}

.app-shell.is-collapsed {
  grid-template-columns: var(--sidebar-w-collapsed) minmax(0, 1fr);
}

/* Tablet: rail column is forced by width only, so the saved desktop preference is untouched */
@media (min-width: 768px) and (max-width: 1023px) {
  .app-shell {
    grid-template-columns: var(--sidebar-w-collapsed) minmax(0, 1fr);
  }
}

/* Mobile: the sidebar leaves the grid and becomes a fixed drawer (see AppSidebar.vue) */
@media (max-width: 767px) {
  .app-shell,
  .app-shell.is-collapsed {
    grid-template-columns: minmax(0, 1fr);
  }
}

.app-main {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.app-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max);
  margin: 0 auto;
  padding: var(--space-6) var(--page-padding) var(--space-12);
}

.app-content:focus {
  outline: none;
}

.skip-link {
  position: absolute;
  left: var(--space-2);
  top: var(--space-2);
  z-index: var(--z-modal);
  padding: var(--space-2) var(--space-4);
  background: var(--color-surface);
  color: var(--color-primary-text);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  font-weight: var(--weight-medium);
  transform: translateY(-200%);
}

.skip-link:focus {
  transform: none;
}

/* Top bar */
.topbar {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: var(--topbar-h);
  padding: 0 var(--page-padding);
  background: rgb(255 255 255 / 0.9);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--color-border);
}

.topbar-title {
  flex: 1;
  min-width: 0;
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  letter-spacing: var(--tracking-tight);
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex: none;
}

.icon-btn {
  display: inline-grid;
  place-items: center;
  width: 36px;
  height: 36px;
  flex: none;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
}

.icon-btn:hover {
  background: var(--color-surface-muted);
  color: var(--color-text);
}

.icon-btn svg {
  width: 18px;
  height: 18px;
}

/* The hamburger only exists where the sidebar is a drawer */
.menu-btn {
  display: none;
}

@media (max-width: 767px) {
  .menu-btn {
    display: inline-grid;
  }
}

/* ---------- Shared component classes (used by every view) ---------- */

/* Page header: title, one-line description, optional actions on the right */
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
  margin-bottom: var(--space-6);
}

.page-header h2 {
  margin: 0;
  font-size: var(--text-xl);
  font-weight: var(--weight-semibold);
  letter-spacing: var(--tracking-tight);
  line-height: var(--leading-tight);
  color: var(--color-text);
}

.page-header p {
  margin: var(--space-1) 0 0;
  color: var(--color-text-muted);
  font-size: var(--text-base);
}

/* KPI tiles */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-xs);
}

.stat-label {
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
}

.stat-value {
  margin-top: var(--space-2);
  font-size: var(--text-2xl);
  font-weight: var(--weight-semibold);
  letter-spacing: var(--tracking-tight);
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
}

/* Status variants tint the value only; the tile stays neutral */
.stat-card.warning .stat-value {
  color: var(--color-warning-text);
}

.stat-card.success .stat-value {
  color: var(--color-success-text);
}

.stat-card.danger .stat-value {
  color: var(--color-danger-text);
}

.stat-card.info .stat-value {
  color: var(--color-info-text);
}

/* Cards */
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-xs);
  margin-bottom: var(--space-6);
}

/* The header bleeds to the card edges (negative margins cancel the card padding) so its divider spans the full width */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin: calc(-1 * var(--space-5)) calc(-1 * var(--space-5)) var(--space-4);
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.card-title {
  margin: 0;
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  letter-spacing: var(--tracking-tight);
  color: var(--color-text);
}

/* Tables */
.table-container {
  overflow-x: auto;
}

/* Tables inside cards run edge to edge; the radius clips hover backgrounds to the card corners */
.card > .table-container {
  margin: 0 calc(-1 * var(--space-5)) calc(-1 * var(--space-5));
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: var(--text-sm);
}

/* Keep wide tables scrollable inside their container instead of crushing columns on narrow screens */
.table-container > table {
  min-width: 640px;
}

th {
  text-align: left;
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface-muted);
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}

/* Identifier column reads as the row label */
td:first-child strong,
td:first-child {
  color: var(--color-text);
  font-weight: var(--weight-medium);
}

/* Identifiers (order IDs, SKUs, amounts) should not break mid-token */
td strong {
  white-space: nowrap;
}

tbody tr:last-child td {
  border-bottom: 0;
}

tbody tr {
  transition: background-color var(--duration-fast);
}

tbody tr:hover td {
  background: var(--color-surface-muted);
}

/* Badges: one pill shape, four status pairs. Every modifier the views use maps onto one pair. */
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  height: 22px;
  padding: 0 var(--space-2);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  white-space: nowrap;
}

.badge.success,
.badge.increasing {
  background: var(--color-success-soft);
  color: var(--color-success-text);
}

.badge.warning,
.badge.medium {
  background: var(--color-warning-soft);
  color: var(--color-warning-text);
}

.badge.danger,
.badge.decreasing,
.badge.high {
  background: var(--color-danger-soft);
  color: var(--color-danger-text);
}

.badge.info,
.badge.low,
.badge.stable {
  background: var(--color-info-soft);
  color: var(--color-info-text);
}

/* Form controls */
input,
select,
textarea {
  font: inherit;
  font-size: var(--text-sm);
  color: var(--color-text);
}

/* Loading / error states share the content card footprint so the layout does not jump */
.loading {
  text-align: center;
  padding: var(--space-12) var(--space-4);
  color: var(--color-text-muted);
  font-size: var(--text-base);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.error {
  background: var(--color-danger-soft);
  border: 1px solid var(--color-danger-soft);
  color: var(--color-danger-text);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin: var(--space-4) 0;
  font-size: var(--text-base);
}
</style>
