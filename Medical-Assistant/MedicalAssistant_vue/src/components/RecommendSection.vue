<template>
  <section class="recommend-section">
    <div class="recommend-container">
      <div class="section-title">
        <h2>推荐医学文档</h2>
        <div class="title-line"></div>
      </div>
      <div class="doc-grid">
        <div
          class="doc-card"
          v-for="(doc, idx) in docs"
          :key="idx"
          @mouseenter="cardHoverIdx = idx"
          @mouseleave="cardHoverIdx = -1"
        >
          <div class="card-header">
            <span class="doc-tag">{{ doc.department }}</span>
            <span class="doc-time">{{ doc.time }}</span>
          </div>
          <div class="card-body">
            <h3 class="doc-title">{{ doc.title }}</h3>
          </div>
          <div class="card-footer">
            <button
              class="view-btn"
              @click="emitViewDoc(doc)"
              :class="{ hover: cardHoverIdx === idx }"
            >
              查看文档
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  docs: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['viewDoc']);

const cardHoverIdx = ref(-1);

const emitViewDoc = (doc) => {
  emit('viewDoc', doc);
};
</script>

<style scoped>
.recommend-section {
  padding: 40px 0;
}

.recommend-container {
  width: 1200px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
}

.section-title h2 {
  font-size: 28px;
  color: #2d3748;
  font-weight: 600;
  margin-bottom: 12px;
}

.title-line {
  width: 80px;
  height: 4px;
  background: linear-gradient(135deg, #2d6a4f, #40916c);
  border-radius: 2px;
  margin: 0 auto;
}

.doc-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.doc-card {
  background-color: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border: 1px solid #e8f4f8;
}

.doc-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.08);
  border-color: #38b2ac;
}

.card-header {
  padding: 16px;
  background-color: #f0f8fb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.doc-tag {
  background-color: #38b2ac;
  color: #ffffff;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.doc-time {
  font-size: 12px;
  color: #718096;
}

.card-body {
  padding: 20px 16px;
}

.doc-title {
  font-size: 16px;
  color: #2d3748;
  font-weight: 500;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  padding: 16px;
  border-top: 1px solid #f0f8fb;
  display: flex;
  justify-content: center;
}

.view-btn {
  padding: 8px 20px;
  background-color: transparent;
  border: 2px solid #40916c;
  color: #40916c;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn.hover {
  background-color: #40916c;
  color: #ffffff;
}
</style>
