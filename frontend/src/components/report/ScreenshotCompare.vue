<template>
  <div class="screenshot-compare" v-if="expected || actual">
    <div class="screenshot-item" v-if="expected">
      <h4>预期截图</h4>
      <img :src="expected" loading="lazy" @error="onImgError" />
    </div>
    <div class="screenshot-item" v-if="actual">
      <h4>实际截图</h4>
      <img :src="actual" loading="lazy" @error="onImgError" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  expected: string | null
  actual: string | null
}>()

function onImgError(e: Event) {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}
</script>

<style scoped>
.screenshot-compare { display: flex; gap: 20px; margin-top: 10px; }
.screenshot-item { flex: 1; }
.screenshot-item h4 { margin: 0 0 8px; font-size: 14px; color: #606266; }
.screenshot-item img { max-width: 100%; border: 1px solid #ebeef5; border-radius: 4px; }
</style>
