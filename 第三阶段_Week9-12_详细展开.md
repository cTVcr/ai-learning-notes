# 第三阶段详细展开（Week 9-12）：实战项目 + 部署 + 求职冲刺

> 前8周积累了技术能力，这4周把能力变成项目产出的求职竞争力

---

## Week 9-10：项目一——CodeMate（智能代码助手Agent）

### 项目定位

这不是一个玩具项目，而是你简历上的核心项目。要能经得住面试深挖。

### 功能设计

```
用户输入："用Spring Boot写一个用户登录接口，包含JWT认证和Redis缓存"

Agent思考链：
  Thought: 需要拆解需求
  → 1. Spring Boot项目结构
  → 2. 登录接口Controller
  → 3. JWT工具类
  → 4. Redis缓存配置
  → 5. 单元测试

  Action: generate_code
  Action Input: Spring Boot登录Controller代码

  Observation: [生成了代码]

  Thought: 代码已生成，需要语法检查
  Action: syntax_check
  Action Input: [生成的代码]

  Observation: 语法正确

  Thought: 需要写单元测试 ...
  Action: generate_test
  ...

  Thought: 全部完成
  Final Answer: [完整的项目代码 + 测试 + 使用说明]
```

### 技术架构

```
┌──────────────┐     SSE/WebSocket      ┌─────────────────┐
│  Vue3前端     │ ◄──────────────────► │  FastAPI后端     │
│  (可选)       │                       │                 │
└──────────────┘                       │  /chat          │
                                       │  /chat/stream   │
                                       │  /projects      │
                                       └────────┬────────┘
                                                │
                          ┌─────────────────────┼─────────────────────┐
                          ▼                     ▼                     ▼
                   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
                   │ LangGraph     │    │ Docker沙箱    │    │ PostgreSQL   │
                   │ Agent编排     │    │ 代码执行      │    │ + Redis      │
                   └──────┬───────┘    └──────────────┘    └──────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   ┌────────────┐  ┌────────────┐  ┌────────────┐
   │ 代码生成    │  │ 语法检查    │  │ 测试生成    │
   │ (LLM)      │  │ (AST解析)   │  │ (LLM)      │
   └────────────┘  └────────────┘  └────────────┘
```

### 开发步骤（10天）

#### Day 57-58：项目骨架 + 代码生成

```python
# models.py —— 核心数据模型
from pydantic import BaseModel, Field
from enum import Enum

class Language(str, Enum):
    JAVA = "java"
    PYTHON = "python"
    GO = "go"

class CodeRequest(BaseModel):
    requirement: str = Field(..., description="自然语言需求描述")
    language: Language = Field(default=Language.JAVA)
    framework: str = Field(default="spring-boot", description="框架")
    context: str = Field(default="", description="已有代码上下文")

class CodeResponse(BaseModel):
    files: list[dict]  # [{"path": "src/...", "content": "..."}]
    explanation: str
    tests: list[dict] | None
    suggestions: list[str] | None

# agent.py —— LangGraph Agent
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

class CodeGenState(TypedDict):
    messages: list
    requirement: str
    language: str
    generated_code: str | None
    test_code: str | None
    review_feedback: str | None
    final_output: str | None

def create_code_agent():
    workflow = StateGraph(CodeGenState)
    
    # 节点
    workflow.add_node("analyze_requirement", analyze_requirement_node)
    workflow.add_node("generate_code", generate_code_node)
    workflow.add_node("syntax_check", syntax_check_node)
    workflow.add_node("generate_test", generate_test_node)
    workflow.add_node("fix_issues", fix_issues_node)
    workflow.add_node("format_output", format_output_node)
    
    # 流程
    workflow.set_entry_point("analyze_requirement")
    workflow.add_edge("analyze_requirement", "generate_code")
    workflow.add_edge("generate_code", "syntax_check")
    
    # 条件：语法有问题就修复，没问题就生成测试
    workflow.add_conditional_edges(
        "syntax_check",
        lambda s: "fix" if s.get("has_errors") else "test",
        {"fix": "fix_issues", "test": "generate_test"}
    )
    workflow.add_edge("fix_issues", "syntax_check")  # 修复后再检查
    workflow.add_edge("generate_test", "format_output")
    workflow.add_edge("format_output", END)
    
    return workflow.compile(checkpointer=MemorySaver())
```

