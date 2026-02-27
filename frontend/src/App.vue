<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 font-sans">
    <nav class="bg-white shadow-lg sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-2xl font-bold text-indigo-600 tracking-tight">Vercel & Render</h1>
          </div>
          <div class="flex items-center space-x-4">
            <template v-if="isAuthenticated">
              <span class="text-gray-600 text-sm hidden md:block">Sesión de: <b>{{ username }}</b></span>
              <button @click="handleLogout" class="bg-red-50 text-red-600 px-4 py-2 rounded-lg text-sm font-bold hover:bg-red-100 transition">
                Cerrar Sesión
              </button>
            </template>
            <div v-else class="flex items-center space-x-2">
              <span class="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></span>
              <span class="text-xs text-gray-500 uppercase font-bold tracking-widest">Requiere Login</span>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      
      <div v-if="!isAuthenticated" class="max-w-md mx-auto">
        <div class="bg-white rounded-2xl shadow-2xl p-8 border border-gray-100 transition-all">
          <div class="text-center mb-8">
            <h2 class="text-3xl font-extrabold text-gray-900">
              {{ isRegisterMode ? 'Crear Cuenta' : '¡Bienvenido!' }}
            </h2>
            <p class="text-gray-500 mt-2 text-sm">
              {{ isRegisterMode ? 'Regístrate para gestionar tus tareas' : 'Ingresa tus datos para acceder' }}
            </p>
          </div>

          <form @submit.prevent="isRegisterMode ? handleRegister() : handleLogin()" class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-gray-400 uppercase mb-1">Usuario</label>
              <input v-model="username" type="text" placeholder="Tu usuario" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition" required />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-400 uppercase mb-1">Contraseña</label>
              <input v-model="password" type="password" placeholder="••••••••" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition" required />
            </div>

            <p v-if="authError" class="text-red-500 text-xs italic text-center bg-red-50 py-2 rounded">{{ authError }}</p>

            <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl shadow-lg shadow-indigo-200 transition transform hover:-translate-y-0.5">
              {{ isRegisterMode ? 'Registrarme' : 'Entrar' }}
            </button>
          </form>

          <div class="mt-8 pt-6 border-t border-gray-100 text-center">
            <button @click="isRegisterMode = !isRegisterMode; authError = ''" class="text-indigo-600 font-bold text-sm hover:underline">
              {{ isRegisterMode ? '¿Ya tienes cuenta? Inicia sesión' : '¿No tienes cuenta? Crea una gratis' }}
            </button>
          </div>
        </div>
      </div>

      <div v-else>
        <div class="bg-white rounded-lg shadow-xl p-8 mb-8 border-l-4 border-indigo-500">
          <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <span class="mr-2">⚡</span> Estado de la Infraestructura
          </h2>
          <div v-if="loading" class="flex items-center space-x-3 text-indigo-600 font-medium">
            <span>Consultando Backend...</span>
          </div>
          <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
            <p class="text-red-900 font-medium">Error: {{ error }}</p>
          </div>
          <div v-else-if="backendStatus" class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-green-50 rounded-xl p-4 text-center">
              <p class="text-xs text-green-700 font-bold uppercase mb-1">Status</p>
              <p class="text-lg text-green-900 font-black">{{ backendStatus.status }}</p>
            </div>
            <div class="bg-blue-50 rounded-xl p-4 text-center">
              <p class="text-xs text-blue-700 font-bold uppercase mb-1">Engine</p>
              <p class="text-lg text-blue-900 font-black">{{ backendEngine }}</p>
            </div>
            <div class="bg-indigo-50 rounded-xl p-4 text-center">
              <p class="text-xs text-indigo-700 font-bold uppercase mb-1">Message</p>
              <p class="text-sm text-indigo-900 font-medium">{{ backendStatus.message }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-xl p-8">
          <div class="flex items-center justify-between mb-8">
            <h2 class="text-3xl font-black text-gray-900 italic underline decoration-indigo-500">Mis Tareas</h2>
            <button @click="loadItems" class="bg-indigo-50 text-indigo-600 px-4 py-2 rounded-lg font-bold hover:bg-indigo-100 transition">🔄 Actualizar</button>
          </div>

          <form @submit.prevent="addItem" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10 bg-gray-50 p-6 rounded-2xl border border-gray-100">
            <div class="md:col-span-2">
              <input v-model="newItemName" type="text" placeholder="¿Qué hay que hacer?" class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition" required />
            </div>
            <select v-model="newItemStatus" class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition">
              <option>Pendiente</option>
              <option>En progreso</option>
              <option>Completado</option>
            </select>
            <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-black py-3 px-6 rounded-xl transition shadow-lg shadow-indigo-100">AÑADIR</button>
          </form>

          <div v-if="items.length === 0" class="text-center py-12 text-gray-400">No hay tareas todavía.</div>

          <div v-else class="space-y-4">
            <div v-for="item in items" :key="item.id" class="group flex flex-col md:flex-row md:items-center md:justify-between gap-4 p-5 border border-gray-100 rounded-2xl hover:bg-indigo-50/30 transition-all">
              <div class="flex-1">
                <div v-if="editingId === item.id" class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <input v-model="editName" type="text" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none" />
                  <select v-model="editStatus" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none">
                    <option>Pendiente</option>
                    <option>En progreso</option>
                    <option>Completado</option>
                  </select>
                </div>
                <div v-else>
                  <p class="font-bold text-gray-800 text-lg">{{ item.name }}</p>
                  <span :class="{'px-3 py-1 rounded-full text-xs font-black uppercase tracking-widest inline-block mt-2': true, 'bg-green-100 text-green-700': item.status === 'Completado', 'bg-blue-100 text-blue-700': item.status === 'En progreso', 'bg-yellow-100 text-yellow-700': item.status === 'Pendiente'}">
                    {{ item.status }}
                  </span>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <template v-if="editingId === item.id">
                  <button @click="saveEdit(item.id)" class="bg-green-500 text-white font-bold py-2 px-4 rounded-xl">OK</button>
                  <button @click="cancelEdit" class="bg-gray-200 text-gray-700 font-bold py-2 px-4 rounded-xl">X</button>
                </template>
                <template v-else>
                  <button @click="startEdit(item)" class="text-indigo-600 font-bold bg-indigo-50 px-3 py-1 rounded-lg">Editar</button>
                  <button @click="removeItem(item.id)" class="text-red-600 font-bold bg-red-50 px-3 py-1 rounded-lg">Borrar</button>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiService } from './services/api'

