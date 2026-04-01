<template>
  <div class="space-y-6">
    <div v-if="results.length === 0" class="text-center py-12 bg-gray-50 rounded-lg border border-dashed border-gray-300">
      <p class="text-gray-500">No results found. Try a different query.</p>
    </div>
    
    <div v-for="(item, index) in results" :key="index" class="bg-white hover:bg-gray-50 transition duration-150 ease-in-out p-6 rounded-lg shadow-sm border border-gray-100 flex flex-col gap-3">
      <div class="flex justify-between items-start">
        <h3 class="text-lg font-semibold text-gray-900 line-clamp-2 pr-4">{{ item.title || 'Untitled Document' }}</h3>
        <span 
          class="px-3 py-1 text-xs font-medium rounded-full shrink-0"
          :class="{
            'bg-purple-100 text-purple-800': item.doc_type === 'Patent',
            'bg-green-100 text-green-800': item.doc_type === 'Research Paper',
            'bg-gray-100 text-gray-800': !item.doc_type
          }"
        >
          {{ item.doc_type || 'Unknown' }}
        </span>
      </div>
      
      <p class="text-gray-600 text-sm line-clamp-3 leading-relaxed">{{ item.abstract }}</p>
      
      <div class="mt-4 flex flex-wrap gap-4 items-center text-xs text-gray-500">
        <div class="flex items-center gap-1">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          {{ formatDate(item.publication_date) }}
        </div>
        
        <div class="flex items-center gap-1" v-if="item.citation_count !== undefined">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          {{ item.citation_count }} Citations
        </div>
        
        <div class="flex items-center gap-1 bg-blue-50 text-blue-700 px-2 py-1 rounded">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
          {{ item.sub_topic || 'Uncategorized' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  results: {
    type: Array,
    required: true,
    default: () => []
  }
});

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown Date';
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return dateString;
    return new Intl.DateTimeFormat('en-US', { year: 'numeric', month: 'short', day: 'numeric' }).format(d);
  } catch {
    return dateString;
  }
};
</script>
