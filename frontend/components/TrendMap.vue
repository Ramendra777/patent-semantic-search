<template>
  <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
    <div class="mb-4">
      <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Growth Velocity</h3>
      <div class="mt-2 space-y-3">
        <div v-for="trend in trends" :key="trend.topic" class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-800 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-blue-500"></span>
            {{ trend.topic }}
          </span>
          <span class="text-sm rounded px-2 py-0.5" 
                :class="trend.velocity > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
            {{ trend.velocity > 0 ? '+' : '' }}{{ trend.velocity.toFixed(1) }} / yr
          </span>
        </div>
      </div>
    </div>
    
    <div class="mt-8 border-t border-gray-100 pt-6">
      <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">Publication Trend (Heatmap)</h3>
      <div class="relative h-64 w-full">
        <Line :data="chartData" :options="chartOptions" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'vue-chartjs';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const props = defineProps({
  trends: {
    type: Array,
    required: true,
    default: () => []
  }
});

// Color palette for different topics
const colors = [
  { border: 'rgb(59, 130, 246)', bg: 'rgba(59, 130, 246, 0.1)' }, // blue-500
  { border: 'rgb(16, 185, 129)', bg: 'rgba(16, 185, 129, 0.1)' }, // green-500
  { border: 'rgb(139, 92, 246)', bg: 'rgba(139, 92, 246, 0.1)' }, // purple-500
  { border: 'rgb(245, 158, 11)', bg: 'rgba(245, 158, 11, 0.1)' }, // amber-500
  { border: 'rgb(236, 72, 153)', bg: 'rgba(236, 72, 153, 0.1)' }  // pink-500
];

const chartData = computed(() => {
  if (!props.trends || props.trends.length === 0) return { labels: [], datasets: [] };
  
  // Find all unique years across all topics to create the common X axis
  const allYearsSet = new Set();
  props.trends.forEach(t => {
    t.years.forEach(y => allYearsSet.add(y));
  });
  
  const sortedYears = Array.from(allYearsSet).sort((a, b) => a - b);
  
  const datasets = props.trends.map((topicData, index) => {
    // Map data to the common X axis
    const dataPoints = sortedYears.map(year => {
      const yearIdx = topicData.years.indexOf(year);
      return yearIdx !== -1 ? topicData.counts[yearIdx] : 0;
    });
    
    const color = colors[index % colors.length];
    
    return {
      label: topicData.topic,
      data: dataPoints,
      borderColor: color.border,
      backgroundColor: color.bg,
      fill: true,
      tension: 0.4,
      pointRadius: 3,
      pointHoverRadius: 6
    };
  });
  
  return {
    labels: sortedYears,
    datasets
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        boxWidth: 8
      }
    },
    tooltip: {
      mode: 'index',
      intersect: false,
    }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { precision: 0 } // whole numbers for document counts
    }
  }
};
</script>