// --- ESTADO DE AUTH ---
const isAuthenticated = ref(false)
const isRegisterMode = ref(false) // Nueva variable para alternar modo
const username = ref('')
const password = ref('')
const authError = ref('')

// --- ESTADO DE LA APP ---
const loading = ref(true)
const error = ref<string | null>(null)
const backendStatus = ref<any>(null)
const backendEngine = ref('FastAPI + MySQL')
const items = ref<Array<{ id: number; name: string; status: string }>>([])
const newItemName = ref('')
const newItemStatus = ref('Pendiente')
const editingId = ref<number | null>(null)
const editName = ref('')
const editStatus = ref('Pendiente')

// --- LÓGICA DE REGISTRO ---
const handleRegister = async () => {
  try {
    authError.value = ''
    await apiService.register({ username: username.value, password: password.value })
    await handleLogin()
  } catch (err: any) {
    // Esto nos dirá el mensaje real que devuelve FastAPI (ej: "El usuario ya existe")
    // O si el servidor ni siquiera responde (ERR_CONNECTION_REFUSED)
    authError.value = err.response?.data?.detail || err.message || 'Error desconocido'
    console.error("Detalle del error:", err.response?.data)
  }
}

// --- LÓGICA DE DATOS ---
const loadItems = async () => {
  try {
    const data = await apiService.listItems()
    items.value = data
  } catch (err: any) {
    if (err.response?.status === 401) {
      handleLogout()
    }
  }
}

const initApp = async () => {
  try {
    loading.value = true
    const [status, data] = await Promise.all([
      apiService.getStatus(),
      apiService.getData(),
    ])
    backendStatus.value = status
    backendEngine.value = data.backend_engine || 'FastAPI + MySQL'
    await loadItems()
  } catch (err) {
    error.value = 'Error de conexión con el servidor'
  } finally {
    loading.value = false
  }
}

// --- LÓGICA DE LOGIN ---
const handleLogin = async () => {
  try {
    authError.value = ''
    const data = await apiService.login(username.value, password.value)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('saved_username', username.value)
    isAuthenticated.value = true
    await initApp()
  } catch (err) {
    authError.value = 'Credenciales inválidas'
  }
}

const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('saved_username')
  isAuthenticated.value = false
  username.value = ''
  password.value = ''
  items.value = []
}

// --- CRUD ---
const addItem = async () => {
  if (!newItemName.value.trim()) return
  await apiService.createItem({
    name: newItemName.value.trim(),
    status: newItemStatus.value,
  })
  newItemName.value = ''
  newItemStatus.value = 'Pendiente'
  await loadItems()
}

const startEdit = (item: any) => {
  editingId.value = item.id
  editName.value = item.name
  editStatus.value = item.status
}

const cancelEdit = () => { editingId.value = null }

const saveEdit = async (itemId: number) => {
  await apiService.updateItem(itemId, {
    name: editName.value.trim(),
    status: editStatus.value,
  })
  cancelEdit()
  await loadItems()
}

const removeItem = async (itemId: number) => {
  await apiService.deleteItem(itemId)
  await loadItems()
}

onMounted(() => {
  const token = localStorage.getItem('access_token')
  if (token) {
    isAuthenticated.value = true
    username.value = localStorage.getItem('saved_username') || 'Usuario'
    initApp()
  } else {
    loading.value = false
  }
})
</script>