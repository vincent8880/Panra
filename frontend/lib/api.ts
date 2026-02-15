import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api'

// Token storage utilities
const TOKEN_KEY = 'auth_token'

export const tokenStorage = {
  get: (): string | null => {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(TOKEN_KEY)
  },
  set: (token: string): void => {
    if (typeof window === 'undefined') return
    localStorage.setItem(TOKEN_KEY, token)
  },
  remove: (): void => {
    if (typeof window === 'undefined') return
    localStorage.removeItem(TOKEN_KEY)
  },
}

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Still needed for session-based auth (email/password)
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = tokenStorage.get()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    // Only log for non-auth endpoints to reduce noise
    if (!config.url?.includes('/auth/')) {
      console.log('✅ [API Interceptor] Token attached:', config.method?.toUpperCase(), config.url, `(${token.substring(0, 20)}...)`)
    }
  } else {
    // Only warn for protected endpoints
    if (!config.url?.includes('/auth/') && !config.url?.includes('/markets/')) {
      console.warn('⚠️ [API Interceptor] NO TOKEN:', config.method?.toUpperCase(), config.url)
    }
  }
  return config
})
 
// Handle 401 errors (token expired)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, clear it
      tokenStorage.remove()
      // Redirect to login if not already there, preserve return URL
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        const next = encodeURIComponent(window.location.pathname + window.location.search)
        window.location.href = `/login?next=${next}`
      }
    }
    return Promise.reject(error)
  }
)

export interface Market {
  id: number
  title: string
  description: string
  slug: string
  question: string
  category: string
  image_url: string | null
  status: 'open' | 'closed' | 'resolved' | 'cancelled'
  resolution: 'yes' | 'no' | 'pending'
  created_at: string
  end_date: string
  resolution_date: string | null
  created_by_username: string
  total_volume: string
  total_liquidity: string
  yes_price: string
  no_price: string
}

export interface Order {
  id: number
  market: number
  market_title: string
  market_slug: string
  user: number
  user_username: string
  side: 'yes' | 'no'
  order_type: 'limit' | 'market'
  price: string
  quantity: string
  status: 'pending' | 'filled' | 'cancelled' | 'partial'
  filled_quantity: string
  created_at: string
  updated_at: string
  filled_at: string | null
}

export interface CreditStatus {
  current: number
  stored: number
  max: number
  days_inactive: number
  next_decay_at: string | null
  regenerating: boolean
  hours_to_full_regen: number | null
  regen_rate_per_hour: number
}

export interface User {
  id: number
  username: string
  email: string
  credits: number
  current_credits: number
  credit_status: CreditStatus
  date_joined: string
}

export interface AuthResponse {
  id: number
  username: string
  email: string
  credits: number
  current_credits: number
  credit_status: CreditStatus
  date_joined: string
  token?: string  // JWT token for API authentication
}

export const marketsApi = {
  getAll: async (params?: { status?: string; category?: string; search?: string }) => {
    const response = await api.get<{ results: Market[] }>('/markets/', { params })
    return response.data.results
  },
  
  getById: async (id: number) => {
    const response = await api.get<Market>(`/markets/${id}/`)
    return response.data
  },
  
  getBySlug: async (slug: string) => {
    const response = await api.get<Market>(`/markets/${slug}/`)
    return response.data
  },
}

export interface Position {
  id: number
  market: number
  market_title: string
  market_slug: string
  yes_shares: string
  no_shares: string
  yes_avg_cost: string
  no_avg_cost: string
  yes_price?: string
  no_price?: string
  updated_at: string
}

export const ordersApi = {
  create: async (data: { market: number; side: 'yes' | 'no'; order_type: 'limit' | 'market'; price: string; quantity: string }) => {
    const response = await api.post<Order>('/trading/orders/', data)
    return response.data
  },
  
  getAll: async () => {
    const response = await api.get<{ results: Order[] } | Order[]>('/trading/orders/')
    // Handle paginated response
    return Array.isArray(response.data) ? response.data : response.data.results
  },
  
  getOpen: async () => {
    const response = await api.get<{ results: Order[] } | Order[]>('/trading/orders/open/')
    // Handle paginated response
    return Array.isArray(response.data) ? response.data : response.data.results
  },
  
  cancel: async (id: number) => {
    const response = await api.post(`/trading/orders/${id}/cancel/`)
    return response.data
  },
}

