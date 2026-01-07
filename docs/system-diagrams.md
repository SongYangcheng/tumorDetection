# NeuroVision 脑肿瘤检测系统 - 系统设计图

## 1. 用例图 (Use Case Diagram)

```mermaid
graph TB
    subgraph "NeuroVision 脑肿瘤检测系统"
        UC1[用户注册与登录]
        UC2[医学影像上传]
        UC3[肿瘤检测与分割]
        UC4[3D重建与可视化]
        UC5[术前规划分析]
        UC6[影像组学分析]
        UC7[检测结果管理]
        UC8[定量分析报告]
        UC9[视频检测]
        UC10[模型对比]
        UC11[用户管理]
        UC12[系统配置]
        UC13[数据集管理]
        UC14[手术路径规划]
    end
    
    User[普通用户]
    Doctor[医生]
    Admin[管理员]
    
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC7
    
    Doctor --> UC1
    Doctor --> UC2
    Doctor --> UC3
    Doctor --> UC4
    Doctor --> UC5
    Doctor --> UC6
    Doctor --> UC7
    Doctor --> UC8
    Doctor --> UC9
    Doctor --> UC10
    Doctor --> UC13
    Doctor --> UC14
    
    Admin --> UC11
    Admin --> UC12
    
    UC3 -.includes.-> UC2
    UC4 -.includes.-> UC3
    UC5 -.includes.-> UC4
    UC8 -.includes.-> UC3
```

## 2. 系统主要流程图 (Main System Flow Chart)

```mermaid
flowchart TD
    Start([用户启动系统]) --> Login{是否已登录?}
    
    Login -->|否| LoginPage[登录/注册页面]
    LoginPage --> Auth[身份认证]
    Auth -->|成功| Dashboard
    Auth -->|失败| LoginPage
    
    Login -->|是| Dashboard[系统仪表盘]
    
    Dashboard --> Choose{选择功能}
    
    Choose -->|病例管理| DataManager[病例管理模块]
    Choose -->|检测工作台| Workbench[检测工作台]
    Choose -->|术前规划| PreOp[术前规划]
    Choose -->|视频检测| Video[视频检测]
    Choose -->|用户管理| UserMgmt[用户管理]
    
    DataManager --> UploadImage[上传医学影像]
    UploadImage --> ValidateFormat{验证格式}
    ValidateFormat -->|不支持| Error1[提示错误]
    ValidateFormat -->|支持| SaveDB[(保存到数据库)]
    SaveDB --> GeneratePreview[生成预览图]
    GeneratePreview --> DataManager
    
    Workbench --> SelectImage[选择待检测影像]
    SelectImage --> ChooseModel{选择模型}
    
    ChooseModel -->|YOLO11| YoloDetect[YOLO11检测]
    ChooseModel -->|UNet| UnetDetect[UNet分割]
    
    YoloDetect --> Inference1[模型推理]
    UnetDetect --> Inference2[模型推理]
    
    Inference1 --> PostProcess1[后处理]
    Inference2 --> PostProcess2[后处理]
    
    PostProcess1 --> GenMask1[生成掩码]
    PostProcess2 --> GenMask2[生成掩码]
    
    GenMask1 --> CalcMetrics[计算定量指标]
    GenMask2 --> CalcMetrics
    
    CalcMetrics --> UpdateDB[(更新检测结果)]
    UpdateDB --> ShowResult[显示检测结果]
    
    ShowResult --> ExportOptions{导出选项}
    ExportOptions -->|查看3D| Reconstruct3D[3D重建]
    ExportOptions -->|术前规划| PreOpAnalysis[术前分析]
    ExportOptions -->|生成报告| GenReport[生成诊断报告]
    
    Reconstruct3D --> LoadNII[加载NII文件]
    LoadNII --> Segment3D[3D分割]
    Segment3D --> MeshGen[网格生成]
    MeshGen --> Render3D[3D渲染]
    Render3D --> Interactive[交互式查看]
    
    PreOp --> LoadPreOpData[加载影像数据]
    LoadPreOpData --> ShowPreOp[显示3D模型]
    ShowPreOp --> PlanPath[规划手术路径]
    PlanPath --> RiskAssess[风险评估]
    RiskAssess --> SavePlan[(保存规划)]
    
    Video --> UploadVideo[上传视频]
    UploadVideo --> VideoProcess[逐帧检测]
    VideoProcess --> VideoResult[生成检测视频]
    
    GenReport --> End([结束])
    Interactive --> End
    SavePlan --> End
    VideoResult --> End
    Error1 --> Dashboard
```

