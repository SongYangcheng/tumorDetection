<template>
  <div class="welcome-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="nav-content">
        <div class="logo">NeuroVision</div>
        <div class="nav-actions">
          <router-link to="/login" class="nav-link">登录</router-link>
          <router-link to="/register" class="nav-link primary">注册</router-link>
        </div>
      </div>
    </nav>

    <!-- 主hero区域 -->
    <section class="hero">
      <div class="hero-content">
        <h1>脑肿瘤智能检测系统</h1>
        <p class="subtitle">基于YOLO11的医学影像深度学习平台</p>
        <p class="description">AI精准分割 · 高效决策 · 智能辅助</p>

        <div class="hero-buttons">
          <router-link to="/login" class="btn btn-primary">进入系统</router-link>
          <a href="#features" class="btn btn-outline">了解更多</a>
        </div>

        <div class="hero-stats">
          <div class="stat-item">
            <div class="stat-value">99.8%</div>
            <div class="stat-name">检测准确率</div>
          </div>
          <div class="divider"></div>
          <div class="stat-item">
            <div class="stat-value">&lt;1s</div>
            <div class="stat-name">推理耗时</div>
          </div>
          <div class="divider"></div>
          <div class="stat-item">
            <div class="stat-value">24/7</div>
            <div class="stat-name">持续可用</div>
          </div>
        </div>
      </div>

      <div class="hero-visual">
        <div class="visual-placeholder">
          <img src="@/assets/images/image.png" alt="脑肿瘤检测医学影像展示" />
        </div>
      </div>
    </section>

    <!-- 核心功能 -->
    <section id="features" class="features">
      <h2>核心功能</h2>
      <div class="features-grid">
        <div class="feature">
          <div class="feature-icon"></div>
          <h3>智能检测</h3>
          <p>基于YOLO11深度学习模型，精准检测脑部肿瘤，支持多种医学影像格式</p>
        </div>

        <div class="feature">
          <div class="feature-icon"></div>
          <h3>定量分析</h3>
          <p>自动计算肿瘤体积、位置、大小等关键指标，生成详细的分析报告</p>
        </div>

        <div class="feature">
          <div class="feature-icon"></div>
          <h3>术前规划</h3>
          <p>基于检测结果进行手术可达性评估，辅助医生制定手术方案</p>
        </div>

        <div class="feature">
          <div class="feature-icon"></div>
          <h3>数据安全</h3>
          <p>JWT令牌认证、数据加密、权限隔离，完全保护患者隐私数据</p>
        </div>

        <div class="feature">
          <div class="feature-icon"></div>
          <h3>高效工作流</h3>
          <p>一键上传、自动检测、实时可视化，大幅提升临床工作效率</p>
        </div>

        <div class="feature">
          <div class="feature-icon"></div>
          <h3>系统监控</h3>
          <p>实时性能指标、模型准确度追踪、使用统计分析</p>
        </div>
      </div>
    </section>

    <!-- 工作流程 -->
    <section class="workflow">
      <h2>工作流程</h2>
      <div class="workflow-steps">
        <div class="step">
          <div class="step-number">1</div>
          <h4>上传影像</h4>
          <p>上传医学影像文件（支持多种格式）</p>
        </div>
        <div class="arrow">→</div>
        <div class="step">
          <div class="step-number">2</div>
          <h4>自动检测</h4>
          <p>AI模型自动分析并检测肿瘤</p>
        </div>
        <div class="arrow">→</div>
        <div class="step">
          <div class="step-number">3</div>
          <h4>结果查看</h4>
          <p>查看检测结果和详细分析</p>
        </div>
        <div class="arrow">→</div>
        <div class="step">
          <div class="step-number">4</div>
          <h4>临床决策</h4>
          <p>基于数据进行术前规划和治疗</p>
        </div>
      </div>
    </section>

    <!-- 技术栈 -->
    <section class="tech-stack">
      <h2>技术支撑</h2>
      <div class="tech-grid">
        <div class="tech-item">
          <div class="tech-name">YOLO11</div>
          <p>深度学习检测模型</p>
        </div>
        <div class="tech-item">
          <div class="tech-name">PyTorch</div>
          <p>模型训练和推理框架</p>
        </div>
        <div class="tech-item">
          <div class="tech-name">Flask</div>
          <p>后端服务框架</p>
        </div>
        <div class="tech-item">
          <div class="tech-name">Vue 3</div>
          <p>前端UI框架</p>
        </div>
        <div class="tech-item">
          <div class="tech-name">MySQL</div>
          <p>数据库</p>
        </div>
        <div class="tech-item">
          <div class="tech-name">JWT</div>
          <p>身份认证方案</p>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 NeuroVision. AI-Powered Medical Imaging Analysis Platform.</p>
        <div class="footer-links">
          <a href="#" class="footer-link">隐私政策</a>
          <a href="#" class="footer-link">服务条款</a>
          <a href="#" class="footer-link">联系我们</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.welcome-container {
  width: 100%;
  background: transparent;
  color: var(--text);
}

