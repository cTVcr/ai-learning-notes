# 第一阶段详细展开（Week 1-4）：Python速成 + LLM基础

---

## Week 1：Python急速上手

> 详细每日计划见 Week1_每日任务表.md

**产出：** MiniChat项目（多模型AI对话服务，已开源GitHub）

---

## Week 2：LangChain入门 + 文档处理 + 向量数据库初探

### Day 8（周一）：LangChain核心三大件

**LangChain是什么？** —— 类比Java的Spring框架，做了一层抽象让LLM开发更规范。

#### 学习内容

1. **Model I/O** —— 和LLM交互的标准接口

```python
# 三种模型抽象
from langchain_openai import ChatOpenAI

# LLM：输入文本 → 输出文本
llm = ChatOpenAI(model="gpt-4", temperature=0.7)
response = llm.invoke("你好")

# ChatModel：输入消息列表 → 输出消息
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
messages = [
    SystemMessage(content="你是Java专家"),
    HumanMessage(content="解释Spring的IOC"),
]
response = llm.invoke(messages)

# 流式输出
for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)
```

2. **PromptTemplate** —— 规范Prompt工程

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 简单模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是{role}，风格是{style}"),
    ("user", "{input}"),
])
prompt_value = prompt.invoke({
    "role": "Java后端专家",
    "style": "简洁幽默",
    "input": "HashMap底层原理是什么"
})

# 带历史的模板（多轮对话）
prompt_with_history = ChatPromptTemplate.from_messages([
    ("system", "你是AI助手"),
    MessagesPlaceholder(variable_name="history"),  # 历史消息占位
    ("user", "{input}"),
])
```

3. **Chain** —— 拼装多个组件

```python
from langchain_core.output_parsers import StrOutputParser

# LCEL语法（LangChain Expression Language）
# 用 | 管道符串联，类比Unix的 pipe 或Java Stream
chain = prompt | llm | StrOutputParser()

# 调用链
result = chain.invoke({
    "role": "Java专家",
    "style": "详细",
    "input": "JVM内存模型"
})

# 流式链
for chunk in chain.stream({"role": "代码助手", "style": "专业", "input": "写快排"}):
    print(chunk, end="", flush=True)
```

**理解要点：**
- LangChain就是"定义了LLM应用的标准零件和组装方式"
- LCEL的`|`管道符是核心语法，记住：**Prompt → LLM → OutputParser**
- 类比Java：PromtpTemplate = JdbcTemplate，Chain = 责任链模式

#### 下午练习

1. 用LangChain重写Week 1的MiniChat项目中的LLM调用部分
2. 实现一个"代码解释器"链：输入代码 → System Prompt(你是程序员) → LLM → 返回解释
3. 体验不同Prompt模板对结果的影响

---

### Day 9（周二）：文档加载与处理

#### 学习内容

```python
# LangChain的Document对象
from langchain_core.documents import Document

doc = Document(
    page_content="这是文档内容...",
    metadata={"source": "file.pdf", "page": 3, "author": "张三"}
)

# --- 各种文档加载器 ---
from langchain_community.document_loaders import (
    PyPDFLoader,          # PDF
    TextLoader,           # TXT
    UnstructuredMarkdownLoader,  # Markdown
    CSVLoader,            # CSV
    JSONLoader,           # JSON
    Docx2txtLoader,       # Word
)

# PDF加载
loader = PyPDFLoader("paper.pdf")
pages = loader.load()  # 按页返回，每页一个Document
print(f"共{len(pages)}页，第一页内容：{pages[0].page_content[:200]}")

# 批量加载
from langchain_community.document_loaders import DirectoryLoader
loader = DirectoryLoader(
    "./docs/",
    glob="**/*.pdf",
    loader_cls=PyPDFLoader
)
docs = loader.load()
print(f"加载了{len(docs)}个文档")
```

#### 文档分块（Chunking）—— RAG最关键的一步

```python
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,  # 最常用
    CharacterTextSplitter,
    TokenTextSplitter,               # 按token数分割
)

