<template>
  <div class="avatar-container">
    <canvas 
      ref="canvasRef" 
      class="avatar-canvas"
      :class="{ 'listening': isListening, 'speaking': isSpeaking }"
    ></canvas>
    <div class="avatar-status">
      <div v-if="isListening" class="status-indicator listening">
        <div class="pulse"></div>
        Listening...
      </div>
      <div v-else-if="isSpeaking" class="status-indicator speaking">
        <div class="wave"></div>
        Speaking...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { KTX2Loader } from 'three/examples/jsm/loaders/KTX2Loader.js'
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js'
import type { AvatarConfig } from '../types'

const props = defineProps<{
  avatarConfig: AvatarConfig
  isListening: boolean
  isSpeaking: boolean
  mouthOpenLevel?: number
  isDarkMode?: boolean
}>()

const canvasRef = ref<HTMLCanvasElement>()
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let avatar: THREE.Group
let animationId: number
let currentAnimation = 'idle'

// Animation mixer for avatar animations
let mixer: THREE.AnimationMixer
let animations: { [key: string]: THREE.AnimationAction } = {}

let faceMesh: THREE.Mesh | null = null
// let jawOpenIndex: number | null = null // Removed unused variable
// Add these for pupil morph targets
let eyeLookInL: number | undefined, eyeLookOutL: number | undefined, eyeLookUpL: number | undefined, eyeLookDownL: number | undefined;
let eyeLookInR: number | undefined, eyeLookOutR: number | undefined, eyeLookUpR: number | undefined, eyeLookDownR: number | undefined;

let animationTime = 0;

// For realistic animation
let lastBlink = Date.now()
let blinkDuration = 180 // ms
let isBlinking = false
let nextBlinkTime = Date.now() + 2000 + Math.random() * 2000
let browRaiseLevel = 0
let smileLevel = 0

// --- Random micro-expression state ---
type RandomFaceState = {
  [key: string]: { t: number; duration: number; target: number; value: number }
  browOuterUpL: { t: number; duration: number; target: number; value: number }
  browOuterUpR: { t: number; duration: number; target: number; value: number }
  cheekPuff: { t: number; duration: number; target: number; value: number }
  cheekSquintL: { t: number; duration: number; target: number; value: number }
  cheekSquintR: { t: number; duration: number; target: number; value: number }
  mouthSmileL: { t: number; duration: number; target: number; value: number }
  mouthSmileR: { t: number; duration: number; target: number; value: number }
  mouthFrownL: { t: number; duration: number; target: number; value: number }
  mouthFrownR: { t: number; duration: number; target: number; value: number }
  browDownL: { t: number; duration: number; target: number; value: number }
  browDownR: { t: number; duration: number; target: number; value: number }
  eyeWideL: { t: number; duration: number; target: number; value: number }
  eyeWideR: { t: number; duration: number; target: number; value: number }
  eyeSquintL: { t: number; duration: number; target: number; value: number }
  eyeSquintR: { t: number; duration: number; target: number; value: number }
  eyeBlinkL: { t: number; duration: number; target: number; value: number }
  eyeBlinkR: { t: number; duration: number; target: number; value: number }
  noseSneerL: { t: number; duration: number; target: number; value: number }
  noseSneerR: { t: number; duration: number; target: number; value: number }
}

const randomFaceState: RandomFaceState = {
  browOuterUpL: { t: 0, duration: 0, target: 0, value: 0 },
  browOuterUpR: { t: 0, duration: 0, target: 0, value: 0 },
  cheekPuff: { t: 0, duration: 0, target: 0, value: 0 },
  cheekSquintL: { t: 0, duration: 0, target: 0, value: 0 },
  cheekSquintR: { t: 0, duration: 0, target: 0, value: 0 },
  mouthSmileL: { t: 0, duration: 0, target: 0, value: 0 },
  mouthSmileR: { t: 0, duration: 0, target: 0, value: 0 },
  mouthFrownL: { t: 0, duration: 0, target: 0, value: 0 },
  mouthFrownR: { t: 0, duration: 0, target: 0, value: 0 },
  browDownL: { t: 0, duration: 0, target: 0, value: 0 },
  browDownR: { t: 0, duration: 0, target: 0, value: 0 },
  eyeWideL: { t: 0, duration: 0, target: 0, value: 0 },
  eyeWideR: { t: 0, duration: 0, target: 0, value: 0 },
  eyeSquintL: { t: 0, duration: 0, target: 0, value: 0 },
  eyeSquintR: { t: 0, duration: 0, target: 0, value: 0 },
  eyeBlinkL: { t: 0, duration: 0, target: 0, value: 0 },
  eyeBlinkR: { t: 0, duration: 0, target: 0, value: 0 },
  noseSneerL: { t: 0, duration: 0, target: 0, value: 0 },
  noseSneerR: { t: 0, duration: 0, target: 0, value: 0 },
}

// --- Random walk state for eyes ---
const randomEyeState = {
  x: 0,
  y: 0,
}

// --- Interactive gaze state ---
const gazeTarget = ref<{ x: number, y: number } | null>(null)
let lastUserGaze = 0;

