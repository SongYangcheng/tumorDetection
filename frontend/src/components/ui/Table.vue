<template>
    <div class="table-wrapper">
        <!-- 表头和操作栏 -->
        <div class="table-header">
            <h3 v-if="title" class="table-title">{{ title }}</h3>
            <div class="table-actions">
                <slot name="actions"></slot>
            </div>
        </div>

        <!-- 搜索栏 -->
        <div v-if="searchable" class="search-bar">
            <input v-model="searchQuery" type="text" placeholder="搜索..." class="search-input" />
        </div>

        <!-- 表格 -->
        <div class="table-container">
            <table class="data-table">
                <!-- 表头 -->
                <thead>
                    <tr class="table-header-row">
                        <th v-if="selectable" class="col-checkbox">
                            <input v-model="selectAll" type="checkbox" class="checkbox" @change="toggleSelectAll" />
                        </th>
                        <th v-for="column in columns" :key="column.key" class="table-header-cell"
                            :style="{ width: column.width }" @click="sortBy(column.key)">
                            <div class="header-content">
                                <span>{{ column.label }}</span>
                                <span v-if="sortKey === column.key" class="sort-icon">
                                    {{ sortAsc ? '▲' : '▼' }}
                                </span>
                            </div>
                        </th>
                        <th v-if="actions" class="col-actions">操作</th>
                    </tr>
                </thead>

                <!-- 表体 -->
                <tbody>
                    <tr v-for="(row, index) in paginatedData" :key="index" class="table-body-row"
                        :class="{ selected: selectedRows.includes(index) }">
                        <!-- 复选框 -->
                        <td v-if="selectable" class="col-checkbox">
                            <input v-model="selectedRows" :value="index" type="checkbox" class="checkbox" />
                        </td>

                        <!-- 数据列 -->
                        <td v-for="column in columns" :key="column.key" class="table-cell"
                            :style="{ width: column.width }">
                            <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
                                {{ formatCellValue(row[column.key], column) }}
                            </slot>
                        </td>

                        <!-- 操作列 -->
                        <td v-if="actions" class="col-actions">
                            <div class="action-buttons">
                                <slot name="row-actions" :row="row">
                                    <button v-for="action in actions" :key="action.label" class="action-btn"
                                        :title="action.label" @click="action.handler(row)">
                                        {{ action.label }}
                                    </button>
                                </slot>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>

            <!-- 空状态 -->
            <div v-if="filteredData.length === 0" class="empty-state">
                <p class="empty-icon">📭</p>
                <p class="empty-text">{{ emptyText }}</p>
            </div>
        </div>

        <!-- 分页 -->
        <div v-if="paginated" class="table-pagination">
            <div class="pagination-info">
                显示 {{ (currentPage - 1) * pageSize + 1 }} 到
                {{ Math.min(currentPage * pageSize, filteredData.length) }}
                条，共 {{ filteredData.length }} 条
            </div>

            <div class="pagination-controls">
                <button class="pagination-btn" :disabled="currentPage === 1" @click="currentPage--">
                    上一页
                </button>
                <span class="pagination-page">第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
                <button class="pagination-btn" :disabled="currentPage === totalPages" @click="currentPage++">
                    下一页
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, PropType } from 'vue'

interface Column {
    key: string
    label: string
    width?: string
    format?: (value: any) => string
    type?: 'text' | 'number' | 'date' | 'status'
}

interface Action {
    label: string
    handler: (row: any) => void
}

const props = defineProps({
    title: String,
    columns: {
        type: Array as PropType<Column[]>,
        required: true,
    },
    data: {
        type: Array as PropType<any[]>,
        required: true,
    },
    actions: {
        type: Array as PropType<Action[]>,
        default: null,
    },
    selectable: {
        type: Boolean,
        default: false,
    },
    searchable: {
        type: Boolean,
        default: false,
    },
    paginated: {
        type: Boolean,
        default: true,
    },
    pageSize: {
        type: Number,
        default: 10,
    },
    emptyText: {
        type: String,
        default: '暂无数据',
    },
})

// 状态
const searchQuery = ref('')
const currentPage = ref(1)
const selectedRows = ref<number[]>([])
const selectAll = ref(false)
const sortKey = ref<string>('')
const sortAsc = ref(true)

// 过滤数据
const filteredData = computed(() => {
    let filtered = [...props.data]

    // 搜索过滤
    if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(row =>
            props.columns.some(col =>
                String(row[col.key]).toLowerCase().includes(query)
            )
        )
    }

    // 排序
    if (sortKey.value) {
        filtered.sort((a, b) => {
            const aVal = a[sortKey.value]
            const bVal = b[sortKey.value]

            if (typeof aVal === 'number' && typeof bVal === 'number') {
                return sortAsc.value ? aVal - bVal : bVal - aVal
            }

            const aStr = String(aVal).toLowerCase()
            const bStr = String(bVal).toLowerCase()
            return sortAsc.value ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr)
        })
    }

    return filtered
})

// 分页数据
const totalPages = computed(() => {
    if (!props.paginated) return 1
    return Math.ceil(filteredData.value.length / props.pageSize)
})

