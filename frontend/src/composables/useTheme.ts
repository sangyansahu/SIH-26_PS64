import { ref } from 'vue'

export type Theme = 'light'

const currentTheme = ref<Theme>('light')

export function useTheme() {
  function setTheme(_theme: string) {
    currentTheme.value = 'light'
    localStorage.removeItem('aicte_theme')
    document.documentElement.classList.remove('dark')
  }

  function toggleTheme() {
    setTheme('light')
  }

  function initTheme() {
    setTheme('light')
  }

  return {
    theme: currentTheme,
    setTheme,
    toggleTheme,
    initTheme,
  }
}