let ambientLight: THREE.AmbientLight

// Persistent random walk for smooth breeze noise
let breezeNoise = { x: 0, y: 0, z: 0 };

function setGazeFromMouse(event: MouseEvent) {
  const rect = (canvasRef.value as HTMLCanvasElement).getBoundingClientRect();
  // Normalize to [-1, 1] with (0,0) center
  const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  const y = -(((event.clientY - rect.top) / rect.height) * 2 - 1);
  gazeTarget.value = { x: Math.max(-1, Math.min(1, x)), y: Math.max(-1, Math.min(1, y)) };
  lastUserGaze = performance.now();
}

function clearGaze() {
  gazeTarget.value = null;
}

function updateRandomFaceState() {
  const now = Date.now()
  for (const key in randomFaceState) {
    const state = randomFaceState[key]
    if (state.t === 0 || now > state.t + state.duration) {
      // Start a new random pulse
      state.t = now
      state.duration = 500 + Math.random() * 10000 // 0.5-1.5s
      state.target = 0.03 + Math.random() * 0.17 // amplitude
    } else {
      // Decay pulse
      const progress = (now - state.t) / state.duration
      state.value = state.target * Math.sin(Math.PI * progress) // smooth in/out
    }
  }
}

function updateRandomEyeState() {
  // Smaller random walk, even slower drift, clamp to [-0.04, 0.04]
  randomEyeState.x += (Math.random() - 0.5) * 0.001
  randomEyeState.y += (Math.random() - 0.5) * 0.001
  randomEyeState.x = Math.max(-0.04, Math.min(0.04, randomEyeState.x))
  randomEyeState.y = Math.max(-0.04, Math.min(0.04, randomEyeState.y))
}

const initThree = async () => {
  if (!canvasRef.value) return

  // Scene setup
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x000000)
  scene.background = null // Transparent background

  // Camera setup
  camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000)
  camera.position.set(0, 0, 3)

  // Renderer setup
  renderer = new THREE.WebGLRenderer({ 
    canvas: canvasRef.value, 
    alpha: true,
    antialias: true 
  })
  // Responsive: use smaller size for mobile
  const isMobile = window.innerWidth <= 768;
  const size = isMobile ? 200 : 300;
  renderer.setSize(size, size)
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap

  // Lighting
  ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambientLight)
  updateAmbientLight()

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(5, 5, 5)
  directionalLight.castShadow = true
  scene.add(directionalLight)

  // Create avatar
  await createAvatar()
  
  // Start render loop
  animate()
}

const createAvatar = async () => {
  const loader = new GLTFLoader()
  // Setup KTX2Loader for KTX2 compressed textures
  const ktx2Loader = new KTX2Loader()
    .setTranscoderPath('/libs/basis/')
    .detectSupport(renderer)
  loader.setKTX2Loader(ktx2Loader)
  // Set MeshoptDecoder directly
  loader.setMeshoptDecoder(MeshoptDecoder)
  loader.load('/facecap.glb', (gltf) => {
    console.log('GLB loaded', gltf)
    avatar = gltf.scene
    avatar.position.set(0, 0, 0)
    avatar.scale.set(1.3, 1.3, 1)
    // Apply normal-based rainbow effect
    avatar.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        (child as THREE.Mesh).material = new THREE.MeshNormalMaterial();
      }
    })
    scene.add(avatar)
    // Find face mesh with morph targets
    avatar.traverse((child) => {
      const influences = (child as THREE.Mesh).morphTargetInfluences;
      if (
        (child as THREE.Mesh).isMesh &&
        influences &&
        influences.length > 0 &&
        (child as THREE.Mesh).morphTargetDictionary
      ) {
        faceMesh = child as THREE.Mesh
        // Assign indices for eye pupil morph targets
        eyeLookInL = (child as THREE.Mesh).morphTargetDictionary?.["eyeLookIn_L"] ?? 0;
        eyeLookOutL = (child as THREE.Mesh).morphTargetDictionary?.["eyeLookOut_L"] ?? 0;
        eyeLookUpL = (child as THREE.Mesh).morphTargetDictionary?.["eyeLookUp_L"] ?? 0;
        eyeLookDownL = (child as THREE.Mesh).morphTargetDictionary?.["eyeLookDown_L"] ?? 0;
        eyeLookInR = (child as THREE.Mesh).morphTargetDictionary?.["eyeLookIn_R"] ?? 0;
        eyeLookOutR = (child as THREE.Mesh).morphTargetDictionary?.["eyeLookOut_R"] ?? 0;
        eyeLookUpR = (child as THREE.Mesh).morphTargetDictionary?.["eyeLookUp_R"] ?? 0;
        eyeLookDownR = (child as THREE.Mesh).morphTargetDictionary?.["eyeLookDown_R"] ?? 0;
      }
    })
    setupAnimations()
  }, undefined, (error) => {
    console.error('Error loading GLB:', error)
    alert('Failed to load avatar model: ' + (error instanceof Error ? error.message : String(error)))
  })
}

