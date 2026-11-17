# 卫戍协议盟约速查 — V1 产品需求与 Agent 实施规范

> **状态**：Ready for implementation  
> **目标**：本地开发与验证，审查通过后通过 GitHub Pages 发布的纯静态单页查询工具  
> **技术栈**：React + TypeScript + Vite + Tailwind CSS；Python 负责构建期 PRTS 数据提取  
> **开发方式**：AI Coding Agent 按本文件自主实现、测试并通过 Git 分阶段提交；推送与发布须经用户审查

## 0. Agent 执行原则（必读）

1. 将本文视为 V1 的产品需求、技术约束和验收标准。优先实现可运行的完整纵向切片，随后补全数据与交互，不要只生成空壳 UI。
2. **仅支持 GitHub Pages 静态部署**：在 localhost 开发与验证，预置 GitHub Actions 发布工作流，但**用户审查通过前禁止 push 或实际发布**。不加入 Cloudflare Pages、Docker、在线数据库、用户账户、服务器或运行时云 API。
3. 数据与图片需要事先下载并保存在本地；浏览页面时**不请求 PRTS 或其他外部 API**。若数据更新失败，应继续使用最后一次成功的本地数据快照。
4. **不要猜测游戏数据**。无法确认的字段保留 `null` / 空数组，并输出数据质量报告；严禁用概念图中的示例干员、阶位、盟约或特质冒充真实数据。
5. 需求明确时直接实现，不要每一步都等待人工批准。遇到来源页面无法访问或结构不一致，优先实现可测试的解析器与诊断结果，明确标注阻塞，不得伪造“已同步成功”。
6. 保持代码小而清晰，避免过度设计；只在功能需要时引入依赖。**Git commit 必须由实际、可验证的阶段成果构成**。
7. 不得覆盖用户已有的未提交更改。若仓库非空，先检查现状再修改；不要使用 `git reset --hard`、强制推送等破坏性命令。
8. 用户在每轮交付后审查代码、数据与 UI；除非用户明确批准，不要合并到 `main`、推送到 GitHub 或触发 Pages 部署。

## 1. 项目目标与范围

### 1.1 使用场景

用户在游玩《明日方舟》卫戍协议时，把网页开在本机浏览器或副屏（本地开发时 `localhost`，发布后为 GitHub Pages URL），几秒钟内完成：

- 按**核心盟约 / 附加盟约**查询盟约效果及所属干员；
- 按**干员**查询所处阶位、核心盟约、附加盟约、特质类型、普通与精锐特质；
- 从一个干员的盟约标签快速跳转到该盟约；
- 按多个盟约、阶位、特质类型筛选干员；
- 查询时无需连接 PRTS，所有数据与头像由静态网站同源提供；本地开发也可使用已有快照（不承诺离线首次访问 Pages）。

### 1.2 V1 必须包含（P0）

- 单页三栏布局：左栏盟约列表，中栏盟约效果和干员网格，右栏选中干员详情。
- 核心盟约/附加盟约/全部切换；盟约名称搜索。
- 盟约详细效果展示，包括原始描述、激活条件及额外触发条件（以来源可获得字段为准）。
- 所属干员网格：真实本地头像、名称、Ⅰ～Ⅵ阶徽标；按阶位过滤和排序。
- 干员详情：真实名称、阶位、原型映射（存在时）、最多 3 个盟约及其类别、特质类型、普通特质、精锐特质。
- 干员名称搜索；多盟约 AND 交叉筛选；特质类型过滤。
- 点击任意盟约标签可以定位对应盟约；明确区分“跳转盟约”和“添加为交叉筛选条件”两种操作。
- 本地 JSON 数据、本地头像、来源信息、数据校验与缺失图片回退。
- Python 数据采集/转换脚本；文档化运行方式；基础自动化测试；Git 阶段性提交。
- GitHub Pages 项目站点兼容性、GitHub Actions 静态构建与发布配置、审查后发布流程。

### 1.3 V1 不做（Out of scope）

- 除 GitHub Pages 以外的云托管、独立后端、数据库、账号、在线同步服务。
- 阵容保存、队伍模拟、伤害计算器、层数动态仿真、抽卡/商店模拟。
- 移动端原生 App、完整 PWA / Service Worker、多人协作。
- 动画大特效、复杂游戏背景、角色立绘、声音、主题皮肤系统。
- 任何绕过访问控制、验证码或反爬限制的抓取技术。
- 自动定时爬取 PRTS 或在 GitHub Pages 浏览器中实时抓取 PRTS；V1 仅本地手动更新，随后提交静态快照。

