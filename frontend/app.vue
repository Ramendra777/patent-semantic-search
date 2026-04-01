<template>
  <div>
    <transition enter-active-class="transition duration-500" enter-from-class="opacity-0" enter-to-class="opacity-100" leave-active-class="transition duration-500" leave-from-class="opacity-100" leave-to-class="opacity-0">
      <HeroSection v-if="showHero" @startSearch="showHero = false" />
    </transition>
    
    <div v-show="!showHero" class="min-h-screen bg-gray-50 flex flex-col font-sans transition-opacity duration-500">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold leading-tight text-gray-900 flex items-center gap-3">
          <svg class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          Document Search System
        </h1>
        <p class="mt-2 text-sm text-gray-600">Explore technical patents and research papers with semantic search & clustering.</p>
      </div>
    </header>
    
    <main class="flex-1 max-w-7xl w-full mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <SearchForm :loading="loading" @search="handleSearch" />
      
      <div v-if="error" class="mb-8 bg-red-50 border-l-4 border-red-400 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{{ error }}</p>
          </div>
        </div>
      </div>
      
      <div v-show="searched && !loading" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Results Column -->
        <div class="lg:col-span-2">
          <h2 class="text-xl font-bold text-gray-800 mb-4 flex items-center justify-between">
            Search Results
            <span v-if="results.length" class="text-sm font-normal text-gray-500 bg-gray-200 px-3 py-1 rounded-full">{{ results.length }} items</span>
          </h2>
          <ResultList :results="results" />
        </div>
        
        <!-- Visualization Column -->
        <div class="lg:col-span-1 border-l pl-0 lg:pl-8 border-gray-200">
          <h2 class="text-xl font-bold text-gray-800 mb-4">Topic Trends</h2>
          <TrendMap v-if="trends && trends.length > 0" :trends="trends" />
          <div v-else class="bg-white p-6 rounded-lg shadow-sm border border-gray-100 text-center text-gray-500 text-sm">
            Visualization will appear here.
          </div>
        </div>
      </div>
      
      <div v-if="loading" class="flex justify-center items-center py-20">
        <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-gray-600 text-lg font-medium">Analyzing documents...</span>
      </div>
    </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import HeroSection from '~/components/ui/HeroSection.vue';

const showHero = ref(true);
const loading = ref(false);
const searched = ref(false);
const results = ref([]);
const trends = ref([]);
const error = ref(null);

const { public: config } = useRuntimeConfig();

const handleSearch = async ({ query, docType, dateFrom, dateTo, minCitations }) => {
  loading.value = true;
  error.value = null;
  searched.value = true;
  
  try {
    const params = new URLSearchParams({ query });
    if (docType) params.append('doc_type', docType);
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    if (minCitations) params.append('min_citations', String(minCitations));
    
    // Using $fetch provided by Nuxt
    const data = await $fetch(`${config.apiBase}/api/search?${params.toString()}`);
    results.value = data.results || [];
    trends.value = data.trends || [];
  } catch (err) {
    error.value = err.message || "An error occurred while fetching results.";
    console.error(err);
  } finally {
    loading.value = false;
  }
};
</script>