const paginatedData = computed(() => {
    if (!props.paginated) return filteredData.value

    const start = (currentPage.value - 1) * props.pageSize
    const end = start + props.pageSize
    return filteredData.value.slice(start, end)
})

// 格式化单元格值
const formatCellValue = (value: any, column: Column): string => {
    if (column.format) return column.format(value)

    if (value === null || value === undefined) return '-'

    switch (column.type) {
        case 'date':
            return new Date(value).toLocaleDateString('zh-CN')
        case 'number':
            return Number(value).toLocaleString()
        default:
            return String(value)
    }
}

// 排序
const sortBy = (key: string) => {
    if (sortKey.value === key) {
        sortAsc.value = !sortAsc.value
    } else {
        sortKey.value = key
        sortAsc.value = true
    }
}

// 全选
const toggleSelectAll = () => {
    if (selectAll.value) {
        selectedRows.value = paginatedData.value.map((_, index) => index)
    } else {
        selectedRows.value = []
    }
}

// 监听页码变化时重置全选
const selectAllComputed = computed({
    get: () => selectAll.value,
    set: (val) => {
        selectAll.value = val
    },
})
</script>

<style scoped>
.table-wrapper {
    display: grid;
    gap: 16px;
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px;
}

/* 表头 */
.table-header {
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    gap: 16px;
}

.table-title {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
}

.table-actions {
    display: flex;
    gap: 8px;
}

/* 搜索栏 */
.search-bar {
    display: flex;
    align-items: center;
}

.search-input {
    width: 100%;
    max-width: 300px;
    padding: 8px 12px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.04);
    color: var(--text);
    font-size: 13px;
}

.search-input:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

/* 表格容器 */
.table-container {
    overflow-x: auto;
    border-radius: 8px;
    border: 1px solid var(--border-color);
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

/* 表头行 */
.table-header-row {
    background: rgba(255, 255, 255, 0.02);
    border-bottom: 2px solid var(--border-color);
}

.table-header-cell {
    padding: 12px 16px;
    text-align: left;
    color: var(--text-muted);
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-size: 11px;
    cursor: pointer;
    user-select: none;
    transition: background 0.2s;
}

.table-header-cell:hover {
    background: rgba(255, 255, 255, 0.05);
}

.header-content {
    display: flex;
    align-items: center;
    gap: 6px;
}

.sort-icon {
    font-size: 10px;
    color: #2563eb;
}

/* 表体行 */
.table-body-row {
    border-bottom: 1px solid var(--border-color);
    transition: all 0.2s;
}

.table-body-row:hover {
    background: rgba(255, 255, 255, 0.03);
}

.table-body-row.selected {
    background: rgba(37, 99, 235, 0.1);
}

/* 表格单元格 */
.table-cell {
    padding: 12px 16px;
    color: var(--text);
    word-break: break-word;
}

/* 复选框列 */
.col-checkbox {
    width: 40px;
    padding: 12px;
    text-align: center;
}

.checkbox {
    cursor: pointer;
    width: 16px;
    height: 16px;
    accent-color: #2563eb;
}

/* 操作列 */
.col-actions {
    width: 120px;
    padding: 12px 16px;
    text-align: center;
}

.action-buttons {
    display: flex;
    gap: 6px;
    justify-content: center;
}

.action-btn {
    padding: 4px 8px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: transparent;
    color: #2563eb;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.action-btn:hover {
    background: rgba(37, 99, 235, 0.1);
    border-color: #2563eb;
}

/* 空状态 */
.empty-state {
    grid-column: 1 / -1;
    text-align: center;
    padding: 40px 20px;
    color: var(--text-muted);
}

.empty-icon {
    font-size: 48px;
    margin: 0 0 12px;
}

.empty-text {
    margin: 0;
    font-size: 14px;
}

/* 分页 */
.table-pagination {
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    gap: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--border-color);
    font-size: 12px;
    color: var(--text-muted);
}

.pagination-info {
    margin: 0;
}

.pagination-controls {
    display: flex;
    align-items: center;
    gap: 8px;
}

.pagination-btn {
    padding: 6px 12px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: transparent;
    color: #2563eb;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
    background: rgba(37, 99, 235, 0.1);
    border-color: #2563eb;
}

.pagination-btn:disabled {
    color: var(--text-muted);
    cursor: not-allowed;
    opacity: 0.5;
}

.pagination-page {
    min-width: 100px;
    text-align: center;
}

/* 响应式 */
@media (max-width: 768px) {
    .table-wrapper {
        padding: 12px;
        gap: 12px;
    }

    .table-header {
        grid-template-columns: 1fr;
    }

    .table-cell {
        padding: 8px 12px;
        font-size: 12px;
    }

    .table-header-cell {
        padding: 8px 12px;
        font-size: 10px;
    }

    .action-btn {
        padding: 2px 6px;
        font-size: 10px;
    }

    .table-pagination {
        grid-template-columns: 1fr;
        gap: 12px;
    }

    .pagination-controls {
        width: 100%;
        justify-content: space-between;
    }
}
</style>
