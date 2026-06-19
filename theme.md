<!DOCTYPE html>
<html lang="en"><head><script id="aura-preview-performance-controller">
(function() {
if (window.__auraPreviewPerformanceController) return;
const nativeRequestAnimationFrame = window.requestAnimationFrame
? window.requestAnimationFrame.bind(window)
: function(callback) { return window.setTimeout(function() { callback(Date.now()); }, 16); };
const nativeCancelAnimationFrame = window.cancelAnimationFrame
? window.cancelAnimationFrame.bind(window)
: window.clearTimeout.bind(window);
const nativeSetInterval = window.setInterval.bind(window);
let paused = false;
let nextFrameId = 1;
const frameRecords = new Map();
const pausedFrameCallbacks = new Map();
const style = document.createElement('style');
style.id = 'aura-preview-performance-style';
style.textContent = [
'html[data-aura-preview-paused="true"] *,',
'html[data-aura-preview-paused="true"] *::before,',
'html[data-aura-preview-paused="true"] *::after {',
'  animation-play-state: paused !important;',
'  transition-duration: 0s !important;',
'  scroll-behavior: auto !important;',
'}'
].join('\n');
document.head.appendChild(style);
window.requestAnimationFrame = function(callback) {
const frameId = nextFrameId++;
if (paused) {
pausedFrameCallbacks.set(frameId, callback);
frameRecords.set(frameId, { paused: true });
return frameId;
}
const nativeFrameId = nativeRequestAnimationFrame(function(timestamp) {
frameRecords.delete(frameId);
callback(timestamp);
});
frameRecords.set(frameId, { nativeFrameId: nativeFrameId });
return frameId;
};
window.cancelAnimationFrame = function(frameId) {
const record = frameRecords.get(frameId);
pausedFrameCallbacks.delete(frameId);
if (record && typeof record.nativeFrameId !== 'undefined') {
nativeCancelAnimationFrame(record.nativeFrameId);
}
frameRecords.delete(frameId);
};
window.setInterval = function(callback, delay) {
const args = Array.prototype.slice.call(arguments, 2);
return nativeSetInterval(function() {
if (paused) return;
callback.apply(this, args);
}, delay);
};
const flushPausedFrames = function() {
const callbacks = Array.from(pausedFrameCallbacks.entries());
pausedFrameCallbacks.clear();
callbacks.forEach(function(entry) {
const frameId = entry[0];
const callback = entry[1];
const nativeFrameId = nativeRequestAnimationFrame(function(timestamp) {
frameRecords.delete(frameId);
callback(timestamp);
});
frameRecords.set(frameId, { nativeFrameId: nativeFrameId });
});
};
const setPaused = function(nextPaused) {
const shouldPause = Boolean(nextPaused);
if (paused === shouldPause) return;
paused = shouldPause;
document.documentElement.toggleAttribute('data-aura-preview-paused', paused);
if (!paused) {
flushPausedFrames();
}
};
window.__auraPreviewPerformanceController = {
setPaused: setPaused,
get paused() {
return paused;
}
};
window.addEventListener('message', function(event) {
if (event.source !== window.parent) return;
if (!event.data || event.data.type !== 'aura-preview-performance-mode') return;
setPaused(event.data.paused);
});
})();
</script>
<!-- =========================================================
Document Setup
========================================================== -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ATELIER AI</title>
<!-- =========================================================
Fonts
========================================================== -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Manrope:wght@400;500;600;700;800&family=Newsreader:opsz,wght@6..72,300;6..72,400;6..72,500&display=swap" rel="stylesheet">
<!-- =========================================================
Libraries
========================================================== -->
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/lucide@latest"></script>
<!-- =========================================================
Global Styles / Design Tokens
========================================================== -->
<style>
:root {
--paper: #f5f0e9;
--ink: #171411;
--muted: #7d7267;
--taupe: #a67b4f;
--panel: #eee5da;
}
body {
margin: 0;
font-family: "Manrope", sans-serif;
background:
radial-gradient(circle at 12% 16%, rgba(255, 255, 255, 0.82), transparent 30%),
radial-gradient(circle at 82% 10%, rgba(221, 211, 198, 0.34), transparent 34%),
var(--paper);
color: var(--ink);
-webkit-font-smoothing: antialiased;
text-rendering: geometricPrecision;
}
.font-logo {
font-family: "Cormorant Garamond", serif;
}
.font-display {
font-family: "Newsreader", serif;
}
.premium-panel {
border: 1px solid #d8c9b8;
background: #eee5da;
box-shadow:
0 24px 64px rgba(42, 31, 22, 0.22),
inset 0 1px 0 rgba(255, 255, 255, 0.65);
}
.material-dot:nth-child(1) {
background: radial-gradient(circle at 35% 25%, #e6dfd5, #bfb5aa);
}
.material-dot:nth-child(2) {
background: linear-gradient(90deg, #786653, #b39a82, #705844);
}
.material-dot:nth-child(3) {
background: radial-gradient(circle at 30% 20%, #333638, #111314);
}
.material-dot:nth-child(4) {
background: radial-gradient(circle at 40% 20%, #d8ceb9, #a9967f);
}
.material-dot:nth-child(5) {
background: linear-gradient(120deg, #6d452d, #b57b4d, #553722);
}
.material-dot:nth-child(6) {
background: radial-gradient(circle at 35% 25%, #e1dcd5, #bdb5ac);
}
.z-35 {
z-index: 35;
}
.z-55 {
z-index: 55;
}
@media (max-width: 1023px) {
.hero-side {
min-height: auto !important;
}
.hero-image-frame {
height: 640px !important;
border-radius: 1.35rem !important;
}
.hero-visual-bleed {
margin-right: 0 !important;
}
}
@media (max-width: 640px) {
.hero-image-frame {
height: 560px !important;
}
}
</style>
<style>
.reveal-on-scroll {
opacity: 0;
transform: translateY(30px);
transition-property: opacity, transform;
transition-duration: 1.2s;
transition-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
}
.reveal-on-scroll.animate-in {
opacity: 1;
transform: translateY(0);
}
@media (prefers-reduced-motion: reduce) {
.reveal-on-scroll {
transition: none;
opacity: 1;
transform: none;
}
}
</style><!-- aura-ga4-start -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2M6V79H761"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-2M6V79H761');
</script>
<!-- aura-ga4-end -->
</head>

  <body class="min-h-screen overflow-x-hidden">
    <!-- =========================================================
  Navigation
  ========================================================== -->
    <header class="w-full">
      <nav class="mx-auto flex max-w-[1510px] items-center justify-between gap-6 px-6 py-7 sm:px-8 lg:px-12 xl:px-14">
        <!-- Logo -->
        <a href="#" class="font-logo shrink-0 text-[1.95rem] font-medium tracking-[0.20em] text-[#171411] sm:text-[2.15rem]">
          ATELIER AI
        </a>

        <!-- Desktop Navigation Links -->
        <div class="hidden items-center gap-10 text-[15px] font-semibold tracking-[-0.02em] text-[#2c2722] lg:flex xl:gap-14">
          <a href="#" class="transition hover:text-[#98704a]">How It Works</a>
          <a href="#" class="transition hover:text-[#98704a]">Styles</a>
          <a href="#" class="transition hover:text-[#98704a]">Pricing</a>
          <a href="#" class="transition hover:text-[#98704a]">Inspiration</a>
          <a href="#" class="transition hover:text-[#98704a]">
            For Professionals
          </a>
        </div>

        <!-- Navigation Actions -->
        <div class="flex items-center gap-5 sm:gap-7">
          <a href="#" class="hidden text-[15px] font-semibold text-[#2c2722] transition hover:text-[#98704a] sm:inline-flex">
            Log in
          </a>

          <a href="#" class="inline-flex h-[54px] items-center justify-center rounded-[12px] bg-[#171614] px-7 text-[15px] font-bold text-white shadow-[0_18px_42px_rgba(25,21,18,0.16)] transition hover:bg-[#29231e]">
            Get Started
          </a>
        </div>
      </nav>
    </header>

    <main>
      <!-- =========================================================
    Section 01 / Hero
    ========================================================== -->
      <section class="pb-16 pt-8 lg:pb-20">
        <div class="mx-auto max-w-[1510px] pl-6 sm:pl-8 lg:pl-12 xl:pl-14">
          <div class="grid items-stretch gap-14 lg:grid-cols-[0.76fr_1.24fr] xl:gap-20">
            <!-- =====================================================
          Hero / Left Content
          ====================================================== -->
            <div class="hero-side flex min-h-[735px] flex-col justify-center pr-6 sm:pr-8 lg:pr-0 xl:min-h-[760px]">
              <div class="max-w-[700px] reveal-on-scroll delay-300">
                <!-- Hero Headline -->
                <h1 class="font-display max-w-[780px] text-[4.2rem] font-normal leading-[0.9] tracking-[-0.078em] text-[#151310] sm:text-[5.25rem] md:text-[5.95rem] lg:text-[5rem] xl:text-[5.9rem] 2xl:text-[6.25rem] reveal-on-scroll">
                  <span class="whitespace-nowrap">See the room</span>
                  <br>
                  before you
                  <br>
                  redesign it.
                </h1>

                <!-- Decorative Rule -->
                <div class="mt-8 h-px w-[4.1rem] bg-[#9f7851] reveal-on-scroll delay-150"></div>

                <!-- Hero Body Copy -->
                <p class="mt-7 max-w-[39rem] text-[1.15rem] font-medium leading-[1.72] tracking-[-0.025em] text-[#3a332d] sm:text-[1.22rem]">
                  Upload your room, explore multiple styles, and generate
                  polished interior concepts in minutes with
                  <span class="font-bold text-[#9a744d]">Atelier AI.</span>
                </p>

                <!-- Hero CTA Group -->
                <div class="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:gap-6 reveal-on-scroll delay-500">
                  <a href="#" class="inline-flex h-[66px] items-center justify-center gap-4 rounded-[12px] bg-[#171614] px-8 text-[1rem] font-bold text-white shadow-[0_24px_54px_rgba(28,22,17,0.18)] transition hover:-translate-y-0.5 hover:bg-[#29231f] sm:min-w-[250px]">
                    <i data-lucide="upload" class="h-6 w-6"></i>
                    Upload Your Room
                  </a>

                  <a href="#" class="inline-flex h-[66px] items-center justify-center gap-4 rounded-[12px] border border-[#d1c4b7] bg-[#f1ebe3] px-8 text-[1rem] font-bold text-[#1c1915] shadow-[0_12px_28px_rgba(88,72,58,0.055)] transition hover:-translate-y-0.5 hover:border-[#c6b49f] hover:bg-[#f8f2ea] sm:min-w-[250px]">
                    <span class="inline-flex h-8 w-8 items-center justify-center rounded-full border border-[#1d1a16]">
                      <i data-lucide="play" class="ml-0.5 h-4 w-4"></i>
                    </span>
                    See How It Works
                  </a>
                </div>

                <!-- Hero Metrics -->
                <div class="mt-10 reveal-on-scroll delay-700">
                  <div class="flex flex-wrap items-center gap-y-6 text-[#181511] lg:flex-nowrap">
                    <!-- Metric 01 -->
                    <div class="flex shrink-0 items-center gap-3.5 pr-5 xl:pr-6">
                      <i data-lucide="users-round" class="h-8 w-8 shrink-0 text-[#9d7650]"></i>
                      <div>
                        <div class="whitespace-nowrap text-[0.8rem] font-semibold text-[#756b60]">
                          Rooms Designed
                        </div>
                        <div class="mt-2 text-[1.02rem] font-extrabold leading-none tracking-[-0.02em]">
                          50K+
                        </div>
                      </div>
                    </div>

                    <div class="hidden h-12 w-px shrink-0 bg-[#d9cfc4] sm:block"></div>

                    <!-- Metric 02 -->
                    <div class="flex shrink-0 items-center gap-3.5 px-5 xl:px-6">
                      <i data-lucide="badge-check" class="h-8 w-8 shrink-0 text-[#9d7650]"></i>
                      <div>
                        <div class="whitespace-nowrap text-[0.8rem] font-semibold text-[#756b60]">
                          User Rating
                        </div>
                        <div class="mt-2 text-[1.02rem] font-extrabold leading-none tracking-[-0.02em]">
                          4.9/5
                        </div>
                      </div>
                    </div>

                    <div class="hidden h-12 w-px shrink-0 bg-[#d9cfc4] sm:block"></div>

                    <!-- Metric 03 -->
                    <div class="flex shrink-0 items-center gap-3.5 pl-5 xl:pl-6">
                      <i data-lucide="shield-check" class="h-8 w-8 shrink-0 text-[#9d7650]"></i>
                      <div>
                        <div class="whitespace-nowrap text-[0.8rem] font-semibold text-[#756b60]">
                          Trusted by
                        </div>
                        <div class="mt-2 whitespace-nowrap text-[1.02rem] font-extrabold leading-none tracking-[-0.02em] text-[#181511]">
                          Design Pros
                        </div>
                      </div>
                    </div>
                  </div>

                  <p class="mt-7 text-[0.96rem] font-medium tracking-[-0.02em] text-[#94897d]">
                    Loved by homeowners, designers, and real estate
                    professionals.
                  </p>
                </div>
              </div>
            </div>

            <!-- =====================================================
          Hero / Right Visual
          ====================================================== -->
            <div class="hero-side hero-visual-bleed relative flex min-h-[735px] items-center xl:min-h-[760px] lg:mr-[calc((1510px-100vw)/2)]">
              <div class="hero-image-frame relative h-[735px] w-full overflow-visible rounded-tl-[1.35rem] rounded-bl-[1.35rem] rounded-tr-none rounded-br-none xl:h-[760px] reveal-on-scroll delay-500">
                <!-- Main Hero Image -->
                <div class="relative h-full w-full overflow-hidden rounded-tl-[1.35rem] rounded-bl-[1.35rem] rounded-tr-none rounded-br-none border border-r-0 border-[#dfd4c8] bg-[#d7cabc] shadow-[0_34px_90px_rgba(71,56,42,0.17)] reveal-on-scroll delay-150">
                  <video src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/generated-videos/66a84ecf-0972-40f3-8a4c-15b11d3aee0a/1779500363762-9c8dfe0b-f52e-462c-ab07-46cb6e1859e9.mp4" poster="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/545b052a-b0c2-4ec1-aeac-c36a8f948a5d_3840w.png" data-aura-generated-video="true" data-aura-video-preset="loop-in-view" muted="" playsinline="" preload="metadata" loop="" aria-label="Warm editorial living room with stone fireplace, organic textures, cream sofa, wood shelving, and soft daylight" class="h-full w-full object-cover object-center"></video>

                  <div class="absolute inset-0 bg-[linear-gradient(90deg,rgba(246,240,231,0.10)_0%,rgba(246,240,231,0.00)_34%,rgba(24,18,14,0.04)_100%)]"></div>
                  <div class="absolute inset-x-0 bottom-0 h-56 bg-gradient-to-t from-[#211913]/26 via-[#211913]/7 to-transparent"></div>
                </div>

                <!-- Before Thumbnail Card -->
                <div class="premium-panel absolute -left-[70px] top-8 z-20 w-[172px] rounded-[15px] p-1.5 sm:w-[185px] lg:-left-[58px] xl:-left-[70px] reveal-on-scroll delay-300">
                  <div class="relative overflow-hidden rounded-[11px] border border-[#e2d5c8] bg-[#f7f1e9] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                    <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/de7c127b-e2ce-4fbc-af38-233509c064a3_800w.png" alt="Before empty room" class="h-[122px] w-full object-cover grayscale-[12%] saturate-[0.78] sm:h-[132px]">

                    <div class="absolute inset-0 bg-gradient-to-t from-[#1d1712]/42 via-transparent to-white/8"></div>

                    <div class="absolute bottom-3 left-3 inline-flex items-center gap-2 rounded-full border border-[#d8c9b8] bg-[#eee5da] px-3.5 py-2 text-[0.82rem] font-extrabold tracking-[-0.02em] text-[#2b241d] shadow-[0_10px_22px_rgba(42,31,22,0.16),inset_0_1px_0_rgba(255,255,255,0.68)]">
                      <span class="h-2 w-2 rounded-full bg-[#f8f3ec] shadow-[inset_0_0_0_1px_rgba(166,123,79,0.18)]"></span>
                      Before
                    </div>
                  </div>
                </div>

                <!-- Dotted Arrow -->
                <svg class="pointer-events-none absolute left-[95px] top-[155px] z-20 hidden h-32 w-44 text-white/95 drop-shadow-[0_3px_10px_rgba(0,0,0,0.20)] sm:block lg:left-[105px] lg:top-[160px]" viewBox="0 0 180 130" fill="none" aria-hidden="true">
                  <path d="M8 9C72 18 126 48 151 102" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-dasharray="5 7"></path>
                  <path d="M137 94L153 105L158 86" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
                </svg>

                <!-- Explore Styles Panel -->
                <aside class="premium-panel absolute right-6 top-[18.5%] z-20 w-[238px] rounded-[1.25rem] p-3.5 sm:right-7 sm:w-[246px] xl:right-8 reveal-on-scroll delay-500">
                  <div class="mb-3.5 flex items-center justify-between">
                    <h2 class="text-[0.9rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                      Explore Styles
                    </h2>

                    <span class="inline-flex h-7 w-7 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                      <i data-lucide="sparkles" class="h-3.5 w-3.5 text-[#9d7650]"></i>
                    </span>
                  </div>

                  <div class="space-y-2.5">
                    <!-- Selected Style -->
                    <button class="group flex w-full items-center gap-2.5 rounded-[10px] border border-[#ad8356] bg-[#f3eadf] p-2 text-left shadow-[0_12px_25px_rgba(115,82,50,0.12),inset_0_1px_0_rgba(255,255,255,0.7)]">
                      <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/545b052a-b0c2-4ec1-aeac-c36a8f948a5d_320w.png" alt="" class="h-[54px] w-[62px] rounded-[8px] object-cover shadow-[0_6px_14px_rgba(46,35,27,0.14)]">
                      <span class="min-w-0 flex-1 text-[0.76rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                        Editorial Luxe
                      </span>
                      <span class="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-[#a77f53] bg-[#efe1d1] text-[#8d653e] shadow-[inset_0_1px_0_rgba(255,255,255,0.7)]">
                        <i data-lucide="check" class="h-3 w-3"></i>
                      </span>
                    </button>

                    <!-- Style Option -->
                    <button class="group relative flex w-full items-center gap-2.5 overflow-hidden rounded-[10px] border border-[#e2d5c8] bg-[#f7f1e9] p-2 text-left shadow-[0_8px_18px_rgba(70,54,42,0.055),inset_0_1px_0_rgba(255,255,255,0.72)] transition duration-300 hover:-translate-y-0.5 hover:border-[#cdb8a3] hover:bg-[#faf4ed] hover:shadow-[0_12px_24px_rgba(70,54,42,0.09),inset_0_1px_0_rgba(255,255,255,0.78)]">
                      <span class="pointer-events-none absolute inset-y-2 left-0 w-[2px] rounded-full bg-[#b38a5f]/0 transition group-hover:bg-[#b38a5f]/70"></span>
                      <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/f0141fd7-e67a-4967-b6eb-a5ad3dd479e8_320w.png" alt="" class="h-[54px] w-[62px] rounded-[8px] object-cover opacity-78 saturate-[0.72] shadow-[0_5px_12px_rgba(46,35,27,0.10)] transition duration-300 group-hover:opacity-95 group-hover:saturate-[0.92]">
                      <span class="flex min-w-0 flex-1 items-center justify-between gap-2">
                        <span class="text-[0.76rem] font-extrabold tracking-[-0.025em] text-[#302922]">
                          Japandi
                        </span>
                        <span class="h-1.5 w-1.5 rounded-full bg-[#c9b9a6] transition group-hover:bg-[#a77f53]"></span>
                      </span>
                    </button>

                    <!-- Style Option -->
                    <button class="group relative flex w-full items-center gap-2.5 overflow-hidden rounded-[10px] border border-[#e2d5c8] bg-[#f7f1e9] p-2 text-left opacity-95 shadow-[0_8px_18px_rgba(70,54,42,0.045),inset_0_1px_0_rgba(255,255,255,0.72)] transition duration-300 hover:-translate-y-0.5 hover:border-[#cdb8a3] hover:bg-[#faf4ed] hover:opacity-100 hover:shadow-[0_12px_24px_rgba(70,54,42,0.09),inset_0_1px_0_rgba(255,255,255,0.78)]">
                      <span class="pointer-events-none absolute inset-y-2 left-0 w-[2px] rounded-full bg-[#b38a5f]/0 transition group-hover:bg-[#b38a5f]/70"></span>
                      <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/aaa4a07b-8f7b-407d-83bb-124126fea659_320w.png" alt="" class="h-[54px] w-[62px] rounded-[8px] object-cover opacity-68 saturate-[0.68] shadow-[0_5px_12px_rgba(46,35,27,0.10)] transition duration-300 group-hover:opacity-92 group-hover:saturate-[0.9]">
                      <span class="flex min-w-0 flex-1 items-center justify-between gap-2">
                        <span class="text-[0.76rem] font-extrabold tracking-[-0.025em] text-[#4b4036]">
                          Modern Organic
                        </span>
                        <span class="h-1.5 w-1.5 rounded-full bg-[#c9b9a6] transition group-hover:bg-[#a77f53]"></span>
                      </span>
                    </button>

                    <!-- Style Option -->
                    <button class="group relative flex w-full items-center gap-2.5 overflow-hidden rounded-[10px] border border-[#e2d5c8] bg-[#f7f1e9] p-2 text-left opacity-88 shadow-[0_8px_18px_rgba(70,54,42,0.035),inset_0_1px_0_rgba(255,255,255,0.72)] transition duration-300 hover:-translate-y-0.5 hover:border-[#cdb8a3] hover:bg-[#faf4ed] hover:opacity-100 hover:shadow-[0_12px_24px_rgba(70,54,42,0.09),inset_0_1px_0_rgba(255,255,255,0.78)]">
                      <span class="pointer-events-none absolute inset-y-2 left-0 w-[2px] rounded-full bg-[#b38a5f]/0 transition group-hover:bg-[#b38a5f]/70"></span>
                      <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/aaa4a07b-8f7b-407d-83bb-124126fea659_320w.png" alt="" class="h-[54px] w-[62px] rounded-[8px] object-cover opacity-58 saturate-[0.62] shadow-[0_5px_12px_rgba(46,35,27,0.10)] transition duration-300 group-hover:opacity-90 group-hover:saturate-[0.9]">
                      <span class="flex min-w-0 flex-1 items-center justify-between gap-2">
                        <span class="text-[0.76rem] font-extrabold tracking-[-0.025em] text-[#5a4d41]">
                          Soft Minimal
                        </span>
                        <span class="h-1.5 w-1.5 rounded-full bg-[#c9b9a6] transition group-hover:bg-[#a77f53]"></span>
                      </span>
                    </button>
                  </div>

                  <a href="#" class="mt-4 flex items-center justify-between rounded-[9px] px-1.5 py-1 text-[0.74rem] font-bold tracking-[-0.02em] text-[#75695e] transition hover:bg-[#f7f1e9] hover:text-[#1c1814]">
                    View all styles
                    <i data-lucide="chevron-right" class="h-4 w-4"></i>
                  </a>
                </aside>

                <!-- Materials Palette Overlay -->
                <div class="premium-panel absolute bottom-5 left-5 z-20 w-[min(74%,36rem)] rounded-[1.25rem] px-4 py-3.5 sm:px-5 reveal-on-scroll delay-700">
                  <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                    <div class="flex items-center gap-2.5 sm:gap-3">
                      <span class="material-dot h-[50px] w-[50px] rounded-full border border-white/60 shadow-[0_5px_12px_rgba(46,35,27,0.10),inset_0_0_0_1px_rgba(80,65,50,0.08)]"></span>
                      <span class="material-dot h-[50px] w-[50px] rounded-full border border-white/60 shadow-[0_5px_12px_rgba(46,35,27,0.10),inset_0_0_0_1px_rgba(80,65,50,0.08)]"></span>
                      <span class="material-dot h-[50px] w-[50px] rounded-full border border-white/45 shadow-[0_5px_12px_rgba(46,35,27,0.10),inset_0_0_0_1px_rgba(255,255,255,0.06)]"></span>
                      <span class="material-dot h-[50px] w-[50px] rounded-full border border-white/60 shadow-[0_5px_12px_rgba(46,35,27,0.10),inset_0_0_0_1px_rgba(80,65,50,0.08)]"></span>
                      <span class="material-dot hidden h-[50px] w-[50px] rounded-full border border-white/45 shadow-[0_5px_12px_rgba(46,35,27,0.10),inset_0_0_0_1px_rgba(80,65,50,0.08)] sm:inline-block"></span>
                      <span class="material-dot hidden h-[50px] w-[50px] rounded-full border border-white/60 shadow-[0_5px_12px_rgba(46,35,27,0.10),inset_0_0_0_1px_rgba(80,65,50,0.08)] sm:inline-block"></span>
                    </div>

                    <div class="hidden h-11 w-px bg-[#cec0b1] sm:block"></div>

                    <div class="flex min-w-[132px] items-center justify-between gap-3">
                      <div>
                        <div class="text-[0.76rem] font-extrabold tracking-[-0.02em] text-[#1d1915]">
                          AI Curated
                        </div>
                        <div class="mt-1 text-[0.72rem] font-semibold tracking-[-0.02em] text-[#74695e]">
                          Materials Palette
                        </div>
                      </div>

                      <span class="inline-flex h-7 w-7 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                        <i data-lucide="sparkles" class="h-3.5 w-3.5 text-[#9d7650]"></i>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- =========================================================
    Section 02 / Philosophy
    ========================================================== -->
      <section class="pb-16 pt-10 lg:pb-20 lg:pt-14">
        <div class="mx-auto max-w-[1510px] px-6 sm:px-8 lg:px-12 xl:px-14">
          <div class="grid items-center gap-16 lg:grid-cols-[0.92fr_1.08fr] xl:gap-20">
            <!-- =====================================================
          Philosophy / Left Content
          ====================================================== -->
            <div class="py-6 lg:py-12 reveal-on-scroll delay-300">
              <!-- Section Label -->
              <div class="mb-5 flex flex-col items-start gap-3 text-[0.95rem] font-bold tracking-[-0.02em] text-[#9a744d] reveal-on-scroll">
                <span>Our Philosophy</span>
                <span class="h-px w-12 bg-[#9f7851]"></span>
              </div>

              <!-- Section Headline -->
              <h2 class="font-display max-w-[720px] text-[3.75rem] font-normal leading-[0.98] tracking-[-0.055em] text-[#151310] sm:text-[4.75rem] md:text-[5.35rem] lg:text-[4.9rem] xl:text-[5.55rem] reveal-on-scroll delay-150">
                Beautiful spaces
                <br>
                begin with better
                <br>
                direction.
              </h2>

              <!-- Section Body Copy -->
              <p class="mt-7 max-w-[39rem] text-[1rem] font-medium leading-[1.75] tracking-[-0.025em] text-[#3a332d] sm:text-[1.06rem]">
                Atelier AI exists to bring clarity to the creative process.
                Upload your room, explore curated styles, and see polished
                concepts in minutes—so you can move from uncertainty to a vision
                you can trust.
              </p>

              <!-- Quote Card -->
              <div class="mt-10 max-w-[500px] rounded-[1.25rem] border border-[#d8c9b8] bg-[#eee5da] px-8 py-7 shadow-[0_26px_70px_rgba(42,31,22,0.14),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll delay-500">
                <div class="flex gap-5">
                  <span class="font-display -mt-3 text-[4.6rem] leading-none text-[#9d7650]">
                    “
                  </span>

                  <div>
                    <p class="font-display text-[1.82rem] font-normal leading-[1.12] tracking-[-0.045em] text-[#191511]">
                      AI should sharpen taste,
                      <br>
                      not replace it.
                    </p>

                    <p class="mt-5 text-[0.86rem] font-bold tracking-[-0.02em] text-[#9a744d]">
                      — Atelier AI
                    </p>
                  </div>
                </div>
              </div>

              <!-- Philosophy Points -->
              <div class="mt-14 w-full max-w-[760px] reveal-on-scroll delay-700">
                <div class="flex items-start">
                  <!-- Philosophy Point 01 -->
                  <div class="flex w-[235px] shrink-0 gap-2 pr-7">
                    <i data-lucide="crosshair" class="mt-0.5 h-9 w-9 shrink-0 text-[#9d7650]"></i>

                    <div>
                      <h3 class="whitespace-nowrap text-[0.98rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                        Clarity First
                      </h3>

                      <p class="mt-2 text-[0.78rem] font-semibold leading-[1.48] tracking-[-0.02em] text-[#756b60]">
                        Turn guesswork into a clear creative direction.
                      </p>
                    </div>
                  </div>

                  <!-- Divider -->
                  <div class="mx-4 h-[84px] w-px shrink-0 bg-[#d8cdc1]"></div>

                  <!-- Philosophy Point 02 -->
                  <div class="flex w-[250px] shrink-0 gap-2 px-1">
                    <i data-lucide="bookmark" class="mt-0.5 h-9 w-9 shrink-0 text-[#9d7650]"></i>

                    <div>
                      <h3 class="whitespace-nowrap text-[0.98rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                        Design, Refined
                      </h3>

                      <p class="mt-2 text-[0.78rem] font-semibold leading-[1.48] tracking-[-0.02em] text-[#756b60]">
                        Curated styles and materials, chosen with intention.
                      </p>
                    </div>
                  </div>

                  <!-- Divider -->
                  <div class="mx-4 h-[84px] w-px shrink-0 bg-[#d8cdc1]"></div>

                  <!-- Philosophy Point 03 -->
                  <div class="flex w-[255px] shrink-0 gap-2 pl-1">
                    <i data-lucide="shield-check" class="mt-0.5 h-9 w-9 shrink-0 text-[#9d7650]"></i>

                    <div>
                      <h3 class="whitespace-nowrap text-[0.98rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                        Trusted Results
                      </h3>

                      <p class="mt-2 text-[0.78rem] font-semibold leading-[1.48] tracking-[-0.02em] text-[#756b60]">
                        Beautiful, buildable ideas you can feel confident in.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- =====================================================
          Philosophy / Right Visual
          ====================================================== -->
            <div class="relative min-h-[760px] lg:min-h-[730px] xl:min-h-[740px] xl:-mr-4">
              <!-- Back Texture Slab -->
              <div class="absolute left-[22%] -top-10 z-10 h-[285px] w-[330px] overflow-hidden rounded-[13px] border border-[#e3d6c9] bg-[#d8c8b8] shadow-[0_28px_74px_rgba(62,48,37,0.16)] xl:left-[20%] reveal-on-scroll">
                <div class="h-full w-full bg-[radial-gradient(circle_at_22%_18%,rgba(255,255,255,0.62),transparent_30%),radial-gradient(circle_at_74%_72%,rgba(116,91,67,0.24),transparent_40%),linear-gradient(135deg,#e1d4c4,#b99d82_46%,#eadfce)]"></div>
              </div>

              <!-- Main Image Layer -->
              <div class="absolute left-[-8%] top-[72px] z-10 h-[520px] w-[370px] overflow-hidden rounded-[13px] border border-[#d8c9b8] bg-[#d7cabc] shadow-[0_38px_92px_rgba(49,37,28,0.24)] xl:left-[-20%] reveal-on-scroll delay-150">
                <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/545b052a-b0c2-4ec1-aeac-c36a8f948a5d_3840w.png" alt="Organic modern interior concept" class="h-full w-full object-cover object-center">
                <div class="absolute inset-0 bg-[linear-gradient(90deg,rgba(22,16,12,0.18),rgba(22,16,12,0.03)_46%,rgba(255,246,235,0.05))]"></div>
              </div>

              <!-- AI Guidance Card -->
              <div class="premium-panel absolute right-[0%] top-[58px] z-30 w-[292px] overflow-hidden rounded-[1.2rem] bg-[#eee5da] p-0 shadow-[0_30px_76px_rgba(49,37,28,0.18),inset_0_1px_0_rgba(255,255,255,0.68)] xl:right-[1%] reveal-on-scroll delay-300">
                <!-- AI Guidance Header -->
                <div class="flex items-center justify-between px-6 py-4">
                  <span class="text-[0.94rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                    AI Guidance
                  </span>

                  <span class="inline-flex h-8 w-8 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                    <i data-lucide="sparkles" class="h-4 w-4 text-[#9d7650]"></i>
                  </span>
                </div>

                <!-- AI Guidance Item 01 -->
                <div class="border-t border-[#d7c9bc] px-6 py-4">
                  <div class="flex items-center gap-4">
                    <span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                      <i data-lucide="scan-search" class="h-4 w-4 text-[#9d7650]"></i>
                    </span>

                    <div>
                      <p class="text-[0.78rem] font-extrabold tracking-[-0.02em] text-[#1c1814]">
                        Style Signals
                      </p>
                      <p class="mt-1 text-[0.72rem] font-semibold leading-[1.25] text-[#74695e]">
                        Warm minimalism
                      </p>
                    </div>
                  </div>
                </div>

                <!-- AI Guidance Item 02 -->
                <div class="border-t border-[#d7c9bc] px-6 py-4">
                  <div class="flex items-center gap-4">
                    <span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                      <i data-lucide="palette" class="h-4 w-4 text-[#9d7650]"></i>
                    </span>

                    <div>
                      <p class="text-[0.78rem] font-extrabold tracking-[-0.02em] text-[#1c1814]">
                        Palette Match
                      </p>
                      <p class="mt-1 text-[0.72rem] font-semibold leading-[1.25] text-[#74695e]">
                        Earthy neutrals
                      </p>
                    </div>
                  </div>
                </div>

                <!-- AI Guidance Item 03 -->
                <div class="border-t border-[#d7c9bc] px-6 py-4">
                  <div class="flex items-center gap-4">
                    <span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                      <i data-lucide="layout-dashboard" class="h-4 w-4 text-[#9d7650]"></i>
                    </span>

                    <div>
                      <p class="text-[0.78rem] font-extrabold tracking-[-0.02em] text-[#1c1814]">
                        Spatial Balance
                      </p>
                      <p class="mt-1 text-[0.72rem] font-semibold leading-[1.25] text-[#74695e]">
                        Open, calm, and inviting
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Material Sample Card -->
              <div class="premium-panel absolute left-[-15%] bottom-[270px] z-55 w-[190px] rounded-[1.05rem] bg-[#eee5da] p-4 shadow-[0_28px_70px_rgba(49,37,28,0.17),inset_0_1px_0_rgba(255,255,255,0.68)] xl:left-[-28%] reveal-on-scroll delay-500">
                <div class="grid grid-cols-2 gap-3">
                  <span class="h-[66px] rounded-[8px] bg-[linear-gradient(135deg,#efe6d8,#c7b49e)] shadow-[0_8px_16px_rgba(46,35,27,0.09),inset_0_1px_0_rgba(255,255,255,0.6)]"></span>
                  <span class="h-[66px] rounded-[8px] bg-[radial-gradient(circle_at_30%_20%,#eee5d8,#bfa68d)] shadow-[0_8px_16px_rgba(46,35,27,0.09),inset_0_1px_0_rgba(255,255,255,0.6)]"></span>
                  <span class="h-[66px] rounded-[8px] bg-[linear-gradient(135deg,#8a6d52,#4f3828)] shadow-[0_8px_16px_rgba(46,35,27,0.09),inset_0_1px_0_rgba(255,255,255,0.25)]"></span>
                  <span class="h-[66px] rounded-[8px] bg-[radial-gradient(circle_at_30%_20%,#343434,#101010)] shadow-[0_8px_16px_rgba(46,35,27,0.09),inset_0_1px_0_rgba(255,255,255,0.14)]"></span>
                </div>
              </div>

              <!-- Before / After Comparison Card -->
              <div class="premium-panel absolute bottom-0 right-[-10%] z-40 w-[min(100%,570px)] rounded-[1.25rem] bg-[#eee5da] p-5 shadow-[0_36px_92px_rgba(49,37,28,0.20),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll delay-700">
                <!-- Comparison Header -->
                <div class="mb-5 grid grid-cols-[1fr_auto_1fr] items-center gap-4 px-1 text-[0.88rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                  <span>Before</span>

                  <span class="inline-flex h-8 w-8 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                    <i data-lucide="arrow-right" class="h-4 w-4 text-[#9d7650]"></i>
                  </span>

                  <span>After: Organic Modern</span>
                </div>

                <!-- Comparison Images -->
                <div class="grid grid-cols-2 gap-4">
                  <div class="overflow-hidden rounded-[11px] border border-[#e2d5c8] bg-[#f7f1e9] p-1.5 shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                    <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/de7c127b-e2ce-4fbc-af38-233509c064a3_800w.png" alt="Before empty room" class="h-[220px] w-full rounded-[8px] object-cover object-center shadow-[0_12px_26px_rgba(46,35,27,0.12)]">
                  </div>

                  <div class="overflow-hidden rounded-[11px] border border-[#e2d5c8] bg-[#f7f1e9] p-1.5 shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                    <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/545b052a-b0c2-4ec1-aeac-c36a8f948a5d_3840w.png" alt="After organic modern room" class="h-[220px] w-full rounded-[8px] object-cover object-center shadow-[0_12px_26px_rgba(46,35,27,0.12)]">
                  </div>
                </div>

                <!-- Confidence Match -->
                <div class="mt-5 flex items-center gap-5 px-2 pb-0.5">
                  <span class="whitespace-nowrap text-[0.76rem] font-extrabold tracking-[-0.02em] text-[#302922]">
                    Confidence Match
                  </span>

                  <span class="h-2 flex-1 overflow-hidden rounded-full bg-[#dfd3c8] shadow-[inset_0_1px_1px_rgba(70,54,42,0.08)]">
                    <span class="block h-full w-[78%] rounded-full bg-[#9d7650]"></span>
                  </span>

                  <span class="text-[0.76rem] font-extrabold tracking-[-0.02em] text-[#302922]">
                    92%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- =========================================================
Section 03 / Style Library
========================================================== -->
      <section class="pb-16 pt-10 lg:pb-20 lg:pt-14">
        <div class="mx-auto max-w-[1510px] px-6 sm:px-8 lg:px-12 xl:px-14">
          <div class="grid items-center gap-16 lg:grid-cols-[0.88fr_1.12fr] xl:gap-20">
            <!-- =====================================================
      Style Library / Left Content
      ====================================================== -->
            <div class="py-6 lg:py-12 reveal-on-scroll delay-300">
              <!-- Section Label -->
              <div class="mb-5 flex flex-col items-start gap-3 text-[0.95rem] font-bold tracking-[-0.02em] text-[#9a744d] reveal-on-scroll">
                <span>Style Library</span>
                <span class="h-px w-12 bg-[#9f7851]"></span>
              </div>

              <!-- Section Headline -->
              <h2 class="font-display max-w-[820px] text-[3.75rem] font-normal leading-[0.98] tracking-[-0.055em] text-[#151310] sm:text-[4.75rem] md:text-[5.25rem] lg:text-[4.65rem] xl:text-[5.25rem] 2xl:text-[5.55rem] reveal-on-scroll delay-150">
                <span class="whitespace-nowrap">Explore signature</span>
                <br>
                <span class="whitespace-nowrap">design directions.</span>
              </h2>

              <!-- Section Body Copy -->
              <p class="mt-7 max-w-[34rem] text-[1rem] font-medium leading-[1.75] tracking-[-0.025em] text-[#3a332d] sm:text-[1.06rem]">
                Curated aesthetics, timeless ideas, and refined interior
                languages designed to help you find the direction that feels
                like home.
              </p>

              <!-- Text Link -->
              <a href="#" class="mt-9 inline-flex items-center gap-3 text-[0.98rem] font-extrabold tracking-[-0.02em] text-[#9a744d] transition hover:text-[#171411] reveal-on-scroll delay-500">
                View all styles
                <i data-lucide="arrow-right" class="h-4 w-4"></i>
              </a>

              <!-- Materials Palette Card -->
              <div class="premium-panel mt-14 max-w-[380px] rounded-[1.25rem] bg-[#eee5da] p-6 shadow-[0_26px_70px_rgba(42,31,22,0.13),inset_0_1px_0_rgba(255,255,255,0.68)] lg:mt-16 reveal-on-scroll delay-700">
                <p class="text-[0.92rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                  Curated Materials Palette
                </p>

                <div class="mt-7 flex items-center gap-3">
                  <span class="material-dot h-[42px] w-[42px] rounded-full border border-white/60 shadow-[0_5px_12px_rgba(46,35,27,0.10),inset_0_0_0_1px_rgba(80,65,50,0.08)]"></span>
                  <span class="material-dot h-[42px] w-[42px] rounded-full border border-white/60 shadow-[0_5px_12px_rgba(46,35,27,0.10),inset_0_0_0_1px_rgba(80,65,50,0.08)]"></span>
                  <span class="material-dot h-[42px] w-[42px] rounded-full border border-white/60 shadow-[0_5px_12px_rgba(46,35,27,0.10),inset_0_0_0_1px_rgba(80,65,50,0.08)]"></span>
                  <span class="material-dot h-[42px] w-[42px] rounded-full border border-white/45 shadow-[0_5px_12px_rgba(46,35,27,0.10),inset_0_0_0_1px_rgba(255,255,255,0.06)]"></span>
                  <span class="material-dot h-[42px] w-[42px] rounded-full border border-white/60 shadow-[0_5px_12px_rgba(46,35,27,0.10),inset_0_0_0_1px_rgba(80,65,50,0.08)]"></span>
                  <span class="hidden h-[42px] w-[42px] rounded-full border border-white/50 bg-[radial-gradient(circle_at_30%_25%,#6b5d36,#302b1c)] shadow-[0_5px_12px_rgba(46,35,27,0.10),inset_0_1px_0_rgba(255,255,255,0.16)] sm:inline-block"></span>
                </div>

                <div class="my-6 h-px w-full bg-[#d8cdc1]"></div>

                <p class="max-w-[18rem] text-[0.8rem] font-semibold leading-[1.55] tracking-[-0.02em] text-[#756b60]">
                  Natural textures, considered finishes, and tonal materials for
                  refined room concepts.
                </p>
              </div>
            </div>

            <!-- =====================================================
Style Library / Right Visual Cards
====================================================== -->
            <div class="relative">
              <div class="grid gap-5 lg:grid-cols-[1.02fr_0.98fr] xl:gap-6">
                <!-- =================================================
    Left Card Column / Two Feature Cards
    ================================================== -->
                <div class="flex flex-col gap-5">
                  <!-- Feature Card 01 / Editorial Luxe -->
                  <article class="premium-panel group overflow-hidden rounded-[1.25rem] bg-[#eee5da] shadow-[0_28px_76px_rgba(49,37,28,0.16),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll">
                    <div class="relative h-[250px] overflow-hidden border-b border-[#d8c9b8]">
                      <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/545b052a-b0c2-4ec1-aeac-c36a8f948a5d_3840w.png" alt="Editorial Luxe interior direction" class="h-full w-full object-cover object-center transition duration-700 group-hover:scale-[1.03]">
                      <div class="absolute inset-0 bg-gradient-to-t from-[#171411]/16 via-transparent to-transparent"></div>
                    </div>

                    <div class="flex items-end justify-between gap-5 p-5">
                      <div class="min-w-0">
                        <div class="flex items-center gap-3">
                          <h3 class="font-display whitespace-nowrap text-[1.78rem] font-normal leading-none tracking-[-0.045em] text-[#171411]">
                            Editorial Luxe
                          </h3>

                          <span class="rounded-full border border-[#d8c9b8] bg-[#f7efe6] px-3 py-1 text-[0.68rem] font-extrabold tracking-[-0.02em] text-[#9a744d] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                            Popular
                          </span>
                        </div>

                        <p class="mt-3 max-w-[22rem] text-[0.86rem] font-semibold leading-[1.5] tracking-[-0.02em] text-[#756b60]">
                          Refined materials, layered textures, and a sense of
                          quiet opulence.
                        </p>
                      </div>

                      <a href="#" class="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)] transition group-hover:translate-x-0.5 group-hover:border-[#ad8356]">
                        <i data-lucide="arrow-right" class="h-4 w-4"></i>
                      </a>
                    </div>
                  </article>

                  <!-- Feature Card 02 / Soft Minimal -->
                  <article class="premium-panel group overflow-hidden rounded-[1.25rem] bg-[#eee5da] shadow-[0_28px_76px_rgba(49,37,28,0.15),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll delay-150">
                    <div class="relative h-[250px] overflow-hidden border-b border-[#d8c9b8]">
                      <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/f0141fd7-e67a-4967-b6eb-a5ad3dd479e8_320w.png" alt="Soft Minimal interior direction" class="h-full w-full object-cover object-center transition duration-700 group-hover:scale-[1.03]">
                      <div class="absolute inset-0 bg-gradient-to-t from-[#171411]/10 via-transparent to-transparent"></div>
                    </div>

                    <div class="flex items-end justify-between gap-5 p-5">
                      <div>
                        <h3 class="font-display text-[1.78rem] font-normal leading-none tracking-[-0.045em] text-[#171411]">
                          Soft Minimal
                        </h3>

                        <p class="mt-3 max-w-[22rem] text-[0.86rem] font-semibold leading-[1.5] tracking-[-0.02em] text-[#756b60]">
                          Understated, serene, intentional. Beauty in
                          simplicity.
                        </p>
                      </div>

                      <a href="#" class="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)] transition group-hover:translate-x-0.5 group-hover:border-[#ad8356]">
                        <i data-lucide="arrow-right" class="h-4 w-4"></i>
                      </a>
                    </div>
                  </article>
                </div>

                <!-- =================================================
    Right Card Column / Three Compact Cards
    ================================================== -->
                <div class="flex flex-col gap-5">
                  <!-- Compact Card 01 / Japandi -->
                  <article class="premium-panel group overflow-hidden rounded-[1.15rem] bg-[#eee5da] shadow-[0_24px_64px_rgba(49,37,28,0.13),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll delay-300">
                    <div class="relative h-[145px] overflow-hidden border-b border-[#d8c9b8]">
                      <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/f0141fd7-e67a-4967-b6eb-a5ad3dd479e8_320w.png" alt="Japandi interior direction" class="h-full w-full object-cover object-center transition duration-700 group-hover:scale-[1.03]">
                    </div>

                    <div class="flex items-end justify-between gap-5 p-5">
                      <div>
                        <h3 class="font-display text-[1.45rem] font-normal leading-none tracking-[-0.045em] text-[#171411]">
                          Japandi
                        </h3>

                        <p class="mt-3 max-w-[18rem] text-[0.82rem] font-semibold leading-[1.5] tracking-[-0.02em] text-[#756b60]">
                          Japanese calm meets Scandinavian simplicity and
                          function.
                        </p>
                      </div>

                      <a href="#" class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)] transition group-hover:translate-x-0.5 group-hover:border-[#ad8356]">
                        <i data-lucide="arrow-right" class="h-4 w-4"></i>
                      </a>
                    </div>
                  </article>

                  <!-- Compact Card 02 / Modern Organic -->
                  <article class="premium-panel group overflow-hidden rounded-[1.15rem] bg-[#eee5da] shadow-[0_24px_64px_rgba(49,37,28,0.13),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll delay-500">
                    <div class="relative h-[145px] overflow-hidden border-b border-[#d8c9b8]">
                      <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/545b052a-b0c2-4ec1-aeac-c36a8f948a5d_320w.png" alt="Modern Organic interior direction" class="h-full w-full object-cover object-center transition duration-700 group-hover:scale-[1.03]">
                    </div>

                    <div class="flex items-end justify-between gap-5 p-5">
                      <div>
                        <h3 class="font-display text-[1.45rem] font-normal leading-none tracking-[-0.045em] text-[#171411]">
                          Modern Organic
                        </h3>

                        <p class="mt-3 max-w-[18rem] text-[0.82rem] font-semibold leading-[1.5] tracking-[-0.02em] text-[#756b60]">
                          Earthy materials, fluid forms, and spaces that feel
                          alive.
                        </p>
                      </div>

                      <a href="#" class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)] transition group-hover:translate-x-0.5 group-hover:border-[#ad8356]">
                        <i data-lucide="arrow-right" class="h-4 w-4"></i>
                      </a>
                    </div>
                  </article>

                  <!-- Compact Card 03 / Warm Contemporary -->
                  <article class="premium-panel group overflow-hidden rounded-[1.15rem] bg-[#eee5da] shadow-[0_24px_64px_rgba(49,37,28,0.13),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll delay-700">
                    <div class="relative h-[145px] overflow-hidden border-b border-[#d8c9b8]">
                      <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/aaa4a07b-8f7b-407d-83bb-124126fea659_320w.png" alt="Warm Contemporary interior direction" class="h-full w-full object-cover object-center transition duration-700 group-hover:scale-[1.03]">
                    </div>

                    <div class="flex items-end justify-between gap-5 p-5">
                      <div>
                        <h3 class="font-display text-[1.45rem] font-normal leading-none tracking-[-0.045em] text-[#171411]">
                          Warm Contemporary
                        </h3>

                        <p class="mt-3 max-w-[18rem] text-[0.82rem] font-semibold leading-[1.5] tracking-[-0.02em] text-[#756b60]">
                          Modern lines, warmth, and texture designed for real
                          life.
                        </p>
                      </div>

                      <a href="#" class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)] transition group-hover:translate-x-0.5 group-hover:border-[#ad8356]">
                        <i data-lucide="arrow-right" class="h-4 w-4"></i>
                      </a>
                    </div>
                  </article>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- =========================================================
Section 04 / How It Works
========================================================== -->
      <section class="pb-16 pt-10 lg:pb-24 lg:pt-14">
        <div class="mx-auto max-w-[1510px] px-6 sm:px-8 lg:px-12 xl:px-14">
          <!-- =====================================================
    How It Works / Header
    ====================================================== -->
          <div class="max-w-[760px] reveal-on-scroll delay-300">
            <!-- Section Label -->
            <div class="mb-5 flex flex-col items-start gap-3 text-[0.95rem] font-bold tracking-[-0.02em] text-[#9a744d] reveal-on-scroll">
              <span>How It Works</span>
              <span class="h-px w-12 bg-[#9f7851]"></span>
            </div>

            <!-- Section Headline -->
            <h2 class="font-display max-w-[760px] text-[3.75rem] font-normal leading-[0.98] tracking-[-0.055em] text-[#151310] sm:text-[4.75rem] md:text-[5.25rem] lg:text-[4.85rem] xl:text-[5.45rem] reveal-on-scroll delay-150">
              From room photo
              <br>
              to refined concept.
            </h2>

            <!-- Section Body Copy -->
            <p class="mt-7 max-w-[39rem] text-[1rem] font-medium leading-[1.75] tracking-[-0.025em] text-[#3a332d] sm:text-[1.06rem]">
              Atelier AI transforms your space in four simple steps—turning
              inspiration into polished, personalized designs.
            </p>
          </div>

          <!-- =====================================================
    How It Works / Step Timeline
    ====================================================== -->
          <div class="mt-12 grid gap-8 lg:grid-cols-4 lg:gap-10 reveal-on-scroll delay-500">
            <!-- Step 01 -->
            <div class="relative reveal-on-scroll">
              <div class="flex items-start gap-4">
                <span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#b8956d] bg-[#f7efe6] text-[0.78rem] font-extrabold text-[#9a744d] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                  1
                </span>

                <div>
                  <h3 class="text-[0.95rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                    Upload Your Room
                  </h3>

                  <p class="mt-3 max-w-[15.5rem] text-[0.82rem] font-semibold leading-[1.55] tracking-[-0.02em] text-[#756b60]">
                    Upload a photo of your space. Good lighting helps our AI
                    capture every detail.
                  </p>
                </div>
              </div>

              <svg class="absolute left-[calc(100%-5rem)] top-[0px] hidden h-8 w-[7rem] text-[#b8956d]/70 lg:block" viewBox="0 0 180 32" fill="none" aria-hidden="true">
                <path d="M2 16C52 16 104 16 160 16" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-dasharray="3 5"></path>
                <path d="M153 9L162 16L153 23" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"></path>
              </svg>
            </div>

            <!-- Step 02 -->
            <div class="relative reveal-on-scroll delay-150">
              <div class="flex items-start gap-4">
                <span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#b8956d] bg-[#f7efe6] text-[0.78rem] font-extrabold text-[#9a744d] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                  2
                </span>

                <div>
                  <h3 class="text-[0.95rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                    Choose a Style Direction
                  </h3>

                  <p class="mt-3 max-w-[15.5rem] text-[0.82rem] font-semibold leading-[1.55] tracking-[-0.02em] text-[#756b60]">
                    Explore curated styles and materials to shape the mood and
                    vision of your space.
                  </p>
                </div>
              </div>

              <svg class="absolute left-[calc(100%-5rem)] top-[0px] hidden h-8 w-[7rem] text-[#b8956d]/70 lg:block" viewBox="0 0 180 32" fill="none" aria-hidden="true">
                <path d="M2 16C52 16 104 16 160 16" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-dasharray="3 5"></path>
                <path d="M153 9L162 16L153 23" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"></path>
              </svg>
            </div>

            <!-- Step 03 -->
            <div class="relative reveal-on-scroll delay-300">
              <div class="flex items-start gap-4">
                <span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#b8956d] bg-[#f7efe6] text-[0.78rem] font-extrabold text-[#9a744d] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                  3
                </span>

                <div>
                  <h3 class="text-[0.95rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                    Generate Concepts
                  </h3>

                  <p class="mt-3 max-w-[15.5rem] text-[0.82rem] font-semibold leading-[1.55] tracking-[-0.02em] text-[#756b60]">
                    Our AI generates multiple high-quality concepts tailored to
                    your room and style.
                  </p>
                </div>
              </div>

              <svg class="absolute left-[calc(100%-5rem)] top-[0px] hidden h-8 w-[7rem] text-[#b8956d]/70 lg:block" viewBox="0 0 180 32" fill="none" aria-hidden="true">
                <path d="M2 16C52 16 104 16 160 16" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-dasharray="3 5"></path>
                <path d="M153 9L162 16L153 23" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"></path>
              </svg>
            </div>

            <!-- Step 04 -->
            <div>
              <div class="flex items-start gap-4">
                <span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#b8956d] bg-[#f7efe6] text-[0.78rem] font-extrabold text-[#9a744d] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                  4
                </span>

                <div>
                  <h3 class="text-[0.95rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                    Refine and Export
                  </h3>

                  <p class="mt-3 max-w-[15.5rem] text-[0.82rem] font-semibold leading-[1.55] tracking-[-0.02em] text-[#756b60]">
                    Customize details, finalize your favorite, and export in
                    high resolution.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- =====================================================
    How It Works / Product Cards
    ====================================================== -->
          <div class="mt-8 grid gap-6 lg:grid-cols-4">
            <!-- Product Card 01 / Upload -->
            <article class="premium-panel flex h-[450px] flex-col overflow-hidden rounded-[1.25rem] bg-[#eee5da] shadow-[0_28px_76px_rgba(49,37,28,0.14),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll">
              <div class="p-5">
                <h3 class="text-[0.88rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                  Upload Your Room
                </h3>

                <div class="mt-5 rounded-[0.95rem] border border-dashed border-[#d5c4b2] bg-[#f7f1e9] px-5 py-6 text-center shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                  <span class="mx-auto inline-flex h-9 w-9 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650]">
                    <i data-lucide="cloud-upload" class="h-4.5 w-4.5"></i>
                  </span>

                  <p class="mt-3 text-[0.72rem] font-semibold tracking-[-0.02em] text-[#756b60]">
                    Drag and drop or click to upload
                  </p>
                </div>
              </div>

              <div class="relative mt-auto h-[230px] overflow-hidden border-t border-[#d8c9b8]">
                <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/de7c127b-e2ce-4fbc-af38-233509c064a3_800w.png" alt="Uploaded empty room" class="h-full w-full object-cover object-center">

                <div class="absolute bottom-4 left-4 inline-flex items-center gap-2 rounded-[0.7rem] border border-[#d8c9b8] bg-[#eee5da] px-3 py-2 text-[0.72rem] font-extrabold tracking-[-0.02em] text-[#2b241d] shadow-[0_10px_22px_rgba(42,31,22,0.16),inset_0_1px_0_rgba(255,255,255,0.68)]">
                  <i data-lucide="check-circle-2" class="h-4 w-4 text-[#9d7650]"></i>
                  IMG_9421.jpg
                  <i data-lucide="chevron-down" class="h-3.5 w-3.5 text-[#9d7650]"></i>
                </div>
              </div>
            </article>

            <!-- Product Card 02 / Explore Styles -->
            <article class="premium-panel flex h-[450px] flex-col overflow-hidden rounded-[1.25rem] bg-[#eee5da] p-5 shadow-[0_28px_76px_rgba(49,37,28,0.14),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll delay-150">
              <div class="mb-4 flex items-center justify-between">
                <h3 class="text-[0.88rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                  Explore Styles
                </h3>

                <span class="inline-flex h-7 w-7 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                  <i data-lucide="sparkles" class="h-3.5 w-3.5 text-[#9d7650]"></i>
                </span>
              </div>

              <div class="space-y-3 flex-1">
                <!-- Selected Style -->
                <button class="group flex w-full items-center gap-3 rounded-[11px] border border-[#ad8356] bg-[#f3eadf] p-2 text-left shadow-[0_12px_25px_rgba(115,82,50,0.12),inset_0_1px_0_rgba(255,255,255,0.7)]">
                  <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/545b052a-b0c2-4ec1-aeac-c36a8f948a5d_320w.png" alt="" class="h-[56px] w-[68px] rounded-[8px] object-cover shadow-[0_6px_14px_rgba(46,35,27,0.14)]">

                  <span class="min-w-0 flex-1 text-[0.76rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                    Editorial Luxe
                  </span>

                  <span class="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-[#a77f53] bg-[#efe1d1] text-[#8d653e]">
                    <i data-lucide="check" class="h-3 w-3"></i>
                  </span>
                </button>

                <!-- Style Option -->
                <button class="group relative flex w-full items-center gap-3 overflow-hidden rounded-[11px] border border-[#e2d5c8] bg-[#f7f1e9] p-2 text-left shadow-[0_8px_18px_rgba(70,54,42,0.055),inset_0_1px_0_rgba(255,255,255,0.72)]">
                  <span class="pointer-events-none absolute inset-y-2 left-0 w-[2px] rounded-full bg-[#b38a5f]/0 transition group-hover:bg-[#b38a5f]/70"></span>
                  <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/f0141fd7-e67a-4967-b6eb-a5ad3dd479e8_320w.png" alt="" class="h-[56px] w-[68px] rounded-[8px] object-cover opacity-78 saturate-[0.72]">
                  <span class="text-[0.76rem] font-extrabold tracking-[-0.025em] text-[#302922]">
                    Japandi
                  </span>
                </button>

                <!-- Style Option -->
                <button class="group relative flex w-full items-center gap-3 overflow-hidden rounded-[11px] border border-[#e2d5c8] bg-[#f7f1e9] p-2 text-left shadow-[0_8px_18px_rgba(70,54,42,0.045),inset_0_1px_0_rgba(255,255,255,0.72)]">
                  <span class="pointer-events-none absolute inset-y-2 left-0 w-[2px] rounded-full bg-[#b38a5f]/0 transition group-hover:bg-[#b38a5f]/70"></span>
                  <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/aaa4a07b-8f7b-407d-83bb-124126fea659_320w.png" alt="" class="h-[56px] w-[68px] rounded-[8px] object-cover opacity-68 saturate-[0.68]">
                  <span class="text-[0.76rem] font-extrabold tracking-[-0.025em] text-[#4b4036]">
                    Modern Organic
                  </span>
                </button>

                <!-- Style Option -->
                <button class="group relative flex w-full items-center gap-3 overflow-hidden rounded-[11px] border border-[#e2d5c8] bg-[#f7f1e9] p-2 text-left shadow-[0_8px_18px_rgba(70,54,42,0.035),inset_0_1px_0_rgba(255,255,255,0.72)]">
                  <span class="pointer-events-none absolute inset-y-2 left-0 w-[2px] rounded-full bg-[#b38a5f]/0 transition group-hover:bg-[#b38a5f]/70"></span>
                  <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/f0141fd7-e67a-4967-b6eb-a5ad3dd479e8_320w.png" alt="" class="h-[56px] w-[68px] rounded-[8px] object-cover opacity-58 saturate-[0.62]">
                  <span class="text-[0.76rem] font-extrabold tracking-[-0.025em] text-[#5a4d41]">
                    Soft Minimal
                  </span>
                </button>
              </div>

              <a href="#" class="mt-5 flex items-center justify-between rounded-[9px] px-1.5 py-1 text-[0.74rem] font-bold tracking-[-0.02em] text-[#75695e] transition hover:bg-[#f7f1e9] hover:text-[#1c1814]">
                View all styles
                <i data-lucide="chevron-right" class="h-4 w-4"></i>
              </a>
            </article>

            <!-- Product Card 03 / Generate Concepts -->
            <article class="premium-panel flex h-[450px] flex-col overflow-hidden rounded-[1.25rem] bg-[#eee5da] shadow-[0_28px_76px_rgba(49,37,28,0.14),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll delay-300">
              <div class="relative min-h-0 flex-1 overflow-hidden border-b border-[#d8c9b8] bg-[#d7cabc]">
                <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/545b052a-b0c2-4ec1-aeac-c36a8f948a5d_3840w.png" alt="Generated room concept" class="h-full w-full object-cover object-center">

                <span class="absolute left-3 top-3 rounded-[0.7rem] border border-[#d8c9b8] bg-[#eee5da] px-3 py-2 text-[0.72rem] font-extrabold tracking-[-0.02em] text-[#2b241d] shadow-[0_10px_22px_rgba(42,31,22,0.16),inset_0_1px_0_rgba(255,255,255,0.68)]">
                  Concept 01
                </span>

                <button class="absolute left-3 top-1/2 inline-flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650] shadow-[0_10px_22px_rgba(42,31,22,0.16),inset_0_1px_0_rgba(255,255,255,0.72)]">
                  <i data-lucide="chevron-left" class="h-4 w-4"></i>
                </button>

                <button class="absolute right-3 top-1/2 inline-flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650] shadow-[0_10px_22px_rgba(42,31,22,0.16),inset_0_1px_0_rgba(255,255,255,0.72)]">
                  <i data-lucide="chevron-right" class="h-4 w-4"></i>
                </button>

                <div class="absolute bottom-4 left-1/2 flex -translate-x-1/2 items-center gap-1.5">
                  <span class="h-2 w-2 rounded-full bg-white"></span>
                  <span class="h-2 w-2 rounded-full bg-white/55"></span>
                  <span class="h-2 w-2 rounded-full bg-white/55"></span>
                  <span class="h-2 w-2 rounded-full bg-white/55"></span>
                  <span class="h-2 w-2 rounded-full bg-white/55"></span>
                </div>
              </div>

              <div class="mt-4 grid grid-cols-3 gap-2.5 px-4 pb-4">
                <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/545b052a-b0c2-4ec1-aeac-c36a8f948a5d_320w.png" alt="" class="h-[66px] w-full rounded-[0.65rem] border border-[#ad8356] object-cover shadow-[0_8px_18px_rgba(70,54,42,0.08)]">
                <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/aaa4a07b-8f7b-407d-83bb-124126fea659_320w.png" alt="" class="h-[66px] w-full rounded-[0.65rem] border border-[#e2d5c8] object-cover shadow-[0_8px_18px_rgba(70,54,42,0.05)]">
                <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/f0141fd7-e67a-4967-b6eb-a5ad3dd479e8_320w.png" alt="" class="h-[66px] w-full rounded-[0.65rem] border border-[#e2d5c8] object-cover shadow-[0_8px_18px_rgba(70,54,42,0.05)]">
              </div>
            </article>

            <!-- Product Card 04 / Refine and Export -->
            <article class="premium-panel flex h-[450px] flex-col overflow-hidden rounded-[1.25rem] bg-[#eee5da] shadow-[0_28px_76px_rgba(49,37,28,0.14),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll delay-500">
              <div class="flex items-center justify-between border-b border-[#d8c9b8] px-5 py-4">
                <button class="inline-flex items-center gap-2 rounded-[0.7rem] border border-[#e2d5c8] bg-[#f7f1e9] px-3 py-2 text-[0.72rem] font-extrabold tracking-[-0.02em] text-[#302922] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                  Final Concept
                  <i data-lucide="chevron-down" class="h-3.5 w-3.5 text-[#9d7650]"></i>
                </button>

                <button class="inline-flex items-center gap-2 rounded-[0.7rem] border border-[#ad8356] bg-[#f7efe6] px-3 py-2 text-[0.72rem] font-extrabold tracking-[-0.02em] text-[#9a744d] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                  <i data-lucide="upload" class="h-3.5 w-3.5"></i>
                  Share
                </button>
              </div>

              <div class="relative min-h-0 flex-1 overflow-hidden">
                <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/545b052a-b0c2-4ec1-aeac-c36a8f948a5d_3840w.png" alt="Final exported concept" class="h-full w-full object-cover object-center">

                <div class="premium-panel absolute bottom-5 right-5 w-[180px] rounded-[1rem] bg-[#eee5da] p-4 shadow-[0_24px_64px_rgba(49,37,28,0.20),inset_0_1px_0_rgba(255,255,255,0.68)]">
                  <p class="text-[0.76rem] font-extrabold tracking-[-0.02em] text-[#1c1814]">
                    Export Options
                  </p>

                  <div class="mt-4 space-y-2.5">
                    <button class="flex w-full items-center justify-between rounded-[0.65rem] border border-[#e2d5c8] bg-[#f7f1e9] px-3 py-2 text-[0.68rem] font-bold text-[#756b60]">
                      High Resolution
                      <i data-lucide="chevron-down" class="h-3.5 w-3.5"></i>
                    </button>

                    <button class="flex w-full items-center justify-between rounded-[0.65rem] border border-[#e2d5c8] bg-[#f7f1e9] px-3 py-2 text-[0.68rem] font-bold text-[#756b60]">
                      PDF Presentation
                      <i data-lucide="chevron-down" class="h-3.5 w-3.5"></i>
                    </button>

                    <button class="mt-1 inline-flex h-10 w-full items-center justify-center gap-2 rounded-[0.75rem] bg-[#171614] text-[0.72rem] font-extrabold tracking-[-0.02em] text-white shadow-[0_18px_42px_rgba(25,21,18,0.18)]">
                      <i data-lucide="download" class="h-3.5 w-3.5"></i>
                      Export Image
                    </button>
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-4 gap-3 border-t border-[#d8c9b8] bg-[#eee5da] px-6 py-4">
                <button class="mx-auto inline-flex h-9 w-9 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650]">
                  <i data-lucide="heart" class="h-4 w-4"></i>
                </button>
                <button class="mx-auto inline-flex h-9 w-9 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650]">
                  <i data-lucide="folder" class="h-4 w-4"></i>
                </button>
                <button class="mx-auto inline-flex h-9 w-9 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650]">
                  <i data-lucide="bookmark" class="h-4 w-4"></i>
                </button>
                <button class="mx-auto inline-flex h-9 w-9 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650]">
                  <i data-lucide="ellipsis" class="h-4 w-4"></i>
                </button>
              </div>
            </article>
          </div>

          <!-- =====================================================
    How It Works / Privacy Banner
    ====================================================== -->
          <div class="mx-auto mt-12 max-w-[920px] rounded-[1rem] border border-[#d8c9b8] bg-[#eee5da] px-6 py-4 shadow-[0_18px_46px_rgba(49,37,28,0.10),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll delay-700">
            <div class="flex flex-col items-start gap-3 text-[0.9rem] font-semibold tracking-[-0.02em] text-[#756b60] sm:flex-row sm:items-center sm:justify-center sm:gap-6">
              <div class="flex items-center gap-3 text-[#1c1814]">
                <i data-lucide="shield-check" class="h-6 w-6 text-[#9d7650]"></i>
                <span class="font-extrabold">Your privacy, our priority</span>
              </div>

              <span class="hidden h-6 w-px bg-[#d8cdc1] sm:block"></span>

              <span>
                Your images are secure and never shared. We use them only to
                generate your designs.
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- =========================================================
Section 05 / AI Intelligence
========================================================== -->
      <section class="pb-16 pt-10 lg:pb-24 lg:pt-14">
        <div class="mx-auto max-w-[1510px] px-6 sm:px-8 lg:px-12 xl:px-14">
          <div class="grid items-center gap-14 lg:grid-cols-[0.72fr_1.28fr] xl:gap-18">
            <!-- =====================================================
      AI Intelligence / Left Content
      ====================================================== -->
            <div class="py-6 lg:py-12 reveal-on-scroll delay-300">
              <!-- Section Label -->
              <div class="mb-5 flex flex-col items-start gap-3 text-[0.95rem] font-bold tracking-[-0.02em] text-[#9a744d] reveal-on-scroll">
                <span>AI Intelligence</span>
                <span class="h-px w-12 bg-[#9f7851]"></span>
              </div>

              <!-- Section Headline -->
              <h2 class="font-display max-w-[720px] text-[3.75rem] font-normal leading-[0.98] tracking-[-0.055em] text-[#151310] sm:text-[4.75rem] md:text-[5.25rem] lg:text-[4.65rem] xl:text-[5.2rem] 2xl:text-[5.45rem] reveal-on-scroll delay-150">
                <span class="whitespace-nowrap">Intelligence</span>
                <br>
                <span class="whitespace-nowrap">behind every</span>
                <br>
                <span class="whitespace-nowrap">design concept.</span>
              </h2>

              <!-- Section Body Copy -->
              <p class="mt-8 max-w-[35rem] text-[1rem] font-medium leading-[1.75] tracking-[-0.025em] text-[#3a332d] sm:text-[1.06rem]">
                Atelier AI reads your room, interprets your style intent,
                curates materials, and proposes spatial improvements —
                instantly.
              </p>

              <!-- Intelligence Points -->
              <div class="mt-9 space-y-5 reveal-on-scroll delay-500">
                <div class="flex items-center gap-4">
                  <span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                    <i data-lucide="scan-search" class="h-4 w-4"></i>
                  </span>
                  <span class="text-[0.95rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                    Understands your space
                  </span>
                </div>

                <div class="flex items-center gap-4">
                  <span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                    <i data-lucide="palette" class="h-4 w-4"></i>
                  </span>
                  <span class="text-[0.95rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                    Matches your style
                  </span>
                </div>

                <div class="flex items-center gap-4">
                  <span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                    <i data-lucide="clipboard-check" class="h-4 w-4"></i>
                  </span>
                  <span class="text-[0.95rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                    Curates with intention
                  </span>
                </div>

                <div class="flex items-center gap-4">
                  <span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                    <i data-lucide="sparkles" class="h-4 w-4"></i>
                  </span>
                  <span class="text-[0.95rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                    Optimizes every detail
                  </span>
                </div>
              </div>
            </div>

            <!-- =====================================================
AI Intelligence / Right Visual
====================================================== -->
            <div class="relative">
              <div class="grid items-stretch gap-0 lg:grid-cols-[1fr_315px]">
                <!-- Before / After Slider -->
                <div class="premium-panel relative h-[700px] overflow-hidden rounded-l-[1.35rem] rounded-r-none bg-[#d7cabc] shadow-[0_34px_90px_rgba(71,56,42,0.18)] reveal-on-scroll">
                  <!-- Slider Root -->
                  <div class="ai-slider relative h-full w-full overflow-hidden" data-slider="">
                    <!-- After Image -->
                    <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/545b052a-b0c2-4ec1-aeac-c36a8f948a5d_3840w.png" alt="AI generated interior concept" class="absolute inset-0 h-full w-full object-cover object-center">

                    <!-- Before Image Clip -->
                    <div class="ai-slider-before absolute inset-0 overflow-hidden" data-before="" style="clip-path: inset(0 50% 0 0);">
                      <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/de7c127b-e2ce-4fbc-af38-233509c064a3_800w.png" alt="Original room before AI concept" class="absolute inset-0 h-full w-full object-cover object-center">
                    </div>

                    <!-- Split Line -->
                    <div class="ai-slider-line absolute inset-y-0 left-1/2 z-20 w-px -translate-x-1/2 bg-white/80 shadow-[0_0_18px_rgba(0,0,0,0.22)]" data-line=""></div>

                    <!-- Drag Handle -->
                    <button type="button" class="ai-slider-handle absolute left-1/2 top-1/2 z-30 inline-flex h-14 w-14 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-white/70 bg-[#f7efe6] text-[#9d7650] shadow-[0_18px_48px_rgba(35,27,20,0.24),inset_0_1px_0_rgba(255,255,255,0.72)]" data-handle="" aria-label="Drag to compare before and AI concept">
                      <i data-lucide="chevrons-left-right" class="h-5 w-5"></i>
                    </button>

                    <!-- Before Label -->
                    <div class="absolute left-5 top-5 z-30 rounded-[0.7rem] border border-white/30 bg-[#171614]/55 px-4 py-2 text-[0.78rem] font-extrabold tracking-[-0.02em] text-white shadow-[0_12px_28px_rgba(0,0,0,0.18)] backdrop-blur-sm">
                      Before
                    </div>

                    <!-- AI Concept Label -->
                    <div class="absolute right-5 top-5 z-30 rounded-[0.7rem] border border-[#d8c9b8] bg-[#eee5da] px-4 py-2 text-[0.78rem] font-extrabold tracking-[-0.02em] text-[#1c1814] shadow-[0_12px_28px_rgba(49,37,28,0.16),inset_0_1px_0_rgba(255,255,255,0.68)]">
                      AI Concept
                    </div>

                    <!-- Bottom Caption Bar -->
                    <div class="absolute inset-x-6 bottom-5 z-30 flex items-center justify-between rounded-[0.95rem] border border-[#d8c9b8] bg-[#eee5da] px-5 py-4 text-[0.78rem] font-extrabold tracking-[-0.02em] text-[#2b241d] shadow-[0_18px_42px_rgba(42,31,22,0.18),inset_0_1px_0_rgba(255,255,255,0.68)]">
                      <span class="inline-flex items-center gap-2 whitespace-nowrap">
                        Warm Minimal
                      </span>

                      <span class="hidden sm:inline-flex items-center gap-2 text-[#5f554c]">
                        Improved flow
                        <span class="h-1 w-1 rounded-full bg-[#b89a78]"></span>
                        Natural light
                        <span class="h-1 w-1 rounded-full bg-[#b89a78]"></span>
                        Textural balance
                      </span>
                    </div>
                  </div>
                </div>

                <!-- AI Analysis Panel -->
                <aside class="relative z-30 flex h-[700px] flex-col rounded-r-[1.35rem] bg-[#171614] px-5 pb-5 pt-5 text-white shadow-[0_34px_90px_rgba(20,16,12,0.30)] reveal-on-scroll delay-150">
                  <!-- Panel Header -->
                  <div class="mb-5 flex items-center justify-between">
                    <h3 class="text-[1rem] font-extrabold tracking-[-0.025em] text-white">
                      Atelier AI Analysis
                    </h3>

                    <span class="inline-flex h-8 w-8 items-center justify-center rounded-full border border-white/12 bg-white/6 text-[#caa57c]">
                      <i data-lucide="sparkles" class="h-4 w-4"></i>
                    </span>
                  </div>

                  <!-- Analysis Items -->
                  <div class="space-y-3">
                    <!-- Analysis Item 01 -->
                    <div class="rounded-[0.9rem] border border-white/10 bg-white/[0.065] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
                      <div class="flex items-center gap-3">
                        <i data-lucide="scan-line" class="h-6 w-6 shrink-0 text-[#caa57c]"></i>

                        <div class="min-w-0 flex-1">
                          <p class="text-[0.82rem] font-extrabold tracking-[-0.02em] text-white">
                            Room Scan
                          </p>
                          <p class="mt-1 text-[0.7rem] font-semibold text-white/62">
                            21.4 m² · Natural Light: Good
                          </p>
                        </div>

                        <i data-lucide="check-circle-2" class="h-5 w-5 shrink-0 text-[#caa57c]"></i>
                      </div>
                    </div>

                    <!-- Analysis Item 02 -->
                    <div class="rounded-[0.9rem] border border-white/10 bg-white/[0.065] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
                      <div class="flex items-center gap-3">
                        <i data-lucide="blend" class="h-6 w-6 shrink-0 text-[#caa57c]"></i>

                        <div class="min-w-0 flex-1">
                          <p class="text-[0.82rem] font-extrabold tracking-[-0.02em] text-white">
                            Style Match
                          </p>
                          <p class="mt-1 text-[0.7rem] font-semibold text-white/62">
                            Warm Minimal · 92% Match
                          </p>
                        </div>

                        <i data-lucide="check-circle-2" class="h-5 w-5 shrink-0 text-[#caa57c]"></i>
                      </div>
                    </div>

                    <!-- Analysis Item 03 -->
                    <div class="rounded-[0.9rem] border border-white/10 bg-white/[0.065] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
                      <div class="flex items-center gap-3">
                        <i data-lucide="sparkles" class="h-6 w-6 shrink-0 text-[#caa57c]"></i>

                        <div class="min-w-0 flex-1">
                          <p class="text-[0.82rem] font-extrabold tracking-[-0.02em] text-white">
                            Materials Palette
                          </p>

                          <div class="mt-2 flex items-center gap-1.5">
                            <span class="h-6 w-6 rounded-full border border-white/30 bg-[#ddd7cd]"></span>
                            <span class="h-6 w-6 rounded-full border border-white/30 bg-[#a8784d]"></span>
                            <span class="h-6 w-6 rounded-full border border-white/30 bg-[#252729]"></span>
                            <span class="h-6 w-6 rounded-full border border-white/30 bg-[#d2cabd]"></span>
                            <span class="h-6 w-6 rounded-full border border-white/30 bg-[#8b8379]"></span>
                          </div>
                        </div>

                        <i data-lucide="check-circle-2" class="h-5 w-5 shrink-0 text-[#caa57c]"></i>
                      </div>
                    </div>

                    <!-- Analysis Item 04 -->
                    <div class="rounded-[0.9rem] border border-white/10 bg-white/[0.065] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
                      <div class="flex items-center gap-3">
                        <i data-lucide="lightbulb" class="h-6 w-6 shrink-0 text-[#caa57c]"></i>

                        <div class="min-w-0 flex-1">
                          <p class="text-[0.82rem] font-extrabold tracking-[-0.02em] text-white">
                            Lighting Analysis
                          </p>
                          <p class="mt-1 text-[0.7rem] font-semibold text-white/62">
                            Recommend: Layered Warm
                          </p>
                        </div>

                        <i data-lucide="check-circle-2" class="h-5 w-5 shrink-0 text-[#caa57c]"></i>
                      </div>
                    </div>

                    <!-- Analysis Item 05 -->
                    <div class="rounded-[0.9rem] border border-white/10 bg-white/[0.065] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
                      <div class="flex items-center gap-3">
                        <i data-lucide="sofa" class="h-6 w-6 shrink-0 text-[#caa57c]"></i>

                        <div class="min-w-0 flex-1">
                          <p class="text-[0.82rem] font-extrabold tracking-[-0.02em] text-white">
                            Furniture Zoning
                          </p>
                          <p class="mt-1 text-[0.7rem] font-semibold text-white/62">
                            Flow Score: 94 / 100
                          </p>
                        </div>

                        <i data-lucide="check-circle-2" class="h-5 w-5 shrink-0 text-[#caa57c]"></i>
                      </div>
                    </div>

                    <!-- Analysis Item 06 -->
                    <div class="rounded-[0.9rem] border border-white/10 bg-white/[0.065] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
                      <div class="flex items-center gap-3">
                        <i data-lucide="wallet-cards" class="h-6 w-6 shrink-0 text-[#caa57c]"></i>

                        <div class="min-w-0 flex-1">
                          <p class="text-[0.82rem] font-extrabold tracking-[-0.02em] text-white">
                            Budget Range
                          </p>
                          <p class="mt-1 text-[0.7rem] font-semibold text-white/62">
                            Estimated: $8,200 - $11,400
                          </p>
                        </div>

                        <i data-lucide="check-circle-2" class="h-5 w-5 shrink-0 text-[#caa57c]"></i>
                      </div>
                    </div>
                  </div>

                  <!-- Report CTA -->
                  <div class="mt-auto pt-5">
                    <a href="#" class="inline-flex w-full items-center justify-center gap-3 rounded-[0.95rem] bg-[#f7efe6] px-5 py-4 text-[0.86rem] font-extrabold tracking-[-0.02em] text-[#171411] shadow-[0_18px_42px_rgba(0,0,0,0.24),inset_0_1px_0_rgba(255,255,255,0.72)] transition hover:bg-white">
                      View Full Report
                      <i data-lucide="arrow-right" class="h-4 w-4"></i>
                    </a>
                  </div>
                </aside>
              </div>
            </div>
          </div>

          <!-- =====================================================
    AI Intelligence / Bottom Trust Bar
    ====================================================== -->
          <div class="premium-panel mt-10 rounded-[1.15rem] bg-[#eee5da] px-8 py-6 shadow-[0_24px_64px_rgba(49,37,28,0.12),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll delay-700">
            <div class="grid gap-8 sm:grid-cols-2 lg:grid-cols-[1fr_auto_1fr_auto_1fr_auto_1fr] lg:items-center">
              <!-- Trust Item 01 -->
              <div class="flex items-center gap-4">
                <i data-lucide="database" class="h-9 w-9 shrink-0 text-[#9d7650]"></i>
                <p class="text-[0.92rem] font-semibold leading-[1.35] tracking-[-0.02em] text-[#3a332d]">
                  Trained on millions
                  <br class="hidden xl:block">
                  of real interiors
                </p>
              </div>

              <div class="hidden h-12 w-px bg-[#d8cdc1] lg:block"></div>

              <!-- Trust Item 02 -->
              <div class="flex items-center gap-4">
                <i data-lucide="sparkles" class="h-9 w-9 shrink-0 text-[#9d7650]"></i>
                <p class="text-[0.92rem] font-semibold leading-[1.35] tracking-[-0.02em] text-[#3a332d]">
                  Design logic meets
                  <br class="hidden xl:block">
                  artificial intelligence
                </p>
              </div>

              <div class="hidden h-12 w-px bg-[#d8cdc1] lg:block"></div>

              <!-- Trust Item 03 -->
              <div class="flex items-center gap-4">
                <i data-lucide="refresh-cw" class="h-9 w-9 shrink-0 text-[#9d7650]"></i>
                <p class="text-[0.92rem] font-semibold leading-[1.35] tracking-[-0.02em] text-[#3a332d]">
                  Continuously learning
                  <br class="hidden xl:block">
                  and improving
                </p>
              </div>

              <div class="hidden h-12 w-px bg-[#d8cdc1] lg:block"></div>

              <!-- Trust Item 04 -->
              <div class="flex items-center gap-4">
                <i data-lucide="user-round" class="h-9 w-9 shrink-0 text-[#9d7650]"></i>
                <p class="text-[0.92rem] font-semibold leading-[1.35] tracking-[-0.02em] text-[#3a332d]">
                  Your vision,
                  <br class="hidden xl:block">
                  intelligently realized
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- =========================================================
Section 06 / Pricing
========================================================== -->
      <section class="pb-16 pt-10 lg:pb-24 lg:pt-14">
        <div class="mx-auto max-w-[1510px] px-6 sm:px-8 lg:px-12 xl:px-14">
          <div class="grid items-start gap-12 lg:grid-cols-[0.52fr_1.48fr] xl:gap-16">
            <!-- =====================================================
      Pricing / Left Content
      ====================================================== -->
            <div class="py-6 lg:py-12 reveal-on-scroll delay-300">
              <!-- Section Label -->
              <div class="mb-5 flex flex-col items-start gap-3 text-[0.95rem] font-bold tracking-[-0.02em] text-[#9a744d] reveal-on-scroll">
                <span>Pricing</span>
                <span class="h-px w-12 bg-[#9f7851]"></span>
              </div>

              <!-- Section Headline -->
              <h2 class="font-display max-w-[520px] text-[3.35rem] font-normal leading-[0.98] tracking-[-0.055em] text-[#151310] sm:text-[4.2rem] md:text-[4.65rem] lg:text-[3.85rem] xl:text-[4.35rem] 2xl:text-[4.65rem] reveal-on-scroll delay-150">
                <span class="whitespace-nowrap">Choose the plan</span>
                <br>
                <span class="whitespace-nowrap">that fits your</span>
                <br>
                <span class="whitespace-nowrap">next project.</span>
              </h2>

              <!-- Section Body Copy -->
              <p class="mt-8 max-w-[29rem] text-[1rem] font-medium leading-[1.75] tracking-[-0.025em] text-[#3a332d] sm:text-[1.06rem]">
                From personal makeovers to full-scale projects, pick the plan
                that gives you the right tools, credits, and support.
              </p>
            </div>

            <!-- =====================================================
      Pricing / Right Content
      ====================================================== -->
            <div class="relative reveal-on-scroll delay-500">
              <!-- Billing Toggle -->
              <div class="mb-14 flex flex-col items-center justify-center gap-3 reveal-on-scroll delay-150">
                <div class="premium-panel inline-flex rounded-[0.95rem] bg-[#eee5da] p-1.5 shadow-[0_18px_46px_rgba(49,37,28,0.11),inset_0_1px_0_rgba(255,255,255,0.68)]">
                  <button class="inline-flex h-11 items-center justify-center rounded-[0.75rem] px-8 text-[0.9rem] font-extrabold tracking-[-0.02em] text-[#6f6257] transition hover:text-[#171411]">
                    Monthly
                  </button>

                  <button class="inline-flex h-11 items-center justify-center rounded-[0.75rem] bg-[#171614] px-8 text-[0.9rem] font-extrabold tracking-[-0.02em] text-white shadow-[0_14px_30px_rgba(25,21,18,0.18)]">
                    Annual
                  </button>
                </div>

                <div class="inline-flex items-center gap-2 rounded-full border border-[#d8c9b8] bg-[#f3eadf] px-4 py-2 text-[0.76rem] font-extrabold tracking-[-0.02em] text-[#9a744d] shadow-[0_12px_28px_rgba(70,54,42,0.08),inset_0_1px_0_rgba(255,255,255,0.72)]">
                  <i data-lucide="sparkles" class="h-3.5 w-3.5"></i>
                  Save up to 20%
                </div>
              </div>

              <!-- Pricing Cards -->
              <div class="grid items-stretch gap-5 lg:grid-cols-3 xl:gap-6">
                <!-- =================================================
          Plan Card / Home
          ================================================== -->
                <article class="premium-panel flex min-h-[720px] flex-col rounded-[1.35rem] bg-[#eee5da] p-7 shadow-[0_28px_76px_rgba(49,37,28,0.13),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll">
                  <h3 class="font-display text-[2.15rem] font-normal leading-none tracking-[-0.055em] text-[#171411]">
                    Home
                  </h3>

                  <!-- Plan Image -->
                  <div class="mt-7 overflow-hidden rounded-[1rem] border border-[#d8c9b8] bg-[#d7cabc] shadow-[0_16px_36px_rgba(49,37,28,0.12)]">
                    <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/f0141fd7-e67a-4967-b6eb-a5ad3dd479e8_320w.png" alt="Home plan interior preview" class="h-[128px] w-full object-cover object-center">

                    <div class="flex items-center justify-center gap-2 bg-[#eee5da] px-3 py-3">
                      <span class="material-dot h-8 w-8 rounded-full border border-white/60 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                      <span class="material-dot h-8 w-8 rounded-full border border-white/60 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                      <span class="material-dot h-8 w-8 rounded-full border border-white/60 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                      <span class="material-dot h-8 w-8 rounded-full border border-white/45 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                      <span class="material-dot h-8 w-8 rounded-full border border-white/45 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                    </div>
                  </div>

                  <p class="mt-6 min-h-[3.5rem] text-[0.88rem] font-semibold leading-[1.55] tracking-[-0.02em] text-[#756b60]">
                    Perfect for personal projects and single-room
                    transformations.
                  </p>

                  <div class="mt-5">
                    <div class="flex items-end gap-1.5">
                      <span class="font-display text-[2.65rem] font-normal leading-none tracking-[-0.055em] text-[#171411]">
                        $19
                      </span>
                      <span class="mb-1 text-[0.88rem] font-extrabold tracking-[-0.02em] text-[#171411]">
                        /mo
                      </span>
                    </div>

                    <p class="mt-2 text-[0.78rem] font-semibold tracking-[-0.02em] text-[#756b60]">
                      Billed annually
                      <span class="ml-1 text-[#9b8f82] line-through">$228</span>
                      <span class="ml-1 font-extrabold text-[#9a744d]">
                        $156
                      </span>
                    </p>
                  </div>

                  <div class="my-6 h-px w-full bg-[#d8cdc1]"></div>

                  <ul class="space-y-3.5">
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      20 AI renders / month
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      10 style explorations / month
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      High-resolution exports
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      Custom material palette
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      Standard support
                    </li>
                  </ul>

                  <a href="#" class="mt-auto inline-flex w-full items-center justify-center rounded-[0.8rem] border border-[#bfa994] bg-[#f7efe6] px-5 py-4 text-[0.88rem] font-extrabold tracking-[-0.02em] text-[#171411] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)] transition hover:border-[#9d7650] hover:bg-white">
                    Start with Home
                  </a>
                </article>

                <!-- =================================================
          Plan Card / Studio
          ================================================== -->
                <article class="premium-panel relative flex min-h-[720px] -translate-y-5 flex-col rounded-[1.35rem] border-[#ad8356] bg-[#eee5da] p-7 shadow-[0_40px_100px_rgba(93,63,35,0.20),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll delay-150">
                  <!-- Popular Badge -->
                  <div class="absolute left-1/2 top-0 min-w-[170px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#ad8356] bg-[#a77f53] px-7 py-2 text-center text-[0.75rem] font-extrabold uppercase tracking-[0.04em] text-white shadow-[0_16px_36px_rgba(93,63,35,0.20)] whitespace-nowrap">
                    Most Popular
                  </div>

                  <h3 class="font-display text-[2.15rem] font-normal leading-none tracking-[-0.055em] text-[#171411]">
                    Studio
                  </h3>

                  <!-- Plan Image -->
                  <div class="mt-7 overflow-hidden rounded-[1rem] border border-[#d8c9b8] bg-[#d7cabc] shadow-[0_16px_36px_rgba(49,37,28,0.12)]">
                    <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/545b052a-b0c2-4ec1-aeac-c36a8f948a5d_320w.png" alt="Studio plan interior preview" class="h-[128px] w-full object-cover object-center">

                    <div class="flex items-center justify-center gap-2 bg-[#eee5da] px-3 py-3">
                      <span class="material-dot h-8 w-8 rounded-full border border-white/60 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                      <span class="material-dot h-8 w-8 rounded-full border border-white/60 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                      <span class="material-dot h-8 w-8 rounded-full border border-white/60 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                      <span class="material-dot h-8 w-8 rounded-full border border-white/45 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                      <span class="material-dot h-8 w-8 rounded-full border border-white/45 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                    </div>
                  </div>

                  <p class="mt-6 min-h-[3.5rem] text-[0.88rem] font-semibold leading-[1.55] tracking-[-0.02em] text-[#756b60]">
                    Ideal for designers and makers managing multiple client
                    spaces.
                  </p>

                  <div class="mt-5">
                    <div class="flex items-end gap-1.5">
                      <span class="font-display text-[2.65rem] font-normal leading-none tracking-[-0.055em] text-[#171411]">
                        $49
                      </span>
                      <span class="mb-1 text-[0.88rem] font-extrabold tracking-[-0.02em] text-[#171411]">
                        /mo
                      </span>
                    </div>

                    <p class="mt-2 text-[0.78rem] font-semibold tracking-[-0.02em] text-[#756b60]">
                      Billed annually
                      <span class="ml-1 text-[#9b8f82] line-through">$588</span>
                      <span class="ml-1 font-extrabold text-[#9a744d]">
                        $468
                      </span>
                    </p>
                  </div>

                  <div class="my-6 h-px w-full bg-[#d8cdc1]"></div>

                  <ul class="space-y-3.5">
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      60 AI renders / month
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      Unlimited style explorations
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      High-resolution exports
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      Custom material palette
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      Project folders &amp; organization
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      Priority support
                    </li>
                  </ul>

                  <a href="#" class="mt-auto inline-flex w-full items-center justify-center rounded-[0.8rem] bg-[#171614] px-5 py-4 text-[0.88rem] font-extrabold tracking-[-0.02em] text-white shadow-[0_18px_42px_rgba(25,21,18,0.18)] transition hover:bg-[#29231f]">
                    Start with Studio
                  </a>
                </article>

                <!-- =================================================
          Plan Card / Pro
          ================================================== -->
                <article class="premium-panel flex min-h-[720px] flex-col rounded-[1.35rem] bg-[#eee5da] p-7 shadow-[0_28px_76px_rgba(49,37,28,0.13),inset_0_1px_0_rgba(255,255,255,0.68)] reveal-on-scroll delay-300">
                  <h3 class="font-display text-[2.15rem] font-normal leading-none tracking-[-0.055em] text-[#171411]">
                    Pro
                  </h3>

                  <!-- Plan Image -->
                  <div class="mt-7 overflow-hidden rounded-[1rem] border border-[#d8c9b8] bg-[#d7cabc] shadow-[0_16px_36px_rgba(49,37,28,0.12)]">
                    <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/aaa4a07b-8f7b-407d-83bb-124126fea659_320w.png" alt="Pro plan interior preview" class="h-[128px] w-full object-cover object-center">

                    <div class="flex items-center justify-center gap-2 bg-[#eee5da] px-3 py-3">
                      <span class="material-dot h-8 w-8 rounded-full border border-white/60 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                      <span class="material-dot h-8 w-8 rounded-full border border-white/60 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                      <span class="material-dot h-8 w-8 rounded-full border border-white/60 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                      <span class="material-dot h-8 w-8 rounded-full border border-white/45 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                      <span class="material-dot h-8 w-8 rounded-full border border-white/45 shadow-[0_4px_10px_rgba(46,35,27,0.10)]"></span>
                    </div>
                  </div>

                  <p class="mt-6 min-h-[3.5rem] text-[0.88rem] font-semibold leading-[1.55] tracking-[-0.02em] text-[#756b60]">
                    Built for professionals and teams delivering at scale.
                  </p>

                  <div class="mt-5">
                    <div class="flex items-end gap-1.5">
                      <span class="font-display text-[2.65rem] font-normal leading-none tracking-[-0.055em] text-[#171411]">
                        $99
                      </span>
                      <span class="mb-1 text-[0.88rem] font-extrabold tracking-[-0.02em] text-[#171411]">
                        /mo
                      </span>
                    </div>

                    <p class="mt-2 text-[0.78rem] font-semibold tracking-[-0.02em] text-[#756b60]">
                      Billed annually
                      <span class="ml-1 text-[#9b8f82] line-through">
                        $1,188
                      </span>
                      <span class="ml-1 font-extrabold text-[#9a744d]">
                        $948
                      </span>
                    </p>
                  </div>

                  <div class="my-6 h-px w-full bg-[#d8cdc1]"></div>

                  <ul class="space-y-3.5 pb-6">
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      120 AI renders / month
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      Unlimited style explorations
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      High-resolution exports
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      Custom material palette
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      Team members up to 5
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      Advanced controls
                    </li>
                    <li class="flex items-center gap-3 text-[0.84rem] font-semibold tracking-[-0.02em] text-[#3a332d]">
                      <i data-lucide="check-circle-2" class="h-4.5 w-4.5 shrink-0 text-[#9d7650]"></i>
                      Priority support
                    </li>
                  </ul>

                  <a href="#" class="mt-auto inline-flex w-full items-center justify-center rounded-[0.8rem] border border-[#bfa994] bg-[#f7efe6] px-5 py-4 text-[0.88rem] font-extrabold tracking-[-0.02em] text-[#171411] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)] transition hover:border-[#9d7650] hover:bg-white">
                    Start with Pro
                  </a>
                </article>
              </div>

              <!-- Professional CTA -->
              <div class="premium-panel mt-8 rounded-[1.15rem] bg-[#eee5da] px-7 py-5 shadow-[0_24px_64px_rgba(49,37,28,0.11),inset_0_1px_0_rgba(255,255,255,0.68)]">
                <div class="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
                  <div class="flex items-center gap-5">
                    <span class="inline-flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-[#d6c5b2] bg-[#f7efe6] text-[#9d7650] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]">
                      <i data-lucide="users-round" class="h-6 w-6"></i>
                    </span>

                    <div>
                      <p class="text-[0.95rem] font-extrabold tracking-[-0.025em] text-[#1c1814]">
                        Designing for clients or managing a team?
                      </p>
                      <p class="mt-1 text-[0.82rem] font-semibold leading-[1.5] tracking-[-0.02em] text-[#756b60]">
                        Our Pro plan includes tools built for collaboration and
                        scale.
                      </p>
                    </div>
                  </div>

                  <a href="#" class="inline-flex items-center justify-center gap-3 rounded-[0.85rem] border border-[#d6c5b2] bg-[#f7efe6] px-7 py-4 text-[0.88rem] font-extrabold tracking-[-0.02em] text-[#171411] shadow-[inset_0_1px_0_rgba(255,255,255,0.72)] transition hover:border-[#9d7650] hover:bg-white">
                    Explore for Professionals
                    <i data-lucide="arrow-right" class="h-4 w-4"></i>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- =========================================================
Section 07 / Final CTA
========================================================== -->
      <section class="relative overflow-hidden pt-10 lg:pt-14 reveal-on-scroll delay-300 delay-500 delay-700">
        <!-- Full-Bleed Background Image -->
        <div class="absolute inset-0 z-0">
          <img src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/545b052a-b0c2-4ec1-aeac-c36a8f948a5d_3840w.png" alt="Warm editorial living room interior" class="h-full w-full object-cover object-center">

          <!-- Cinematic Overlay -->
          <div class="absolute inset-0 bg-[linear-gradient(90deg,rgba(18,13,9,0.72)_0%,rgba(18,13,9,0.38)_42%,rgba(18,13,9,0.52)_100%)]"></div>
          <div class="absolute inset-0 bg-[radial-gradient(circle_at_50%_35%,rgba(255,238,215,0.14),transparent_38%)]"></div>
          <div class="absolute inset-x-0 bottom-0 h-[38%] bg-gradient-to-t from-[#171411] via-[#171411]/62 to-transparent"></div>
        </div>

        <div class="relative z-10 mx-auto max-w-[1510px] px-6 pb-14 pt-20 sm:px-8 lg:px-12 lg:pb-20 lg:pt-28 xl:px-14">
          <!-- =====================================================
    Final CTA / Main Card
    ====================================================== -->
          <div class="mx-auto max-w-[720px] rounded-[1.45rem] border border-[#e2d5c8] bg-[#f3eee7]/95 px-7 py-8 shadow-[0_38px_110px_rgba(0,0,0,0.32),inset_0_1px_0_rgba(255,255,255,0.72)] backdrop-blur-[2px] sm:px-10 sm:py-10 lg:px-12 lg:py-12">
            <!-- CTA Headline -->
            <h2 class="font-display mx-auto max-w-[620px] text-center text-[3.25rem] font-normal leading-[0.98] tracking-[-0.06em] text-[#151310] sm:text-[4.25rem] md:text-[4.85rem] lg:text-[5.15rem] reveal-on-scroll delay-150">
              Design the next
              <br>
              version of your
              <br>
              room with clarity.
            </h2>

            <!-- Decorative Rule -->
            <div class="mx-auto mt-7 h-px w-14 bg-[#9f7851]"></div>

            <!-- CTA Body -->
            <p class="mx-auto mt-7 max-w-[35rem] text-center text-[1rem] font-medium leading-[1.75] tracking-[-0.025em] text-[#3a332d] sm:text-[1.06rem]">
              Upload your room and explore multiple styles, materials, and
              layouts in minutes. Make confident design decisions before you
              commit.
            </p>

            <!-- CTA Buttons -->
            <div class="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <a href="#" class="inline-flex h-[62px] w-full items-center justify-center gap-4 rounded-[12px] bg-[#171614] px-8 text-[0.98rem] font-extrabold tracking-[-0.02em] text-white shadow-[0_24px_54px_rgba(28,22,17,0.22)] transition hover:-translate-y-0.5 hover:bg-[#29231f] sm:w-auto sm:min-w-[245px]">
                <i data-lucide="upload" class="h-5 w-5"></i>
                Upload Your Room
              </a>

              <a href="#" class="inline-flex h-[62px] w-full items-center justify-center gap-4 rounded-[12px] border border-[#d1c4b7] bg-[#f7f1e9] px-8 text-[0.98rem] font-extrabold tracking-[-0.02em] text-[#1c1915] shadow-[0_12px_28px_rgba(88,72,58,0.07),inset_0_1px_0_rgba(255,255,255,0.72)] transition hover:-translate-y-0.5 hover:border-[#c6b49f] hover:bg-white sm:w-auto sm:min-w-[220px]">
                <span class="inline-flex h-8 w-8 items-center justify-center rounded-full border border-[#1d1a16]">
                  <i data-lucide="play" class="ml-0.5 h-4 w-4"></i>
                </span>
                Book a Demo
              </a>
            </div>

            <!-- CTA Metrics -->
            <div class="mt-9 rounded-[1rem] border border-[#ded1c4] bg-[#eee5da]/82 px-5 py-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)]">
              <div class="grid gap-5 sm:grid-cols-3 sm:divide-x sm:divide-[#d6c8ba]">
                <div class="flex items-center justify-center gap-3 sm:px-4">
                  <i data-lucide="users-round" class="h-7 w-7 shrink-0 text-[#9d7650]"></i>
                  <div>
                    <p class="text-[0.78rem] font-semibold tracking-[-0.02em] text-[#756b60]">
                      Loved by
                    </p>
                    <p class="mt-1 text-[0.9rem] font-extrabold tracking-[-0.02em] text-[#171411]">
                      50K+ homeowners
                    </p>
                  </div>
                </div>

                <div class="flex items-center justify-center gap-3 sm:px-4">
                  <i data-lucide="shield-check" class="h-7 w-7 shrink-0 text-[#9d7650]"></i>
                  <div>
                    <p class="text-[0.78rem] font-semibold tracking-[-0.02em] text-[#756b60]">
                      Trusted by
                    </p>
                    <p class="mt-1 text-[0.9rem] font-extrabold tracking-[-0.02em] text-[#171411]">
                      Design Pros
                    </p>
                  </div>
                </div>

                <div class="flex items-center justify-center gap-3 sm:px-4">
                  <i data-lucide="badge-check" class="h-7 w-7 shrink-0 text-[#9d7650]"></i>
                  <div>
                    <p class="text-[0.78rem] font-semibold tracking-[-0.02em] text-[#756b60]">
                      User Rating
                    </p>
                    <p class="mt-1 text-[0.9rem] font-extrabold tracking-[-0.02em] text-[#171411]">
                      4.9/5
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- =====================================================
Final CTA / Audience Strip
====================================================== -->
          <div class="mx-auto mt-16 max-w-[1040px] rounded-[1.25rem] border border-[rgba(202,165,124,0.26)] bg-[rgba(23,20,17,0.82)] px-7 py-7 text-white shadow-[0_34px_90px_rgba(0,0,0,0.30),inset_0_1px_0_rgba(202,165,124,0.08)] backdrop-blur-md sm:px-8">
            <div class="grid gap-0 lg:grid-cols-4 lg:items-center">
              <!-- Quote -->
              <div class="px-2 text-left lg:pr-8">
                <p class="font-display text-[1.35rem] font-normal leading-[1.18] tracking-[-0.045em] text-white/90">
                  “Atelier AI helps us show
                  <br class="hidden sm:block">
                  clients what’s possible —
                  <br class="hidden sm:block">
                  before we lift a hammer.”
                </p>

                <p class="mt-5 text-[0.84rem] font-bold tracking-[-0.02em] text-[#caa57c]">
                  — Interior Designer
                </p>
              </div>

              <!-- Audience 01 -->
              <div class="flex flex-col items-center border-t border-[rgba(202,165,124,0.24)] px-6 pt-7 text-center lg:border-l lg:border-t-0 lg:pt-0">
                <i data-lucide="user-round" class="h-8 w-8 shrink-0 text-[#caa57c]"></i>

                <p class="mt-4 text-[0.95rem] font-extrabold tracking-[-0.02em] text-white">
                  For Homeowners
                </p>

                <p class="mt-2 max-w-[12rem] text-[0.82rem] font-semibold leading-[1.48] tracking-[-0.02em] text-white/66">
                  Design with confidence before you renovate.
                </p>
              </div>

              <!-- Audience 02 -->
              <div class="flex flex-col items-center border-t border-[rgba(202,165,124,0.24)] px-6 pt-7 text-center lg:border-l lg:border-t-0 lg:pt-0">
                <i data-lucide="briefcase-business" class="h-8 w-8 shrink-0 text-[#caa57c]"></i>

                <p class="mt-4 text-[0.95rem] font-extrabold tracking-[-0.02em] text-white">
                  For Designers
                </p>

                <p class="mt-2 max-w-[12rem] text-[0.82rem] font-semibold leading-[1.48] tracking-[-0.02em] text-white/66">
                  Present ideas faster and beautifully.
                </p>
              </div>

              <!-- Audience 03 -->
              <div class="flex flex-col items-center border-t border-[rgba(202,165,124,0.24)] px-6 pt-7 text-center lg:border-l lg:border-t-0 lg:pt-0">
                <i data-lucide="building-2" class="h-8 w-8 shrink-0 text-[#caa57c]"></i>

                <p class="mt-4 text-[0.95rem] font-extrabold tracking-[-0.02em] text-white">
                  For Real Estate Pros
                </p>

                <p class="mt-2 max-w-[13rem] text-[0.82rem] font-semibold leading-[1.48] tracking-[-0.02em] text-white/66">
                  Help buyers see the true potential.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- =========================================================
Footer / Light Mode
========================================================== -->
      <footer class="relative overflow-hidden border-t border-[#ded1c4] bg-[#f5f0e9] text-[#171411]">
        <!-- Subtle Footer Texture -->
        <div class="pointer-events-none absolute inset-0">
          <div class="absolute inset-0 bg-[radial-gradient(circle_at_14%_12%,rgba(255,255,255,0.72),transparent_30%),radial-gradient(circle_at_82%_0%,rgba(221,211,198,0.36),transparent_34%)]"></div>
        </div>

        <div class="relative z-10 mx-auto max-w-[1510px] px-6 py-12 sm:px-8 lg:px-12 xl:px-14">
          <!-- Footer Top -->
          <div class="grid gap-10 border-b border-[#d8cdc1] pb-10 lg:grid-cols-[1.25fr_0.75fr_0.75fr_0.95fr]">
            <!-- Footer Brand -->
            <div>
              <a href="#" class="font-logo text-[2rem] font-medium tracking-[0.20em] text-[#171411]">
                ATELIER AI
              </a>

              <p class="mt-5 max-w-[24rem] text-[0.94rem] font-semibold leading-[1.65] tracking-[-0.02em] text-[#756b60]">
                AI-assisted interior direction for homeowners, designers, and
                real estate teams who want clearer design decisions.
              </p>
            </div>

            <!-- Footer Column 01 -->
            <div>
              <h3 class="text-[0.82rem] font-extrabold uppercase tracking-[0.08em] text-[#9a744d]">
                Product
              </h3>

              <ul class="mt-5 space-y-3.5 text-[0.9rem] font-semibold tracking-[-0.02em] text-[#756b60]">
                <li>
                  <a href="#" class="transition hover:text-[#171411]">
                    How It Works
                  </a>
                </li>
                <li>
                  <a href="#" class="transition hover:text-[#171411]">
                    Style Library
                  </a>
                </li>
                <li>
                  <a href="#" class="transition hover:text-[#171411]">
                    AI Intelligence
                  </a>
                </li>
                <li>
                  <a href="#" class="transition hover:text-[#171411]">
                    Pricing
                  </a>
                </li>
              </ul>
            </div>

            <!-- Footer Column 02 -->
            <div>
              <h3 class="text-[0.82rem] font-extrabold uppercase tracking-[0.08em] text-[#9a744d]">
                For Teams
              </h3>

              <ul class="mt-5 space-y-3.5 text-[0.9rem] font-semibold tracking-[-0.02em] text-[#756b60]">
                <li>
                  <a href="#" class="transition hover:text-[#171411]">
                    Interior Designers
                  </a>
                </li>
                <li>
                  <a href="#" class="transition hover:text-[#171411]">
                    Real Estate Pros
                  </a>
                </li>
                <li>
                  <a href="#" class="transition hover:text-[#171411]">
                    Studios
                  </a>
                </li>
                <li>
                  <a href="#" class="transition hover:text-[#171411]">
                    Book a Demo
                  </a>
                </li>
              </ul>
            </div>

            <!-- Footer Column 03 -->
            <div>
              <h3 class="text-[0.82rem] font-extrabold uppercase tracking-[0.08em] text-[#9a744d]">
                Stay Updated
              </h3>

              <p class="mt-5 max-w-[22rem] text-[0.9rem] font-semibold leading-[1.6] tracking-[-0.02em] text-[#756b60]">
                Get new style drops, product updates, and practical design
                workflow ideas.
              </p>

              <form class="premium-panel mt-5 flex overflow-hidden rounded-[0.95rem] bg-[#eee5da] p-1.5 shadow-[0_18px_46px_rgba(49,37,28,0.10),inset_0_1px_0_rgba(255,255,255,0.68)]">
                <input type="email" placeholder="Email address" class="min-w-0 flex-1 bg-transparent px-3 text-[0.86rem] font-semibold text-[#171411] placeholder:text-[#9b8f82] focus:outline-none">

                <button type="submit" class="inline-flex h-10 shrink-0 items-center justify-center rounded-[0.7rem] bg-[#171614] px-5 text-[0.82rem] font-extrabold tracking-[-0.02em] text-white shadow-[0_14px_30px_rgba(25,21,18,0.16)] transition hover:bg-[#29231f]">
                  Join
                </button>
              </form>
            </div>
          </div>

          <!-- Footer Bottom -->
          <div class="flex flex-col gap-4 pt-7 text-[0.82rem] font-semibold tracking-[-0.02em] text-[#8c8176] sm:flex-row sm:items-center sm:justify-between">
            <p>© 2026 Atelier AI. All rights reserved.</p>

            <div class="flex flex-wrap items-center gap-5">
              <a href="#" class="transition hover:text-[#171411]">Privacy</a>
              <a href="#" class="transition hover:text-[#171411]">Terms</a>
              <a href="#" class="transition hover:text-[#171411]">Security</a>
            </div>
          </div>
        </div>
      </footer>
    </main>

    <!-- =========================================================
  Scripts
  ========================================================== -->
    <script>
      lucide.createIcons({
        attrs: {
          "stroke-width": 1.6
        }
      });
    </script>

    <!-- =========================================================
AI Intelligence Slider Script
========================================================== -->
    <script>
        document.querySelectorAll("[data-slider]").forEach((slider) => {
          const before = slider.querySelector("[data-before]");
          const line = slider.querySelector("[data-line]");
          const handle = slider.querySelector("[data-handle]");

          let isDragging = false;

          const setPosition = (clientX) => {
            const rect = slider.getBoundingClientRect();
            const x = Math.min(Math.max(clientX - rect.left, 0), rect.width);
            const percent = (x / rect.width) * 100;

            before.style.clipPath = `inset(0 ${100 - percent}% 0 0)`;
      line.style.left = `${percent}%`;
      handle.style.left = `${percent}%`;
          };

          const startDragging = (event) => {
            isDragging = true;
            const clientX = event.touches ? event.touches[0].clientX : event.clientX;
            setPosition(clientX);
          };

          const drag = (event) => {
            if (!isDragging) return;
            const clientX = event.touches ? event.touches[0].clientX : event.clientX;
            setPosition(clientX);
          };

          const stopDragging = () => {
            isDragging = false;
          };

          slider.addEventListener("mousedown", startDragging);
          slider.addEventListener("touchstart", startDragging, { passive: true });

          window.addEventListener("mousemove", drag);
          window.addEventListener("touchmove", drag, { passive: true });

          window.addEventListener("mouseup", stopDragging);
          window.addEventListener("touchend", stopDragging);
        });
    </script>

    <script>
      (function() {
        function initAnimations() {
          const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
              if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                obs.unobserve(entry.target);
              }
            });
          }, { threshold: 0.1 });
          document.querySelectorAll('.reveal-on-scroll').forEach(el => observer.observe(el));
        }
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initAnimations);
        } else {
          initAnimations();
        }
      })();
    </script>
  
<script data-aura-video-controller="true">
(function () {
  function playVideo(video) {
    var promise = video.play();
    if (promise && typeof promise.catch === "function") {
      promise.catch(function () {});
    }
  }

  function setupVideo(video) {
    if (video.__auraVideoReady === true) return;
    video.__auraVideoReady = true;
    video.removeAttribute("data-aura-video-ready");
    video.removeAttribute("data-aura-video-played");
    video.muted = true;
    video.playsInline = true;

    var preset = video.dataset.auraVideoPreset || "loop-in-view";
    if (preset === "hover") {
      video.addEventListener("mouseenter", function () {
        playVideo(video);
      });
      video.addEventListener("mouseleave", function () {
        video.pause();
        video.currentTime = 0;
      });
      return;
    }

    if (!("IntersectionObserver" in window)) {
      playVideo(video);
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          if (preset === "play-once" && video.__auraVideoPlayed === true) {
            return;
          }
          playVideo(video);
        } else {
          video.pause();
        }
      });
    }, { threshold: 0.35 });

    if (preset === "play-once") {
      video.addEventListener("ended", function () {
        video.__auraVideoPlayed = true;
      }, { once: true });
    }

    observer.observe(video);
  }

  function setupVideos() {
    document
      .querySelectorAll("video[data-aura-video-preset]")
      .forEach(setupVideo);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupVideos);
  } else {
    setupVideos();
  }
})();</script></body></html>