## 3. 系统功能结构图 (System Function Structure Diagram)

```mermaid
graph TB
    System[NeuroVision脑肿瘤检测系统]
    
    System --> Auth[身份认证模块]
    System --> ImageMgmt[影像管理模块]
    System --> Detection[检测分析模块]
    System --> Planning[术前规划模块]
    System --> UserMgmt[用户管理模块]
    System --> Report[报告生成模块]
    
    Auth --> A1[用户注册]
    Auth --> A2[用户登录]
    Auth --> A3[密码管理]
    Auth --> A4[权限控制]
    Auth --> A5[JWT认证]
    
    ImageMgmt --> I1[影像上传]
    ImageMgmt --> I2[格式转换]
    ImageMgmt --> I3[预览生成]
    ImageMgmt --> I4[病例管理]
    ImageMgmt --> I5[数据集管理]
    ImageMgmt --> I6[DICOM支持]
    ImageMgmt --> I7[NII文件处理]
    
    Detection --> D1[YOLO11检测]
    Detection --> D2[UNet分割]
    Detection --> D3[模型对比]
    Detection --> D4[批量检测]
    Detection --> D5[视频检测]
    Detection --> D6[实时流检测]
    
    D1 --> D1A[实例分割]
    D1 --> D1B[边界框检测]
    D1 --> D1C[置信度评分]
    
    D2 --> D2A[像素级分割]
    D2 --> D2B[掩码生成]
    D2 --> D2C[多类别分割]
    
    Planning --> P1[3D重建]
    Planning --> P2[手术路径规划]
    Planning --> P3[风险评估]
    Planning --> P4[可达性分析]
    Planning --> P5[血管接近度]
    Planning --> P6[功能区评估]
    
    P1 --> P1A[体绘制]
    P1 --> P1B[网格生成]
    P1 --> P1C[三维可视化]
    P1 --> P1D[交互操作]
    
    UserMgmt --> U1[用户CRUD]
    UserMgmt --> U2[角色管理]
    UserMgmt --> U3[权限分配]
    UserMgmt --> U4[操作日志]
    UserMgmt --> U5[个人资料]
    
    Report --> R1[定量分析]
    Report --> R2[影像组学]
    Report --> R3[诊断报告]
    Report --> R4[统计图表]
    Report --> R5[数据导出]
    
    R1 --> R1A[肿瘤体积]
    R1 --> R1B[肿瘤面积]
    R1 --> R1C[最大直径]
    R1 --> R1D[位置坐标]
    
    R2 --> R2A[纹理特征]
    R2 --> R2B[形状特征]
    R2 --> R2C[强度特征]
    R2 --> R2D[小波特征]
```

## 4. 系统数据流图 (Data Flow Diagram)