const setupAnimations = () => {
  // Create animation mixer
  mixer = new THREE.AnimationMixer(avatar)

  // Speaking animation - more dynamic movement
  const speakingTrackX = new THREE.NumberKeyframeTrack(
    '.rotation[x]',
    [0, 0.5, 1, 1.5, 2],
    [0, 0.1, 0, -0.1, 0]
  );
  const speakingTrackY = new THREE.NumberKeyframeTrack(
    '.rotation[y]',
    [0, 0.5, 1, 1.5, 2],
    [0, 0, 0, 0, 0]
  );
  const speakingTrackZ = new THREE.NumberKeyframeTrack(
    '.rotation[z]',
    [0, 0.5, 1, 1.5, 2],
    [0, 0, 0, 0, 0]
  );
  const speakingClip = new THREE.AnimationClip('speaking', 2, [speakingTrackX, speakingTrackY, speakingTrackZ]);
  animations.speaking = mixer.clipAction(speakingClip)
  animations.speaking.setLoop(THREE.LoopRepeat, Infinity)

  // Listening animation - attentive pose
  const listeningTrackX = new THREE.NumberKeyframeTrack(
    '.rotation[x]',
    [0, 1, 2],
    [0, 0, 0]
  );
  const listeningTrackY = new THREE.NumberKeyframeTrack(
    '.rotation[y]',
    [0, 1, 2],
    [0, 0.05, 0]
  );
  const listeningTrackZ = new THREE.NumberKeyframeTrack(
    '.rotation[z]',
    [0, 1, 2],
    [0, 0.1, 0]
  );
  const listeningClip = new THREE.AnimationClip('listening', 2, [listeningTrackX, listeningTrackY, listeningTrackZ]);
  animations.listening = mixer.clipAction(listeningClip)
  animations.listening.setLoop(THREE.LoopRepeat, Infinity)

  // Start with idle animation (no movement)
  playAnimation('idle')
}

const playAnimation = (animationName: string) => {
  if (currentAnimation === animationName) return

  // Fade out current animation
  if (animations[currentAnimation]) {
    animations[currentAnimation].fadeOut(0.3)
  }

  // Fade in new animation
  if (animations[animationName]) {
    animations[animationName].reset().fadeIn(0.3).play()
    currentAnimation = animationName
  }
}

