<template>
  <div class="relative min-h-screen overflow-hidden bg-black text-white">
    <!-- Gradient background with grain effect -->
    <div class="flex flex-col items-end absolute -right-60 -top-10 blur-xl z-0 pointer-events-none">
      <div class="h-[10rem] rounded-full w-[60rem] z-1 bg-gradient-to-b blur-[6rem] from-purple-600 to-sky-600"></div>
      <div class="h-[10rem] rounded-full w-[90rem] z-1 bg-gradient-to-b blur-[6rem] from-pink-900 to-yellow-400"></div>
      <div class="h-[10rem] rounded-full w-[60rem] z-1 bg-gradient-to-b blur-[6rem] from-yellow-600 to-sky-500"></div>
    </div>
    
    <!-- Grain Overlay -->
    <div class="absolute inset-0 z-0 opacity-20 pointer-events-none bg-[url('data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E')]"></div>

    <!-- Content container -->
    <div class="relative z-10 transition-opacity duration-300">
      <!-- Navigation -->
      <nav class="container mx-auto flex items-center justify-between px-4 py-4 mt-6">
        <div class="flex items-center">
          <div class="flex h-8 w-8 items-center justify-center rounded-full bg-white text-black">
            <span class="font-bold">⚡</span>
          </div>
          <span class="ml-2 text-xl font-bold text-white">PatentSearch</span>
        </div>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center space-x-6">
          <div class="flex items-center space-x-8">
            <template v-for="item in navItems" :key="item.label">
              <a href="#" class="flex items-center text-sm font-medium text-gray-300 hover:text-white transition-colors">
                <span>{{ item.label }}</span>
                <svg v-if="item.hasDropdown" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ml-1.5 opacity-70">
                  <path d="m6 9 6 6 6-6" />
                </svg>
              </a>
            </template>
          </div>
          <div class="flex items-center space-x-3 border-l border-gray-700 pl-6">
            <button class="text-sm font-medium text-gray-300 hover:text-white transition-colors">
              Log in
            </button>
          </div>
        </div>

        <!-- Mobile menu button -->
        <button
          class="md:hidden flex items-center justify-center h-10 w-10 rounded-md hover:bg-white/10 transition-colors"
          @click="mobileMenuOpen = !mobileMenuOpen"
        >
          <span class="sr-only">Toggle menu</span>
          <component :is="mobileMenuOpen ? X : Menu" class="h-6 w-6 text-white" />
        </button>
      </nav>

      <!-- Mobile Navigation Menu using Vue Transition -->
      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="transform -translate-y-full opacity-0"
        enter-to-class="transform translate-y-0 opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="transform translate-y-0 opacity-100"
        leave-to-class="transform -translate-y-full opacity-0"
      >
        <div
          v-if="mobileMenuOpen"
          class="fixed inset-0 z-50 flex flex-col p-4 bg-black/95 backdrop-blur-md md:hidden h-screen"
        >
          <div class="flex flex-col h-full relative">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <div class="flex h-8 w-8 items-center justify-center rounded-full bg-white text-black">
                  <span class="font-bold">⚡</span>
                </div>
                <span class="ml-2 text-xl font-bold text-white">PatentSearch</span>
              </div>
              <button class="h-10 w-10 flex items-center justify-center rounded-md hover:bg-white/10" @click="mobileMenuOpen = false">
                <X class="h-6 w-6 text-white" />
              </button>
            </div>
            <div class="mt-8 flex flex-col space-y-2 flex-1">
              <template v-for="item in navItems" :key="item.label">
                <a href="#" class="flex items-center justify-between border-b border-gray-800 py-4 text-lg text-white hover:text-blue-400 transition-colors">
                  <span>{{ item.label }}</span>
                  <ArrowRight class="h-4 w-4 text-gray-500" />
                </a>
              </template>
              <div class="pt-8 space-y-4">
                <button class="w-full text-center py-3 border border-gray-700 rounded-lg text-white font-medium hover:bg-white/5 transition-colors">
                  Log in
                </button>
                <button class="w-full text-center py-3 bg-white text-black rounded-lg font-medium hover:bg-gray-100 transition-colors">
                  Get Started For Free
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Badge -->
      <div class="mx-auto mt-12 mb-8 flex max-w-fit items-center justify-center space-x-2 rounded-full bg-white/10 px-5 py-2.5 backdrop-blur-sm border border-white/5 hover:bg-white/20 transition-colors cursor-pointer" @click="$emit('startSearch')">
        <span class="text-sm font-medium text-white shadow-sm">
          Join the semantic revolution today!
        </span>
        <ArrowRight class="h-4 w-4 text-white" />
      </div>

      <!-- Hero main content -->
      <div class="container mx-auto px-4 text-center mt-4">
        <h1 class="mx-auto max-w-5xl text-5xl font-extrabold tracking-tight text-white md:text-6xl lg:text-[5rem] lg:leading-[1.1]">
          AI-Powered Semantic<br/><span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400">Document Search</span>
        </h1>
        <p class="mx-auto mt-6 max-w-2xl text-lg text-gray-400 leading-relaxed">
          Explore technical patents and research papers with advanced vector search and real-time topic clustering. Your research toolkit redefined into something beautiful.
        </p>
        <div class="mt-10 flex flex-col items-center justify-center space-y-4 sm:flex-row sm:space-x-6 sm:space-y-0">
          <button @click="$emit('startSearch')" class="h-14 rounded-full bg-white px-8 text-base font-semibold text-black hover:bg-gray-200 transition-colors shadow-[0_0_20px_rgba(255,255,255,0.3)]">
            Start Searching Now
          </button>
          <button class="h-14 rounded-full border border-gray-700 bg-black/20 backdrop-blur-sm px-8 text-base font-medium text-white hover:bg-white/10 hover:border-gray-500 transition-colors">
            Watch Demo
          </button>
        </div>

        <!-- Dashboard Preview Graphic -->
        <div class="relative mx-auto my-20 w-full max-w-6xl px-4 lg:px-0 transition-transform duration-500 hover:scale-[1.02]">
          <!-- Glow effect behind image -->
          <div class="absolute inset-x-10 inset-y-10 rounded-[2rem] bg-gradient-to-r from-blue-500/30 to-purple-500/30 blur-[4rem]" />

          <img
            src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop"
            alt="Semantic Clustering Interface Preview"
            class="relative w-full h-auto object-cover object-top border border-gray-800 shadow-2xl rounded-2xl md:rounded-[2rem] bg-gray-900 aspect-[16/9] lg:aspect-[2/1] opacity-90 ring-1 ring-white/10"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { ArrowRight, Menu, X } from 'lucide-vue-next';

defineEmits(['startSearch']);

const mobileMenuOpen = ref(false);

const navItems = [
  { label: 'Use Cases', hasDropdown: true },
  { label: 'Products', hasDropdown: true },
  { label: 'Resources', hasDropdown: true },
  { label: 'Pricing', hasDropdown: false },
];
</script>
