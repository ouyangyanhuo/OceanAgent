<script setup>
defineProps({
  size: {
    type: String,
    default: 'small',
    validator: (v) => ['small', 'big'].includes(v),
  },
})
</script>

<template>
  <!-- 小尺寸：70 粒子，12 条路径 -->
  <div v-if="size === 'small'" class="ocean-current-layer">
    <svg viewBox="0 0 1000 600" preserveAspectRatio="none">
      <path class="current-flow strong-current" d="M10 505 C160 445,320 365,520 255 S825 150,1000 90" />
      <path class="current-flow delay-a" d="M0 545 C165 470,320 405,510 325 S790 245,1000 175" />
      <path class="current-flow delay-b" d="M70 595 C235 515,420 425,610 305 S865 180,1000 75" />
      <path class="current-flow coastal-current" d="M115 575 C220 485,315 385,405 292" />
      <path class="current-flow coastal-current delay-c" d="M175 610 C260 525,345 430,438 345" />
      <path class="current-flow strong-current delay-d" d="M245 610 C450 500,660 350,1000 120" />
      <path class="current-flow delay-e" d="M35 360 C90 315,155 255,240 180" />
      <path class="current-flow delay-f" d="M540 465 C640 355,760 245,875 145" />
      <path class="current-flow thin-current" d="M315 570 C430 500,548 430,700 320 S900 210,980 140" />
      <path class="current-flow thin-current delay-b" d="M20 255 C125 225,230 195,365 120" />
      <path class="current-flow thin-current delay-e" d="M640 585 C700 490,770 405,910 305" />
      <path class="current-flow thin-current delay-c" d="M470 590 C560 505,680 415,795 315" />
    </svg>
    <div class="ocean-particles small-particles">
      <span
        v-for="i in 70"
        :key="i"
        :style="{
          left: ((i * 37) % 100) + '%',
          top: ((i * 23) % 100) + '%',
          animationDelay: -((i * 0.17) % 6).toFixed(2) + 's',
          animationDuration: (6 + (i % 7)) + 's',
        }"
      ></span>
    </div>
  </div>

  <!-- 大尺寸：150 粒子，18 条路径 -->
  <div v-else class="ocean-current-layer big-current">
    <svg viewBox="0 0 1400 900" preserveAspectRatio="none">
      <path class="current-flow strong-current" d="M0 710 C250 650,500 550,850 380 S1200 220,1400 100" />
      <path class="current-flow delay-a" d="M0 620 C220 580,480 480,760 350 S1100 220,1350 80" />
      <path class="current-flow delay-b" d="M0 520 C220 470,460 380,700 280 S1000 180,1300 60" />
      <path class="current-flow delay-c" d="M100 800 C300 720,500 620,850 420 S1150 250,1380 120" />
      <path class="current-flow delay-d" d="M180 850 C400 760,650 600,980 360 S1250 180,1400 80" />
      <path class="current-flow strong-current delay-e" d="M200 720 C450 600,650 480,950 300" />
      <path class="current-flow thin-current" d="M100 400 C250 360,420 300,620 220" />
      <path class="current-flow thin-current delay-a" d="M300 500 C500 420,700 320,1000 180" />
      <path class="current-flow delay-b" d="M500 850 C650 720,800 620,1000 450" />
      <path class="current-flow delay-c" d="M650 800 C800 650,1000 500,1300 300" />
      <path class="current-flow thin-current delay-d" d="M920 880 C1020 720,1160 580,1370 390" />
      <path class="current-flow thin-current delay-e" d="M820 120 C1000 160,1180 190,1400 245" />
      <path class="current-flow delay-f" d="M0 260 C210 240,430 220,650 175 S1040 105,1400 55" />
      <path class="current-flow thin-current delay-c" d="M0 820 C180 760,330 690,520 585 S850 420,1110 260" />
      <path class="current-flow strong-current delay-b" d="M70 900 C290 790,520 665,785 515 S1160 315,1400 210" />
      <path class="current-flow thin-current delay-a" d="M1120 900 C1200 780,1280 650,1400 520" />
      <path class="current-flow delay-e" d="M0 110 C170 135,340 145,540 130 S900 90,1210 20" />
      <path class="current-flow thin-current delay-f" d="M420 900 C520 760,640 625,820 480 S1080 285,1320 130" />
    </svg>
    <div class="ocean-particles big-particles">
      <span
        v-for="i in 150"
        :key="i"
        :style="{
          left: ((i * 29) % 100) + '%',
          top: ((i * 41) % 100) + '%',
          animationDelay: -((i * 0.13) % 8).toFixed(2) + 's',
          animationDuration: (7 + (i % 9)) + 's',
        }"
      ></span>
    </div>
  </div>