```mermaid
graph LR
    subgraph "外部实体"
        User[用户/医生]
        Admin[管理员]
    end
    
    subgraph "前端 Vue3"
        UI[用户界面]
        Router[路由管理]
        Store[状态管理 Pinia]
        API[API服务层]
    end
    
    subgraph "后端 Flask"
        AuthAPI[认证API]
        ImageAPI[影像API]
        DetectionAPI[检测API]
        ReconAPI[重建API]
        UserAPI[用户API]
        
        AuthMiddleware[认证中间件]
        
        AIEngine[AI推理引擎]
        ImageProcessor[影像处理器]
        MeshGenerator[网格生成器]
    end
    
    subgraph "数据存储"
        MySQL[(MySQL数据库)]
        FileStorage[(文件存储系统)]
    end
    
    subgraph "AI模型"
        YOLO11[YOLO11模型]
        UNet[UNet模型]
        ResNeXt[ResNeXt模型]
    end
    
    User -->|登录请求| UI
    UI --> Router
    Router --> Store
    Store --> API
    
    API -->|POST /auth/login| AuthAPI
    AuthAPI -->|验证| MySQL
    AuthAPI -->|JWT Token| API
    
    User -->|上传影像| UI
    API -->|POST /medical/upload| ImageAPI
    ImageAPI -->|保存文件| FileStorage
    ImageAPI -->|保存元数据| MySQL
    ImageAPI -->|生成预览| ImageProcessor
    
    User -->|请求检测| UI
    API -->|POST /yolo/detect| DetectionAPI
    DetectionAPI -->|加载影像| FileStorage
    DetectionAPI -->|推理| AIEngine
    AIEngine -->|使用| YOLO11
    AIEngine -->|或使用| UNet
    AIEngine -->|返回结果| DetectionAPI
    DetectionAPI -->|后处理| ImageProcessor
    DetectionAPI -->|保存结果| MySQL
    DetectionAPI -->|保存掩码| FileStorage
    DetectionAPI -->|返回| API
    API -->|显示结果| UI
    
    User -->|请求3D重建| UI
    API -->|POST /reconstruction/generate| ReconAPI
    ReconAPI -->|读取NII| FileStorage
    ReconAPI -->|分割| AIEngine
    AIEngine -->|使用| UNet
    ReconAPI -->|网格化| MeshGenerator
    MeshGenerator -->|保存STL| FileStorage
    ReconAPI -->|更新状态| MySQL
    ReconAPI -->|返回模型| API
    API -->|3D渲染| UI
    
    Admin -->|管理用户| UI
    API -->|GET/POST/PUT/DELETE /admin/users| UserAPI
    UserAPI -->|CRUD操作| MySQL
    
    AuthMiddleware -.验证Token.-> AuthAPI
    AuthMiddleware -.验证Token.-> ImageAPI
    AuthMiddleware -.验证Token.-> DetectionAPI
    AuthMiddleware -.验证Token.-> ReconAPI
    AuthMiddleware -.验证Token.-> UserAPI
    
    style User fill:#e1f5ff
    style Admin fill:#ffe1e1
    style MySQL fill:#fff4e1
    style FileStorage fill:#fff4e1
    style YOLO11 fill:#e1ffe1
    style UNet fill:#e1ffe1
    style ResNeXt fill:#e1ffe1
```

## 5. 用户管理时序图 (User Management Sequence Diagram)

### 5.1 用户注册流程

```mermaid
sequenceDiagram
    actor User as 用户
    participant UI as 前端界面
    participant Router as Vue Router
    participant API as API服务
    participant Backend as Flask后端
    participant AuthBP as auth_bp
    participant DB as MySQL数据库
    
    User->>UI: 1. 访问注册页面
    UI->>Router: 2. 路由到 /register
    Router->>UI: 3. 加载 RegisterView
    
    User->>UI: 4. 填写注册信息<br/>(用户名/邮箱/密码)
    User->>UI: 5. 点击注册按钮
    
    UI->>UI: 6. 前端表单验证
    alt 验证失败
        UI-->>User: 显示错误提示
    end
    
    UI->>API: 7. POST /api/auth/register<br/>{username, email, password}
    API->>Backend: 8. HTTP Request
    Backend->>AuthBP: 9. 路由到注册处理器
    
    AuthBP->>AuthBP: 10. 验证必需字段
    AuthBP->>AuthBP: 11. 验证邮箱格式
    
    AuthBP->>DB: 12. 查询用户名是否存在
    DB-->>AuthBP: 13. 返回查询结果
    
    alt 用户名已存在
        AuthBP-->>Backend: 409 用户名已存在
        Backend-->>API: Error Response
        API-->>UI: 显示错误
        UI-->>User: 提示用户名已存在
    end
    
    AuthBP->>DB: 14. 查询邮箱是否存在
    DB-->>AuthBP: 15. 返回查询结果
    
    alt 邮箱已注册
        AuthBP-->>Backend: 409 邮箱已被注册
        Backend-->>API: Error Response
        API-->>UI: 显示错误
        UI-->>User: 提示邮箱已注册
    end
    
    AuthBP->>AuthBP: 16. 创建User对象
    AuthBP->>AuthBP: 17. 密码哈希处理
    AuthBP->>DB: 18. 插入新用户记录
    DB-->>AuthBP: 19. 返回用户ID
    AuthBP->>DB: 20. 提交事务
    
    AuthBP-->>Backend: 21. 201 注册成功<br/>{message, user_id}
    Backend-->>API: 22. Success Response
    API-->>UI: 23. 注册成功
    UI-->>User: 24. 显示成功消息<br/>跳转到登录页
```

### 5.2 用户登录流程

