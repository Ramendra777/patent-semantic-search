<template>
  <div class="bg-white shadow-sm rounded-lg p-6 mb-8 border border-gray-100">
    <form @submit.prevent="submitSearch" class="flex flex-col md:flex-row gap-4">
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
          placeholder="e.g. machine learning in healthcare..."
          required
        />
      </div>
      
      <div class="w-full md:w-48">
        <label for="doctype" class="sr-only">Document Type</label>
        <select 
          id="doctype" 
          v-model="docType" 
          class="block w-full py-3 pl-3 pr-10 border border-gray-300 bg-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition duration-150 ease-in-out"
        >
          <option value="">All Types</option>
          <option value="Patent">Patents</option>
          <option value="Research Paper">Research Papers</option>
        </select>
      </div>

      <button 
        type="submit" 
        :disabled="loading"
        class="w-full md:w-auto px-6 py-3 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition duration-150 ease-in-out flex items-center justify-center"
      >
        <span v-if="loading">Searching...</span>
        <span v-else>Search</span>
      </button>
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

const submitSearch = () => {
  if (query.value.trim()) {
    emit('search', { query: query.value, docType: docType.value });
  }
};
</script>
