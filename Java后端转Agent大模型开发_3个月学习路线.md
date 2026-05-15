# Java后端转Agent大模型开发 —— 3个月学习路线

> 适用人群：大三学生，有Java后端基础（Spring Boot、MySQL、Redis等）
> 目标：3个月内具备Agent大模型开发能力，能独立完成项目并用于求职/竞赛

---

## 你的优势分析（Java后端背景）

| 已有技能 | 在Agent开发中的复用 |
|---------|-------------------|
| Java OOP + 设计模式 | Agent架构设计、工具链抽象 |
| Spring Boot / MVC | 理解Agent服务的API设计和中间件 |
| MySQL / Redis | RAG系统的向量数据库、缓存层 |
| Maven / Git / Linux | 项目构建、部署、协作 |
| 多线程 / 并发 | Agent异步调用、流式输出 |

**核心转变**：Java → Python（主语言切换），后端CRUD → LLM应用层开发

---

## 总体路线图

```
Month 1: Python速成 + LLM基础（内功）
Month 2: Agent核心 + RAG + 框架（招式）
Month 3: 实战项目 + 部署 + 面试（出山）
```

---

## 第一阶段：Python速成 + LLM基础（第1-4周）

### 目标
- Python写熟练，能用FastAPI写接口
- 理解LLM基本原理（Transformer、Prompt、Token）
- 能调用OpenAI/国内大模型API完成简单任务

### Week 1-2: Python急速上手

**你不需要从零学Python**，你有Java基础，重点是对比学习：

| 概念 | Java | Python |
|------|------|--------|
| 变量 | `int x = 10;` | `x = 10` |
| 列表 | `List<Integer>` | `[1, 2, 3]` |
| 字典 | `Map<String, Object>` | `{"key": "value"}` |
| 循环 | `for (int i=0; i<n; i++)` | `for i in range(n)` |
| 类 | `class A {}` | `class A:` (注意冒号) |
| 包管理 | Maven/Gradle | pip/conda/poetry |

**必学内容（每天2-3小时，2周搞定）：**