```mermaid
sequenceDiagram
    actor User as 用户
    participant UI as 前端界面
    participant Store as Pinia Store
    participant API as API服务
    participant Backend as Flask后端
    participant AuthBP as auth_bp
    participant JWT as JWT Manager
    participant DB as MySQL数据库
    
    User->>UI: 1. 访问登录页面
    User->>UI: 2. 输入用户名和密码
    User->>UI: 3. 点击登录按钮
    
    UI->>API: 4. POST /api/auth/login<br/>{username, password}
    API->>Backend: 5. HTTP Request
    Backend->>AuthBP: 6. 路由到登录处理器
    
    AuthBP->>AuthBP: 7. 验证必需字段
    
    AuthBP->>DB: 8. 查询用户<br/>WHERE username=?
    DB-->>AuthBP: 9. 返回用户对象
    
    alt 用户不存在
        AuthBP-->>Backend: 401 用户名或密码错误
        Backend-->>API: Error Response
        API-->>UI: 登录失败
        UI-->>User: 显示错误消息
    end
    
    AuthBP->>AuthBP: 10. 验证密码哈希
    
    alt 密码错误
        AuthBP-->>Backend: 401 用户名或密码错误
        Backend-->>API: Error Response
        API-->>UI: 登录失败
        UI-->>User: 显示错误消息
    end
    
    AuthBP->>AuthBP: 11. 检查账户状态<br/>(is_active)
    
    alt 账户已禁用
        AuthBP-->>Backend: 403 账户已被禁用
        Backend-->>API: Error Response
        API-->>UI: 登录失败
        UI-->>User: 显示账户禁用消息
    end
    
    AuthBP->>JWT: 12. 创建JWT Token<br/>identity=user.id
    JWT-->>AuthBP: 13. 返回 access_token
    
    AuthBP->>AuthBP: 14. 构建响应数据<br/>{token, user_info}
    AuthBP-->>Backend: 15. 200 登录成功
    Backend-->>API: 16. Success Response
    
    API->>Store: 17. 存储用户信息和Token
    Store->>Store: 18. 保存到 localStorage
    
    API-->>UI: 19. 登录成功
    UI-->>User: 20. 跳转到仪表盘
```

### 5.3 管理员管理用户流程

```mermaid
sequenceDiagram
    actor Admin as 管理员
    participant UI as 前端界面
    participant API as API服务
    participant Backend as Flask后端
    participant UserBP as user_management_bp
    participant Middleware as require_auth
    participant DB as MySQL数据库
    
    Admin->>UI: 1. 访问用户管理页面
    UI->>API: 2. GET /api/admin/users<br/>Authorization: Bearer {token}
    API->>Backend: 3. HTTP Request
    Backend->>Middleware: 4. 验证JWT Token
    Middleware->>Middleware: 5. 解析Token
    Middleware->>DB: 6. 查询当前用户
    DB-->>Middleware: 7. 返回用户对象
    
    alt 非管理员
        Middleware-->>Backend: 403 权限不足
        Backend-->>API: Forbidden
        API-->>UI: 显示无权限
        UI-->>Admin: 提示权限不足
    end
    
    Middleware->>UserBP: 8. 注入 current_user
    UserBP->>DB: 9. 查询所有用户<br/>分页/搜索/排序
    DB-->>UserBP: 10. 返回用户列表
    UserBP->>UserBP: 11. 序列化用户数据
    UserBP-->>Backend: 12. 200 用户列表
    Backend-->>API: 13. Success Response
    API-->>UI: 14. 显示用户列表
    
    Admin->>UI: 15. 选择操作<br/>(创建/编辑/删除)
    
    rect rgb(240, 248, 255)
        Note over Admin,DB: 创建新用户
        Admin->>UI: 16a. 点击创建用户
        UI->>API: 17a. POST /api/admin/users<br/>{username, email, password, is_admin}
        API->>Backend: 18a. HTTP Request
        Backend->>UserBP: 19a. 创建用户处理器
        UserBP->>UserBP: 20a. 验证数据
        UserBP->>DB: 21a. 插入新用户
        DB-->>UserBP: 22a. 返回用户ID
        UserBP-->>Backend: 23a. 201 创建成功
        Backend-->>API: 24a. Response
        API-->>UI: 25a. 刷新用户列表
    end
    
    rect rgb(255, 248, 240)
        Note over Admin,DB: 编辑用户信息
        Admin->>UI: 16b. 点击编辑用户
        UI->>API: 17b. PUT /api/admin/users/{id}<br/>{email, is_active, is_admin}
        API->>Backend: 18b. HTTP Request
        Backend->>UserBP: 19b. 更新用户处理器
        UserBP->>DB: 20b. 查询用户
        DB-->>UserBP: 21b. 返回用户对象
        UserBP->>UserBP: 22b. 更新字段
        UserBP->>DB: 23b. 提交更新
        UserBP-->>Backend: 24b. 200 更新成功
        Backend-->>API: 25b. Response
        API-->>UI: 26b. 刷新用户列表
    end
    
    rect rgb(255, 240, 240)
        Note over Admin,DB: 删除用户
        Admin->>UI: 16c. 点击删除用户
        UI->>UI: 17c. 确认对话框
        Admin->>UI: 18c. 确认删除
        UI->>API: 19c. DELETE /api/admin/users/{id}
        API->>Backend: 20c. HTTP Request
        Backend->>UserBP: 21c. 删除用户处理器
        UserBP->>DB: 22c. 查询用户
        UserBP->>DB: 23c. 删除用户及关联数据
        UserBP->>DB: 24c. 提交事务
        UserBP-->>Backend: 25c. 200 删除成功
        Backend-->>API: 26c. Response
        API-->>UI: 27c. 刷新用户列表
    end
```

