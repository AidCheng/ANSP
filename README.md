# 卫戍协议 · 盟约速查

非官方《明日方舟》卫戍协议本地查询工具。数据来自 [PRTS「卫戍协议·规程/PRTS盟约记录」](https://prts.wiki/w/卫戍协议·规程/PRTS盟约记录)，与其他期数不混用。游戏及图片权利归各自权利人所有。公开发布前须核查 PRTS 的内容许可、署名与素材使用条款；仓库中的图片来自 PRTS 页面明确引用的素材；素材权利仍属于各自权利人。

## 当前数据与已知限制

选用的是「卫戍协议·规程」，采集时 PRTS 将其列为当前活动。数据来自该页 MediaWiki revision **450591**，共 26 个盟约、143 条干员，采集时间和分阶数量见 `public/data/metadata.json` 与 `data/reports/sync.json`。页面是本地快照，浏览时不请求外部 API。盟约图标和干员头像通过同一修订页面中明确的图片地址获取；下载结果、源地址及缺失情况见 `data/reports/images.json`。部分 Wiki 模板未能转换成纯文本，原有标记保留在效果中，见报告的 `unknownTemplates`；因此内容尚需人工核对。测试 fixture 包含取自先前版本「卫戍协议：盟约」的一小段示例（修订 449018）及明确标注的合成测试盟约，仅用于测试，绝不进入实际数据。

当前实现是可审查的初版，尚未完成图片许可核查、完整模板格式化和更多前端交互自动化测试，不能视为满足全部 V1 验收条件。PRTS 可能更新格式或修改页面数据，请审查每次同步生成的报告。

## 本地运行

需要 Node.js 22.12+（推荐 Node 22 LTS）和 Python 3.9+。

```bash
npm ci
npm run dev
```

打开终端输出的 localhost 地址。开发服务器只读本地静态 JSON，不会自动联网。验证：

```bash
npm run typecheck
npm run test
python3 -m unittest discover -s scripts/tests
python3 scripts/validate_data.py
npm run build
npm run preview
```

## 手动更新数据

```bash
python3 -m pip install -r scripts/requirements.txt
python3 scripts/sync_prts.py --config config/data-source.json
python3 scripts/sync_images.py
python3 scripts/validate_data.py
```

数据脚本使用标准库，访问选定页面的 MediaWiki API，失败重试并在解析或校验失败时保留原快照。检查 `data/reports/sync.json` 的缺图、未识别模板、阶位统计和来源修订。图片脚本核对页面修订，并仅下载页面明确引用的素材，限制请求频率，重试失败并保留已有图片；数据或模板结构变化时可能报错，需要检查解析器和报告。字段来源为页面的盟约与参战干员模板；分类由盟约分组决定，阶位来自表格标题。无来源字段不猜测。请勿将不同期数页面混合。

## GitHub Pages

工作流仅构建已提交快照，不抓取 PRTS。项目站点根据 `GITHUB_REPOSITORY` 自动设置 `/<仓库名>/`；`<用户名>.github.io` 用户站点使用 `/`。可通过 `VITE_BASE_PATH` 覆盖。非根路径本地验证示例：

```bash
VITE_BASE_PATH=/test-repo/ npm run build
VITE_BASE_PATH=/test-repo/ npm run preview
# 打开终端给出的地址
```

审查数据、代码、图片许可及 UI 后，用户可配置 GitHub remote 并推送；在 GitHub 的 Settings → Pages → Build and deployment 中选择 GitHub Actions。只有用户明确批准后才合并 main、推送或部署。`workflow_dispatch` 和 main 分支 push 都会触发工作流。