## 2. 数据来源、版本及采集策略

### 2.1 可核实的起始来源

- PRTS「卫戍协议：盟约/PRTS盟约记录」：https://prts.wiki/w/卫戍协议：盟约/PRTS盟约记录
- PRTS「卫戍协议：盟约 下半/PRTS盟约记录」：https://prts.wiki/w/卫戍协议：盟约_下半/PRTS盟约记录
- PRTS「卫戍协议·规程/PRTS盟约记录」：https://prts.wiki/w/卫戍协议·规程/PRTS盟约记录
- PRTS「模板:卫戍协议/参战干员」：https://prts.wiki/w/模板:卫戍协议/参战干员
- PRTS「卫戍协议」总览：https://prts.wiki/w/卫戍协议
- MediaWiki Imageinfo API 文档：https://www.mediawiki.org/wiki/API:Imageinfo

**注意**：上述为候选来源，存在多个版本/期数，**不得合并**。在第一次抓取前读取各页标题、所属活动/期数、页面说明和修订信息，确定唯一默认数据集。若无法可靠推断“当前活动版本”，按仓库配置文件显式选择一个源版本；在 README 中披露该选择，不可暗自混合。V1 可以只完整支持一个确定版本，其余版本不强制实现切换。

### 2.2 版本模型

`config/data-source.json` 固定：

```json
{
  "datasetId": "replace-with-verified-edition-id",
  "displayName": "从 PRTS 核实后填写的期数名称",
  "wikiPageTitle": "卫戍协议：盟约/PRTS盟约记录",
  "wikiBaseUrl": "https://prts.wiki",
  "revisionId": null
}
```

- `datasetId` 为稳定且唯一的本地标识；实际填入经核实的信息。
- 初次成功采集时，记录页面修订 ID、抓取时间（ISO 8601）、来源 URL、解析器版本及统计信息。
- 如来源拆分成多个子页，只能在确认属于**同一数据集**后将 `sourcePages` 扩展为列表。
- 不在 V1 UI 放置不可用的“第 X 期”选择器；仅在界面角落显示当前数据版本/采集时间。

### 2.3 获取方式

优先采用 PRTS 可用的 MediaWiki Action API（查询 Wikitext、解析页面或图片 `imageinfo`）。Agent 先验证实际端点、访问权限及响应结构，不要假设 API 一定可用。若 API 不可用且站点允许，可降级解析公开 HTML，但应将解析器隔离、留存测试样本并说明局限。

参战干员模板有如下逻辑字段（字段名依据已知 PRTS 模板，实际抓取时再次验证）：

```text
干员, 原型, 盟约1, 盟约2, 盟约3,
特质类型, icon, 特质1, 特质2
```

解析时同时保留表格/标题所决定的Ⅰ～Ⅵ阶。模板不一定显式包含阶位，**必须从所在分组上下文提取，不得默认 VI 阶或由角色稀有度推断**。

普通/精锐特质作为不同文本存储，保留原始数值、触发词、换行、括号与特殊说明（例如 `<获得时>`）。禁止以正则删除玩法信息。支持保留 PRTS 原文及保守的展示格式化。

### 2.4 头像下载

- 优先从页面明确给出的文件/图片链接，或 Wiki 文件标题映射，经 MediaWiki `imageinfo` 查出实际下载 URL；不要只靠 `头像 {名字}.png` 猜文件名。
- 支持 `干员` 与 `原型` 头像关系，保留来源字段和映射规则；如有卫戍协议专用头像，优先使用源页面明确指定的素材。
- 下载到 `public/avatars/`；使用稳定 ID 或内容哈希命名以避免特殊字符路径冲突。
- 可直接保存原图格式；WebP 转换**可选**，只有在环境依赖简单且不损坏图像时执行。
- 必须有限速、超时、重试、失败日志与 User-Agent 标识，遵守站点规则，不绕过反爬限制。
- 某头像无法下载时用统一占位图并生成缺失清单，不能使整个数据更新失败。
- 记录素材来源与原站版权说明；本地个人使用仍保留可追溯性。

### 2.5 同步命令与离线行为

提供以下命令（名称可等价但须写入 README）：

```bash
python -m pip install -r scripts/requirements.txt
python scripts/sync_prts.py --config config/data-source.json
python scripts/validate_data.py
npm install
npm run dev
```