### 5.4 用户修改个人资料流程

```mermaid
sequenceDiagram
    actor User as 用户
    participant UI as 个人资料页面
    participant API as API服务
    participant Backend as Flask后端
    participant UserBP as user_management_bp
    participant Middleware as JWT验证
    participant DB as MySQL数据库
    
    User->>UI: 1. 访问个人资料页面
    UI->>API: 2. GET /api/admin/profile
    API->>Backend: 3. HTTP Request + JWT Token
    Backend->>Middleware: 4. 验证Token
    Middleware->>DB: 5. 查询当前用户
    DB-->>Middleware: 6. 返回用户对象
    Middleware->>UserBP: 7. 注入 current_user
    UserBP->>UserBP: 8. 序列化用户数据
    UserBP-->>Backend: 9. 200 用户信息
    Backend-->>API: 10. Response
    API-->>UI: 11. 显示用户信息
    
    User->>UI: 12. 修改资料<br/>(邮箱等)
    User->>UI: 13. 点击保存
    
    UI->>API: 14. PUT /api/admin/profile<br/>{email}
    API->>Backend: 15. HTTP Request
    Backend->>Middleware: 16. 验证Token
    Middleware->>DB: 17. 查询当前用户
    DB-->>Middleware: 18. 返回用户对象
    Middleware->>UserBP: 19. 注入 current_user
    
    UserBP->>UserBP: 20. 验证邮箱格式
    
    UserBP->>DB: 21. 检查邮箱唯一性
    DB-->>UserBP: 22. 返回查询结果
    
    alt 邮箱已被使用
        UserBP-->>Backend: 409 邮箱已存在
        Backend-->>API: Error Response
        API-->>UI: 显示错误
        UI-->>User: 提示邮箱已被使用
    end
    
    UserBP->>UserBP: 23. 更新用户对象
    UserBP->>DB: 24. 提交更新
    DB-->>UserBP: 25. 更新成功
    
    UserBP-->>Backend: 26. 200 更新成功
    Backend-->>API: 27. Response
    API-->>UI: 28. 显示成功消息
    UI-->>User: 29. 刷新页面显示
    
    rect rgb(255, 245, 245)
        Note over User,DB: 修改密码流程
        User->>UI: 30. 点击修改密码
        User->>UI: 31. 输入旧密码和新密码
        User->>UI: 32. 点击确认
        
        UI->>API: 33. POST /api/admin/profile/change-password<br/>{old_password, new_password}
        API->>Backend: 34. HTTP Request
        Backend->>Middleware: 35. 验证Token
        Middleware->>UserBP: 36. 注入 current_user
        
        UserBP->>UserBP: 37. 验证旧密码
        
        alt 旧密码错误
            UserBP-->>Backend: 400 密码错误
            Backend-->>API: Error Response
            API-->>UI: 显示错误
            UI-->>User: 提示密码错误
        end
        
        UserBP->>UserBP: 38. 设置新密码哈希
        UserBP->>DB: 39. 更新密码
        DB-->>UserBP: 40. 更新成功
        
        UserBP-->>Backend: 41. 200 密码修改成功
        Backend-->>API: 42. Response
        API-->>UI: 43. 显示成功消息
        UI-->>User: 44. 提示重新登录
    end
```

