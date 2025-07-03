export interface AvatarConfig {
  model: string
  gender: 'neutral' | 'feminine' | 'masculine'
  outfit: 'casual' | 'formal' | 'creative' | 'tech'
  hairColor: string
  skinTone: string
  eyeColor: string
}

export interface PersonalityConfig {
  name: string
  age: number
  role: string
  style: string
  bio: string
  emotional_stability: number
  friendliness: number
  creativity: number
  curiosity: number
  formality: number
  empathy: number
  humor: number
  domain_knowledge: string[]
  quirks: string
  lore: string
  personality: string
  conversation_style: string
  description: string
  lang?: string
}

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
}

export interface AIConfig {
  model: string
  temperature: number
  maxTokens: number
}