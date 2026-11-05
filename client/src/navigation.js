// Single source of truth for sidebar navigation and the top bar page title.
// Labels are i18n keys; routes mirror the router config in main.js.
// Icons are trusted, hardcoded 24px-viewBox path data (never user input).
const ICONS = {
  home: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>',
  box: '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="M3 8l9 5 9-5"/><path d="M12 13v8"/>',
  cart: '<circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.5 12h11.5l2-8H6"/>',
  wallet: '<rect x="3" y="6" width="18" height="14" rx="2"/><path d="M16 13h2"/><path d="M3 10h18"/>',
  trend: '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
  file: '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/><path d="M8 13h8M8 17h5"/>'
}

export const navGroups = [
  {
    id: 'main',
    label: null,
    items: [{ to: '/', label: 'nav.overview', icon: ICONS.home }]
  },
  {
    id: 'operations',
    label: 'nav.sectionOperations',
    items: [
      { to: '/inventory', label: 'nav.inventory', icon: ICONS.box },
      { to: '/orders', label: 'nav.orders', icon: ICONS.cart }
    ]
  },
  {
    id: 'insights',
    label: 'nav.sectionInsights',
    items: [
      { to: '/spending', label: 'nav.finance', icon: ICONS.wallet },
      { to: '/demand', label: 'nav.demandForecast', icon: ICONS.trend },
      { to: '/reports', label: 'nav.reports', icon: ICONS.file }
    ]
  }
]

export const navItems = navGroups.flatMap((g) => g.items)
