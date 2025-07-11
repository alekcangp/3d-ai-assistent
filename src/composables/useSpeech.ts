import { ref } from 'vue'

declare var SpeechRecognition: any;

export const speechAmplitude = ref<number>(0)
export const isListening = ref(false)

export function useSpeech() {
  let recognition: any = null
  let synthesis: SpeechSynthesis | null = null

  const initializeSpeech = () => {
    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognition = new SpeechRecognition()
      recognition.continuous = false
      recognition.interimResults = false
      recognition.lang = 'en-US'
    }
    // Initialize Speech Synthesis
    if ('speechSynthesis' in window) {
      synthesis = window.speechSynthesis
    }
  }

  const startListening = (callback: (transcript: string) => void, lang: string = 'ru-RU', onError?: (error: string) => void) => {
    // Always re-initialize recognition for reliability
      initializeSpeech()
    if (!recognition) {
      console.warn('Speech recognition not supported')
      return
    }
    recognition.lang = lang;
    if (isListening.value) return
    isListening.value = true
    // Clean up previous event handlers
    recognition.onresult = null
    recognition.onerror = null
    recognition.onend = null
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript
      callback(transcript)
    }
    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('Speech recognition error:', event.error)
      isListening.value = false
      if (onError) onError(event.error)
    }
    recognition.onend = () => {
      isListening.value = false
    }
    try {
      recognition.start()
    } catch (error) {
      console.error('Failed to start speech recognition:', error)
      isListening.value = false
    }
  }

  const stopListening = () => {
    if (recognition && isListening.value) {
      recognition.stop()
      isListening.value = false
    }
  }

  const getVoicesAsync = (): Promise<SpeechSynthesisVoice[]> => {
    return new Promise((resolve) => {
      const voices = synthesis?.getVoices() || [];
      if (voices.length) {
        resolve(voices);
      } else {
        window.speechSynthesis.onvoiceschanged = () => {
          resolve(synthesis?.getVoices() || []);
        };
      }
    });
  };

  const speak = async (text: string, onBoundary?: () => void, lang: string = 'ru-RU'): Promise<void> => {
      if (!synthesis) {
        initializeSpeech()
      }

      if (!synthesis) {
        console.warn('Speech synthesis not supported')
        return
      }

      // Cancel any ongoing speech
      synthesis.cancel()

      const utterance = new SpeechSynthesisUtterance(text)
      
      // Configure voice settings
      utterance.rate = 0.9
      utterance.pitch = 1.0
      utterance.volume = 0.8
      utterance.lang = lang

      // Wait for voices to be loaded
      const voices = await getVoicesAsync()
      
      // Prefer a voice that matches the requested language
      let preferredVoice = voices.find(voice => voice.lang === lang && (voice.name.includes('Natural') || voice.name.includes('Enhanced') || voice.name.includes('Premium')))
        || voices.find(voice => voice.lang === lang)
        || voices.find(voice => voice.lang.startsWith(lang.split('-')[0]))
        || voices.find(voice => voice.lang.startsWith('ru'))
        || voices.find(voice => voice.lang.startsWith('en'))
      
      if (preferredVoice) {
        utterance.voice = preferredVoice
      }

      if (onBoundary) {
        utterance.onboundary = () => {
          onBoundary()
        }
      }

      return new Promise((resolve, reject) => {
        utterance.onend = () => {
          if ('speechSynthesis' in window && 'AudioContext' in window) {
            const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)()
            const analyser = audioCtx.createAnalyser()
            analyser.fftSize = 2048
            const dataArray = new Uint8Array(analyser.fftSize)
            let animationId: number | null = null

            // Create a dummy oscillator to keep the context alive (Safari fix)
            const osc = audioCtx.createOscillator()
            osc.connect(audioCtx.destination)
            osc.start()
            osc.stop(audioCtx.currentTime + 0.01)

            // Try to capture system audio (speech synthesis output)
            // This only works if the browser supports audio capture from speech synthesis
            // Fallback: set amplitude to 0.5 while speaking
            function updateAmplitude() {
              analyser.getByteTimeDomainData(dataArray)
              // Calculate RMS amplitude
              let sum = 0
              for (let i = 0; i < dataArray.length; i++) {
                const val = (dataArray[i] - 128) / 128
                sum += val * val
              }
              const rms = Math.sqrt(sum / dataArray.length)
              speechAmplitude.value = rms
              animationId = requestAnimationFrame(updateAmplitude)
            }

            // Start amplitude updates
            speechAmplitude.value = 0.3
            animationId = requestAnimationFrame(updateAmplitude)

            // When speech ends, stop updates
            const cleanup = () => {
              if (animationId) cancelAnimationFrame(animationId)
              speechAmplitude.value = 0
              if (audioCtx && audioCtx.state !== 'closed') audioCtx.close()
            }
            (window as any).speechSynthesis.addEventListener('end', cleanup, { once: true })
          } else {
            // Fallback: set amplitude to 0.3 while speaking
            speechAmplitude.value = 0.3;
            (window as any).speechSynthesis.addEventListener('end', () => { speechAmplitude.value = 0 }, { once: true })
          }
          resolve()
        }
        utterance.onerror = (event) => {
          console.error('Speech synthesis error:', event)
          reject(event)
        }
        if (synthesis) {
          synthesis.speak(utterance)
        }
      })
  }

  const stopSpeaking = () => {
    if (synthesis) {
      synthesis.cancel()
    }
  }

  // Initialize on first use
  initializeSpeech()

  return {
    startListening,
    stopListening,
    speak,
    stopSpeaking,
    isListening,
    isSupported: !!recognition && !!synthesis
  }
}

// Extend Window interface for TypeScript
declare global {
  interface Window {
    SpeechRecognition: any
    webkitSpeechRecognition: any
  }
}

type SpeechRecognitionErrorEvent = {
  error: string;
  message?: string;
};