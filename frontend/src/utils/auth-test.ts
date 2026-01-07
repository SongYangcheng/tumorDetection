/**
 * 认证调试工具
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api'

export async function testAuthentication() {
    const token = localStorage.getItem('access_token')

    console.log('=== 认证测试开始 ===')
    console.log('1. Token 存在:', !!token)

    if (!token) {
        console.error('[错误] 未找到 access_token')
        return {
            success: false,
            error: '未找到token',
            suggestion: '请先登录'
        }
    }

    console.log('2. Token 长度:', token.length)
    console.log('3. Token 前20字符:', token.substring(0, 20))

    // 测试API调用
    try {
        console.log('4. 测试API调用: /api/profile')
        const response = await fetch(`${API_BASE_URL}/profile`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })

        console.log('5. 响应状态:', response.status, response.statusText)

        if (response.ok) {
            const data = await response.json()
            console.log('[成功] 认证成功! 用户:', data.user?.username)
            return {
                success: true,
                user: data.user
            }
        } else {
            const errorText = await response.text()
            console.error('[错误] 认证失败:', errorText)

            if (response.status === 401) {
                console.error('Token 无效或已过期')
                return {
                    success: false,
                    error: 'Token无效',
                    suggestion: '请重新登录'
                }
            }

            return {
                success: false,
                error: `HTTP ${response.status}`,
                detail: errorText
            }
        }
    } catch (error: any) {
        console.error('[错误] 网络错误:', error)
        return {
            success: false,
            error: '网络错误',
            detail: error.message
        }
    } finally {
        console.log('=== 认证测试结束 ===')
    }
}

// 在浏览器控制台中使用: window.testAuth()
if (typeof window !== 'undefined') {
    (window as any).testAuth = testAuthentication
}