- `npm run dev` **只读取已有本地数据，不自动抓取 PRTS**。
- 第一次克隆后的可用性：仓库需包含一份经过核实的默认数据快照及必要头像；若受体积/授权限制不能提交完整头像，必须评估 GitHub Pages 是否仍能完整显示，并明确缺图回退与资源生成流程；不得宣称已完整发布。
- 更新时采用临时输出目录 + 验证成功后替换正式文件，避免失败导致原有数据损坏。
- 在 `data/reports/` 生成同步结果摘要：总盟约数、总干员记录数、按阶位计数、缺失字段、缺图、无法解析的模板、重复键与来源修订。

## 3. 数据模型（TypeScript 接口）

以下接口作为前端和构建脚本的数据契约。允许增补字段，但不要破坏基础含义。

```ts
export type BondCategory = 'core' | 'additional';
export type OperatorTier = 1 | 2 | 3 | 4 | 5 | 6;

export interface Bond {
  id: string;                 // dataset 内唯一稳定 ID
  name: string;
  category: BondCategory;
  activationCount: number | null;
  effectText: string;         // PRTS 原文，不能编造
  extraEffectText?: string | null;
  notes?: string[];
  sourceUrl: string;
}

export interface OperatorEntry {
  id: string;                 // 必须区分版本、阶位及重名条目
  name: string;
  tier: OperatorTier;
  prototypeName?: string | null;
  avatarPath?: string | null; // 相对静态资源路径，例如 avatars/xxx.png；由统一 assetUrl 解析
  coreBondIds: string[];
  additionalBondIds: string[];
  traitType: string | null;
  normalTrait: string | null;
  eliteTrait: string | null;
  sourceUrl: string;
}

export interface DatasetMetadata {
  datasetId: string;
  displayName: string;
  sourcePages: Array<{ url: string; revisionId: number | null }>;
  fetchedAt: string;
  counts: { bonds: number; operators: number; missingAvatars: number };
}
```

关键约束：

1. 不可根据 `盟约1` 的位置直接判断核心盟约；必须和被选数据集的盟约分类表关联，或有明确来源依据。
2. 每条 `OperatorEntry` 的所有盟约 ID 必须能在 `bonds.json` 中找到；找不到就报告错误，不静默丢弃。
3. 重名、多阶位、原型替代必须得到独立且稳定的 ID，避免 UI 把不同记录合并。
4. 游戏内自选/甄选干员与 PRTS 固定的参战干员数据库不是一回事；V1 默认展示来源记录的预设条目，不推断所有可自选干员的盟约。
5. 不要错误地把“无精锐特质”显示成与普通特质相同；缺失时显示“未收录”。

推荐输出：

```text
public/data/bonds.json
public/data/operators.json
public/data/metadata.json
```

## 4. UI / UX 规范

### 4.1 风格

**极简工具型 Dashboard，非游戏美术复刻。** 参考上一版简洁浅色概念图的**信息层级**，不要照搬其中未经验证的游戏数据。

- 默认浅色主题：白色、灰白背景、深灰正文；蓝色仅用于当前选中状态与交互强调。
- 不用复杂背景画、罗德岛装饰、发光描边、粒子、渐变大图、3D 效果。
- 干员头像是唯一主要视觉素材；盟约图标如无法可靠获取，可使用纯文字/简洁通用图标。
- 字体优先系统中文字体；细边框、小圆角、轻微间距；紧凑但不拥挤。
- 视觉优先级：**盟约效果 > 干员阶位/头像 > 干员特质**。

### 4.2 桌面三栏布局