const animate = () => {
  animationId = requestAnimationFrame(animate)

  // Add a single null check to prevent TS2532 errors
  if (!faceMesh || !faceMesh.morphTargetInfluences || !faceMesh.morphTargetDictionary) {
    renderer.render(scene, camera)
    return
  }

  // Update animations
  if (mixer) {
    mixer.update(0.032) // 30fps
  }

  // Use persistent animation time for all facial movement
  animationTime += 0.008; // slow, tune as needed

  // --- Small random breeze for avatar head (idle only) ---
  if (avatar && !props.isSpeaking && !props.isListening) {
    // Defensive: Ensure avatar.rotation is a THREE.Euler
    if (!(avatar.rotation instanceof THREE.Euler)) {
      console.warn('avatar.rotation was not a THREE.Euler. Resetting values.');
      (avatar.rotation as THREE.Euler).set(0, 0, 0, 'XYZ');
    }
    // Defensive: Ensure avatar.rotation.order is a valid string
    const validOrders = ['XYZ', 'YZX', 'ZXY', 'XZY', 'YXZ', 'ZYX'];
    if (typeof avatar.rotation.order !== 'string' || !validOrders.includes(avatar.rotation.order)) {
      console.warn('avatar.rotation.order was invalid:', avatar.rotation.order, '. Resetting to "XYZ".');
      avatar.rotation.order = 'XYZ';
    }
    const t = animationTime;
    // Persistent random walk for smooth noise
    breezeNoise.x += (Math.random() - 0.5) * 0.00015;
    breezeNoise.y += (Math.random() - 0.5) * 0.00015;
    breezeNoise.z += (Math.random() - 0.5) * 0.00010;
    // Clamp noise to a small range
    breezeNoise.x = Math.max(-0.012, Math.min(0.012, breezeNoise.x));
    breezeNoise.y = Math.max(-0.012, Math.min(0.012, breezeNoise.y));
    breezeNoise.z = Math.max(-0.008, Math.min(0.008, breezeNoise.z));

    // Smoother, lower amplitude sine for gentle sway
    const breezeX = 0.035 * Math.sin(t * 0.6) + breezeNoise.x;
    const breezeY = 0.035 * Math.sin(t * 0.4 + 1.2) + breezeNoise.y;
    const breezeZ = 0.022 * Math.sin(t * 0.8 + 2.1) + breezeNoise.z;
    avatar.rotation.set(breezeX, breezeY, breezeZ, 'XYZ');
    
  } else if (avatar) {
    // Reset to neutral if not idle (let animation mixer take over)
    avatar.rotation.set(0, 0, 0, 'XYZ');
    
  }

  // Realistic facial animation
  if (faceMesh && faceMesh.morphTargetInfluences && faceMesh.morphTargetDictionary) {
    // Use elapsed time for all facial movement
    const t = animationTime * 0.2; // slow, tune as needed

    // --- 1. Mouth/Jaw: sync to mouthOpenLevel or breathing when silent ---
    // Only reset jaw-related morphs, not cheeks or brows
    const jawTargets = ["jawOpen", "mouthFunnel", "mouthPucker", "mouthRollUpper", "mouthRollLower", "mouthShrugUpper", "mouthShrugLower", "mouthClose"]
    jawTargets.forEach(name => {
      const idx = faceMesh?.morphTargetDictionary?.[name] ?? 0;
      if (typeof idx === 'number') {
        if (name === 'jawOpen') {
          if (typeof props.mouthOpenLevel === 'number' && (props.isSpeaking || props.mouthOpenLevel > 0)) {
            // Overlay fast sine and noise for realism
            const now = performance.now() / 1000;
            const fastOsc = 0.08 * Math.sin(now * 12.0 + t * 2.0); // fast, subtle
            const noise = 0.06 * (Math.random() - 0.5);
            if (faceMesh && faceMesh.morphTargetInfluences) {
              faceMesh.morphTargetInfluences[idx] = Math.max(0, Math.min(1, (props.mouthOpenLevel * 0.6) + fastOsc + noise));
            }
          } else {
            // Subtle breathing: slow, small sine wave
            if (faceMesh && faceMesh.morphTargetInfluences) {
              faceMesh.morphTargetInfluences[idx] = 0.04 + 0.03 * Math.abs(Math.sin(t * 0.0012));
            }
          }
        } else if (props.isSpeaking && ["mouthFunnel", "mouthPucker"].includes(name)) {
          // Subtle random movement for lips during speech
          if (faceMesh && faceMesh.morphTargetInfluences) {
            faceMesh.morphTargetInfluences[idx] = 0.05 * Math.abs(Math.sin(t * 2.5 + Math.random() * 2));
          }
        } else {
          if (faceMesh && faceMesh.morphTargetInfluences) {
            faceMesh.morphTargetInfluences[idx] = 0;
          }
        }
      }
    })
    // Do NOT reset cheeks or brows here!

    // --- 1b. Face mimic: subtle, coordinated random movement during speech ---
    if (props.isSpeaking && typeof props.mouthOpenLevel === 'number') {
      // Use slow t for all facial mimic
      // Cheeks: puff and squint a little, not always at the same time, plus random micro-movement
      const cheekPuff = faceMesh?.morphTargetDictionary?.["cheekPuff"] ?? 0;
      const cheekSquintL = faceMesh?.morphTargetDictionary?.["cheekSquint_L"] ?? 0;
      const cheekSquintR = faceMesh?.morphTargetDictionary?.["cheekSquint_R"] ?? 0;
      if (typeof cheekPuff === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[cheekPuff] = 0.05 + 0.07 * Math.abs(Math.sin(t + 1)) * Math.random() + (randomFaceState.cheekPuff.value || 0);
        }
      }
      if (typeof cheekSquintL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[cheekSquintL] = 0.04 + 0.06 * Math.abs(Math.sin(t * 1.2 + 2)) * Math.random() + (randomFaceState.cheekSquintL.value || 0);
        }
      }
      if (typeof cheekSquintR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[cheekSquintR] = 0.04 + 0.06 * Math.abs(Math.sin(t * 1.3 + 3)) * Math.random() + (randomFaceState.cheekSquintR.value || 0);
        }
      }
      // Brows: subtle up/down, not both at once, plus random micro-movement
      const browDownL = faceMesh?.morphTargetDictionary?.["browDown_L"] ?? 0;
      const browDownR = faceMesh?.morphTargetDictionary?.["browDown_R"] ?? 0;
      const browOuterUpL = faceMesh?.morphTargetDictionary?.["browOuterUp_L"] ?? 0;
      const browOuterUpR = faceMesh?.morphTargetDictionary?.["browOuterUp_R"] ?? 0;
      if (typeof browDownL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browDownL] = 0.03 * Math.abs(Math.sin(t * 0.7 + 1)) * Math.random() + (randomFaceState.browOuterUpL.value || 0);
        }
      }
      if (typeof browDownR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browDownR] = 0.03 * Math.abs(Math.sin(t * 0.8 + 2)) * Math.random() + (randomFaceState.browOuterUpR.value || 0);
        }
      }
      if (typeof browOuterUpL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browOuterUpL] = 0.04 * Math.abs(Math.sin(t * 0.9 + 1)) * Math.random() + (randomFaceState.browOuterUpL.value || 0);
        }
      }
      if (typeof browOuterUpR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browOuterUpR] = 0.04 * Math.abs(Math.sin(t + 2)) * Math.random() + (randomFaceState.browOuterUpR.value || 0);
        }
      }
      // Lips: subtle press/stretch (mouthPress even more reduced), smile/frown random micro-movement
      const mouthPressL = faceMesh?.morphTargetDictionary?.["mouthPress_L"] ?? 0;
      const mouthPressR = faceMesh?.morphTargetDictionary?.["mouthPress_R"] ?? 0;
      const mouthStretchL = faceMesh?.morphTargetDictionary?.["mouthStretch_L"] ?? 0;
      const mouthStretchR = faceMesh?.morphTargetDictionary?.["mouthStretch_R"] ?? 0;
      if (typeof mouthPressL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[mouthPressL] = 0.005 * Math.abs(Math.sin(t * 1.1 + 1)) * Math.random();
        }
      }
      if (typeof mouthPressR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[mouthPressR] = 0.005 * Math.abs(Math.sin(t * 1.2 + 2)) * Math.random();
        }
      }
      if (typeof mouthStretchL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[mouthStretchL] = 0.004 * Math.abs(Math.sin(t * 1.1 + 3)) * Math.random();
        }
      }
      if (typeof mouthStretchR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[mouthStretchR] = 0.004 * Math.abs(Math.sin(t * 1.2 + 4)) * Math.random();
        }
      }
      const smileL = faceMesh?.morphTargetDictionary?.["mouthSmile_L"] ?? 0;
      const smileR = faceMesh?.morphTargetDictionary?.["mouthSmile_R"] ?? 0;
      if (typeof smileL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[smileL] = (randomFaceState.mouthSmileL.value || 0);
        }
      }
      if (typeof smileR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[smileR] = (randomFaceState.mouthSmileR.value || 0);
        }
      }
      const mouthFrownL = faceMesh?.morphTargetDictionary?.["mouthFrown_L"] ?? 0;
      const mouthFrownR = faceMesh?.morphTargetDictionary?.["mouthFrown_R"] ?? 0;
      if (typeof mouthFrownL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[mouthFrownL] = (randomFaceState.mouthFrownL.value || 0);
        }
      }
      if (typeof mouthFrownR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[mouthFrownR] = (randomFaceState.mouthFrownR.value || 0);
        }
      }
    } else if (props.isListening) {
      // Listening: use same random micro-movement logic as idle
      // Cheeks: puff and squint a little, not always at the same time, plus random micro-movement
      const cheekPuff = faceMesh?.morphTargetDictionary?.["cheekPuff"] ?? 0;
      const cheekSquintL = faceMesh?.morphTargetDictionary?.["cheekSquint_L"] ?? 0;
      const cheekSquintR = faceMesh?.morphTargetDictionary?.["cheekSquint_R"] ?? 0;
      if (typeof cheekPuff === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[cheekPuff] = 0.018 + 0.018 * Math.sin(t + 1) + 0.0045 * Math.random() + 1.5 * (randomFaceState.cheekPuff.value || 0);
        }
      }
      if (typeof cheekSquintL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[cheekSquintL] = 0.012 + 0.012 * Math.sin(t * 1.1 + 2) + 0.003 * Math.random() + 1.5 * (randomFaceState.cheekSquintL.value || 0);
        }
      }
      if (typeof cheekSquintR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[cheekSquintR] = 0.012 + 0.012 * Math.sin(t * 1.2 + 3) + 0.003 * Math.random() + 1.5 * (randomFaceState.cheekSquintR.value || 0);
        }
      }
      const browDownL = faceMesh?.morphTargetDictionary?.["browDown_L"] ?? 0;
      const browDownR = faceMesh?.morphTargetDictionary?.["browDown_R"] ?? 0;
      const browOuterUpL = faceMesh?.morphTargetDictionary?.["browOuterUp_L"] ?? 0;
      const browOuterUpR = faceMesh?.morphTargetDictionary?.["browOuterUp_R"] ?? 0;
      if (typeof browDownL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browDownL] = 0.012 * (0.5 + 0.5 * Math.sin(t * 0.9 + 1)) + 0.003 * Math.random();
        }
      }
      if (typeof browDownR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browDownR] = 0.012 * (0.5 + 0.5 * Math.sin(t * 1.1 + 2)) + 0.003 * Math.random();
        }
      }
      if (typeof browOuterUpL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browOuterUpL] = 0.045 * (0.5 + 0.5 * Math.sin(t * 1.2 + 3)) + 0.006 * Math.random() + 1.5 * (randomFaceState.browOuterUpL.value || 0);
        }
      }
      if (typeof browOuterUpR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browOuterUpR] = 0.045 * (0.5 + 0.5 * Math.sin(t * 0.8 + 4)) + 0.006 * Math.random() + 1.5 * (randomFaceState.browOuterUpR.value || 0);
        }
      }
      const smileL = faceMesh?.morphTargetDictionary?.["mouthSmile_L"] ?? 0;
      const smileR = faceMesh?.morphTargetDictionary?.["mouthSmile_R"] ?? 0;
      if (typeof smileL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[smileL] = 0.18 + 0.045 * Math.sin(t * 0.7 + 1) + 1.5 * (randomFaceState.mouthSmileL.value || 0);
        }
      }
      if (typeof smileR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[smileR] = 0.18 + 0.045 * Math.sin(t * 0.7 + 2) + 1.5 * (randomFaceState.mouthSmileR.value || 0);
        }
      }
      const mouthFrownL = faceMesh?.morphTargetDictionary?.["mouthFrown_L"] ?? 0;
      const mouthFrownR = faceMesh?.morphTargetDictionary?.["mouthFrown_R"] ?? 0;
      if (typeof mouthFrownL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[mouthFrownL] = 1.5 * (randomFaceState.mouthFrownL.value || 0);
        }
      }
      if (typeof mouthFrownR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[mouthFrownR] = 1.5 * (randomFaceState.mouthFrownR.value || 0);
        }
      }
    } else {
      // Small, realistic mimic in silence
      // Cheeks: more expressive in idle (even slower)
      const cheekPuff = faceMesh?.morphTargetDictionary?.["cheekPuff"] ?? 0;
      const cheekSquintL = faceMesh?.morphTargetDictionary?.["cheekSquint_L"] ?? 0;
      const cheekSquintR = faceMesh?.morphTargetDictionary?.["cheekSquint_R"] ?? 0;
      if (typeof cheekPuff === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[cheekPuff] = 0.018 + 0.018 * Math.sin(t + 1) + 0.0045 * Math.random() + 1.5 * (randomFaceState.cheekPuff.value || 0);
        }
      }
      if (typeof cheekSquintL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[cheekSquintL] = 0.012 + 0.012 * Math.sin(t * 1.1 + 2) + 0.003 * Math.random() + 1.5 * (randomFaceState.cheekSquintL.value || 0);
        }
      }
      if (typeof cheekSquintR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[cheekSquintR] = 0.012 + 0.012 * Math.sin(t * 1.2 + 3) + 0.003 * Math.random() + 1.5 * (randomFaceState.cheekSquintR.value || 0);
        }
      }
      // Brows: more expressive in idle (even slower)
      const browDownL = faceMesh?.morphTargetDictionary?.["browDown_L"] ?? 0;
      const browDownR = faceMesh?.morphTargetDictionary?.["browDown_R"] ?? 0;
      const browOuterUpL = faceMesh?.morphTargetDictionary?.["browOuterUp_L"] ?? 0;
      const browOuterUpR = faceMesh?.morphTargetDictionary?.["browOuterUp_R"] ?? 0;
      if (typeof browDownL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browDownL] = 0.012 * (0.5 + 0.5 * Math.sin(t * 0.9 + 1)) + 0.003 * Math.random();
        }
      }
      if (typeof browDownR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browDownR] = 0.012 * (0.5 + 0.5 * Math.sin(t * 1.1 + 2)) + 0.003 * Math.random();
        }
      }
      if (typeof browOuterUpL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browOuterUpL] = 0.045 * (0.5 + 0.5 * Math.sin(t * 1.2 + 3)) + 0.006 * Math.random() + 1.5 * (randomFaceState.browOuterUpL.value || 0);
        }
      }
      if (typeof browOuterUpR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browOuterUpR] = 0.045 * (0.5 + 0.5 * Math.sin(t * 0.8 + 4)) + 0.006 * Math.random() + 1.5 * (randomFaceState.browOuterUpR.value || 0);
        }
      }
      // Lips: more expressive in idle (even slower)
      const mouthPressL = faceMesh?.morphTargetDictionary?.["mouthPress_L"] ?? 0;
      const mouthPressR = faceMesh?.morphTargetDictionary?.["mouthPress_R"] ?? 0;
      const mouthStretchL = faceMesh?.morphTargetDictionary?.["mouthStretch_L"] ?? 0;
      const mouthStretchR = faceMesh?.morphTargetDictionary?.["mouthStretch_R"] ?? 0;
      if (typeof mouthPressL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[mouthPressL] = 0.0075 * Math.abs(Math.sin(t * 1.3 + 1)) * Math.random();
        }
      }
      if (typeof mouthPressR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[mouthPressR] = 0.0075 * Math.abs(Math.sin(t * 1.4 + 2)) * Math.random();
        }
      }
      if (typeof mouthStretchL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[mouthStretchL] = 0.006 * Math.abs(Math.sin(t * 1.1 + 3)) * Math.random();
        }
      }
      if (typeof mouthStretchR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[mouthStretchR] = 0.006 * Math.abs(Math.sin(t * 1.2 + 4)) * Math.random();
        }
      }
      // Smile: more expressive in idle (even slower)
      const smileL = faceMesh?.morphTargetDictionary?.["mouthSmile_L"] ?? 0;
      const smileR = faceMesh?.morphTargetDictionary?.["mouthSmile_R"] ?? 0;
      if (typeof smileL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[smileL] = 0.18 + 0.045 * Math.sin(t * 0.7 + 1) + 1.5 * (randomFaceState.mouthSmileL.value || 0);
        }
      }
      if (typeof smileR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[smileR] = 0.18 + 0.045 * Math.sin(t * 0.7 + 2) + 1.5 * (randomFaceState.mouthSmileR.value || 0);
        }
      }
      const mouthFrownL = faceMesh?.morphTargetDictionary?.["mouthFrown_L"] ?? 0;
      const mouthFrownR = faceMesh?.morphTargetDictionary?.["mouthFrown_R"] ?? 0;
      if (typeof mouthFrownL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[mouthFrownL] = 1.5 * (randomFaceState.mouthFrownL.value || 0);
        }
      }
      if (typeof mouthFrownR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[mouthFrownR] = 1.5 * (randomFaceState.mouthFrownR.value || 0);
        }
      }
      // Eyes: more expressive in idle (even slower)
      const eyeWideL = faceMesh?.morphTargetDictionary?.["eyeWide_L"] ?? 0;
      const eyeWideR = faceMesh?.morphTargetDictionary?.["eyeWide_R"] ?? 0;
      const eyeSquintL = faceMesh?.morphTargetDictionary?.["eyeSquint_L"] ?? 0;
      const eyeSquintR = faceMesh?.morphTargetDictionary?.["eyeSquint_R"] ?? 0;
      
      const eyeBlinkL = faceMesh?.morphTargetDictionary?.["yeBlink_L"] ?? 0;
      const eyeBlinkR = faceMesh?.morphTargetDictionary?.["yeBlink_R"] ?? 0;

      
      if (typeof eyeWideL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[eyeWideL] = 0.12 + 0.015 * Math.sin(t * 0.6 + 1)+ 1.5 * (randomFaceState.eyeWideL.value || 0);
        }
      }
      if (typeof eyeWideR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[eyeWideR] = 0.12 + 0.015 * Math.sin(t * 0.6 + 2)+ 1.5 * (randomFaceState.eyeWideR.value || 0);
        }
      }
      if (typeof eyeSquintL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[eyeSquintL] = 0.015 + 0.015 * Math.sin(t * 0.5 + 1)+ 1.5 * (randomFaceState.eyeSquintL.value || 0);
        }
      }
      if (typeof eyeSquintR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[eyeSquintR] = 0.015 + 0.015 * Math.sin(t * 0.5 + 2)+ 1.5 * (randomFaceState.eyeSquintR.value || 0);
        }
      }
      
       if (typeof eyeSquintL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[eyeBlinkL] = 0.015 + 0.015 * Math.sin(t * 0.5 + 1)+ 1.5 * (randomFaceState.eyeBlinkL.value || 0);
        }
      }
      if (typeof eyeSquintR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[eyeBlinkR] = 0.015 + 0.015 * Math.sin(t * 0.5 + 2)+ 1.5 * (randomFaceState.eyeBlinkR.value || 0);
        }
      }
      
      
      // --- INTERACTIVE GAZE USING MORPH TARGETS ---
      let gaze = { x: 0, y: 0 };
      if (gazeTarget.value && performance.now() - lastUserGaze < 2000) {
        gaze = gazeTarget.value;
      } else {
        gaze.x = 0.2 * Math.sin(t * 0.5 + Math.sin(t * 0.2)) + randomEyeState.x * 5;
        gaze.y = 0.2 * Math.sin(t * 0.4 + Math.cos(t * 0.3)) + randomEyeState.y * 5;
      }
      gaze.x = Math.max(-1, Math.min(1, gaze.x));
      gaze.y = Math.max(-1, Math.min(1, gaze.y));
      if (typeof eyeLookInL === 'number' && typeof eyeLookOutL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[eyeLookInL] = Math.max(0, -gaze.x);
          faceMesh.morphTargetInfluences[eyeLookOutL] = Math.max(0, gaze.x);
        }
      }
      if (typeof eyeLookInR === 'number' && typeof eyeLookOutR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[eyeLookInR] = Math.max(0, -gaze.x);
          faceMesh.morphTargetInfluences[eyeLookOutR] = Math.max(0, gaze.x);
        }
      }
      if (typeof eyeLookUpL === 'number' && typeof eyeLookDownL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[eyeLookUpL] = Math.max(0, gaze.y);
          faceMesh.morphTargetInfluences[eyeLookDownL] = 0.7;
        }
      }
      if (typeof eyeLookUpR === 'number' && typeof eyeLookDownR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[eyeLookUpR] = Math.max(0, gaze.y);
          faceMesh.morphTargetInfluences[eyeLookDownR] = 0.7;
        }
      }
    }

    // --- 2. Eyes: natural blinking ---
    const now = Date.now()
    const blinkL = faceMesh?.morphTargetDictionary?.["eyeBlink_L"] ?? 0;
    const blinkR = faceMesh?.morphTargetDictionary?.["eyeBlink_R"] ?? 0;
    if (now > nextBlinkTime && !isBlinking) {
      isBlinking = true
      lastBlink = now
    }
    if (isBlinking) {
      // Animate blink (close then open)
      let t = (now - lastBlink) / blinkDuration
      let blinkValue = t < 0.5 ? t * 2 : (1 - t) * 2
      blinkValue = Math.max(0, Math.min(1, blinkValue))
      if (typeof blinkL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[blinkL] = blinkValue;
        }
      }
      if (typeof blinkR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[blinkR] = blinkValue;
        }
      }
      if (t >= 1) {
        isBlinking = false
        nextBlinkTime = now + 2000 + Math.random() * 2000
        if (typeof blinkL === 'number') {
          if (faceMesh && faceMesh.morphTargetInfluences) {
            faceMesh.morphTargetInfluences[blinkL] = 0;
          }
        }
        if (typeof blinkR === 'number') {
          if (faceMesh && faceMesh.morphTargetInfluences) {
            faceMesh.morphTargetInfluences[blinkR] = 0;
          }
        }
      }
    } else {
      if (typeof blinkL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[blinkL] = 0;
        }
      }
      if (typeof blinkR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[blinkR] = 0;
        }
      }
    }

    // --- 3. Brows: subtle up/down at start/end of speech ---
    // Only apply browRaiseLevel to browInnerUp and outer brows if not idle
    if ((props.isSpeaking || props.isListening) && browRaiseLevel !== undefined) {
      const browInnerUp = faceMesh?.morphTargetDictionary?.["browInnerUp"] ?? 0;
      if (typeof browInnerUp === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browInnerUp] = browRaiseLevel;
        }
      }
      // Optionally, add a little to outer brows
      const browOuterUpL = faceMesh?.morphTargetDictionary?.["browOuterUp_L"] ?? 0;
      const browOuterUpR = faceMesh?.morphTargetDictionary?.["browOuterUp_R"] ?? 0;
      if (typeof browOuterUpL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browOuterUpL] += browRaiseLevel * 0.5;
        }
      }
      if (typeof browOuterUpR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[browOuterUpR] += browRaiseLevel * 0.5;
        }
      }
    }
    // --- 4. Smile: small smile at end of speech ---
    // Only apply smileLevel to mouthSmile_L/R if not idle
    if ((props.isSpeaking || props.isListening) && smileLevel !== undefined) {
      const smileL = faceMesh?.morphTargetDictionary?.["mouthSmile_L"] ?? 0;
      const smileR = faceMesh?.morphTargetDictionary?.["mouthSmile_R"] ?? 0;
      if (typeof smileL === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[smileL] += smileLevel;
        }
      }
      if (typeof smileR === 'number') {
        if (faceMesh && faceMesh.morphTargetInfluences) {
          faceMesh.morphTargetInfluences[smileR] += smileLevel;
        }
      }
    }

    
  }

  updateRandomFaceState()
  updateRandomEyeState()

  renderer.render(scene, camera)
}

