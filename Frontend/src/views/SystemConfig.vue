<template>
  <div class="system-config">
    <el-card shadow="never">
      <div class="toolbar">
        <span class="tip">系统配置项会保存到 SQLite 数据库，启动时自动读取并同步到前端。</span>
        <el-button type="primary" :icon="Plus" @click="openCreate">新增配置</el-button>
      </div>

      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="key" label="配置键" min-width="180" />
        <el-table-column prop="value" label="配置值" min-width="260" show-overflow-tooltip />
        <el-table-column prop="description" label="说明" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" :icon="Edit" @click="openEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑配置' : '新增配置'" width="480px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="配置键">
          <el-input v-model="form.key" :disabled="isEdit" placeholder="如：theme" />
        </el-form-item>
        <el-form-item label="配置值">
          <el-input v-model="form.value" type="textarea" :rows="2" placeholder="配置值" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="form.description" placeholder="配置说明（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getConfig, setConfig, deleteConfig } from '@/api/config'

interface ConfigItem {
  key: string
  value: string
  description: string | null
}

const list = ref<ConfigItem[]>([])
const loading = ref(false)

const dialogVisible = ref(false)
const isEdit = ref(false)
const form = reactive({ key: '', value: '', description: '' })

async function loadList() {
  loading.value = true
  try {
    const res = await getConfig()
    list.value = res.data || []
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEdit.value = false
  Object.assign(form, { key: '', value: '', description: '' })
  dialogVisible.value = true
}

function openEdit(row: ConfigItem) {
  isEdit.value = true
  Object.assign(form, { key: row.key, value: row.value, description: row.description || '' })
  dialogVisible.value = true
}

async function save() {
  if (!form.key) return ElMessage.warning('请输入配置键')
  await setConfig(form.key, { value: form.value, description: form.description || undefined })
  ElMessage.success('保存成功')
  dialogVisible.value = false
  await loadList()
}

async function handleDelete(row: ConfigItem) {
  await ElMessageBox.confirm(`确定删除配置 "${row.key}" 吗？`, '提示', { type: 'warning' })
  await deleteConfig(row.key)
  ElMessage.success('删除成功')
  await loadList()
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
.tip {
  color: #909399;
  font-size: 13px;
}
</style>