#### Day 59-60：Docker代码沙箱

```python
# 安全执行用户代码——不能直接在服务器上运行！
import docker
import tempfile
import os

class DockerSandbox:
    """代码沙箱——在隔离容器中执行代码"""
    
    def __init__(self):
        self.client = docker.from_env()
        self.image = "python:3.11-slim"  # 或 openjdk:17-slim
    
    def run_code(self, code: str, language: str, timeout=30):
        """在Docker容器中执行代码"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 写入代码文件
            if language == "python":
                filepath = os.path.join(tmpdir, "main.py")
            elif language == "java":
                filepath = os.path.join(tmpdir, "Main.java")
            
            with open(filepath, "w") as f:
                f.write(code)
            
            # 在隔离容器中执行
            try:
                result = self.client.containers.run(
                    image=self.image,
                    command=f"python /code/main.py" if language == "python" else
                            f"javac /code/Main.java && java -cp /code Main",
                    volumes={tmpdir: {"bind": "/code", "mode": "ro"}},
                    mem_limit="256m",
                    cpu_quota=50000,
                    network_disabled=True,  # 禁用网络
                    read_only=True,
                    timeout=timeout,
                    remove=True,
                )
                return {"success": True, "output": result.decode()}
            except docker.errors.ContainerError as e:
                return {"success": False, "error": str(e)}
    
    def check_syntax(self, code: str, language: str):
        """语法检查（不执行代码，只编译/语法分析）"""
        if language == "python":
            import ast
            try:
                ast.parse(code)
                return {"valid": True, "errors": []}
            except SyntaxError as e:
                return {"valid": False, "errors": [str(e)]}
        elif language == "java":
            # 用 javac -Xlint 做编译检查
            ...
```

#### Day 61-62：流式输出 + 测试

```python
# 流式输出Agent的执行过程（给前端展示思考链）
from fastapi.responses import StreamingResponse
import json

@app.post("/code/stream")
async def code_stream(req: CodeRequest):
    async def event_stream():
        agent = create_code_agent()
        
        async for event in agent.astream_events(
            {"requirement": req.requirement, "language": req.language},
            version="v2"
        ):
            kind = event["event"]
            
            if kind == "on_chat_model_stream":
                # LLM输出（逐token）
                content = event["data"]["chunk"].content
                if content:
                    yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
            
            elif kind == "on_tool_start":
                # 开始执行工具
                yield f"data: {json.dumps({'type': 'tool_start', 'tool': event['name']})}\n\n"
            
            elif kind == "on_tool_end":
                # 工具执行完毕
                yield f"data: {json.dumps({'type': 'tool_end', 'tool': event['name']})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

#### Day 63-66：前端 + 联调 + 部署

- 前端用Vue3（或者用Streamlit简化），展示：
  - 左侧：需求输入框
  - 右侧：分步骤展示Agent的执行过程和最终代码
  - 代码高亮（highlight.js）
- Docker Compose一键部署
- 写README + 录屏演示

### 简历上怎么写

> **CodeMate - 智能代码助手Agent**
>
> 基于LangGraph构建的多工具代码生成Agent，支持自然语言驱动的代码生成、语法检查、单元测试和Bug修复。
> - 采用DAG状态图编排代码生成流程（需求分析→生成→检查→测试→修复）
> - Docker容器沙箱安全执行用户代码，内存限制+网络隔离
> - SSE流式输出Agent思考链和代码生成过程，支持中断和重试
> - 技术栈：Python/FastAPI/LangGraph/Docker/Redis/PostgreSQL

---

## Week 10-11：项目二——EnterpriseRAG（企业知识库系统）

### 项目定位

RAG是Agent开发面试的必问题，这个项目是你回答所有RAG问题的底气。

### 核心功能

1. **文档管理**
   - 上传：PDF/Word/Markdown/TXT/图片(OCR)/网页
   - 批量导入：文件夹、压缩包
   - 文档版本管理

2. **知识库管理**
   - 创建多个知识库（不同业务线）
   - 权限控制（谁能访问哪个库）
   - 知识库合并/拆分

3. **问答**
   - 自然语言问答（流式输出）
   - 引用溯源（标注来源文档、页码、段落）
   - 多轮对话（上下文记忆）
   - 对比问答（两个文档的异同）

4. **管理后台**
   - 文档使用统计
   - 问答日志
   - 未命中的问题收集

### 技术架构（生产级）

```
┌─────────────────────────────────────────────────────┐
│                    Nginx (反向代理)                    │
└─────────┬──────────────────────────┬────────────────┘
          │                          │
          ▼                          ▼
