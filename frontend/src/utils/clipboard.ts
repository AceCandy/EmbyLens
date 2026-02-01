/**
 * Clipboard Utility
 */

export async function copyText(text: string): Promise<boolean> {
  if (!text) return false
  
  // 1. 尝试现代 API
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text)
      return true
    } catch (err) {
      console.warn('Modern clipboard API failed', err)
    }
  }
  
  // 2. 尝试事件注入方案 (对 HTTP 环境更友好)
  return copyTextFallback(text)
}

/**
 * 核心回退方案：利用 copy 事件监听器注入数据
 */
export function copyTextFallback(text: string): boolean {
  if (!text) return false

  let success = false
  const listener = (e: ClipboardEvent) => {
    if (e.clipboardData) {
      e.clipboardData.setData('text/plain', text)
      e.preventDefault()
      success = true
    }
  }

  // 绑定监听器 -> 触发复制指令 -> 移除监听器
  document.addEventListener('copy', listener)
  try {
    const result = document.execCommand('copy')
    // 如果 execCommand 返回 false 且监听器没跑，那才是真的失败
    if (!result) {
      console.warn('execCommand returned false')
    }
  } catch (err) {
    console.error('execCommand threw error', err)
  }
  document.removeEventListener('copy', listener)

  // 如果事件方案失败，最后再尝试一次 textarea 方案
  if (!success) {
    const textArea = document.createElement("textarea")
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.left = '-9999px'
    textArea.style.top = '0'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    try {
      success = document.execCommand('copy')
    } catch (err) {}
    document.body.removeChild(textArea)
  }

  return success
}

export function copyElementContent(selector: string): boolean {
  const element = document.querySelector(selector)
  if (!element) return false
  const range = document.createRange()
  range.selectNodeContents(element)
  const selection = window.getSelection()
  if (!selection) return false
  selection.removeAllRanges()
  selection.addRange(range)
  try {
    return document.execCommand('copy')
  } catch (err) {
    return false
  } finally {
    selection.removeAllRanges()
  }
}
