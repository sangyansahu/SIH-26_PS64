<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/client'
import SihLogo from '@/components/SihLogo.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import {
  FileText,
  Users,
  UploadCloud,
  Trophy,
  ArrowRight,
  Play,
  Lightbulb,
  Search,
  Building2,
  ShieldCheck,
  Calendar,
} from 'lucide-vue-next'

const router = useRouter()
const activeTab = ref('Home')
const searchQuery = ref('')

interface NavAction {
  name: string
  action: () => void
}

const navItems: NavAction[] = [
  { name: 'Home', action: () => window.scrollTo({ top: 0, behavior: 'smooth' }) },
  { name: 'About', action: () => document.getElementById('about-section')?.scrollIntoView({ behavior: 'smooth' }) },
  { name: 'Problem Statements', action: () => router.push('/complaints') },
  { name: 'Institutions', action: () => router.push('/institutions') },
  { name: 'Overlaps', action: () => router.push('/overlaps') },
]

function handleNavClick(item: NavAction) {
  activeTab.value = item.name
  item.action()
}

const featureCards = [
  {
    title: 'Problem Statements',
    description: 'Explore real-world challenges from various ministries and sectors.',
    icon: FileText,
    link: '/complaints',
  },
  {
    title: 'Team & Participation',
    description: 'Form your team, register and start building your solution.',
    icon: Users,
    link: '/institutions',
  },
  {
    title: 'Submission & Evaluation',
    description: 'Submit your ideas and go through the evaluation process.',
    icon: UploadCloud,
    link: '/overlaps',
  },
  {
    title: 'Results & Recognition',
    description: 'Get recognized, win exciting prizes and make an impact.',
    icon: Trophy,
    link: '/reports',
  },
]

interface UpdateItem {
  date: string
  text: string
}

const updates = ref<UpdateItem[]>([])
const loadingUpdates = ref(true)

async function loadUpdates() {
  loadingUpdates.value = true
  try {
    const res = await apiClient.get('/complaints', {
      params: { per_page: 3, sort_by: 'created_at', sort_dir: 'desc' },
    })
    const items = res.data.items || []
    if (items.length > 0) {
      updates.value = items.map((c: any) => {
        const d = c.created_at ? new Date(c.created_at) : new Date()
        const formattedDate = d.toLocaleDateString('en-IN', {
          day: '2-digit',
          month: 'short',
          year: 'numeric',
        })
        return {
          date: formattedDate,
          text: `Case #${c.case_number} registered for ${c.institution_name} under ${c.category}.`,
        }
      })
    } else {
      const now = new Date()
      const fmt = (d: Date) =>
        d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
      updates.value = [
        { date: fmt(now), text: 'SIH64 portal active across all central AICTE autonomous bureaus.' },
        {
          date: fmt(new Date(now.getTime() - 7 * 86400000)),
          text: 'Cross-bureau grievance deduplication engine operational for institutional intake.',
        },
        {
          date: fmt(new Date(now.getTime() - 14 * 86400000)),
          text: 'Statutory compliance tracking and SLA monitoring protocols enforced.',
        },
      ]
    }
  } catch (err) {
    const now = new Date()
    const fmt = (d: Date) =>
      d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
    updates.value = [
      { date: fmt(now), text: 'SIH64 portal active across all central AICTE autonomous bureaus.' },
      {
        date: fmt(new Date(now.getTime() - 7 * 86400000)),
        text: 'Cross-bureau grievance deduplication engine operational for institutional intake.',
      },
      {
        date: fmt(new Date(now.getTime() - 14 * 86400000)),
        text: 'Statutory compliance tracking and SLA monitoring protocols enforced.',
      },
    ]
  } finally {
    loadingUpdates.value = false
  }
}

onMounted(() => {
  loadUpdates()
})

