<template>
  <div class="bg-white shadow-sm rounded-lg p-6 mb-8 border border-gray-100">
    <form @submit.prevent="submitSearch" class="space-y-4">
      <!-- Row 1: Query + Search Button -->
      <div class="flex flex-col md:flex-row gap-4">
        <div class="flex-grow relative">
          <label for="query" class="sr-only">Search technological insights...</label>
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input 
            id="query" 
            v-model="query" 
            type="text" 
            class="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition duration-150 ease-in-out" 
            placeholder="e.g. machine learning in healthcare diagnostics..."
            required
          />
        </div>

        <button 
          type="submit" 
          :disabled="loading"
          class="w-full md:w-auto px-6 py-3 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition duration-150 ease-in-out flex items-center justify-center gap-2"
        >
          <svg v-if="loading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          <span>{{ loading ? 'Searching...' : 'Search' }}</span>
        </button>
      </div>

      <!-- Row 2: Filters (collapsible) -->
      <div>
        <button type="button" @click="showFilters = !showFilters" class="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1 transition-colors">
          <svg class="h-4 w-4 transition-transform" :class="{ 'rotate-180': showFilters }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
          {{ showFilters ? 'Hide Filters' : 'Show Advanced Filters' }}
        </button>

        <transition 
          enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="max-h-0 opacity-0"
          enter-to-class="max-h-48 opacity-100"
          leave-active-class="transition-all duration-200 ease-in"
          leave-from-class="max-h-48 opacity-100"
          leave-to-class="max-h-0 opacity-0"
        >
          <div v-show="showFilters" class="overflow-hidden">
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-100">
              <!-- Document Type -->
              <div>
                <label for="doctype" class="block text-xs font-medium text-gray-500 mb-1">Document Type</label>
                <select 
                  id="doctype" 
                  v-model="docType" 
                  class="block w-full py-2 pl-3 pr-8 border border-gray-300 bg-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition duration-150 ease-in-out"
                >
                  <option value="">All Types</option>
                  <option value="Patent">Patents</option>
                  <option value="Research Paper">Research Papers</option>
                </select>
              </div>

              <!-- Date From -->
              <div>
                <label for="dateFrom" class="block text-xs font-medium text-gray-500 mb-1">Date From</label>
                <input 
                  id="dateFrom" 
                  v-model="dateFrom" 
                  type="date" 
                  class="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition duration-150 ease-in-out"
                />
              </div>

              <!-- Date To -->
              <div>
                <label for="dateTo" class="block text-xs font-medium text-gray-500 mb-1">Date To</label>
                <input 
                  id="dateTo" 
                  v-model="dateTo" 
                  type="date" 
                  class="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition duration-150 ease-in-out"
                />
              </div>

              <!-- Min Citations -->
              <div>
                <label for="minCitations" class="block text-xs font-medium text-gray-500 mb-1">Min. Citations</label>
                <input 
                  id="minCitations" 
                  v-model.number="minCitations" 
                  type="number" 
                  min="0"
                  placeholder="0"
                  class="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition duration-150 ease-in-out"
                />
              </div>
            </div>
          </div>
        </transition>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  loading: Boolean
});

const emit = defineEmits(['search']);

const query = ref('');
const docType = ref('');
const dateFrom = ref('');
const dateTo = ref('');
const minCitations = ref(null);
const showFilters = ref(false);

const submitSearch = () => {
  if (query.value.trim()) {
    emit('search', {
      query: query.value,
      docType: docType.value,
      dateFrom: dateFrom.value,
      dateTo: dateTo.value,
      minCitations: minCitations.value,
    });
  }
};
</script>