┌──────────────────┐    ┌─────────────────────────┐
│  Vue3 管理后台    │    │  FastAPI 后端服务         │
│  (可选)           │    │                         │
└──────────────────┘    │  /upload  文档上传        │
                        │  /query   问答接口        │
                        │  /admin   管理后台        │
                        └──────────┬──────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  MinIO/OSS       │   │  Milvus/Qdrant   │   │  PostgreSQL      │
│  原始文件存储     │   │  向量存储         │   │  业务数据         │
└──────────────────┘   └──────────────────┘   └──────────────────┘
          │                        │
          └────────────┬───────────┘
                       ▼
          ┌───────────────────────────┐
          │  Redis (缓存 + 会话)      │
          └───────────────────────────┘
```

### 开发步骤（10天）

#### Day 67-68：文档处理Pipeline

```python
# document_pipeline.py —— 完整的文档处理流水线

class DocumentPipeline:
    """文档处理流水线：加载 → 解析 → 清洗 → 分块 → 向量化 → 入库"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.loaders = self._init_loaders()
        self.splitter = self._init_splitter()
        self.embedding = self._init_embedding()
        self.vectorstore = self._init_vectorstore()
    
    def process(self, file_path: str) -> ProcessResult:
        """
        处理单个文档的完整流程
        返回：处理的chunk数、耗时、文件大小
        """
        start = time.time()
        
        # 1. 选择合适的Loader
        ext = Path(file_path).suffix.lower()
        loader = self.loaders.get(ext)
        if not loader:
            raise UnsupportedFormatError(f"不支持的文件格式：{ext}")
        
        # 2. 加载文档
        raw_docs = loader.load(file_path)
        
        # 3. 清洗
        cleaned_docs = self._clean(raw_docs)
        
        # 4. 智能分块
        chunks = self.splitter.split_documents(cleaned_docs)
        
        # 5. 向量化 + 入库
        self.vectorstore.add_documents(chunks)
        
        elapsed = time.time() - start
        return ProcessResult(
            file=file_path,
            chunks=len(chunks),
            chars=sum(len(c.page_content) for c in chunks),
            time_seconds=elapsed,
        )
    
    def _clean(self, docs: list[Document]) -> list[Document]:
        """文档清洗"""
        for doc in docs:
            # 去除多余空白
            doc.page_content = re.sub(r'\s+', ' ', doc.page_content)
            # 去除页眉页脚（PDF常见噪声）
            doc.page_content = self._remove_headers_footers(doc.page_content)
            # 去除控制字符
            doc.page_content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', doc.page_content)
        return docs
```

#### Day 69-70：高级检索 + RAG问答

```python
# advanced_retrieval.py

class AdvancedRetriever:
    """高级检索器：多路召回 + 重排序 + 后处理"""
    
    def __init__(self, vectorstore, bm25_index, reranker):
        self.vectorstore = vectorstore
        self.bm25 = bm25_index
        self.reranker = reranker
    
    def retrieve(self, query: str, top_k=4, strategy="hybrid"):
        """多策略检索入口"""
        
        if strategy == "hybrid":
            # 多路召回
            dense_results = self._dense_retrieval(query, k=top_k * 3)  # 多召回一些
            sparse_results = self._sparse_retrieval(query, k=top_k * 2)
            
            # RRF融合
            fused = self._reciprocal_rank_fusion(
                [dense_results, sparse_results],
                k=60
            )
            
            # 重排序
            reranked = self.reranker.rerank(query, fused, top_k=top_k)
            return reranked
        
        elif strategy == "self_query":
            # LLM先提取结构化过滤条件，再检索
            return self._self_query_retrieval(query, top_k)
        
        else:
            # 纯语义检索
            return self.vectorstore.similarity_search(query, k=top_k)
    
    def _reciprocal_rank_fusion(self, result_lists, k=60):
        """RRF融合多路召回结果"""
        scores = {}
        for results in result_lists:
            for rank, doc in enumerate(results):
                doc_id = doc.metadata.get("id", doc.page_content[:50])
                scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
        
        # 按RRF分数排序
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_docs
```

#### Day 71-72：流式问答 + 引用溯源

```python
# 引用溯源是RAG系统的关键——让用户知道答案从哪来

class CitationChain:
    """带引用溯源的问答链"""
    
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
    
    async def aquery(self, question: str):
        # 检索
        docs = self.retriever.retrieve(question)
        
        # 构建Prompt（要求标注引用）
        context_parts = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", "N/A")
            context_parts.append(f"[来源{i+1}] 文档：{source}，页码：{page}\n{doc.page_content}")
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""根据以下文档内容回答问题。在回答中标注信息来源（用 [来源X] 格式）。

文档内容：
{context}

要求：
1. 每句话有依据的都标注 [来源X]
2. 如果不同来源有矛盾，请指出
3. 如果无法从文档中找到答案，明确说明

问题：{question}
"""
        # 流式返回
        async for chunk in self.llm.astream(prompt):
            yield chunk
    
    async def aquery_stream(self, question: str):
        """流式问答 + 在结束时返回引用信息"""
        docs = self.retriever.retrieve(question)
        
        # 先返回引用信息
        citations = [
            {
                "id": i + 1,
                "source": doc.metadata.get("source", "unknown"),
                "page": doc.metadata.get("page", "N/A"),
                "snippet": doc.page_content[:150],
            }
            for i, doc in enumerate(docs)
        ]
        yield {"type": "citations", "data": citations}
        
        # 再流式返回答案
        async for chunk in self.aquery(question):
            yield {"type": "token", "data": chunk}
