# Qdrant 孤立向量清理工具使用说明

## 功能说明

该工具用于**自动清理 MinIO 中已删除文档对应的向量化数据**，避免 Qdrant 数据库中存在孤立的向量。

### 工作原理

1. **扫描 Qdrant** - 获取所有文档的元数据（文件名、MinIO 路径）
2. **检查 MinIO** - 验证每个文档是否仍然存在于 MinIO 中
3. **清理孤立向量** - 如果 MinIO 中不存在，则从 Qdrant 中删除对应向量
4. **记录日志** - 详细记录清理过程，便于追踪

---

## 使用方法

### 方式一：双击运行批处理文件（推荐）

直接双击 `run_cleanup.bat` 文件，然后选择：

```
1. 立即执行一次清理          # 手动清理一次
2. 启动定时服务              # 每天凌晨 2:00 自动执行
3. 仅测试，不实际执行        # 测试配置是否正确
```

### 方式二：命令行运行

```bash
# 手动清理一次
python cleanup_orphan_vectors.py

# 启动定时服务
python scheduler_cleanup.py
```

---

## 定时任务配置

### 默认配置
- **执行时间**：每天凌晨 2:00
- **日志文件**：`cleanup_orphan_vectors.log`
- **处理集合**：`medical_documents`

### 修改执行时间

编辑 `scheduler_cleanup.py`，找到这一行：

```python
schedule.every().day.at("02:00").do(job)
```

修改时间即可，例如改为凌晨 3:30：

```python
schedule.every().day.at("03:30").do(job)
```

---

## Windows 任务计划程序（可选）

如果需要更稳定的定时执行，可以使用 Windows 任务计划程序：

### 步骤：

1. **打开任务计划程序**
   - Win + R → 输入 `taskschd.msc` → 回车

2. **创建基本任务**
   - 右侧点击"创建基本任务"
   - 名称：`Qdrant 向量清理`
   - 触发器：每天
   - 时间：`02:00:00`
   - 操作：启动程序
   - 程序/脚本：`python.exe`
   - 添加参数：`cleanup_orphan_vectors.py`
   - 起始于：`D:\86152\Medical-Assistant\FastAPI1`

3. **高级设置**
   - 勾选"不管用户是否登录都要运行"
   - 勾选"使用最高权限运行"

---

## 日志查看

清理日志会保存在 `cleanup_orphan_vectors.log` 文件中，格式如下：

```
2026-03-23 15:30:11,233 - __main__ - INFO - 开始清理孤立的向量化数据
2026-03-23 15:30:11,236 - __main__ - INFO - 📊 处理集合：medical_documents
2026-03-23 15:30:11,236 - __main__ - INFO - 📋 集合中共有 0 个唯一文件
2026-03-23 15:30:11,237 - __main__ - INFO - ✅ 清理完成！检查文件数：0
```

---

## 常见问题

### Q1: 清理会误删吗？
不会。只有当 MinIO 中**确实不存在**该文档时，才会删除对应的向量。

### Q2: 清理会影响正在运行的服务吗？
不会。清理脚本独立运行，不影响 FastAPI 服务。

### Q3: 需要一直开着终端吗？
- 如果使用**定时服务模式**（选项 2），需要保持终端开启
- 如果使用**Windows 任务计划程序**，不需要开终端

### Q4: 多久执行一次合适？
建议**每天执行一次**，在业务低峰期（如凌晨 2 点）。

---

## 技术细节

### 核心函数

1. **`check_document_exists(minio_path)`**
   - 检查文档是否在 MinIO 中存在
   - 返回 True/False

2. **`delete_vectors_by_filename(collection_name, filename)`**
   - 根据文件名删除向量
   - 支持批量删除同一文件的所有分块向量

3. **`cleanup_orphan_vectors()`**
   - 主清理函数
   - 返回清理统计信息

### 数据处理流程

```
Qdrant 扫描 → 提取文件名 → MinIO 验证 → 删除孤立向量
     ↓
  记录日志 → 生成报告
```

---

## 注意事项

1. **首次运行前**确保 Qdrant 和 MinIO 服务正常运行
2. **定期查看日志**，确认清理工作正常
3. **不要同时运行多个清理进程**，避免冲突
4. **备份重要数据**，虽然不会误删，但建议定期备份

---

## 文件清单

```
FastAPI1/
├── cleanup_orphan_vectors.py    # 核心清理脚本
├── scheduler_cleanup.py         # 定时任务调度器
├── run_cleanup.bat             # Windows 启动脚本
└── README_CLEANUP.md           # 使用说明（本文件）
```
