<template>
  <div class="bg-white border-2 border-gray-200 rounded-xl p-5 space-y-4">

    <!-- État : prêt -->
    <div v-if="state === 'idle'" class="text-center space-y-3">
      <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto">
        <i class="pi pi-microphone text-2xl text-gray-500"></i>
      </div>
      <p class="text-sm text-gray-600">Appuyez pour commencer l'enregistrement</p>
      <Button
        label="Démarrer l'enregistrement"
        icon="pi pi-microphone"
        @click="startRecording"
      />
    </div>

    <!-- État : enregistrement -->
    <div v-else-if="state === 'recording'" class="text-center space-y-3">
      <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto animate-pulse">
        <i class="pi pi-microphone text-2xl text-red-600"></i>
      </div>
      <div class="flex items-center justify-center gap-2">
        <div class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
        <span class="text-sm font-medium text-red-600">Enregistrement en cours</span>
        <span class="font-mono text-sm text-gray-600">{{ formattedDuration }}</span>
      </div>

      <!-- Visualiseur audio simple -->
      <div class="flex items-center justify-center gap-1 h-8">
        <div
          v-for="i in 12"
          :key="i"
          class="w-1 bg-red-400 rounded-full transition-all"
          :style="{ height: `${audioLevels[i - 1] || 4}px` }"
        />
      </div>

      <Button
        label="Arrêter"
        icon="pi pi-stop"
        severity="danger"
        @click="stopRecording"
      />
    </div>

    <!-- État : uploading -->
    <div v-else-if="state === 'uploading'" class="text-center space-y-3">
      <ProgressSpinner style="width: 40px; height: 40px" />
      <p class="text-sm text-gray-500">Envoi en cours...</p>
    </div>

    <!-- État : terminé -->
    <div v-else-if="state === 'done'" class="space-y-3">
      <div class="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
        <i class="pi pi-check-circle text-green-600 text-xl"></i>
        <div class="flex-1">
          <p class="text-sm font-medium text-green-800">Audio enregistré</p>
          <p class="text-xs text-green-600">{{ formattedDuration }} • Enregistrement {{ recordCount }}</p>
        </div>
        <Button
          icon="pi pi-refresh"
          text
          severity="secondary"
          size="small"
          v-tooltip="'Recommencer'"
          @click="resetRecording"
        />
      </div>

      <!-- Lecture de l'audio enregistré -->
      <div v-if="audioBlob" class="bg-gray-50 rounded-lg p-3">
        <audio
          :src="audioPreviewUrl as string"
          controls
          class="w-full h-8"
        />
      </div>
    </div>

    <!-- Erreur -->
    <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg">
      <p class="text-sm text-red-700">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  sessionId: string
  teilNumber: number
  questionId: string
}>()

const emit = defineEmits<{
  recorded: [audioFile: string, url: string]
}>()

type State = 'idle' | 'recording' | 'uploading' | 'done'

const state = ref<State>('idle')
const error = ref<string | null>(null)
const duration = ref(0)
const recordCount = ref(0)
const audioBlob = ref<Blob | null>(null)
const audioPreviewUrl = ref<string | null>(null)
const audioLevels = ref<number[]>(Array(12).fill(4))

let mediaRecorder: MediaRecorder | null = null
let chunks: BlobEvent['data'][] = []
let durationTimer: ReturnType<typeof setInterval> | null = null
let analyserInterval: ReturnType<typeof setInterval> | null = null
let audioContext: AudioContext | null = null
let analyser: AnalyserNode | null = null

const formattedDuration = computed(() => {
  const m = Math.floor(duration.value / 60)
  const s = duration.value % 60
  return `${m}:${s.toString().padStart(2, '0')}`
})

const startRecording = async () => {
  error.value = null
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    // Visualiseur
    audioContext = new AudioContext()
    const source = audioContext.createMediaStreamSource(stream)
    analyser = audioContext.createAnalyser()
    analyser.fftSize = 32
    source.connect(analyser)

    analyserInterval = setInterval(() => {
      if (!analyser) return
      const data = new Uint8Array(analyser.frequencyBinCount)
      analyser.getByteFrequencyData(data)
      audioLevels.value = Array.from(data.slice(0, 12)).map(v =>
        Math.max(4, Math.round((v / 255) * 32))
      )
    }, 100)

    // Recorder
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
    chunks = []

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data)
    }

    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunks, { type: 'audio/webm' })
      audioBlob.value = blob
      audioPreviewUrl.value = URL.createObjectURL(blob)
      stream.getTracks().forEach(t => t.stop())
      await uploadAudio(blob)
    }

    mediaRecorder.start(100)
    state.value = 'recording'
    duration.value = 0
    durationTimer = setInterval(() => duration.value++, 1000)

  } catch (err: any) {
    error.value = 'Impossible d\'accéder au microphone. Vérifiez les permissions.'
    console.error(err)
  }
}

const stopRecording = () => {
  if (mediaRecorder && state.value === 'recording') {
    mediaRecorder.stop()
    if (durationTimer) clearInterval(durationTimer)
    if (analyserInterval) clearInterval(analyserInterval)
    audioContext?.close()
    state.value = 'uploading'
  }
}

const uploadAudio = async (blob: Blob) => {
  state.value = 'uploading'
  try {
    const config = useRuntimeConfig()
    const { OpenAPI } = await import('#shared/api')
    const token = useCookie('access_token')

    const formData = new FormData()
    formData.append('file', blob, `sprechen_teil${props.teilNumber}.webm`)

    const response = await fetch(
      `${OpenAPI.BASE}/api/v1/sessions/${props.sessionId}/upload-audio?teil_number=${props.teilNumber}`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
        body: formData,
      }
    )

    if (!response.ok) throw new Error('Upload échoué')

    const data = await response.json()
    recordCount.value++
    state.value = 'done'
    emit('recorded', data.audio_file, data.url)

  } catch (err: any) {
    error.value = 'Erreur lors de l\'envoi. Réessayez.'
    state.value = 'idle'
    console.error(err)
  }
}

const resetRecording = () => {
  if (audioPreviewUrl.value) URL.revokeObjectURL(audioPreviewUrl.value)
  audioBlob.value = null
  audioPreviewUrl.value = null
  state.value = 'idle'
  duration.value = 0
  error.value = null
}

onUnmounted(() => {
  if (durationTimer) clearInterval(durationTimer)
  if (analyserInterval) clearInterval(analyserInterval)
  audioContext?.close()
  if (audioPreviewUrl.value) URL.revokeObjectURL(audioPreviewUrl.value)
})
</script>