推荐在宽屏（≥ 1100 px）使用：

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│ 卫戍协议 · 盟约速查             [版本信息]              [搜索干员...]         │
├────────────────┬──────────────────────────────────┬────────────────────────────┤
│ 核心 / 附加/全部│ [当前盟约名称] [分类]             │ [头像] 干员名  [Ⅵ阶]       │
│ [搜索盟约]     │ 激活人数、盟约完整效果           │ 核心盟约 / 附加盟约        │
│                │                                  │                            │
│ 盟约 A         │ 所属干员（N）                    │ 特质类型                   │
│ 盟约 B         │ [Ⅰ][Ⅱ][Ⅲ][Ⅳ][Ⅴ][Ⅵ]  [排序]  │ 普通特质                   │
│ 盟约 C ...     │ [头像][头像][头像][头像]         │ 精锐特质                   │
│                │ [头像][头像][头像][头像]         │                            │
└────────────────┴──────────────────────────────────┴────────────────────────────┘
```

建议左栏约 220–260 px、右栏约 290–360 px，中栏自适应；页面尽量保持一屏可查阅，长列表独立滚动。不要因响应式而将关键内容完全隐藏。

### 4.3 交互规则

**盟约列表**
- 分类 Tab：核心 / 附加 / 全部，选中效果明确。
- 输入关键词可按盟约名称实时过滤；无结果显示空状态。
- 点击盟约：更新中栏标题、完整效果、属于该盟约的干员列表；保留符合逻辑的阶位与搜索状态，若当前干员不再匹配则取消选中。

**干员网格**
- 每张卡片显示头像、中文名称、清晰的罗马数字阶位。鼠标与键盘均可选择。
- 阶位筛选支持“全部”及Ⅰ～Ⅵ，支持阶位升序/降序与名称排序。
- 点击卡片：右侧显示该记录完整详细信息，突出当前选中卡片。
- 头像不存在时显示占位图，界面不报错。

**右侧详情**
- 展示头像、名称、阶位、可选原型名称、所有核心/附加盟约标签。
- 展示特质类型、普通特质、精锐特质的全文；保留换行。
- 点击盟约标签默认“跳转到该盟约”；另设清晰的 `+ 添加筛选` 操作，避免行为含糊。

**多条件筛选**
- 允许用户从盟约列表/筛选区添加多个盟约条件，默认 **AND**：结果必须同时拥有所有已选盟约。
- 筛选条件可逐个删除或一键清空；结果数随筛选变化。
- 干员名称搜索、阶位、特质类型与盟约 AND 条件共同生效。
- 筛选无结果时说明当前条件并可一键清空。
- 对于“当前盟约”和“交叉筛选”关系，采用一致规则：默认在当前盟约集合上叠加 AND 条件，并在界面明确展示所有生效条件。

**显示细节**
- 精锐特质标签仅在有原始文本时显示内容；缺失显示“未收录”。
- 对公式、括号说明、百分号等完整显示；不把完整效果缩成不可查看的省略号。
- 使用 `white-space: pre-wrap` 或同等安全的纯文本渲染，不直接注入未经清理的 Wiki HTML。
- 可额外添加“返回 PRTS 来源”文字链接，但 V1 的本地使用不依赖其可访问。

### 4.4 窄屏适配

- 900–1099 px：右侧详情可以抽屉/覆盖层形式展示，中栏保持可用。
- < 900 px：左侧盟约列表以可展开筛选栏呈现，卡片列数降低。
- 不要求手机端像素级优化，但不可出现横向内容截断导致无法查询。

### 4.5 状态与容错

必须覆盖：加载中、数据不存在/损坏、无搜索结果、头像缺失、没有选中干员、特质缺失。前端不应因单条记录格式错误而整页白屏；数据构建阶段应主动阻止严重无效数据进入正式快照。

## 5. 推荐项目结构

```text
sweep-lookup/
├── REQUIREMENTS.md
├── README.md
├── .gitignore
├── .github/
│   └── workflows/
│       └── deploy.yml             # GitHub Pages CI/CD（审查后启用发布）
├── package.json
├── vite.config.ts
├── tsconfig.json
├── config/
│   └── data-source.json
├── scripts/
│   ├── requirements.txt
│   ├── sync_prts.py
│   ├── validate_data.py
│   ├── parsers/                 # Wikitext / HTML 解析（按需）
│   └── tests/                   # 解析器 fixture 测试
├── data/
│   ├── fixtures/                # 最小且可复现实例
│   └── reports/                 # 同步与数据质量报告
├── public/
│   ├── data/
│   │   ├── bonds.json
│   │   ├── operators.json
│   │   └── metadata.json
│   └── avatars/
│       └── placeholder.svg
└── src/
    ├── App.tsx
    ├── components/
    │   ├── BondSidebar.tsx
    │   ├── BondDetails.tsx
    │   ├── OperatorGrid.tsx
    │   ├── OperatorCard.tsx
    │   ├── OperatorDetails.tsx
    │   └── FilterBar.tsx
    ├── hooks/
    ├── lib/                     # selectors、排序、路径校验
    ├── types/
    ├── styles/
    └── tests/
