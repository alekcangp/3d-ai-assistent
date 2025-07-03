import { openDB, type DBSchema, type IDBPDatabase } from 'idb'

interface AppDB extends DBSchema {
  settings: {
    key: string
    value: any
  }
  messages: {
    key: string
    value: any
  }
}

class LocalStorageService {
  private db: IDBPDatabase<AppDB> | null = null

  async init() {
    if (this.db) return this.db

    this.db = await openDB<AppDB>('ai-assistant', 1, {
      upgrade(db) {
        if (!db.objectStoreNames.contains('settings')) {
          db.createObjectStore('settings')
        }
        if (!db.objectStoreNames.contains('messages')) {
          db.createObjectStore('messages')
        }
      }
    })

    return this.db
  }

  async save(store: 'settings' | 'messages', key: string, value: any) {
    const db = await this.init()
    const serializableValue = JSON.parse(JSON.stringify(value))
    await db.put(store, serializableValue, key)
  }

  async load(store: 'settings' | 'messages', key: string, defaultValue: any = null) {
    try {
      const db = await this.init()
      const value = await db.get(store, key)
      return value !== undefined ? value : defaultValue
    } catch (error) {
      console.warn('Failed to load from IndexedDB, falling back to localStorage:', error)
      
      // Fallback to localStorage
      try {
        const stored = localStorage.getItem(`${store}_${key}`)
        return stored ? JSON.parse(stored) : defaultValue
      } catch {
        return defaultValue
      }
    }
  }
}

const storage = new LocalStorageService()

export function useLocalStorage() {
  const saveToStorage = async (key: string, value: any) => {
    try {
      const serializableValue = JSON.parse(JSON.stringify(value))
      await storage.save('settings', key, serializableValue)
    } catch (error) {
      console.warn('Failed to save to IndexedDB, using localStorage:', error)
      localStorage.setItem(key, JSON.stringify(value))
    }
  }

  const loadFromStorage = async (key: string, defaultValue: any = null) => {
    return await storage.load('settings', key, defaultValue)
  }

  const saveMessages = async (messages: any[]) => {
    try {
      await storage.save('messages', 'chat_history', messages)
    } catch (error) {
      console.warn('Failed to save messages to IndexedDB:', error)
    }
  }

  const loadMessages = async () => {
    return await storage.load('messages', 'chat_history', [])
  }

  return {
    saveToStorage,
    loadFromStorage,
    saveMessages,
    loadMessages
  }
}