const updateAvatarAppearance = () => {
  if (!avatar) return

  // Update colors based on config
  avatar.children.forEach((child) => {
    const mesh = child as THREE.Mesh;
    if (mesh.material instanceof THREE.MeshPhongMaterial) {
      if (mesh.geometry instanceof THREE.SphereGeometry) {
        if (mesh.position.y > 0.6 && props.avatarConfig.hairColor) {
          mesh.material.color.setHex(parseInt(props.avatarConfig.hairColor.replace('#', '0x')))
        } else if (mesh.position.y > 0.4 && props.avatarConfig.skinTone) {
          mesh.material.color.setHex(parseInt(props.avatarConfig.skinTone.replace('#', '0x')))
        }
      }
    }
  })
}

function updateAmbientLight() {
  if (!ambientLight) return
  if (props.isDarkMode) {
    ambientLight.color.set(0x999)
    ambientLight.intensity = 0.5
  } else {
    ambientLight.color.set(0x0)
    ambientLight.intensity = 1.5
  }
}

// Expose play animation method
defineExpose({
  playAnimation
})

// Watch for config changes
watch(() => props.avatarConfig, updateAvatarAppearance, { deep: true })

watch(() => props.isListening, (listening) => {
  if (listening) {
    playAnimation('listening')
  } else if (!props.isSpeaking) {
    playAnimation('idle')
  }
})

