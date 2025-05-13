<template>
  <div class="grid gap-6">
    <div
      v-for="(entry, i) in paginatedEntries"
      :key="i"
      class="border border-neutral-700 p-4 rounded-xl bg-neutral-900"
    >
      <p class="text-xs mb-2 opacity-50">{{ entry.path }}</p>

      <audio
        :src="`${basePath}/${entry.bucket}${entry.path}`"
        controls
        class="w-full mb-3 rounded"
      />

      <label class="block text-sm mb-1">Filename</label>
      <input
        v-model="entry.name"
        class="w-full bg-neutral-800 p-2 rounded border border-neutral-700 text-sm"
      />

      <label class="block text-sm mt-4 mb-1">Tags</label>
      <input
        v-model="entry.tagsString"
        class="w-full bg-neutral-800 p-2 rounded border border-neutral-700 text-sm"
        placeholder="comma-separated tags"
      />

      <button
        @click="approve(currentPageStart + i)"
        class="mt-4 px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm"
      >
        ✅ Approve
      </button>
    </div>

    <div class="flex items-center justify-between mt-8">
      <button
        @click="prevPage"
        :disabled="currentPage === 0"
        class="px-4 py-2 bg-neutral-700 rounded disabled:opacity-40"
      >
        ◀ Prev
      </button>

      <span class="text-sm text-neutral-400">Page {{ currentPage + 1 }} / {{ totalPages }}</span>

      <button
        @click="nextPage"
        :disabled="currentPage >= totalPages - 1"
        class="px-4 py-2 bg-neutral-700 rounded disabled:opacity-40"
      >
        Next ▶
      </button>
    </div>

    <button
      @click="saveApproved"
      class="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded mt-6"
    >
      💾 Save Approved
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const entries = ref([])
const approved = ref([])
const basePath = '/sounds'

const currentPage = ref(0)
const pageSize = 10

const currentPageStart = computed(() => currentPage.value * pageSize)
const paginatedEntries = computed(() =>
  entries.value.slice(currentPageStart.value, currentPageStart.value + pageSize)
)
const totalPages = computed(() => Math.ceil(entries.value.length / pageSize))

function nextPage() {
  if (currentPage.value < totalPages.value - 1) currentPage.value++
}

function prevPage() {
  if (currentPage.value > 0) currentPage.value--
}

onMounted(async () => {
  const res = await fetch('http://localhost:8000/tagged')
  const data = await res.json()

  entries.value = data.map(item => ({
    ...item,
    tagsString: item.tags.join(', ')
  }))
})

function saveApproved() {
  fetch("http://localhost:8000/approve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(approved.value)
  }).then(() => {
    alert("Approved sounds saved!")
  })
}


function approve(index) {
  const item = entries.value[index]
  approved.value.push({
    path: item.path,
    name: item.name,
    tags: item.tagsString.split(',').map(tag => tag.trim())
  })
  entries.value.splice(index, 1)
}

</script>

<style>
audio::-webkit-media-controls-panel {
  background-color: #111;
}
</style>
