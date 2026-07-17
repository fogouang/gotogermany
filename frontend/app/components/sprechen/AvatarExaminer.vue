<!-- components/sprechen/AvatarExaminer.vue -->
<template>
  <svg viewBox="0 0 100 100" class="rounded-full bg-linear-to-b from-[#173a35] to-[#0c211d] avatar-breathe">
    <defs>
      <linearGradient id="examinerSkinTone" x1="0" y1="0" x2="0.3" y2="1">
        <stop offset="0%" stop-color="#f0c49c" />
        <stop offset="100%" stop-color="#dba876" />
      </linearGradient>
      <linearGradient id="examinerBrandGrad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#2dd4bf" />
        <stop offset="100%" stop-color="#047857" />
      </linearGradient>
    </defs>
    <circle cx="26" cy="43" r="4.5" fill="url(#examinerSkinTone)" />
    <circle cx="74" cy="43" r="4.5" fill="url(#examinerSkinTone)" />
    <circle cx="50" cy="42" r="22" fill="url(#examinerSkinTone)" />
    <ellipse cx="59" cy="48" rx="10" ry="14" fill="#c8935f" opacity="0.18" />
    <path d="M27 34 Q29 11 50 11 Q71 11 73 34 Q73 21 50 19 Q27 21 27 34 Z" fill="#23282f" />
    <path d="M35 33 Q41 30 47 33" fill="none" stroke="#2b2019" stroke-width="1.6" stroke-linecap="round" />
    <path d="M53 33 Q59 30 65 33" fill="none" stroke="#2b2019" stroke-width="1.6" stroke-linecap="round" />
    <circle cx="41" cy="41" r="7" fill="none" stroke="#2b2019" stroke-width="2" />
    <circle cx="59" cy="41" r="7" fill="none" stroke="#2b2019" stroke-width="2" />
    <line x1="48" y1="41" x2="52" y2="41" stroke="#2b2019" stroke-width="2" />
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
    <path d="M14 100 Q20 70 50 70 Q80 70 86 100 Z" fill="#1f2733" />
    <path d="M40 70 L50 84 L60 70 L54 68 L46 68 Z" fill="#f4f4f4" />
    <path d="M47 70 L50 92 L53 70 Z" fill="url(#examinerBrandGrad)" />
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