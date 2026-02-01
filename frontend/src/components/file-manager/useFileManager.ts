import { ref, reactive, computed, h } from 'vue'
import { useMessage, useDialog, NInput } from 'naive-ui'
import { getParentPath } from './utils'
import type { FileItem, FileProvider } from './types'

export function useFileManager(props: { hostId: number | string, provider: FileProvider, initialPath?: string }) {
  const message = useMessage()
  const dialog = useDialog()
  
  const loading = ref(false)
  const items = ref<FileItem[]>([])
  const currentPath = ref(props.initialPath || '/')
  const selectedPath = ref<string | null>(null)
  const pathParts = computed(() => currentPath.value.split('/').filter(p => p))

  const showPermissionModal = ref(false)
  const showEditor = ref(false)
  const showMkdirModal = ref(false)
  const showMkfileModal = ref(false)
  const activeItem = ref<FileItem | null>(null)
  const newDirName = ref('')
  const newFileName = ref('')

  const clipboard = reactive({
    path: '',
    name: '',
    type: 'copy' as 'copy' | 'cut'
  })

  const browse = async (path: string) => {
    loading.value = true
    selectedPath.value = null
    try {
      const res = await props.provider.ls(props.hostId, path)
      currentPath.value = res.current_path
      items.value = res.items
    } catch (e: any) {
      console.error('[FileManager] Browse failed:', e)
      message.error('加载失败: ' + (e.response?.data?.detail || e.message))
    } finally {
      loading.value = false
    }
  }

  const selectItem = (item: FileItem) => {
    selectedPath.value = item.path
  }

  const jumpTo = (index: number) => {
    const target = '/' + pathParts.value.slice(0, index + 1).join('/')
    browse(target)
  }

  const openEditor = (item: FileItem) => {
    activeItem.value = item
    showEditor.value = true
  }

  const copyToClipboard = (text: string) => {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(() => {
        message.success('已复制到剪贴板')
      }).catch(() => {
        fallbackCopy(text)
      })
    } else {
      fallbackCopy(text)
    }
  }

  const fallbackCopy = (text: string) => {
    const textArea = document.createElement("textarea")
    textArea.value = text
    textArea.style.position = "fixed"
    textArea.style.left = "-9999px"
    textArea.style.top = "0"
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    try {
      document.execCommand('copy')
      message.success('已复制到剪贴板')
    } catch (err) {
      message.error('无法复制路径')
    }
    document.body.removeChild(textArea)
  }

  const copyPath = (path: string) => {
    copyToClipboard(path)
  }

  const handleCopy = (item: FileItem, type: 'copy' | 'cut' = 'copy') => {
    clipboard.path = item.path
    clipboard.name = item.name
    clipboard.type = type
    message.info(type === 'copy' ? '已复制' : '已剪切')
  }

  const handlePaste = async () => {
    if (!clipboard.path) return
    loading.value = true
    try {
      const target = (currentPath.value.endsWith('/') ? currentPath.value : currentPath.value + '/') + clipboard.name
      await props.provider.action(props.hostId, clipboard.type === 'copy' ? 'copy' : 'move', clipboard.path, target)
      message.success('粘贴成功')
      browse(currentPath.value)
    } catch (e: any) {
      message.error('粘贴失败: ' + (e.response?.data?.detail || e.message))
    } finally {
      loading.value = false
    }
  }

  const createFile = async (name: string) => {
    if (!name) return false
    try {
      const target = (currentPath.value.endsWith('/') ? currentPath.value : currentPath.value + '/') + name
      await props.provider.write(props.hostId, target, '')
      message.success('文件已创建')
      browse(currentPath.value)
      return true
    } catch (e: any) {
      message.error('创建失败: ' + (e.response?.data?.detail || e.message))
      return false
    }
  }

  const onMkdir = async () => {
    if (!newDirName.value) return
    try {
      const target = (currentPath.value.endsWith('/') ? currentPath.value : currentPath.value + '/') + newDirName.value
      await props.provider.action(props.hostId, 'mkdir', target)
      message.success('文件夹已创建')
      newDirName.value = ''
      showMkdirModal.value = false
      browse(currentPath.value)
    } catch (e: any) {
      message.error('创建失败: ' + (e.response?.data?.detail || e.message))
    }
  }

  const handleAction = async (key: string, item: FileItem) => {
    if (key === 'rename') {
      let newName = item.name
      dialog.info({
        title: '重命名',
        content: () => h(NInput, { 
          defaultValue: item.name, 
          onUpdateValue: (v) => newName = v,
          placeholder: '输入新名称' 
        }),
        positiveText: '确定',
        onPositiveClick: async () => {
          try {
            const target = getParentPath(item.path) + '/' + newName
            await props.provider.action(props.hostId, 'rename', item.path, target)
            message.success('重命名成功')
            browse(currentPath.value)
          } catch (e: any) {
            message.error('重命名失败')
          }
        }
      })
    } else if (key === 'delete') {
      dialog.warning({
        title: '确认删除',
        content: `确定要删除 ${item.name} 吗？此操作不可撤销。`,
        positiveText: '确认',
        onPositiveClick: async () => {
          try {
            await props.provider.action(props.hostId, 'delete', item.path)
            message.success('已删除')
            browse(currentPath.value)
          } catch (e: any) {
            console.error('[FileManager] Delete failed:', e)
            message.error('删除失败: ' + (e.response?.data?.detail || e.message))
          }
        }
      })
    } else if (key === 'chmod') {
      activeItem.value = item
      showPermissionModal.value = true
    }
  }

  return {
    loading, items, currentPath, pathParts, selectedPath,
    showPermissionModal, showEditor, showMkdirModal, showMkfileModal, activeItem, newDirName, newFileName,
    clipboard,
    browse, jumpTo, handleAction, openEditor, onMkdir, getParentPath, selectItem,
    copyPath, handleCopy, handlePaste, createFile
  }
}