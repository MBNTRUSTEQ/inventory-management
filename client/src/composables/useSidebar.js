import { ref, watch } from 'vue'

const STORAGE_KEY = 'sidebar-collapsed'

// Must stay in sync with the 767px breakpoint in App.vue / AppSidebar.vue.
const MOBILE_QUERY = '(max-width: 767px)'

const readCollapsed = () => {
  try {
    return localStorage.getItem(STORAGE_KEY) === '1'
  } catch {
    return false
  }
}

// Module-level refs: one shared instance for every caller (singleton, like useFilters).
// `collapsed` is the user's persisted desktop preference.
const collapsed = ref(readCollapsed())
const mobileOpen = ref(false)

watch(collapsed, (v) => {
  try {
    localStorage.setItem(STORAGE_KEY, v ? '1' : '0')
  } catch {
    // Storage unavailable (private mode): keep the in-memory state only.
  }
})

// The rail (collapsed / tablet) is pure CSS. Only the mobile breakpoint is tracked in JS, so an
// open drawer is dropped when the viewport grows past it.
if (typeof window !== 'undefined' && window.matchMedia) {
  const mobileMq = window.matchMedia(MOBILE_QUERY)
  mobileMq.addEventListener('change', (e) => {
    if (!e.matches) mobileOpen.value = false
  })
}

export function useSidebar() {
  const toggleCollapsed = () => { collapsed.value = !collapsed.value }
  const openMobile = () => { mobileOpen.value = true }
  const closeMobile = () => { mobileOpen.value = false }
  return { collapsed, mobileOpen, toggleCollapsed, openMobile, closeMobile }
}