/* 导航栏 */
.navbar {
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.2));
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 0;
  height: 60px;
  width: 100%;
}

.nav-content {
  max-width: 100%;
  margin: 0;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-actions {
  display: flex;
  gap: 12px;
}

.nav-link {
  padding: 8px 16px;
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--text);
  transition: all 0.3s;
  font-size: 14px;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-link.primary {
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: white;
}

.nav-link.primary:hover {
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

/* Hero section */
.hero {
  max-width: 1200px;
  margin: 0 auto;
  padding: 140px 24px 80px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

.hero-content h1 {
  font-size: 48px;
  font-weight: 800;
  margin: 0 0 16px 0;
  line-height: 1.2;
  background: linear-gradient(135deg, var(--text) 0%, rgba(255, 255, 255, 0.7) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 20px;
  color: var(--text-muted);
  margin: 0 0 12px 0;
  font-weight: 600;
}

.description {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 32px 0;
  line-height: 1.6;
}

.hero-buttons {
  display: flex;
  gap: 16px;
  margin-bottom: 40px;
}

.btn {
  padding: 14px 32px;
  border-radius: var(--radius-lg);
  text-decoration: none;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.3s;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: white;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(37, 99, 235, 0.4);
}

.btn-outline {
  background: transparent;
  color: var(--text);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.btn-outline:hover {
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.05);
}

.hero-stats {
  display: flex;
  gap: 24px;
  align-items: center;
  padding: 24px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 4px;
}

.stat-name {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
  text-transform: uppercase;
}

.divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
}

.hero-visual {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg);
  padding: 40px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  font-size: 18px;
  color: var(--text-muted);
  backdrop-filter: blur(8px);
}

.visual-placeholder img {
  max-width: 100%;
  height: auto;
  max-height: 280px;
  object-fit: contain;
}

/* Features section */
.features {
  max-width: 1200px;
  margin: 80px auto;
  padding: 0 24px;
}

.features h2,
.workflow h2,
.tech-stack h2 {
  font-size: 36px;
  font-weight: 800;
  text-align: center;
  margin-bottom: 48px;
  color: var(--text);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.feature {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg);
  padding: 32px;
  transition: all 0.3s;
  backdrop-filter: blur(8px);
}

.feature:hover {
  border-color: rgba(37, 99, 235, 0.3);
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.1);
  transform: translateY(-4px);
}

.feature-icon {
  font-size: 40px;
  margin-bottom: 16px;
  display: block;
}

.feature h3 {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: var(--text);
}

.feature p {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.6;
}

/* Workflow section */
.workflow {
  max-width: 1200px;
  margin: 80px auto;
  padding: 0 24px;
}

.workflow-steps {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.step {
  flex: 1;
  min-width: 200px;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg);
  padding: 24px;
  text-align: center;
  backdrop-filter: blur(8px);
}

.step-number {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  margin: 0 auto 16px;
}

.step h4 {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: var(--text);
}

.step p {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.arrow {
  font-size: 24px;
  color: var(--primary);
  font-weight: 700;
  text-align: center;
  min-width: 30px;
}

/* Tech stack section */
.tech-stack {
  max-width: 1200px;
  margin: 80px auto;
  padding: 0 24px;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
}

.tech-item {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg);
  padding: 24px;
  text-align: center;
  transition: all 0.3s;
  backdrop-filter: blur(8px);
}

.tech-item:hover {
  border-color: rgba(34, 211, 238, 0.3);
  box-shadow: 0 4px 12px rgba(34, 211, 238, 0.1);
}

.tech-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
  display: block;
}

.tech-item p {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
}

/* Footer */
.footer {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.3);
  margin-top: 80px;
  padding: 40px 0;
  width: 100%;
}

.footer-content {
  max-width: 100%;
  margin: 0;
  text-align: center;
  padding: 0;
}

.footer-content p {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0 0 16px 0;
}

.footer-links {
  display: flex;
  justify-content: center;
  gap: 24px;
}

.footer-link {
  font-size: 12px;
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.3s;
}

.footer-link:hover {
  color: var(--text);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero {
    grid-template-columns: 1fr;
    padding: 40px 24px;
  }

  .hero-content h1 {
    font-size: 32px;
  }

  .subtitle {
    font-size: 16px;
  }

  .description {
    font-size: 14px;
  }

  .hero-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .hero-stats {
    flex-direction: column;
    gap: 16px;
  }

  .divider {
    width: 100%;
    height: 1px;
  }

  .workflow-steps {
    flex-direction: column;
  }

  .arrow {
    transform: rotate(90deg);
    margin: 0;
  }

  .features h2,
  .workflow h2,
  .tech-stack h2 {
    font-size: 28px;
  }

  .nav-actions {
    gap: 8px;
  }

  .nav-link {
    padding: 6px 12px;
    font-size: 12px;
  }
}
</style>