# 递归字符分割器（推荐默认方案）
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # 每块500个字符
    chunk_overlap=50,      # 重叠50个字符（保持上下文连贯）
    separators=["\n\n", "\n", "。", ".", " ", ""],  # 分割优先级
    length_function=len,
)

chunks = text_splitter.split_documents(pages)
print(f"{len(pages)}页 → {len(chunks)}个文本块")

for i, chunk in enumerate(chunks[:3]):
    print(f"--- Chunk {i} (长度{len(chunk.page_content)}) ---")
    print(chunk.page_content[:200])
```

**分块策略（面试高频！）：**
| 文档类型 | chunk_size建议 | overlap建议 | 说明 |
|---------|---------------|------------|------|
| 技术文档 | 500-800 | 50-100 | 段落级别 |
| 法律合同 | 300-500 | 100-150 | 需要更多重叠 |
| FAQ/短文本 | 200-300 | 0 | 每条独立 |
| 学术论文 | 1000-1500 | 100-200 | 段落/章节级别 |

#### 下午练习

1. 下载一篇文章PDF，用PyPDFLoader加载并分块
2. 尝试不同的chunk_size，观察分块效果
3. 写一个工具函数：输入目录路径，输出所有文档的文本块列表

---

### Day 10（周三）：Embedding + 向量数据库ChromaDB

#### 学习内容

```python
# Embedding：把文本变成向量
# 类比：Java里 hashCode() 把对象变成数字，Embedding 把文本变成高维向量
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",  # 性价比最高
    # base_url="..."  如果用的国内模型
)

# 单条文本向量化
text = "Spring Boot是一个Java框架"
vector = embeddings.embed_query(text)
print(f"向量维度：{len(vector)}")  # text-embedding-3-small → 1536维
print(f"前5个值：{vector[:5]}")

# 批量向量化
texts = ["Java后端", "Python数据分析", "Go微服务"]
vectors = embeddings.embed_documents(texts)
print(f"{len(texts)}条文本 → {len(vectors)}个向量")

# --- ChromaDB：向量数据库 ---
# 类比：MySQL存数据，ChromaDB存向量 + 元数据
import chromadb
from langchain_chroma import Chroma

# 创建向量库（内存模式）
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="my_docs",
    # persist_directory="./chroma_db",  # 持久化到磁盘
)

# 语义搜索
results = vectorstore.similarity_search(
    "Spring Boot怎么配置数据源？",
    k=4  # 返回最相似的4条
)

for i, doc in enumerate(results):
    print(f"--- 结果{i+1} ---")
    print(doc.page_content[:200])
    print(f"来源：{doc.metadata.get('source')}")
    print()

# 带相似度分数的搜索
results_with_score = vectorstore.similarity_search_with_score(
    "Spring Boot怎么配置数据源？", k=4
)
for doc, score in results_with_score:
    print(f"Score: {score:.4f} | {doc.page_content[:100]}")

# MMR检索（最大边际相关——兼顾相关性和多样性）
results = vectorstore.max_marginal_relevance_search(
    "Spring Boot配置", k=4, fetch_k=10  # 先取10条，再选4条最多样的
)
```

#### 下午练习

1. 把你Week 1写的MiniChat代码文件，分块存入ChromaDB
2. 用自然语言搜索代码：比如"流式输出是怎么实现的"
3. 对比`similarity_search`和`max_marginal_relevance_search`的结果差异

---

### Day 11（周四）：RAG初体验——文档问答系统

> 整合Week 2学的一切，做第一个RAG应用

#### RAG基础流程

```
用户提问 → Embedding → 向量检索 → 获取相关文档块
                                      ↓
              生成答案 ← LLM ← 把文档块+问题拼成Prompt
```

```python
# 完整的RAG问答链
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Step 1：准备向量库（假设已完成文档加载+分块+存入ChromaDB）
retriever = vectorstore.as_retriever(
    search_type="similarity",  # 或 "mmr"
    search_kwargs={"k": 4}
)

