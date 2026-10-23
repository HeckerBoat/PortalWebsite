<template>
  <div class="dashboard">
    <el-card shadow="never">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="keyword"
            placeholder="搜索文件名 / 标题 / 路径"
            clearable
            style="width: 320px"
            @keyup.enter="loadList"
            @clear="loadList"
          >
            <template #append>
              <el-button :icon="Search" @click="loadList" />
            </template>
          </el-input>
        </div>
        <div class="toolbar-right">
          <el-button type="primary" :icon="Refresh" :loading="scanning" @click="handleScan">
            扫描同步
          </el-button>
          <el-button :icon="RefreshRight" @click="loadList">刷新</el-button>
        </div>
      </div>

      <el-table :data="list" v-loading="loading" stripe style="width: 100%" empty-text="暂无数据，请点击扫描同步">
        <el-table-column type="index" label="#" width="55" />
        <el-table-column prop="filename" label="文件名" min-width="180" show-overflow-tooltip />
        <el-table-column prop="title" label="页面标题" min-width="220" show-overflow-tooltip />
        <el-table-column prop="url" label="访问 URL" min-width="260">
          <template #default="{ row }">
            <el-link type="primary" :href="row.url" target="_blank">{{ row.url }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="100">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="last_modified" label="最后修改" width="170">
          <template #default="{ row }">{{ formatDate(row.last_modified) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button type="success" size="small" :icon="CopyDocument" @click="copyUrl(row)">复制URL</el-button>
            <el-button type="primary" size="small" :icon="Edit" @click="openEdit(row)">编辑</el-button>
            <el-button type="info" size="small" :icon="View" @click="openPreview(row)">预览</el-button>
            <el-button type="danger" size="small" :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editVisible" title="编辑 HTML 信息" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="文件名">
          <el-input :value="editForm.filename" disabled />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="editForm.title" placeholder="页面标题" />
        </el-form-item>
        <el-form-item label="URL">
          <el-input v-model="editForm.url" placeholder="访问 URL" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" placeholder="备注描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 预览弹窗 -->
    <el-dialog v-model="previewVisible" :title="previewTitle" width="80%" top="5vh">
      <iframe :src="previewUrl" style="width: 100%; height: 70vh; border: 0" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Refresh, RefreshRight, CopyDocument, Edit, View, Delete,
} from '@element-plus/icons-vue'
import { listHtml, scanHtml, updateHtml, deleteHtml, type HtmlFileItem } from '@/api/html'

const list = ref<HtmlFileItem[]>([])
const loading = ref(false)
const scanning = ref(false)
const keyword = ref('')

const editVisible = ref(false)
const editForm = reactive<Partial<HtmlFileItem>>({})

const previewVisible = ref(false)
const previewUrl = ref('')
const previewTitle = ref('')

async function loadList() {
  loading.value = true
  try {
    const res = await listHtml(keyword.value || undefined)
    list.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function handleScan() {
  scanning.value = true
  try {
    const res = await scanHtml()
    ElMessage.success(`扫描完成：新增 ${res.data.added}，更新 ${res.data.updated}，删除 ${res.data.removed}`)
    await loadList()
  } finally {
    scanning.value = false
  }
}

function getFullUrl(url: string) {
  if (url.startsWith('http')) return url
  return `${window.location.origin}${url}`
}

async function copyUrl(row: HtmlFileItem) {
  const full = getFullUrl(row.url)
  try {
    await navigator.clipboard.writeText(full)
    ElMessage.success(`已复制：${full}`)
  } catch {
    // 降级方案
    const ta = document.createElement('textarea')
    ta.value = full
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    ElMessage.success(`已复制：${full}`)
  }
}

function openEdit(row: HtmlFileItem) {
  Object.assign(editForm, {
    id: row.id,
    filename: row.filename,
    title: row.title || '',
    url: row.url,
    description: row.description || '',
  })
  editVisible.value = true
}

async function saveEdit() {
  if (!editForm.id) return
  await updateHtml(editForm.id, {
    title: editForm.title || '',
    url: editForm.url || '',
    description: editForm.description || '',
  })
  ElMessage.success('保存成功')
  editVisible.value = false
  await loadList()
}

function openPreview(row: HtmlFileItem) {
  previewUrl.value = row.url
  previewTitle.value = row.title || row.filename
  previewVisible.value = true
}

async function handleDelete(row: HtmlFileItem) {
  await ElMessageBox.confirm(`确定删除记录 "${row.filename}" 吗？（不会删除磁盘文件）`, '提示', {
    type: 'warning',
  })
  await deleteHtml(row.id)
  ElMessage.success('删除成功')
  await loadList()
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

function formatDate(s: string | null) {
  if (!s) return '-'
  return s.replace('T', ' ').slice(0, 19)
}

onMounted(loadList)
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.toolbar-right {
  display: flex;
  gap: 8px;
}
</style>