## 6. 核心检测流程时序图 (Detection Sequence Diagram)

```mermaid
sequenceDiagram
    actor User as 用户
    participant UI as 检测界面
    participant API as API服务
    participant Backend as Flask后端
    participant DetectBP as yolo_detection_bp
    participant AIEngine as AI推理引擎
    participant YOLO as YOLO11模型
    participant ImgProc as 图像处理器
    participant DB as MySQL数据库
    participant Storage as 文件存储
    
    User->>UI: 1. 选择影像进行检测
    User->>UI: 2. 点击开始检测
    
    UI->>API: 3. POST /api/yolo/detect/{image_id}
    API->>Backend: 4. HTTP Request
    Backend->>DetectBP: 5. 路由到检测处理器
    
    DetectBP->>DB: 6. 查询影像记录
    DB-->>DetectBP: 7. 返回MedicalImage对象
    
    DetectBP->>Storage: 8. 读取影像文件
    Storage-->>DetectBP: 9. 返回图像数据
    
    DetectBP->>ImgProc: 10. 预处理图像<br/>(标准化/增强)
    ImgProc-->>DetectBP: 11. 返回处理后图像
    
    DetectBP->>AIEngine: 12. 请求推理<br/>(image, model='yolo11')
    AIEngine->>YOLO: 13. 加载模型权重
    YOLO-->>AIEngine: 14. 模型就绪
    
    AIEngine->>YOLO: 15. 执行推理<br/>predict(image)
    YOLO-->>AIEngine: 16. 返回原始结果<br/>(boxes, masks, scores)
    
    AIEngine->>AIEngine: 17. 后处理<br/>(NMS/阈值过滤)
    AIEngine-->>DetectBP: 18. 返回检测结果
    
    DetectBP->>ImgProc: 19. 生成分割掩码
    ImgProc-->>DetectBP: 20. 返回掩码图像
    
    DetectBP->>Storage: 21. 保存掩码文件
    Storage-->>DetectBP: 22. 返回文件路径
    
    DetectBP->>ImgProc: 23. 生成叠加图
    ImgProc-->>DetectBP: 24. 返回叠加图像
    
    DetectBP->>Storage: 25. 保存叠加图
    Storage-->>DetectBP: 26. 返回文件路径
    
    DetectBP->>DetectBP: 27. 计算定量指标<br/>(体积/面积/中心点)
    
    DetectBP->>DetectBP: 28. 构建结果数据<br/>(JSON格式)
    
    DetectBP->>DB: 29. 更新MedicalImage记录<br/>(yolo_* 字段)
    DB-->>DetectBP: 30. 更新成功
    
    DetectBP-->>Backend: 31. 200 检测完成<br/>{results, metrics, paths}
    Backend-->>API: 32. Response
    API-->>UI: 33. 显示检测结果
    
    UI->>UI: 34. 渲染掩码叠加图
    UI->>UI: 35. 显示定量指标
    UI->>UI: 36. 显示检测实例列表
    
    UI-->>User: 37. 呈现完整结果
```

## 系统技术栈总结

### 前端技术栈
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **路由**: Vue Router
- **状态管理**: Pinia
- **3D渲染**: Three.js + OrbitControls
- **UI组件**: 自定义组件库
- **HTTP客户端**: Axios

### 后端技术栈
- **框架**: Flask
- **ORM**: Flask-SQLAlchemy
- **认证**: Flask-JWT-Extended
- **数据库**: MySQL (pymysql驱动)
- **AI框架**: PyTorch + Ultralytics (YOLO)
- **图像处理**: Pillow, OpenCV, nibabel, pydicom
- **3D处理**: trimesh, SimpleITK

### AI模型
- **YOLO11**: 目标检测与实例分割
- **UNet**: 语义分割
- **ResNeXt50**: 分类与特征提取

### 数据存储
- **关系数据库**: MySQL
- **文件存储**: 本地文件系统
  - 医学影像: `backend/uploads/medical_images/`
  - NII文件: `backend/uploads/nii_files/`
  - 分割结果: `backend/uploads/segmentation_results/`
  - 3D模型: `backend/uploads/3d_models/`

---

**文档版本**: 1.0  
**生成日期**: 2026年1月6日  
**系统版本**: NeuroVision v1.0