# Step 2：定义"把文档和问题组合成Prompt"的链
system_prompt = """你是一个基于文档的问答助手。
请仅根据以下上下文回答问题。如果上下文中没有答案，就说不知道，不要编造。

上下文：
{context}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "{input}"),
])

# Step 3：创建问答链
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# Step 4：提问
response = rag_chain.invoke({"input": "什么是IOC容器？"})

print("问题：", response["input"])
print("答案：", response["answer"])
print("\n引用来源：")
for i, doc in enumerate(response["context"]):
    print(f"  [{i+1}] {doc.metadata.get('source', 'unknown')}")
    print(f"      {doc.page_content[:100]}...")
```

#### 下午练习

1. 找一本电子书（技术类PDF），做成RAG问答系统
2. 测试不同类型的问题：事实查询、概念解释、跨章节总结
3. 记录"幻觉"情况：什么时候答案不准？怎么改进？

---

### Day 12-13（周五-六）：项目——个人知识库助手

**项目名称：MyKB（My Knowledge Base）**

**功能：**
- [ ] 上传PDF/TXT/Markdown，自动解析并存入向量库
- [ ] 支持多知识库（不同文件夹 = 不同collection）
- [ ] Web界面上传文件 + 问答
- [ ] 引用溯源：每条答案标注来源文档和位置
- [ ] 对话历史管理

**项目结构：**
```
mykb/
├── main.py              # FastAPI主程序
├── loader.py            # 文档加载+分块逻辑
├── vectorstore.py       # ChromaDB管理
├── rag_chain.py         # RAG问答链
├── models.py            # Pydantic模型
├── static/
│   └── index.html       # 前端界面
└── data/
    └── uploads/         # 上传的文档
```

**技术要点（面试会说）：**
1. 为什么选ChromaDB？（轻量、Python原生、开发阶段够用）
2. 分块策略怎么选的？（根据文档类型：技术文档500字+50重叠）
3. 怎么减少幻觉？（System Prompt限制必须基于上下文回答）

**产出：MyKB项目开源到GitHub，写README**

---

### Day 14（周日）：阶段总结 + 前端补充（可选）

1. **补充前端知识**（如果感兴趣做全栈）：
   - Vue3基础（国内Agent项目前端常用Vue）
   - 或者直接用Streamlit/Gradio（Python写前端，超快）

2. **Streamlit速成**（10分钟学会的"前端"）：
   ```python
   import streamlit as st
   
   st.title("我的RAG问答")
   
   uploaded_file = st.file_uploader("上传文档", type=["pdf", "txt"])
   
   if prompt := st.chat_input("输入你的问题"):
       st.chat_message("user").write(prompt)
       with st.chat_message("assistant"):
           response = st.write_stream(rag_chain.stream({"input": prompt}))
   ```

3. **写第一阶段学习总结**，发技术博客

---

## Week 3：FastAPI深入 + Prompt Engineering进阶 + 模型原理

### Day 15-16：FastAPI生产级开发

```python
# --- 中间件（Java的Filter/Interceptor）---
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """每个请求都打日志 + 计时"""
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    print(f"{request.method} {request.url.path} → {response.status_code} ({duration:.2f}s)")
    return response

# --- 后台任务 ---
from fastapi import BackgroundTasks

def save_to_db(question, answer):
    """耗时操作放后台"""
    time.sleep(2)
    print(f"已存储: {question} → {answer}")

@app.post("/ask")
async def ask(question: str, background_tasks: BackgroundTasks):
    answer = rag_chain.invoke({"input": question})
    background_tasks.add_task(save_to_db, question, answer["answer"])
    return answer

# --- 异常处理 ---
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "path": str(request.url)}
    )

# --- 配置管理（类比Spring的application.yml）---
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    model_name: str = "gpt-4"
    chroma_persist_dir: str = "./chroma_db"
    max_upload_size_mb: int = 10
    
    class Config:
        env_file = ".env"  # 从.env文件读取

settings = Settings()

# --- 限流（类比Sentinel/Guava RateLimiter）---
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat")
@limiter.limit("10/minute")  # 每分钟最多10次
async def chat(request: Request, ...):
    ...
```

### Day 17-18：Prompt Engineering系统学习

**资源：**[Prompt Engineering Guide](https://www.promptingguide.ai/zh)

#### 核心技巧实践

```python
# 1. 角色扮演（Role Prompting）
ROLE_TEMPLATE = """你是一名拥有10年经验的{role}。你的回答风格是{style}。
现在请回答以下问题：{question}"""

# 2. Few-shot（少量样本）
FEW_SHOT_TEMPLATE = """请将以下英文翻译成中文：