watch(() => props.isSpeaking, (speaking) => {
  if (speaking) {
    playAnimation('speaking')
  } else if (!props.isListening) {
    playAnimation('idle')
  }
})

watch(() => props.isDarkMode, () => {
  updateAmbientLight()
})

onMounted(async () => {
  animationTime = 0; // Reset animation time on mount
  await initThree()
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  if (renderer) {
    renderer.dispose()
  }
  if (canvasRef.value) {
    canvasRef.value.removeEventListener('mousemove', setGazeFromMouse)
    canvasRef.value.removeEventListener('mouseleave', clearGaze)
  }
})

// Global trap for any mutation of Euler.order (development only)
if (true) {
  (function() {
    let _orderKey = Symbol('order');
    Object.defineProperty(THREE.Euler.prototype, 'order', {
      set(value) {
        if (typeof value !== 'string') {
          console.error('Attempted to set Euler.order to non-string:', value, new Error().stack);
          return; // Ignore the assignment
        }
        this[_orderKey] = value;
      },
      get() {
        return this[_orderKey] || 'XYZ';
      },
      configurable: true,
      enumerable: true
    });
  })();
}
</script>

<style scoped>
.avatar-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.avatar-canvas {
  width: 550px;
  height: 550px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.avatar-canvas.listening {
  box-shadow: 0 0 30px rgba(34, 197, 94, 0.5);
  border-color: rgba(34, 197, 94, 0.5);
}

.avatar-canvas.speaking {
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.5);
  border-color: rgba(59, 130, 246, 0.5);
}

.avatar-status {
  min-height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
}

.status-indicator.listening {
  background: rgba(34, 197, 94, 0.8);
}

.status-indicator.speaking {
  background: rgba(59, 130, 246, 0.8);
}

.pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 1.5s ease-in-out infinite;
}

.wave {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: wave 0.8s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

@keyframes wave {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(1.5); }
}

@media (max-width: 768px) {
  .avatar-canvas {
    width: 300px;
    height: 300px;
  }
}
</style>