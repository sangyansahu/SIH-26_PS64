<script setup lang="ts">
defineProps<{
  showSubtitle?: boolean
  lightText?: boolean
  size?: 'sm' | 'md' | 'lg'
}>()
</script>

<template>
  <div class="flex items-center gap-2.5 select-none">
    <!-- Illuminated SIH64 Bulb Emblem -->
    <div
      :class="[
        'relative flex shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-slate-900 to-slate-950 p-1.5 shadow-md border border-slate-800',
        size === 'lg' ? 'w-11 h-11' : size === 'sm' ? 'w-7 h-7' : 'w-9 h-9',
      ]"
    >
      <svg
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        class="w-full h-full"
        aria-hidden="true"
      >
        <!-- Outer Glow Particles -->
        <circle cx="24" cy="20" r="18" fill="url(#bulbGlow)" opacity="0.3" />
        
        <!-- Lightbulb Outline -->
        <path
          d="M17 29C15.5 27 14 23.5 14 19.5C14 14 18.5 9.5 24 9.5C29.5 9.5 34 14 34 19.5C34 23.5 32.5 27 31 29"
          stroke="#38bdf8"
          stroke-width="2"
          stroke-linecap="round"
        />
        
        <!-- Left Brain/Idea Half (Saffron/Orange) -->
        <path
          d="M24 12C20.5 12 17.5 15 17.5 19C17.5 22.5 19.5 25 21 27V29H24V12Z"
          fill="#f97316"
          opacity="0.9"
        />
        <!-- Right Brain/Circuit Half (Cyan/Green) -->
        <path
          d="M24 12C27.5 12 30.5 15 30.5 19C30.5 22.5 28.5 25 27 27V29H24V12Z"
          fill="#10b981"
          opacity="0.9"
        />

        <!-- Brain Fold Divides -->
        <path
          d="M21 16C19.5 17 19.5 19 21 20M20 23C21 24 22 24.5 24 24.5M27 16C28.5 17 28.5 19 27 20M28 23C27 24 26 24.5 24 24.5"
          stroke="#ffffff"
          stroke-width="1.2"
          stroke-linecap="round"
        />
        
        <!-- Center Divider -->
        <line x1="24" y1="11" x2="24" y2="29" stroke="#ffffff" stroke-width="1.5" />

        <!-- Base Thread & Contact -->
        <rect x="20" y="30" width="8" height="2.5" rx="1" fill="#94a3b8" />
        <rect x="21" y="33.5" width="6" height="2" rx="0.8" fill="#cbd5e1" />
        <path d="M22 36.5C22 37.5 23 38 24 38C25 38 26 37.5 26 36.5H22Z" fill="#f97316" />

        <defs>
          <radialGradient id="bulbGlow" cx="0.5" cy="0.5" r="0.5">
            <stop offset="0%" stop-color="#38bdf8" />
            <stop offset="100%" stop-color="#0f172a" stop-opacity="0" />
          </radialGradient>
        </defs>
      </svg>
    </div>

    <!-- Text Typography -->
    <div>
      <div class="flex items-center gap-1.5 leading-none">
        <span
          :class="[
            'font-bold tracking-tight',
            lightText ? 'text-white' : 'text-slate-900 dark:text-white',
            size === 'lg' ? 'text-xl' : size === 'sm' ? 'text-sm' : 'text-base',
          ]"
        >
          SIH64
        </span>
        <span class="inline-flex items-center gap-0.5">
          <span class="w-1.5 h-1.5 rounded-full bg-[#f97316]"></span>
          <span class="w-1.5 h-1.5 rounded-full bg-slate-300 dark:bg-slate-600"></span>
          <span class="w-1.5 h-1.5 rounded-full bg-[#10b981]"></span>
        </span>
      </div>
      <p
        v-if="showSubtitle !== false"
        :class="[
          'text-xs tracking-tight mt-0.5',
          lightText ? 'text-slate-400' : 'text-slate-500 dark:text-[#989898]',
        ]"
      >
        Ideas for a Smarter India
      </p>
    </div>
  </div>
</template>