</template>

<style scoped>
.ocean-current-layer {
  position: absolute;
  inset: 0;
  z-index: 520;
  pointer-events: none;
  overflow: hidden;
}
.ocean-current-layer svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
.current-flow {
  fill: none;
  stroke: #8efcff;
  stroke-width: 3.2;
  opacity: .86;
  stroke-linecap: round;
  stroke-dasharray: 14 24;
  filter:
    drop-shadow(0 0 8px rgba(142, 252, 255, .95))
    drop-shadow(0 0 18px rgba(0, 180, 255, .45));
  animation:
    flowMove 7.5s linear infinite,
    flowGlow 3.2s ease-in-out infinite;
}
.strong-current {
  stroke: #c9ffff;
  stroke-width: 4.4 !important;
  opacity: .95;
  stroke-dasharray: 18 24;
}
.coastal-current {
  stroke: #00ffe0;
  stroke-width: 3.6 !important;
  opacity: .92;
}
.thin-current {
  stroke-width: 2.1 !important;
  opacity: .58;
  stroke-dasharray: 8 18;
}
.big-current .current-flow {
  stroke-width: 3.4;
}
.big-current .strong-current {
  stroke-width: 4.8 !important;
}
.delay-a { animation-delay: -1s, -.4s; }
.delay-b { animation-delay: -2s, -.8s; }
.delay-c { animation-delay: -3s, -1.2s; }
.delay-d { animation-delay: -4s, -1.6s; }
.delay-e { animation-delay: -5s, -2s; }
.delay-f { animation-delay: -6s, -2.4s; }

.ocean-particles {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
}
.ocean-particles span {
  position: absolute;
  width: 3px;
  height: 22px;
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(230, 255, 255, .98), rgba(0, 220, 255, .35), transparent);
  box-shadow: 0 0 7px rgba(155, 255, 255, .9), 0 0 18px rgba(0, 180, 255, .45);
  opacity: .78;
  transform: rotate(58deg);
  animation: particleMove linear infinite;
}
.small-particles span:nth-child(3n) { width: 2px; height: 16px; opacity: .52; }
.small-particles span:nth-child(4n) { opacity: .95; }
.big-particles span { width: 3px; height: 24px; }
.big-particles span:nth-child(5n) { width: 2px; height: 15px; opacity: .48; }
.big-particles span:nth-child(7n) { height: 30px; opacity: .92; }

@keyframes flowMove {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -260; }
}
@keyframes flowGlow {
  0% { opacity: .48; }
  50% { opacity: .96; }
  100% { opacity: .48; }
}
@keyframes particleMove {
  from { transform: translateX(-40px) translateY(30px) rotate(58deg) scale(.75); }
  to { transform: translateX(170px) translateY(-115px) rotate(58deg) scale(1.08); }
}
.ocean-current-layer::before {
  content: '';
  position: absolute;
  inset: -20%;
  z-index: 1;
  pointer-events: none;
  background:
    radial-gradient(circle at 22% 78%, rgba(0, 255, 255, .12), transparent 22%),
    radial-gradient(circle at 68% 30%, rgba(0, 160, 255, .14), transparent 24%),
    radial-gradient(circle at 78% 72%, rgba(0, 255, 180, .09), transparent 28%);
  animation: oceanBreath 5s ease-in-out infinite;
  mix-blend-mode: screen;
}
@keyframes oceanBreath {
  0%, 100% { opacity: .45; transform: scale(1); }
  50% { opacity: .85; transform: scale(1.04); }
}
</style>