```

#### Day 73-76：管理后台 + 监控 + 部署

- 管理后台功能
- 对话日志收集与分析（未命中的问题 → 补充文档）
- Docker Compose部署（Nginx + FastAPI + Milvus + PostgreSQL + Redis + MinIO）
- 写详细的README + 架构图

### 简历上怎么写

> **EnterpriseRAG - 企业级知识库问答系统**
>
> 面向企业场景的多知识库RAG系统，支持多格式文档解析、智能分块、混合检索与引用溯源。
> - 设计多路召回架构（向量语义 + BM25关键词 + Reranker精排），召回率提升30%+
> - 实现引用溯源机制，答案可追溯至原始文档页码，满足企业合规要求
> - 支持多知识库隔离、权限管理、未命中问题收集等企业特性
> - 技术栈：Python/FastAPI/LangChain/Milvus/PostgreSQL/Redis/MinIO/Docker

---

## Week 11-12：项目三（加分项）+ 面试准备

### 选项A：Multi-Agent协作系统（进阶）

**场景：** 自动化市场调研：搜集信息 → 分析数据 → 生成报告

### 选项B：MCP Server（技术前瞻）

```python
# MCP = Model Context Protocol
# Agent调用外部工具的标准协议，类比USB统一接口
# 现在是2025-2026的热门方向，写在简历上很加分

# 实现一个MCP Server，让Agent能访问你的企业系统
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationCapabilities

server = Server("enterprise-tools")