英文：Hello World
中文：你好世界

英文：Machine Learning
中文：机器学习

英文：{text}
中文："""

# 3. Chain-of-Thought（思维链——最重要！）
COT_TEMPLATE = """请解决以下问题。在给出最终答案前，请一步步思考。

问题：{question}

请按以下格式回答：
思考过程：
1. ...
2. ...
3. ...

最终答案：..."""

# 4. ReAct（推理+行动）
REACT_TEMPLATE = """你可以使用以下工具：
{tools}

请使用以下格式回答：
Thought: 我需要思考什么
Action: 我需要使用哪个工具
Action Input: 工具的输入
Observation: 工具的返回结果
... (Thought/Action/Action Input/Observation 可以重复)
Thought: 我现在知道最终答案了
Final Answer: 最终答案

问题：{question}
{history}
"""

# 5. 结构化输出
STRUCTURED_TEMPLATE = """分析以下代码，并以JSON格式返回结果：

```java
{code}
```

返回格式（严格遵守）：
{{
    "language": "java",
    "bugs": ["bug1", "bug2"],
    "suggestions": ["suggestion1", "suggestion2"],
    "complexity": "low/medium/high",
    "score": 0-100
}}
"""
```

### Day 19-20：LLM原理速览

**只需要理解层面，不要求推导公式**

#### 用Java类比理解Transformer

```
Java Web请求处理流程：
  请求 → Filter链 → Controller → Service → Repository → DB
                                    ↑
                               核心处理逻辑在这里

Transformer：
  Token → Embedding → Multi-Head Attention → Feed Forward → ... → 输出Token
                           ↑
                     "理解"上下文的核心

Attention机制白话：
  句子："我/爱/吃/苹果/因为/它/很/甜"
  问题："它"指的是什么？

  Attention = "它"去关注句子里所有其他词，计算每个词和自己的相关度
  结果："苹果"得分最高 → "它"指代"苹果"

  类比Java：就像依赖注入时，Spring扫描所有Bean找到最匹配的那个
```

**必须理解的概念（面试会问）：**

| 概念 | 一句话解释 | Java类比 |
|------|-----------|---------|
| Token | LLM处理的最小文本单元 | `String.split()` 的产物 |
| Embedding | 把文本变成数学向量 | `Object.hashCode()`，但语义相近的向量也近 |
| Attention | 让模型知道上下文哪个词重要 | SQL JOIN时的权重计算 |
| Temperature | 控制回答随机性(0=保守,1=创意) | 随机算法的seed |
| Top-p | 核采样，只考虑累积概率到p的词 | 截断不靠谱的候选 |
| SFT | 有监督微调（给正确答案学习） | 看参考答案学习 |
| RLHF | 人类反馈强化学习（偏好对齐） | Code Review打分学习 |

---

## Week 4：向量数据库深入 + RAG进阶

### Day 21-22：ChromaDB → Milvus过渡

```python
# ChromaDB（开发环境）
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# Milvus（生产环境，类比从H2升级到MySQL）
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

# 连接Milvus
connections.connect(host="localhost", port="19530")

# 定义Schema（类比建表DDL）
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1536),
]
schema = CollectionSchema(fields, "问答知识库")
collection = Collection("qa_knowledge", schema)

# 创建索引（类比MySQL的CREATE INDEX）
index_params = {
    "metric_type": "IP",  # 内积相似度
    "index_type": "IVF_FLAT",
    "params": {"nlist": 128}
}
collection.create_index("vector", index_params)

# LangChain封装（统一接口）
from langchain_milvus import Milvus
vectorstore = Milvus(
    embedding_function=embeddings,
    connection_args={"host": "localhost", "port": "19530"},
    collection_name="qa_knowledge"
)
```

**面试题准备：**
- ChromaDB vs Milvus怎么选？
  - 开发/小数据(<10万条)：ChromaDB，零配置
  - 生产/大数据(>10万条)：Milvus，支持分布式、多种索引、GPU加速

### Day 23-24：高级RAG策略实战

```python
# 1. 混合检索（Hybrid Search）—— 关键词 + 向量
# 问题：纯向量检索可能漏掉精确关键词匹配
# 方案：BM25关键词搜索 + 向量语义搜索 → 加权合并

# 2. 重排序（Reranking）
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

# 先召回多一点的文档
retriever = vectorstore.as_retriever(search_kwargs={"k": 20})

# 用Reranker精排
compressor = CohereRerank(top_n=4)  # 20条里精选4条
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever
)

# 效果对比
basic_docs = retriever.invoke("Spring Boot配置")       # 粗排20条取前4
reranked_docs = compression_retriever.invoke("Spring Boot配置")  # 精排后4条

# 3. 自查询检索（Self-Querying）
# 问题："2024年发布的Java框架有哪些？"
# → 先提取过滤条件：year=2024, language=Java
# → 再语义搜索：框架
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

metadata_field_info = [
    AttributeInfo(name="year", description="发布年份", type="integer"),
    AttributeInfo(name="language", description="编程语言", type="string"),
    AttributeInfo(name="type", description="技术类型", type="string"),
]

self_query_retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectorstore,
    document_contents="技术文档集合",
    metadata_field_info=metadata_field_info,
)

# 4. 多路召回融合（Fusion Retrieval）
# 方案：向量检索 + BM25检索 + 知识图谱检索 → 结果融合
# 融合策略：RRF(倒数排名融合) 或 加权投票
```

### Day 25-26：项目——“读论文”RAG系统

**项目：PaperQA —— 论文阅读理解助手**

**核心功能：**
1. 上传论文PDF → 自动解析（标题、作者、摘要、章节）
2. 智能分块：按章节+段落分割，保留结构信息
3. 问答功能：事实查询 + 概念解释 + 跨章节关联
4. 论文对比：上传2篇论文，找异同点

**技术亮点（写在简历上）：**
- 基于LangChain实现论文结构化解析与智能分块
- 采用混合检索策略（向量相似度 + BM25关键词 + Reranker精排）
- 支持引用溯源，答案可追溯到原文具体段落

---

### Day 27-28：阶段复习 + GitHub建设

1. **整理第一阶段的3个项目到GitHub：**
   - MiniChat（Week 1）
   - MyKB 知识库助手（Week 2）
   - PaperQA 论文问答（Week 4）

2. **每个项目的README模版：**
   ```markdown
   # 项目名
   ## 功能
   - xxx
   ## 技术栈
   Python 3.11 / FastAPI / LangChain / ChromaDB / OpenAI API
   ## 快速开始
   ```bash
   pip install -r requirements.txt
   python main.py
   ```
   ## 项目结构
   ...
   ## 示例
   (截图/录屏)
   ```

3. **写阶段总结博客**（掘金/CSDN/知乎）
4. **检查技能清单：**
   - [ ] Python异步编程熟练
   - [ ] FastAPI独立开发完整后端
   - [ ] LangChain的Chain/LCEL熟练
   - [ ] RAG全链路理解（文档→分块→Embedding→检索→生成）
   - [ ] 向量数据库基本操作（ChromaDB）
   - [ ] Prompt Engineering（角色/CoT/ReAct/结构化输出）
   - [ ] LLM API调用（同步+流式+多模型）
   - [ ] GitHub上有3个开源AI项目

---

## 第一阶段总结

**完成标志：** 能独立用FastAPI + LangChain搭建RAG问答系统

**进入第二阶段的前提：**
- Python写代码不需要频繁查语法
- 能独立搭一个带前端的RAG Demo
- 理解Embedding/向量检索/LLM调用的基本流程
- GitHub上有至少2个AI相关项目