```

允许根据实现适当调整文件夹，不需要为了目录结构引入额外框架。可用 `fetch` 从 `/data/*.json` 读取静态资源；不使用 Redux、Zustand 等状态库，除非实际出现难以维护的复杂状态。

## 6. Git 工作流与 GitHub Pages 发布（必须执行）

### 6.1 分支与审查

- 在项目根目录执行 `git init -b main`（如果项目已有 Git，保留现有历史和分支）。初次提交需求文档、README、`.gitignore` 等可验证成果。
- **每一个 V1 功能使用 `feat/v1-static-explorer` 分支开发**，仅在本地 commit。用户审查通过后才创建 PR/合并到 `main`；若尚未配置 GitHub 远程，则给出配置步骤而不擅自创建或推送仓库。
- Agent 可在分支上持续开发并提交，但在交付审查前必须停止；**不得未经批准执行 `git push`、合并到 main、触发公开发布**。
- 不更改 Git 全局配置；提交作者身份如缺失，先检查当前仓库可用配置，不得冒用用户身份。
- 每次审查交付提供 `git log --oneline`、`git diff main...HEAD --stat`、`git status`、本地预览指令与待审事项；若无可比较的 main 基线，则明确说明。

### 6.2 推荐 Commit 节点

```text
 docs: specify static-site requirements and review gates
chore: initialize Vite React TypeScript project
feat(data): add PRTS source config and parser
feat(data): normalize bond and operator datasets
feat(assets): download and map operator avatars
feat(ui): implement minimal three-column explorer
feat(filters): implement search tier and bond intersection
test: add dataset validation and interaction tests
ci: configure GitHub Pages build and publish workflow
docs: complete local usage and source attribution
```

每步可根据实际实现拆分/合并，但保持可追溯性，提交前运行相关测试。

### 6.3 GitHub Pages 约束

- V1 面向 `https://<USERNAME>.github.io/<REPO>/` 这种**项目站点**；部署路径不假设为根路径。仓库名称若未确定，通过配置或构建环境确定 `base`，不要硬编码一个猜测的 repo 名称。
- Vite `base` 在项目站点上配置为 `/<REPO>/`，而 localhost 开发仍应工作；可在 `vite.config.ts` 根据 `GITHUB_REPOSITORY` 或显式环境变量计算生产 base，必要时允许覆盖。若是 `<USERNAME>.github.io` 用户站点则使用 `/`。路径选择写入 README。
- 所有 JSON、头像、占位图和可选图标使用 `import.meta.env.BASE_URL`/统一 `assetUrl()` 拼接；组件不要直接拼接根路径 `/avatars/`。
- 使用 `.github/workflows/deploy.yml`：`push` 到 `main` 或 `workflow_dispatch` 触发，权限最小化（`contents: read`、`pages: write`、`id-token: write`），步骤包含 checkout、setup-node、`npm ci`、质量检查、`npm run build`、configure-pages、upload-pages-artifact（`dist/`）、deploy-pages。应合理配置并发避免覆盖部署。
- 发布不运行 Python 抓取：**同步 PRTS 必须提前在本地完成**，GitHub Actions 仅使用已提交的 JSON、图片和锁文件构建，保证可重现。
- 禁止将 PRTS API 密钥、凭据、个人文件或网络代理配置提交到仓库；网站运行时不依赖第三方请求。
- 因公开发布，README 和站点页脚必须包含非官方声明、PRTS 数据来源和图片权利归属说明，并在发布前检查来源站条款、许可、署名要求及素材使用边界。不能简单假定百科头像可随意再分发。
- GitHub 侧需由用户在 **Settings → Pages → Build and deployment → Source → GitHub Actions** 启用 Pages，并确认仓库可公开展示相关数据与素材。**只有用户审查批准后才连接 remote / push / 合并部署。**
- 项目无需 React Router；如果后来加入客户端路由，必须设计 GitHub Pages 刷新时的 404 兼容策略。V1 单页无此问题。

### 6.4 本地与发布前验证

```bash
npm ci
npm run dev
npm run typecheck
npm run test
npm run build
npm run preview
```

- 本地验证 `http://localhost:5173/`（实际端口以 Vite 输出为准）。
- 必须再以非根路径构建并预览，检查 `/<REPO>/data/*.json`、头像、字体/图标 URL 不 404。可通过固定的测试 repo 名称或脚本完成，不能只验证根目录。
- Pages 工作流配置就绪不等于站点已发布；在获得用户批准之前只汇报“待发布”。

### 6.5 .gitignore

必须忽略：`node_modules/`、`dist/`、`.venv/`、`__pycache__/`、`.pytest_cache/`、临时下载文件和抓取缓存。不要无意忽略最终需要的已核实数据快照或本地头像。图片资源是否纳入 Git 需考虑 Pages 及原始素材授权，优先可复现构建。

### 6.6 完成时交付审查

Agent 最终须汇报：
- 已完成与尚未完成的功能；
- 确切使用的 PRTS 页面、数据期数和 revision；
- 记录条数、缺失头像数量、验证是否通过；
- `npm run dev` 与非根路径预览的操作方法；
- 测试/构建结果，Pages 工作流是否准备好；
- `git log --oneline`、`git diff main...HEAD --stat` 与 `git status`；
- **明确请求用户审查，未获批准不得推送或发布**。

## 7. 测试要求

### 7.1 数据测试（Python）

- 同一数据集内盟约 ID 唯一、干员条目 ID 唯一；
- 干员阶位仅能为 1～6；
- 所有盟约引用可解析；核心和附加分类一致；
- 模板字段缺失、特殊字符、跨行特质、原型映射、重复名字能正确处理；
- 输出统计信息和原始记录数合理匹配；
- 当抓取失败时保留上一个有效快照；
- 至少包含来自真实页面的、在合理范围内可再分发的最小解析 fixture（保留源页 URL 和获取时间）。

### 7.2 前端测试（Vitest + React Testing Library）

- 选择盟约更新效果及网格；
- 选择干员更新右侧详情；
- 多盟约 AND 交集正确；
- 阶位和特质过滤正确；
- 搜索与筛选叠加正确；
- 无结果、缺头像、缺精锐特质的空状态正确。

### 7.3 最低质量门槛

```bash
npm run typecheck
npm run test
npm run build
python scripts/validate_data.py
```

所有命令必须通过。若某项因来源网络不可用阻塞，须准确记录，不可以仅声称“测试通过”。如有浏览器测试能力，进行一次真实 localhost 手动/自动浏览验证。

## 8. 完成定义（Definition of Done）

- [ ] 在一台本地开发电脑，按 README 操作能够启动页面。
- [ ] GitHub Pages 的非根路径构建和预览通过，静态资源均可正确加载。
- [ ] GitHub Actions Pages 工作流已配置，且公开发布前已经提供用户审查机会。
- [ ] 浏览/查询使用本地或同源静态资源，不需要实时访问 PRTS。
- [ ] 页面清楚显示数据集对应的 PRTS 期数及抓取时间。
- [ ] 支持所有已核实的核心与附加盟约，效果内容来自 PRTS。
- [ ] 该数据集的预设干员条目按Ⅰ～Ⅵ阶正确显示，带真实或占位头像。
- [ ] 干员详情包含真实盟约配置、特质类型、普通与精锐特质。
- [ ] 盟约导航、搜索、多盟约 AND、阶位过滤、特质过滤正常工作。
- [ ] 缺失数据有合理提示，不会崩溃或静默使用伪造数据。
- [ ] 有一条可复现的同步路径和可读的数据质量报告。
- [ ] 自动化测试/构建通过，Git 有阶段性提交，工作区干净（或说明遗留差异）；用户批准前没有 push、合并或部署。

## 9. 推荐实施顺序（Agent 自主推进）

1. 读取本需求，检查环境与 Git 状态；初始化 Vite React TS + Tailwind、测试配置。
2. 实测 PRTS 来源，选定并锁定单一期数；下载最小样本并确认模板及阶位解析。
3. 定义 JSON schema / TS 类型；实现解析器、规范化、校验器、原子写入与数据报告。
4. 接入头像元数据查询/下载；缺图回退；确认数据可离线加载。
5. 用实际数据实现三栏 UI，先完成盟约 → 干员 → 特质的查询闭环。
6. 添加搜索、阶位、特质类型、多盟约 AND 过滤，并补充测试。
7. 配置 GitHub Pages 项目子路径和 Actions 工作流；检查静态资源路径与生产预览。
8. 完善错误/空状态、README、来源与授权说明；运行所有检查，在功能分支完成 Git 提交，等待用户审查后再发布。

## 10. 对 Agent 的最终指令

**请直接在当前项目目录内实现以上 V1，包含 GitHub Pages 兼容配置和工作流，但在用户审查批准前不要合并、推送或实际部署。不要替我选择未经核实的游戏数据。优先保证数据准确和检索流畅，其次才是视觉细节。全程通过本地 Git 进行版本控制，完成后按第 6.6 节提交审查材料。**