@server.list_tools()
async def list_tools():
    return [
        {
            "name": "query_employees",
            "description": "查询员工信息",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "department": {"type": "string"},
                    "name": {"type": "string"},
                }
            }
        },
        {
            "name": "get_sales_report",
            "description": "获取销售报表",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                },
                "required": ["start_date", "end_date"]
            }
        }
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "query_employees":
        return await db.query_employees(**arguments)
    elif name == "get_sales_report":
        return await report_service.get_sales(**arguments)
```

### 选项C：开源贡献（长期加分）

- 给LangChain/LangGraph提PR（修文档bug或者小功能）
- 翻译英文AI技术文章到中文
- 写一个自己的小工具库并开源

---

## 面试准备专项（贯穿Week 11-12）

### 技术面试高频题（准备逐字稿）

#### 1. RAG相关

**Q: RAG的完整流程是怎样的？**
```
答：RAG全称Retrieval-Augmented Generation，流程分为离线和在线两部分。

离线阶段：
1. 文档加载：从各种格式（PDF/Word/网页）提取文本
2. 文本清洗：去噪声、统一格式
3. 智能分块：用语义分块或递归分块，chunk_size一般500-1000字
4. Embedding：用embedding模型（如text-embedding-3-small）把文本块转成向量
5. 向量入库：存入Milvus/Qdrant等向量数据库

在线阶段：
1. 用户提问 → Embedding转向量
2. 多路召回：向量检索（语义相似）+ BM25检索（关键词匹配）
3. RRF融合召回结果
4. Reranker精排（如bge-reranker）
5. 构建Prompt：把检索到的文档+用户问题拼成上下文
6. LLM生成答案
7. 引用溯源标注
```

**Q: 怎么减少RAG的幻觉？**
```
1. System Prompt限制：明确要求"如果上下文中没有信息就说不知道"
2. 提高检索质量：多路召回+Reranker，确保上下文准确
3. 引用溯源：要求LLM标注来源，倒逼其基于文档回答
4. 阈值过滤：设置相似度阈值，低于阈值的文档不纳入上下文
5. 后处理校验：用另一个LLM检查答案是否与上下文一致
```

**Q: 分块大小怎么选？**
```
这是一个权衡问题：
- 小块（200-400字）：检索更精确，但上下文少，容易断章取义
- 大块（1000-2000字）：上下文丰富，但检索精度下降，噪音多

实践中的方案：
- 技术文档：500-800字，50-100字重叠
- 法律/合同：300-500字，100-150字重叠（不允许遗漏）
- FAQ：每条独立，不用拆分

高级方案：父子文档检索（Small-to-Big），用小粒度检索+大粒度返回
```

#### 2. Agent相关

**Q: Agent的本质是什么？和普通LLM调用有什么区别？**
```
Agent = LLM + 思考循环 + 工具调用 + 记忆

区别：
- 普通LLM调用：输入→输出，单次无状态
- Agent：LLM在循环中自主决策，每步决定"下一步做什么"
  - 调用工具获取外部信息
  - 根据工具结果调整策略
  - 多步推理直到完成任务

类比Java：普通LLM调用像调用一个静态方法，Agent像一个有状态机的业务流程引擎。
```

**Q: ReAct模式和Plan-Execute模式各有什么优劣？**
```
ReAct（推理+行动交织）：
- 优点：灵活，每步都根据最新信息决策
- 缺点：Token消耗大（每步都输出思考过程），可能走偏
- 适合：探索性任务、信息不完整的情况

Plan-Execute（先规划再执行）：
- 优点：Token消耗少（规划一次，执行无需重复思考），效率高
- 缺点：中间遇到意外无法调整
- 适合：明确的任务、步骤可预见的场景

