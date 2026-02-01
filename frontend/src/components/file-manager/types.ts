export interface FileItem {
  name: string
  path: string
  is_dir: boolean
  size?: number
  mtime?: number
  mode?: string
}

export interface FileProvider {
  ls: (hostId: number | string, path: string) => Promise<{ current_path: string; items: FileItem[] }>
  read: (hostId: number | string, path: string) => Promise<{ content: string }>
  write: (hostId: number | string, path: string, content: string) => Promise<any>
  action: (hostId: number | string, action: string, path: string, target?: string) => Promise<any>
  chmod: (hostId: number | string, data: any) => Promise<any>
}