export const positionsApi = {
  getAll: async () => {
    const response = await api.get<{ results: Position[] } | Position[]>('/trading/positions/')
    // Handle paginated response
    return Array.isArray(response.data) ? response.data : response.data.results
  },
}

export interface LeaderboardUser {
  id: number
  username: string
  total_points: number
  weekly_points: number
  monthly_points: number
  win_streak: number
  accuracy_percentage: number
  roi_percentage: number
  rank?: number
}

export interface UserStats {
  user: {
    id: number
    username: string
    total_points: number
    weekly_points: number
    monthly_points: number
    rank: number
  }
  trading: {
    win_streak: number
    best_win_streak: number
    markets_predicted_correctly: number
    total_markets_traded: number
    accuracy_percentage: number
    roi_percentage: number
    total_trades: number
    markets_traded: number
    active_positions: number
  }
  credits: {
    current: number
    stored: number
    max: number
  }
  volume: {
    total_volume_traded: number
    total_profit_loss: number
    unrealized_pnl: number
  }
}

export const usersApi = {
  getMe: async () => {
    const token = tokenStorage.get()
    console.log('🔍 [usersApi.getMe] Token check:', token ? `Token exists (${token.substring(0, 20)}...)` : '❌ NO TOKEN')
    const response = await api.get<User>('/auth/users/me/')
    console.log('✅ [usersApi.getMe] Success, user:', response.data.username)
    return response.data
  },
  
  getCredits: async () => {
    const response = await api.get<{ credits: number; status: CreditStatus }>('/auth/users/credits/')
    return response.data
  },
}

export const authApi = {
  getCsrf: async () => {
    const response = await api.get<{ csrfToken: string }>('/auth/csrf/')
    return response.data.csrfToken
  },

  signup: async (data: { username: string; email: string; password: string }) => {
    const csrfToken = await authApi.getCsrf()
    const response = await api.post<AuthResponse>(
      '/auth/signup/',
      data,
      {
        headers: {
          'X-CSRFToken': csrfToken,
        },
      }
    )
    // Store JWT token if provided
    if (response.data.token) {
      tokenStorage.set(response.data.token)
    }
    return response.data
  },

  login: async (data: { username?: string; email?: string; password: string }) => {
    const csrfToken = await authApi.getCsrf()
    const response = await api.post<AuthResponse>(
      '/auth/login/',
      data,
      {
        headers: {
          'X-CSRFToken': csrfToken,
        },
      }
    )
    // Store JWT token if provided
    if (response.data.token) {
      tokenStorage.set(response.data.token)
      console.log('✅ [authApi.login] Token stored:', response.data.token.substring(0, 20) + '...')
    } else {
      console.warn('⚠️ [authApi.login] NO TOKEN in response!', response.data)
    }
    return response.data
  },

  logout: async () => {
    // Clear token
    tokenStorage.remove()
    // Also call backend logout (for session-based auth)
    try {
      const csrfToken = await authApi.getCsrf()
      await api.post(
        '/auth/logout/',
        {},
        {
          headers: {
            'X-CSRFToken': csrfToken,
          },
        }
      )
    } catch {
      // Ignore errors
    }
  },

  getGoogleAuthUrl: async () => {
    const response = await api.get<{ auth_url: string }>('/auth/google/init/')
    return response.data.auth_url
  },
}

export const leaderboardApi = {
  getAllTime: async () => {
    const response = await api.get<{ results: LeaderboardUser[]; type: string }>('/auth/leaderboard/all-time/')
    return response.data
  },
  
  getWeekly: async () => {
    const response = await api.get<{ results: LeaderboardUser[]; type: string }>('/auth/leaderboard/weekly/')
    return response.data
  },
  
  getMonthly: async () => {
    const response = await api.get<{ results: LeaderboardUser[]; type: string }>('/auth/leaderboard/monthly/')
    return response.data
  },
  
  getAroundMe: async () => {
    const response = await api.get<{ results: LeaderboardUser[]; user_rank: number; user_points: number }>('/auth/leaderboard/around-me/')
    return response.data
  },
}

export const statsApi = {
  getMyStats: async () => {
    const response = await api.get<UserStats>('/auth/stats/me/')
    return response.data
  },

  getUserStats: async (userId: number) => {
    const response = await api.get<UserStats>(`/auth/stats/${userId}/stats/`)
    return response.data
  },

  getUserStatsByUsername: async (username: string) => {
    const response = await api.get<UserStats>(
      `/auth/stats/by-username/${encodeURIComponent(username)}/`
    )
    return response.data
  },
}

export default api





