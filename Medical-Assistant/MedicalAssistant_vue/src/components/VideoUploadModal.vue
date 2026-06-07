<template>
  <div class="modal-mask" v-if="visible" @click="handleMaskClick"></div>
  <div class="upload-modal" v-if="visible">
    <div class="modal-header">
      <h3>上传医学视频</h3>
    </div>
    <div class="modal-body">
      <form class="upload-form">
        <div class="form-item">
          <label class="form-label">视频标题：</label>
          <input
            v-model="formData.title"
            class="form-input"
            placeholder="请输入视频标题"
          />
        </div>
        <div class="form-item">
          <label class="form-label">所属科室：</label>
          <select v-model="formData.department" class="form-select">
            <option value="">请选择科室</option>
            <option value="内科">内科</option>
            <option value="外科">外科</option>
            <option value="儿科">儿科</option>
            <option value="急诊科">急诊科</option>
            <option value="妇产科">妇产科</option>
            <option value="神经科">神经科</option>
          </select>
        </div>
        <div class="form-item">
          <label class="form-label">视频文件：</label>
          <div class="file-upload-wrapper">
            <input
              type="file"
              class="file-input"
              accept="video/*"
              @change="handleFileChange"
            />
            <span class="file-placeholder">
              {{ selectedFileName || "点击选择视频文件（支持MP4/AVI/MOV）" }}
            </span>
          </div>
        </div>
        <div class="form-item">
          <label class="form-label">访问权限：</label>
          <div class="permission-radio-group">
            <label class="radio-item">
              <input
                type="radio"
                name="permission"
                value="admin"
                v-model="formData.permission"
              />
              仅管理员可见
            </label>
            <label class="radio-item">
              <input
                type="radio"
                name="permission"
                value="doctor"
                v-model="formData.permission"
              />
              对应科室医生可见
            </label>
            <label class="radio-item">
              <input
                type="radio"
                name="permission"
                value="all"
                v-model="formData.permission"
              />
              所有用户可见
            </label>
          </div>
        </div>
      </form>
    </div>
    <div class="modal-footer">
      <button class="btn cancel-btn" @click="handleCancel">取消</button>
      <button class="btn submit-btn" @click.prevent="handleSubmit">确认上传</button>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, watch } from 'vue';
import { upload_medical } from "@/api/api.js";

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  formData: {
    type: Object,
    required: true,
    default: () => ({
      title: '',
      department: '',
      permission: 'admin',
      file: null
    })
  }
});

const emit = defineEmits(['submit', 'cancel']);

const selectedFileName = ref('');

watch(() => props.visible, (val) => {
  if (!val) {
    selectedFileName.value = '';
  }
});

const handleFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    selectedFileName.value = file.name;
    props.formData.file = file;
  }
};

const handleMaskClick = () => {
  emit('cancel');
};

const handleCancel = () => {
  emit('cancel');
};

const handleSubmit = async () => {
  if (!props.formData.title.trim()) {
    alert('请输入视频标题');
    return;
  }
  if (!props.formData.department) {
    alert('请选择所属科室');
    return;
  }
  if (!props.formData.file) {
    alert('请选择要上传的视频文件');
    return;
  }

  try {
    const formData = new FormData();
    formData.append('title', props.formData.title);
    formData.append('department', props.formData.department);
    formData.append('permission', props.formData.permission);
    formData.append('files', props.formData.file);

    await upload_medical(`/upload/medical-videos/`, formData);
    alert('上传视频成功！')
  } catch (error) {
    console.error('422错误详情：', error.response?.data);
    console.error('上传失败:', error);
    alert('上传失败，请重试！');
  }
};
</script>

<style scoped>
/* 遮罩层 */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

/* 弹窗容器 */
.upload-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
}

/* 弹窗标题 */
.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333333;
}

/* 表单内容区 */
.modal-body {
  padding: 20px;
}

.upload-form {
  width: 100%;
}

/* 表单项 */
.form-item {
  margin-bottom: 18px;
  display: flex;
  align-items: flex-start;
}

/* 标签 */
.form-label {
  width: 100px;
  text-align: right;
  padding-right: 12px;
  font-size: 14px;
  color: #333;
  line-height: 32px;
}

/* 输入框 */
.form-input {
  flex: 1;
  height: 32px;
  padding: 0 8px;
  border: 1px solid #dcdcdc;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
}

.form-input:focus {
  border-color: #409eff;
}

/* 下拉框 */
.form-select {
  flex: 1;
  height: 32px;
  padding: 0 8px;
  border: 1px solid #dcdcdc;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  background: #fff;
}

/* 文件上传框 */
.file-upload-wrapper {
  flex: 1;
  position: relative;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 32px;
  opacity: 0;
  cursor: pointer;
  z-index: 1;
}

.file-placeholder {
  display: block;
  width: 100%;
  height: 32px;
  line-height: 32px;
  padding: 0 8px;
  border: 1px solid #dcdcdc;
  border-radius: 4px;
  font-size: 14px;
  color: #666;
  background: #fff;
}

/* 权限单选框 */
.permission-radio-group {
  flex: 1;
  display: flex;
  gap: 16px;
  padding-top: 6px;
}

.radio-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #333;
  cursor: pointer;
}

.radio-item input {
  margin-right: 4px;
  accent-color: #409eff;
}

/* 弹窗底部按钮 */
.modal-footer {
  padding: 12px 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: center;
  gap: 20px;
}

.btn {
  padding: 8px 24px;
  border-radius: 4px;
  border: 1px solid #dcdcdc;
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn {
  background-color: #ffffff;
  color: #666666;
}

.cancel-btn:hover {
  background-color: #f5f5f5;
}

.submit-btn {
  background-color: #409eff;
  color: white;
  border-color: #409eff;
}

.submit-btn:hover {
  background-color: #66b1ff;
}
</style>