function handleSearch() {
  if (searchQuery.value.trim()) {
    router.push({ path: '/complaints', query: { q: searchQuery.value.trim() } })
  } else {
    router.push('/')
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#e8efe0] dark:bg-[#161716] text-[#22261f] dark:text-[#e6eae2] flex flex-col font-sans transition-colors">
    <!-- Top Landing Header -->
    <header class="sticky top-0 z-40 bg-[#0c2340] border-b border-[#14325a] text-white px-4 sm:px-8 py-3 transition-colors shadow-sm select-none">
      <div class="max-w-7xl mx-auto flex items-center justify-between gap-4">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-3">
          <SihLogo light-text size="md" :show-subtitle="true" />
        </router-link>

        <!-- Nav Links -->
        <nav class="hidden md:flex items-center gap-6" aria-label="Landing Navigation">
          <button
            v-for="item in navItems"
            :key="item.name"
            type="button"
            :class="[
              'text-xs font-medium transition-colors py-1 relative',
              activeTab === item.name
                ? 'text-white font-semibold after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-[#f97316]'
                : 'text-slate-300 hover:text-white',
            ]"
            @click="handleNavClick(item)"
          >
            {{ item.name }}
          </button>
        </nav>

        <!-- Right Search & Access CTAs -->
        <div class="flex items-center gap-3">
          <!-- Search Box -->
          <div class="hidden lg:flex items-center bg-[#071728] border border-[#16355d] rounded-lg px-2.5 py-1.5 w-48 text-xs text-slate-300 focus-within:border-[#38bdf8] transition">
            <Search class="w-3.5 h-3.5 text-slate-400 mr-2 shrink-0" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search..."
              class="bg-transparent w-full focus:outline-none placeholder-slate-400 text-xs text-white"
              @keydown.enter="handleSearch"
            />
          </div>

          <ThemeToggle />

          <router-link
            to="/login"
            class="hidden sm:inline-block px-3 py-1.5 text-xs font-medium text-slate-200 hover:text-white transition-colors"
          >
            Login
          </router-link>

          <router-link
            to="/"
            class="inline-flex items-center justify-center gap-1.5 px-4 py-1.5 rounded-lg bg-[#c2410c] hover:bg-[#9a3412] text-white text-xs font-semibold shadow-sm transition-all"
          >
            <span>Enter Portal</span>
            <ArrowRight class="w-3.5 h-3.5" />
          </router-link>
        </div>
      </div>
    </header>

    <!-- Main Landing Container -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-10">
      <!-- Hero Section -->
      <section id="about-section" class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center pt-2 pb-4">
        <!-- Left Hero Copy -->
        <div class="lg:col-span-7 space-y-4">
          <div class="inline-flex items-center gap-1.5 rounded-full bg-orange-100 dark:bg-[#33200a] border border-orange-200 dark:border-[#522900] px-3 py-1 text-xs font-semibold text-orange-900 dark:text-[#f97316]">
            <span>Welcome to SIH64</span>
          </div>

          <h1 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-[#22261f] dark:text-white [text-wrap:balance]">
            Innovate <span class="text-[#f97316]">•</span> Build <span class="text-[#f97316]">•</span> Transform
          </h1>

          <p class="text-[#5f6656] dark:text-[#989898] text-sm sm:text-base leading-relaxed max-w-xl [text-wrap:pretty]">
            SIH64 is a platform to bring together bright minds, innovative ideas and real-world problem statements to build solutions for a better tomorrow.
          </p>

          <div class="flex flex-wrap items-center gap-3 pt-2">
            <router-link
              to="/"
              class="inline-flex items-center gap-2 rounded-lg bg-[#c2410c] hover:bg-[#9a3412] px-5 py-2.5 text-xs font-semibold text-white shadow-md transition-all duration-150"
            >
              <span>Explore Problem Statements</span>
              <ArrowRight class="w-4 h-4" />
            </router-link>

            <router-link
              to="/complaints"
              class="inline-flex items-center gap-2 rounded-lg border border-[#dfe7d6] dark:border-[#2f332b] bg-white dark:bg-[#1e201d] hover:bg-slate-50 dark:hover:bg-[#252922] px-4 py-2.5 text-xs font-semibold text-slate-700 dark:text-[#cccccc] transition-colors"
            >
              <Play class="w-3.5 h-3.5 text-[#f97316] fill-current" />
              <span>How It Works</span>
            </router-link>
          </div>
        </div>

        <!-- Right Hero Illustration Graphic -->
        <div class="lg:col-span-5 relative flex items-center justify-center">
          <div class="relative w-full max-w-md aspect-square rounded-2xl bg-gradient-to-br from-blue-50/70 to-indigo-50/40 dark:from-[#1b263b]/40 dark:to-[#0f172a]/60 border border-[#dfe7d6] dark:border-[#2f332b] p-6 flex flex-col items-center justify-center overflow-hidden shadow-sm">
            <!-- India Map Silhouette Outline in background -->
            <div class="absolute inset-0 pointer-events-none -z-0 flex items-center justify-center">
              <svg
                class="w-full h-full text-blue-200/40 dark:text-blue-900/15"
                viewBox="0 0 400 400"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M200,40 Q240,60 220,100 T260,160 T220,220 T200,320 T180,220 T140,160 T180,100 Z" opacity="0.4" />
              </svg>
            </div>

            <!-- Center Illuminated Bulb Motif -->
            <div class="relative z-10 flex flex-col items-center">
              <div class="relative w-28 h-28 flex items-center justify-center">
                <div class="absolute inset-0 rounded-full bg-orange-400/20 dark:bg-orange-500/10 blur-xl animate-pulse"></div>
                <!-- Glowing Brain Bulb Vector -->
                <svg viewBox="0 0 64 64" fill="none" class="w-24 h-24">
                  <!-- Bulb Base -->
                  <path d="M22 42C19 39 17 34 17 28C17 19.7 23.7 13 32 13C40.3 13 47 19.7 47 28C47 34 45 39 42 42" stroke="#0284c7" stroke-width="2.5" stroke-linecap="round" />
                  <!-- Saffron Brain Left -->
                  <path d="M32 17C26 17 21 21.5 21 27.5C21 32 24 36.5 26 39.5V42H32V17Z" fill="#f97316" />
                  <!-- Cyan Brain Right -->
                  <path d="M32 17C38 17 43 21.5 43 27.5C43 32 40 36.5 38 39.5V42H32V17Z" fill="#0ea5e9" />
                  <line x1="32" y1="16" x2="32" y2="42" stroke="#ffffff" stroke-width="2" />
                  <rect x="27" y="44" width="10" height="3" rx="1.5" fill="#94a3b8" />
                  <rect x="28.5" y="48.5" width="7" height="2.5" rx="1" fill="#cbd5e1" />
                  <path d="M29.5 52.5C29.5 54 30.5 55 32 55C33.5 55 34.5 54 34.5 52.5H29.5Z" fill="#f97316" />
                </svg>
              </div>

              <!-- Surrounding Domain Badges -->
              <div class="flex items-center gap-3 mt-4">
                <span class="p-2 rounded-full bg-white dark:bg-[#252526] shadow-sm border border-slate-200 dark:border-[#383838] text-blue-600 dark:text-[#38bdf8]" title="Engineering">
                  <Building2 class="w-4 h-4" />
                </span>
                <span class="p-2 rounded-full bg-white dark:bg-[#252526] shadow-sm border border-slate-200 dark:border-[#383838] text-[#10b981]" title="Sustainability">
                  <ShieldCheck class="w-4 h-4" />
                </span>
                <span class="p-2 rounded-full bg-white dark:bg-[#252526] shadow-sm border border-slate-200 dark:border-[#383838] text-[#f97316]" title="Innovation">
                  <Lightbulb class="w-4 h-4" />
                </span>
              </div>
            </div>

            <!-- Vertical Tagline + Tricolor bar -->
            <div class="mt-6 flex flex-col items-center text-center relative z-10">
              <span class="text-xs font-bold tracking-wider uppercase text-slate-800 dark:text-white">
                Smart India Hackathon 64
              </span>
              <!-- Indian Tricolor Line -->
              <div class="flex items-center gap-1 mt-1.5">
                <span class="w-6 h-1 rounded-full bg-[#f97316]"></span>
                <span class="w-6 h-1 rounded-full bg-slate-300 dark:bg-slate-500"></span>
                <span class="w-6 h-1 rounded-full bg-[#10b981]"></span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 4 Feature Cards Grid (Side-by-side icons, No Stacked AI Container) -->
      <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="card in featureCards"
          :key="card.title"
          class="group rounded-xl border border-[#dfe7d6] dark:border-[#2f332b] bg-white dark:bg-[#1e201d] p-5 flex flex-col justify-between hover:border-slate-300 dark:hover:border-[#3e3e42] transition-all duration-150 shadow-sm"
        >
          <div class="space-y-3">
            <div class="flex items-center gap-3">
              <div class="flex size-8 items-center justify-center rounded-lg bg-blue-50 dark:bg-[#142e4e] text-blue-600 dark:text-[#38bdf8] shrink-0 border border-blue-100 dark:border-[#1d4370]">
                <component :is="card.icon" class="w-4 h-4" aria-hidden="true" />
              </div>
              <h2 class="text-xs font-semibold uppercase tracking-wider text-slate-900 dark:text-white [text-wrap:balance]">
                {{ card.title }}
              </h2>
            </div>

            <p class="text-xs text-[#5f6656] dark:text-[#989898] leading-relaxed [text-wrap:pretty]">
              {{ card.description }}
            </p>
          </div>

          <router-link
            :to="card.link"
            class="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 dark:text-[#38bdf8] hover:text-blue-800 dark:hover:text-[#60cdff] mt-4 pt-3 border-t border-[#dfe7d6] dark:border-[#2f332b] transition-colors"
          >
            <span>Learn More</span>
            <ArrowRight class="w-3.5 h-3.5" />
          </router-link>
        </div>
      </section>

      <!-- Bottom Split Section: Latest Updates + Challenge Callout -->
      <section class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        <!-- Latest Updates (8 cols) -->
        <div class="lg:col-span-8 rounded-xl border border-[#dfe7d6] dark:border-[#2f332b] bg-white dark:bg-[#1e201d] p-5 shadow-sm">
          <div class="flex items-center gap-2 border-b border-[#dfe7d6] dark:border-[#2f332b] pb-3">
            <span class="w-1 h-4 rounded-full bg-[#f97316]"></span>
            <h2 class="text-xs font-semibold uppercase tracking-wider text-slate-900 dark:text-white">
              Latest Updates
            </h2>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4 divide-y sm:divide-y-0 sm:divide-x divide-[#dfe7d6] dark:divide-[#2f332b]">
            <article
              v-for="(u, idx) in updates"
              :key="idx"
              class="pt-3 sm:pt-0 sm:px-3 first:pl-0 last:pr-0 space-y-1.5"
            >
              <div class="flex items-center gap-1.5 text-xs font-mono font-medium text-slate-400 dark:text-[#989898]">
                <Calendar class="w-3 h-3 text-[#f97316]" />
                <span>{{ u.date }}</span>
              </div>
              <p class="text-xs text-slate-600 dark:text-[#cccccc] leading-relaxed [text-wrap:pretty]">
                {{ u.text }}
              </p>
            </article>
          </div>
        </div>

        <!-- Deep Navy Callout Box (4 cols) -->
        <div class="lg:col-span-4 rounded-xl bg-[#0c2340] dark:bg-[#0b1a30] text-white p-5 flex flex-col justify-between shadow-md border border-[#14325a]">
          <div class="space-y-3">
            <div class="flex items-center gap-3">
              <div class="flex size-8 shrink-0 items-center justify-center rounded-lg bg-[#183a66] text-[#f97316]">
                <Lightbulb class="w-4 h-4 fill-current" />
              </div>

              <h2 class="text-xs font-semibold uppercase tracking-wider text-white [text-wrap:balance]">
                Be a part of India's largest innovation challenge
              </h2>
            </div>

            <p class="text-xs text-slate-300 leading-relaxed [text-wrap:pretty]">
              Register your institution or evaluate live problem statements across central technical bureaus.
            </p>
          </div>

          <router-link
            to="/"
            class="inline-flex items-center justify-center gap-1.5 mt-5 rounded-lg bg-white text-[#0c2340] hover:bg-slate-100 px-4 py-2 text-xs font-bold transition-all shadow-sm"
          >
            <span>Register Now</span>
            <ArrowRight class="w-3.5 h-3.5" />
          </router-link>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="mt-auto border-t border-[#dfe7d6] dark:border-[#2f332b] bg-white dark:bg-[#101110] py-6 px-4 sm:px-8 text-xs text-[#5f6656] dark:text-[#989898]">
      <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <span class="font-bold text-slate-800 dark:text-white">SIH64</span>
          <span>| All India Council for Technical Education</span>
        </div>
        <div class="flex items-center gap-4">
          <router-link to="/" class="hover:text-blue-600 dark:hover:text-white transition">Dashboard</router-link>
          <router-link to="/complaints" class="hover:text-blue-600 dark:hover:text-white transition">Complaints</router-link>
          <router-link to="/overlaps" class="hover:text-blue-600 dark:hover:text-white transition">Overlaps</router-link>
          <router-link to="/institutions" class="hover:text-blue-600 dark:hover:text-white transition">Institutions</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>
