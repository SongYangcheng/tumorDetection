// 基础API URL - 与后端端口保持一致
const API_BASE_URL =
  ((import.meta.env.VITE_API_BASE_URL as string | undefined) || 'http://127.0.0.1:8000') + '/api'

export interface RegisterRequest {
  username: string
  password: string
  email?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface User {
  id: number
  username: string
  email: string
  created_at: string
  is_admin?: boolean
}

export interface RegisterResponse {
  message: string
  user: User
}

export interface LoginResponse {
  message: string
  access_token: string
  user: User
}

export interface ProfileResponse {
  user: User
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

export interface ChangePasswordResponse {
  message: string
}

// 认证相关的API服务
class AuthService {
  private token: string | null = null

  constructor() {
    // 从localStorage中获取已存储的token
    this.token = localStorage.getItem('access_token')
  }

  // 注册
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await fetch(`${API_BASE_URL}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '注册失败')
    }

    return response.json()
  }

  // 登录
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '登录失败')
    }

    const result = await response.json()

    // 存储token
    if (result.access_token) {
      this.token = result.access_token
      localStorage.setItem('access_token', result.access_token)
    }

    return result
  }

  // 获取用户信息
  async getProfile(): Promise<ProfileResponse> {
    const response = await fetch(`${API_BASE_URL}/profile`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '获取用户信息失败')
    }

    return response.json()
  }

  // 修改密码
  async changePassword(data: ChangePasswordRequest): Promise<ChangePasswordResponse> {
    const response = await fetch(`${API_BASE_URL}/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.token}`,
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '修改密码失败')
    }

    return response.json()
  }

  // 登出
  logout(): void {
    this.token = null
    localStorage.removeItem('access_token')
  }

  // 检查是否已登录
  isLoggedIn(): boolean {
    return this.token !== null
  }

  // 获取当前token
  getToken(): string | null {
    return this.token
  }
}

export const authService = new AuthService()
export type UserProfile = User
