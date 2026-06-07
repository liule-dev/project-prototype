<template>
  <div class="medical-system">
    <!-- 顶部导航栏 -->
    <HeaderSection
      v-model:searchInput="searchInput"
      @model-dialog="handleModelDialog"
    />

    <!-- 功能操作区 -->
    <!-- 功能操作区 -->
  <FunctionSection
    @upload-click="showUploadModal = true"
    @video-click="showVideoModal = true"
    @image-click="showImageModal = true"
    @manage-click="handleUpdate"

  />
  <ai></ai>
    <!-- 上传文档表单弹窗 -->
    <UploadModal
      :visible="showUploadModal"
      :form-data="uploadForm"
      @submit="submitUpload"
      @cancel="showUploadModal = false"
    />
    <!-- 视频上传弹窗 -->
  <VideoUploadModal
    :visible="showVideoModal"
    :form-data="videoForm"
    @submit="submitVideo"
    @cancel="showVideoModal = false"
  />

  <!-- 图片上传弹窗 -->
  <ImageUploadModal
    :visible="showImageModal"
    :form-data="imageForm"
    @submit="submitImage"
    @cancel="showImageModal = false"
  />
  </div>

</template>

<script setup>
import { ref, reactive } from 'vue';
import HeaderSection from './HeaderSection.vue';
import FunctionSection from './FunctionSection.vue';
import RecommendSection from './RecommendSection.vue';
import UploadModal from './UploadModal.vue';
import VideoUploadModal from "@/components/VideoUploadModal.vue";
import ImageUploadModal from "@/components/ImageUploadModal.vue";
import Ai from "@/components/ai.vue";

// 搜索/对话输入
const searchInput = ref('');
// 控制上传弹窗显示
const showUploadModal = ref(false);
const showVideoModal = ref(false);  // 新增视频上传弹窗
const showImageModal = ref(false);  // 新增图片上传弹窗



// 上传表单数据
const uploadForm = reactive({
  title: '',
  department: '',
  file: null,
  permission: 'admin'
});

// 功能方法
const handleModelDialog = () => {
  if (searchInput.value.trim()) {
    console.log(`向模型发送：${searchInput.value}`);
  } else {
    alert('请输入对话内容');
  }
};



const handleUpdate = () => {
  window.open('http://localhost:9001/browser/medical-docs-bucket/');  // 打开更新页面
};


// 提交上传
const submitUpload = async (data) => {
  // 表单验证
  if (!data.title) {
    alert('请填写文档标题');
    return;
  }
  if (!data.department) {
    alert('请选择所属科室');
    return;
  }
  if (!data.file) {
    alert('请选择要上传的文件');
    return;
  }

  try {
    // 模拟上传请求（实际项目替换为真实接口）
    console.log('开始上传文档：', data);
    // 构建FormData（文件上传必须用FormData）
    const formData = new FormData();
    formData.append('title', data.title);
    formData.append('department', data.department);
    formData.append('permission', data.permission);
    formData.append('file', data.file);

    // 示例：await fetch('/api/upload', { method: 'POST', body: formData });

    alert('文档上传成功！');
    showUploadModal.value = false;

    // 重置表单
    Object.assign(uploadForm, {
      title: '',
      department: '',
      file: null,
      permission: 'admin'
    });
  } catch (error) {
    console.error('上传失败:', error);
    alert('上传失败，请重试！');
  }
};


// 视频上传表单数据
const videoForm = reactive({
  title: '',
  department: '',
  file: null,
  permission: 'admin'
});

// 图片上传表单数据
const imageForm = reactive({
  title: '',
  department: '',
  file: null,
  permission: 'admin'
});

// 提交视频上传
const submitVideo = async (data) => {
  if (!data.title) {
    alert('请填写视频标题');

    return;
  }
  if (!data.department) {
    alert('请选择所属科室');
    return;
  }
  if (!data.file) {
    alert('请选择要上传的视频文件');
    return;
  }

  try {
    const formData = new FormData();
    formData.append('title', data.title);
    formData.append('department', data.department);
    formData.append('permission', data.permission);
    formData.append('file', data.file);

    // 示例：await fetch('/api/upload-video', { method: 'POST', body: formData });

    alert('视频上传成功！');
    showVideoModal.value = false;

    // 重置表单
    Object.assign(videoForm, {
      title: '',
      department: '',
      file: null,
      permission: 'admin'
    });
  } catch (error) {
    console.error('上传失败:', error);
    alert('上传失败，请重试！');
  }
};

// 提交图片上传
const submitImage = async (data) => {
  if (!data.title) {
    alert('请填写图片标题');
    return;
  }
  if (!data.department) {
    alert('请选择所属科室');
    return;
  }
  if (!data.file) {
    alert('请选择要上传的图片文件');
    return;
  }

  try {
    const formData = new FormData();
    formData.append('title', data.title);
    formData.append('department', data.department);
    formData.append('permission', data.permission);
    formData.append('file', data.file);

    // 示例：await fetch('/api/upload-image', { method: 'POST', body: formData });

    alert('图片上传成功！');
    showImageModal.value = false;

    // 重置表单
    Object.assign(imageForm, {
      title: '',
      department: '',
      file: null,
      permission: 'admin'
    });
  } catch (error) {
    console.error('上传失败:', error);
    alert('上传失败，请重试！');
  }
};



</script>


<style scoped>
.medical-system {
  background-color: #f8fafc;
  min-height: 100vh;
  width: 100%;
}
</style>