1. **基础语法**（3天）
   - 资源：[廖雪峰Python教程](https://www.liaoxuefeng.com/wiki/1016959663602400)（免费，只看前6章）
   - 重点：list/dict/set comprehension、lambda、装饰器、with语句
   - 练习：用Python重写你之前Java课程设计的一个模块

2. **异步编程**（2天）—— *Agent开发核心*
   - `async/await`、`asyncio`、`aiohttp`
   - 这是Java里相对薄弱的，要重点学
   - 资源：[Real Python - Async IO](https://realpython.com/async-io-python/)

3. **FastAPI框架**（3天）—— *替代Spring Boot*
   - 资源：[FastAPI官方教程](https://fastapi.tiangolo.com/zh/tutorial/)
   - 对比着Spring Boot学：路由 → @app.get/post、依赖注入 → Depends、中间件 → Middleware
   - 练习：用FastAPI写一个简单的CRUD接口，连MySQL

4. **Pydantic数据校验**（2天）
   - Java有Bean Validation，Python有Pydantic
   - 资源：[Pydantic官方文档](https://docs.pydantic.dev/latest/)

5. **LangChain基础**（4天）
   - 资源：[LangChain官方教程](https://python.langchain.com/docs/tutorials/)
   - 重点：Chain、Prompt Template、LLM调用、Output Parser
   - 练习：做一个"PDF问答机器人"

### Week 3-4: LLM核心概念

**必学内容：**

1. **LLM原理（理解层面，不要求推导公式）**
   - 资源：Andrej Karpathy的 [Intro to Large Language Models](https://www.youtube.com/watch?v=zjkBMFhNj_g)（1小时视频，必看）
   - 资源：李沐 [动手学深度学习](https://zh.d2l.ai/) 第11章（选看）
   - 理解：Token、Embedding、Attention、Transformer架构、Pretrain/SFT/RLHF

2. **Prompt Engineering**
   - 资源：[Prompt Engineering Guide](https://www.promptingguide.ai/zh)（免费，中文版）
   - 重点：Few-shot、Chain-of-Thought、ReAct、结构化输出
   - 练习：用不同Prompt策略完成同一任务，对比效果

3. **API调用实战**
   - OpenAI API / 国内：通义千问、DeepSeek、智谱GLM
   - 资源：[OpenAI Cookbook](https://cookbook.openai.com/)
   - 练习：封装一个统一的大模型调用工具类（类比Java的Service层）

4. **向量数据库入门**
   - 理解：Embedding、相似度检索（余弦相似度）
   - 工具：ChromaDB（轻量入门）、Milvus（生产级）
   - 资源：[ChromaDB文档](https://docs.trychroma.com/)

**Week 4 产出：** 一个基于FastAPI的"文档问答API"，支持上传TXT/PDF，能回答问题

---

## 第二阶段：Agent核心 + RAG + 框架深度（第5-8周）

### 目标
- 理解Agent的ReAct/Plan-Execute模式
- 掌握RAG全链路（切片→向量化→检索→重排序→生成）
- 熟练使用LangChain/LangGraph构建Agent

### Week 5-6: RAG（检索增强生成）—— 面试必问

RAG是Agent的"记忆系统"，也是面试最高频考点。

**学习路径：**

1. **RAG原理全景**（1天）
   - 资源：[LangChain RAG教程](https://python.langchain.com/docs/tutorials/rag/)
   - 理解：为什么要RAG（幻觉问题、知识截断）、基础流程

2. **文档处理**（2天）
   - 资源：[LangChain Document Loaders](https://python.langchain.com/docs/integrations/document_loaders/)
   - 重点：PDF解析(PyPDF2/pdfplumber)、文本分块策略、元数据管理
   - 实操：用Java类比——这就是"数据入库"环节

3. **Embedding与向量检索**（2天）
   - Embedding模型选择：text-embedding-3-small、bge-large-zh-v1.5
   - 向量数据库：ChromaDB(本地开发) → Milvus/Qdrant(生产)
   - 实操：把一本电子书切片存入向量库，做语义搜索

4. **高级RAG策略**（3天）—— *拉开差距的关键*
   - 多路召回（关键词 + 向量混合检索）
   - 重排序（Reranker模型：bge-reranker）
   - 父子文档检索（Small-to-Big）
   - 自查询检索（Self-Querying）
   - 资源：[Advanced RAG Techniques](https://www.deeplearning.ai/short-courses/advanced-retrieval-for-ai/)（DeepLearning.AI免费短课）

5. **GraphRAG**（2天，进阶了解）
   - 知识图谱 + RAG
   - 资源：[微软GraphRAG](https://microsoft.github.io/graphrag/)

### Week 7-8: Agent核心开发

这是最关键的两周，直接决定你能不能做Agent开发。

**学习路径：**

1. **Agent理论**（1天）
   - 资源：[Lilian Weng - LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)（必读博客）
   - 核心：Planning（规划）、Memory（记忆）、Tool Use（工具使用）
   - 对比Java：Agent就像一个有自主决策能力的"业务编排引擎"

2. **ReAct模式**（2天）
   - Reasoning + Acting：思考→行动→观察→思考→...循环
   - 资源：[ReAct论文](https://arxiv.org/abs/2210.03629) + LangChain ReAct实现
   - 实操：自己实现一个简单的ReAct循环（不用框架）

3. **LangChain Agent深度**（3天）
   - Agent类型：OpenAI Functions、ReAct、Structured Chat
   - 核心概念：AgentExecutor、Tool、AgentFinish、Intermediate Steps
   - 资源：[LangChain Agents文档](https://python.langchain.com/docs/modules/agents/)

4. **LangGraph**（3天）—— *2024-2025主流*
   - 状态图驱动的Agent框架
   - 重点：StateGraph、Node、Edge、Conditional Edge、Checkpoint
   - 资源：[LangGraph官方教程](https://langchain-ai.github.io/langgraph/tutorials/)
   - 实操：用LangGraph重写之前的ReAct Agent

5. **Tool定义与Function Calling**（2天）
   - 如何定义Tool（类比Java的接口方法）
   - OpenAI Function Calling / Tool Call机制
   - 实操：写一个能查数据库、调API、执行Python代码的Agent

6. **Multi-Agent**（1天，进阶了解）
   - 多Agent协作：CrewAI、AutoGen
   - 资源：[CrewAI文档](https://docs.crewai.com/)

**Week 8 产出：** 一个完整的Agent Demo——能接收自然语言指令，自动拆解任务、调用工具、返回结果的智能助手

---

## 第三阶段：实战项目 + 部署 + 求职准备（第9-12周）

### Week 9-10: 项目一——智能代码助手Agent

**项目描述：** 输入自然语言需求，Agent自动生成Java/Python代码、运行测试、修复Bug

**技术栈：** FastAPI + LangGraph + OpenAI/DeepSeek + Docker代码沙箱 + Redis

**核心功能：**
- 需求理解 → 代码生成 → 语法检查 → 单元测试 → Bug修复
- 流式输出（SSE/WebSocket）
- 会话管理（多轮对话上下文）

**亮点：** 
- 代码沙箱隔离执行（安全）
- 和GitHub Copilot对比分析（体现思考）

### Week 10-11: 项目二——企业知识库RAG系统

**项目描述：** 上传企业内部文档，构建知识库，支持自然语言问答

**技术栈：** FastAPI + LangChain + Milvus/Qdrant + MySQL + MinIO

**核心功能：**
- 多格式文档解析（PDF/Word/Markdown/图片OCR）
- 智能分块 + 混合检索 + 重排序
- 引用溯源（答案标注来源文档和页码）
- 权限管理（不同用户可访问不同知识库）

**亮点：**
- 完整的RAG Pipeline
- 生产级架构（对比你的Java项目经验）
- 向量库性能优化（索引、量化）

### Week 11-12: 项目三——多Agent协作系统（加分项）

**项目描述：** 多个Agent分工协作完成复杂任务（如：市场调研→数据分析→报告生成）

**技术栈：** CrewAI/LangGraph + FastAPI + Redis消息队列

**核心功能：**
- 规划Agent：拆解任务
- 执行Agent：调用工具执行子任务
- 审查Agent：检查结果质量
- Agent间通信机制

**简历上的写法：** "基于LangGraph实现的多Agent协作系统，通过DAG任务编排和消息总线实现Agent间解耦通信"

---

## 学习资源汇总（按优先级排序）

### 必看课程（免费）⭐⭐⭐⭐⭐

| 资源 | 链接 | 说明 |
|------|------|------|
| 吴恩达 LangChain开发 | [DeepLearning.AI](https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/) | 1小时短课，入门必看 |
| 吴恩达 LangChain Chat with Your Data | [DeepLearning.AI](https://www.deeplearning.ai/short-courses/langchain-chat-with-your-data/) | RAG入门 |
| 吴恩达 Building Agentic RAG with LlamaIndex | [DeepLearning.AI](https://www.deeplearning.ai/short-courses/building-agentic-rag-with-llamaindex/) | Agent + RAG结合 |
| 吴恩达 Multi AI Agent Systems | [DeepLearning.AI](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) | CrewAI多Agent |
| 吴恩达 AI Agentic Design Patterns | [DeepLearning.AI](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/) | AutoGen模式 |

### 必读文档 ⭐⭐⭐⭐

| 资源 | 链接 |
|------|------|
| LangChain官方文档 | https://python.langchain.com/docs/ |
| LangGraph官方教程 | https://langchain-ai.github.io/langgraph/tutorials/ |
| FastAPI官方教程 | https://fastapi.tiangolo.com/zh/tutorial/ |
| OpenAI Cookbook | https://cookbook.openai.com/ |
| Prompt Engineering Guide | https://www.promptingguide.ai/zh |

### 推荐书籍（选1-2本精度）

| 书籍 | 说明 |
|------|------|
| 《大规模语言模型：从理论到实践》 | 国内作者，适合入门理论 |
| 《LangChain编程：从入门到实践》 | 实战导向 |
| 《Building LLM Apps》by Valentina Alto | 英文，全面但需要基础 |

### GitHub项目参考 ⭐⭐⭐⭐

| 项目 | 说明 |
|------|------|
| [LangChain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat) | 国内最火RAG项目，基于LangChain |
| [FastGPT](https://github.com/labring/FastGPT) | 国内开源的AI知识库 |
| [Dify](https://github.com/langgenius/dify) | LLM应用开发平台，学架构设计 |
| [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | 最早的自主Agent，学Agent思想 |

---

## 每日学习计划参考（Weekday）

| 时段 | 内容 | 时长 |
|------|------|------|
| 上午 | 看课程/读论文/看文档（输入） | 2h |
| 下午 | 动手写代码（输出） | 3h |
| 晚上 | 复盘、写笔记、逛GitHub/公众号 | 1h |

> 周六日各4-5小时做项目，连续推进

---

## 求职/面试专项建议

### 简历关键词（必须出现）

```
Python, FastAPI, LangChain, LangGraph, RAG, Agent, LLM,
向量数据库(Milvus/ChromaDB), Function Calling, Prompt Engineering,
Docker, Redis, MySQL, 流式输出(SSE/WebSocket)
```

### 常见面试题（准备方向）

1. **RAG全流程**：文档怎么切？Embedding怎么选？检索怎么优化？幻觉怎么处理？
2. **Agent原理**：ReAct vs Plan-Execute区别？Tool怎么定义？Token消耗怎么控制？
3. **项目深挖**：你项目里最大挑战是什么？怎么解决？
4. **Java vs Python**：为什么转？Java经验怎么看？（强调工程能力和架构思维）
5. **部署相关**：GPU选型？并发怎么处理？成本怎么控制？

### 与纯AI背景应届生的差异点（你的卖点）

- 你有工程落地能力（Java后端项目经验）
- 你懂数据库、缓存、分布式（RAG系统天然需要）
- 你写过生产级代码（单元测试、CI/CD、代码规范）
- Agent开发不只是调API，需要扎实的软件工程功底

---

## 技术趋势补充（2025-2026）

1. **MCP协议（Model Context Protocol）**：Agent与外部工具的标准协议，类比USB统一接口
   - 资源：https://modelcontextprotocol.io/
2. **LangGraph主导Agent编排**：LangChain的Agent模块逐渐被LangGraph取代
3. **Vercel AI SDK / Mastra**：TypeScript生态的Agent框架也在崛起
4. **本地模型部署**：Ollama + llama.cpp + vLLM，降低API成本

---

## 检查清单（3个月后对照）

- [ ] Python异步编程熟练（async/await）
- [ ] FastAPI能独立写完整的后端服务
- [ ] 理解Transformer/Attention/Prompt/Token核心概念
- [ ] 能用LangChain/LangGraph构建Agent
- [ ] 掌握RAG全链路（切片→向量化→检索→生成）
- [ ] 了解至少2种向量数据库
- [ ] 独立完成2-3个完整项目并开源到GitHub
- [ ] 能解释ReAct/Function Calling/Multi-Agent原理
- [ ] 流式输出（SSE）在项目中落地
- [ ] Docker部署LLM应用
- [ ] 简历更新完毕，可以投递

---

> **最后一句大实话**：Agent开发目前门槛不高（相比传统ML算法），Java后端转过来有天然优势——你缺的不是编码能力，是LLM领域知识和Python熟练度。3个月每天投入4-5小时，完全够你拿到大模型应用开发的实习/校招offer。加油！
