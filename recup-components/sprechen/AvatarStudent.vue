<!-- components/sprechen/AvatarStudent.vue -->
<template>
  <svg viewBox="0 0 100 100" class="rounded-full bg-linear-to-b from-[#173a35] to-[#0c211d] avatar-breathe">
    <defs>
      <linearGradient id="studentSkinTone" x1="0" y1="0" x2="0.3" y2="1">
        <stop offset="0%" stop-color="#f0c49c" />
        <stop offset="100%" stop-color="#dba876" />
      </linearGradient>
      <linearGradient id="studentBrandGrad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#2dd4bf" />
        <stop offset="100%" stop-color="#047857" />
      </linearGradient>
    </defs>
    <circle cx="26" cy="44" r="4.5" fill="url(#studentSkinTone)" />
    <circle cx="74" cy="44" r="4.5" fill="url(#studentSkinTone)" />
    <circle cx="50" cy="42" r="22" fill="url(#studentSkinTone)" />
    <ellipse cx="59" cy="48" rx="10" ry="14" fill="#c8935f" opacity="0.18" />
    <path d="M27 37 Q26 14 50 13 Q74 14 73 37 Q73 30 62 25 Q56 33 50 25 Q44 33 38 25 Q27 30 27 37 Z" fill="#5c3a20" />
    <path d="M35 33 Q41 30.5 47 33" fill="none" stroke="#2b2019" stroke-width="1.6" stroke-linecap="round" />
    <path d="M53 33 Q59 30.5 65 33" fill="none" stroke="#2b2019" stroke-width="1.6" stroke-linecap="round" />
    <g class="avatar-eyes">
      <circle cx="41" cy="41" r="2.6" fill="#2b2019" />
      <circle cx="59" cy="41" r="2.6" fill="#2b2019" />
      <circle cx="42" cy="39.5" r="0.8" fill="#fff" />
      <circle cx="60" cy="39.5" r="0.8" fill="#fff" />
    </g>
    <path d="M50 42 L48.5 49 Q50 50.5 51.5 49" fill="none" stroke="#c8935f" stroke-width="1.4" stroke-linecap="round" />
    <rect
      x="44" y="53" width="12" height="4" rx="2"
      fill="#a15c46"
      class="avatar-mouth"
      :class="talking ? 'is-talking' : ''"
    />
    <path d="M25 28 Q50 8 75 28" fill="none" stroke="#374151" stroke-width="5" stroke-linecap="round" />
    <circle cx="25" cy="32" r="6" fill="url(#studentBrandGrad)" />
    <circle cx="75" cy="32" r="6" fill="url(#studentBrandGrad)" />
    <path d="M12 100 Q20 68 50 68 Q80 68 88 100 Z" fill="url(#studentBrandGrad)" />
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ talking?: boolean }>(), { talking: false });
</script>

<style scoped>
.avatar-breathe {
  animation: avatar-breathe 4s ease-in-out infinite;
  transform-origin: 50% 100%;
}
@keyframes avatar-breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}
.avatar-eyes {
  animation: avatar-blink 4.5s ease-in-out infinite;
  transform-origin: 50px 40px;
}
@keyframes avatar-blink {
  0%, 92%, 100% { transform: scaleY(1); }
  96% { transform: scaleY(0.1); }
}
.avatar-mouth {
  transform-origin: 50px 54px;
  transition: transform 0.15s ease;
}
.avatar-mouth.is-talking {
  animation: avatar-talk 0.42s ease-in-out infinite;
}
@keyframes avatar-talk {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(2.2); }
}
@media (prefers-reduced-motion: reduce) {
  .avatar-breathe, .avatar-eyes, .avatar-mouth.is-talking {
    animation: none !important;
  }
}
</style>