实践中LangGraph支持混合模式：先规划，执行中遇到问题再ReAct调整
```

**Q: Agent怎么控制成本（Token消耗）？**
```
1. 限制最大步数（max_iterations）
2. 限制工具调用次数
3. 上下文裁剪：历史消息太长时，只保留最近的N轮或做摘要
4. 选择便宜的模型做中间步骤（规划用便宜模型，最终输出用贵模型）
5. 缓存相同/相似问题的结果
6. 工具结果做摘要（而不是把完整结果塞回去）
```

#### 3. 项目深挖

**Q: 你的CodeMate项目最大的技术挑战是什么？**
```
（根据你实际开发中遇到的问题回答，这里给思路）
1. 代码安全执行：用Docker沙箱（内存限制、网络禁用、超时机制）
2. 修复循环：代码生成→检查→修复→再检查，怎么避免死循环？加最大轮次+每轮对比变化
3. 长代码生成：Token限制导致代码截断 → 分文件生成 + 续写机制
```

#### 4. 系统设计

**Q: 设计一个支持100万文档的企业知识库RAG系统**
```
架构要点：
1. 接入层：Nginx负载均衡，API网关做限流鉴权
2. 应用层：FastAPI集群（无状态，可水平扩展）
3. 存储层：
   - Milvus集群（向量检索，分片+副本）
   - Elasticsearch（关键词检索+BK25）
   - PostgreSQL（业务数据）
   - MinIO（原始文件存储）
4. 缓存层：Redis集群（热点问题缓存、会话管理）
5. 消息队列：RabbitMQ/Kafka（文档处理异步化，削峰填谷）
6. 监控：Prometheus + Grafana
```

#### 5. 行为面试

**Q: 为什么从Java后端转到Agent开发？**
```
话术参考：
"我的Java后端基础让我理解了软件工程的全流程——从需求分析到系统设计到上线运维。
在学习过程中我发现Agent开发特别需要这种工程化思维，而不只是调API。
Agent本质上是'用LLM做决策的业务编排系统'，和我在Java里做的微服务编排有相同的架构思想。
所以我选择转型，把工程能力和AI能力结合。"
```

### 投递策略

**目标岗位：**
- 大模型应用开发工程师
- AI Agent开发工程师
- LLM应用开发（RAG方向）
- AI平台开发（偏工程）

**投递时间线（应届生）：**
- Week 9-10：整理简历，开始投实习岗位
- Week 11：面试复盘，调整项目和话术
- Week 12：集中面试期

**公司建议（按难度递进）：**
1. 练手：中小型AI创业公司
2. 目标：AI独角兽（智谱、月之暗面、Minimax、百川等）
3. 冲刺：大厂AI部门（字节、阿里、腾讯、百度）

---

## 全阶段检查清单

### 技术能力
- [ ] Python异步编程熟练（手写async/await没有任何障碍）
- [ ] FastAPI独立构建完整后端服务
- [ ] LangChain的Chain/LCEL/Prompt熟练使用
- [ ] LangGraph的StateGraph/Node/Edge能独立设计
- [ ] Agent原理：能解释ReAct循环、Function Calling机制
- [ ] RAG全链路：文档处理→分块→多路召回→重排序→生成→引用
- [ ] 向量数据库：ChromaDB开发 + Milvus生产级
- [ ] 流式输出：SSE/WebSocket在项目中落地
- [ ] Docker部署LLM应用全流程

### 项目产出
- [ ] GitHub 3个以上AI项目（CodeMate + EnterpriseRAG + 其他）
- [ ] 每个项目有完整README（功能+技术栈+截图+快速开始）
- [ ] 至少1个项目录了演示视频
- [ ] 技术博客至少3篇

### 面试准备
- [ ] RAG全链路能讲10分钟以上
- [ ] Agent原理能画图讲解
- [ ] 项目难点能展开说3-5分钟
- [ ] 系统设计题能给出完整架构
- [ ] 准备好"为什么转型"的话术

---

> **最后的话：**
> 3个月很短，也很长。短到你不能什么都学，长到足够你从Java后端变成合格的Agent开发者。
> 关键在于：每天坚持、项目驱动、不要只看不写。
> 你的Java工程经验是独特优势，不是累赘。
> 大模型应用开发缺的不是"懂AI的人"，缺的是"能工程化落地AI的人"——那就是你。
> 加油，大三正是最好的时机！
