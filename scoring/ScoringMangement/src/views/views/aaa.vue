const handleModify = (rowData) => {
  modifyDialogRef.value.admin_openDialog(rowData);
};

const emits = defineEmits(['refreshList']);
defineExpose({ admin_openDialog });
onMounted(() => {
  console.log('当前题目ID:', props.topicId);

  if (props.topicId) {
    loadTopicData(props.topicId);
  }
});