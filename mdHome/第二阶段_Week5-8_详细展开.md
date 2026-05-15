# 第二阶段详细展开（Week 5-8）：Agent核心 + RAG进阶 + 框架深度

> 这是整个学习路线最关键的4周，决定你到底是"调API的"还是"Agent开发者"

---

## Week 5：RAG全面深入（面试高发区）

### Day 29-30：高级分块策略

RAG的瓶颈往往不是模型，而是**文档怎么切**。

```python
# 1. 语义分块（Semantic Chunking）—— 按语义边界分
# 问题：固定长度分块会把一句话切成两半
# 方案：用Embedding计算句子间相似度，在相似度骤降处分隔

from langchain_experimental.text_splitter import SemanticChunker

semantic_splitter = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",  # 相似度低于某个百分位时分隔
)
chunks = semantic_splitter.split_documents(docs)

# 2. 父子文档（Parent-Child / Small-to-Big）
# 问题：小块检索准确但缺乏上下文，大块检索有上下文但不精确
# 方案：用小块检索，返回时带上父块（大块）作为上下文

# 3. 多粒度分块
# 同时维护多个粒度的索引：
# - 细粒度（100字）：精确检索
# - 中粒度（500字）：一般问答
# - 粗粒度（2000字）：总结类问题

# 4. 结构化文档处理（Markdown/HTML）
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on
)
chunks = markdown_splitter.split_text(markdown_text)
# 每个chunk的metadata会包含 h1, h2, h3 信息
```

**动手：用不同分块策略处理同一本书，对比RAG问答效果，记录哪种策略在什么问题上更准。**

---

### Day 31-32：多路检索 + 重排序实战

```python
# 完整的高级RAG Pipeline

# Step 1: 多路召回
# 路1：密集向量检索
dense_retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 10}
)

# 路2：稀疏向量检索（BM25）
from langchain_community.retrievers import BM25Retriever
bm25_retriever = BM25Retriever.from_documents(all_chunks)
bm25_retriever.k = 10

# 路3：自查询检索（元数据过滤）
self_query_retriever = SelfQueryRetriever.from_llm(...)

# Step 2: 结果融合（RRF: Reciprocal Rank Fusion）
from langchain.retrievers import EnsembleRetriever

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, dense_retriever],
    weights=[0.3, 0.7],  # BM25权重0.3，向量权重0.7
)

# Step 3: 重排序
from langchain.retrievers import ContextualCompressionRetriever
# 使用bge-reranker（中文效果好）
# 或Cohere Rerank API

# Step 4: 后处理去重
# 合并、去重、截断

# 完整Pipeline
rag_chain_with_advanced_retrieval = (
    {"context": ensemble_retriever | compression | dedup,
     "input": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

**面试要点：**
- 为什么要多路召回？—— 向量检索偏语义可能漏精确匹配，BM25补位
- 为什么要Reranker？—— 初排用轻量模型（embedding cosine距离），精度不够；精排用重模型（cross-encoder），精度高
- RRF怎么算？—— `RRF(d) = Σ 1/(k + rank_i(d))`，k通常取60，平滑排名

---

### Day 33-34：GraphRAG入门

**核心思想：** 普通RAG是"关键词匹配"，GraphRAG是"关系理解"

```python
# 理解GraphRAG的两个层次：

# 层次1：用知识图谱辅助检索
# 问题："乔布斯的妻子是谁？"
# 普通RAG：检索"乔布斯" → 找到一堆文档 → LLM抽取答案
# GraphRAG：检索"乔布斯"实体 → 走关系边"配偶" → 找"劳伦·鲍威尔"实体
# → 返回实体+关联文档 → LLM生成答案

# 层次2：微软GraphRAG
# 从文档自动构建实体-关系图 → 社区检测 → 为每个社区生成摘要
# 查询时：局部检索 + 社区摘要 → 全局理解

# 实操推荐：
# 使用LightRAG（比微软GraphRAG更轻量）
# pip install lightrag-hku
```

```python
# LightRAG示例
from lightrag import LightRAG

rag = LightRAG(
    working_dir="./lightrag_data",
    llm_model_func=llm_call,           # 你的LLM调用函数
    embedding_func=embedding_call,      # 你的Embedding函数
)

# 插入文档
rag.insert("苹果公司由史蒂夫·乔布斯于1976年创立...")

# 查询（自动利用图结构）
result = rag.query("乔布斯创立了哪些公司？", mode="hybrid")
# mode: "local"(局部), "global"(全局), "hybrid"(混合), "naive"(普通RAG)
```

**GraphRAG是加分项不是必选项**，先理解思想，面试能说清楚即可。

---

### Day 35：Week 5复习 + 项目优化

- 把PaperQA项目升级：加上混合检索 + Reranker + 语义分块
- 在项目的README里写上技术选型理由（面试要说的）

---

## Week 6：Agent核心——从理论到手写

> 这是整个路线最重要的7天

### Day 36：Agent理论基础（必读论文精讲）

**必读：**[Lilian Weng - LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)

**Agent = LLM + 规划(Planning) + 记忆(Memory) + 工具(Tool Use)**

```
┌──────────────────────────────────────┐
│              Agent                    │
│                                       │
│  1. Planning（规划）                  │
│     - 任务分解（子目标）              │
│     - 反思与改进（Self-Reflection）   │
│                                       │
│  2. Memory（记忆）                    │
│     - 短期记忆（上下文窗口）          │
│     - 长期记忆（外部存储）            │
│                                       │
│  3. Tool Use（工具使用）              │
│     - 学习调用外部API                 │
│     - 代码执行                        │
│     - 数据库查询                      │
└──────────────────────────────────────┘
```

**用Java类比理解Agent：**

| Agent概念 | Java类比 |
|-----------|---------|
| LLM | 决策引擎（大脑） |
| Tool | Service类的方法 |
| Memory | Redis缓存 + MySQL持久化 |
| Planning | 工作流引擎 / 状态机 |
| Agent Executor | Spring的Bean容器 + 调度器 |

---

### Day 37：ReAct模式——手写一个Agent

```python
# 不用任何框架，手写ReAct循环
# 这样你才能真正理解Agent的工作原理

import re
import json

class SimpleReActAgent:
    """手写ReAct Agent —— 理解了原理，LangChain只是工具"""
    
    def __init__(self, llm_call, tools: dict, max_iterations=5):
        """
        llm_call: 调用LLM的函数，输入消息列表返回文本
        tools: {"工具名": 工具函数}
        max_iterations: 最大循环次数，防止死循环
        """
        self.llm_call = llm_call
        self.tools = tools
        self.max_iterations = max_iterations
    
    def run(self, question: str):
        """Agent主循环"""
        history = []
        
        prompt = f"""你可以使用以下工具：
{self._format_tools()}

请用以下格式回答：
Thought: [你的思考过程]
Action: [工具名称]
Action Input: [工具输入]
Observation: [工具返回]
... (Thought/Action/Action Input/Observation 可重复)
Thought: 我知道答案了
Final Answer: [最终回答]

问题：{question}
"""
        
        messages = [{"role": "user", "content": prompt}]
        
        for i in range(self.max_iterations):
            # 调用LLM
            response = self.llm_call(messages)
            messages.append({"role": "assistant", "content": response})
            
            # 解析LLM输出
            action, action_input = self._parse_action(response)
            
            if action is None:
                # 没有Action → 意味着输出了Final Answer
                final_answer = self._parse_final_answer(response)
                if final_answer:
                    return {
                        "answer": final_answer,
                        "steps": len([m for m in messages if m["role"] == "assistant"]),
                        "history": history
                    }
                continue
            
            # 执行工具
            if action in self.tools:
                observation = self.tools[action](action_input)
                history.append({
                    "action": action,
                    "input": action_input,
                    "observation": observation
                })
                # 把执行结果反馈给LLM
                messages.append({
                    "role": "user",
                    "content": f"Observation: {observation}"
                })
            else:
                messages.append({
                    "role": "user",
                    "content": f"错误：没有名为{action}的工具。可用工具：{list(self.tools.keys())}"
                })
        
        return {"answer": "达到最大循环次数，任务未完成", "steps": self.max_iterations}
    
    def _format_tools(self):
        return json.dumps({
            name: func.__doc__ or "无描述"
            for name, func in self.tools.items()
        }, ensure_ascii=False)
    
    def _parse_action(self, text):
        """解析 Action: xxx\nAction Input: xxx"""
        action_match = re.search(r'Action:\s*(.+?)(?:\n|$)', text)
        input_match = re.search(r'Action Input:\s*(.+?)(?:\n|$)', text)
        
        if action_match:
            action = action_match.group(1).strip()
            action_input = input_match.group(1).strip() if input_match else ""
            return action, action_input
        return None, None
    
    def _parse_final_answer(self, text):
        """解析 Final Answer: xxx"""
        match = re.search(r'Final Answer:\s*(.+?)(?:\n|$)', text)
        if match:
            return match.group(1).strip()
        return None


# 使用示例
def search_web(query):
    """在网上搜索信息"""
    # 实际项目中接入搜索引擎API
    return f"搜索「{query}」的结果：..."

def calculate(expression):
    """执行数学计算"""
    try:
        return str(eval(expression))
    except:
        return f"计算失败：{expression}"

def get_weather(city):
    """获取城市天气"""
    return f"{city}：晴，25°C"

agent = SimpleReActAgent(
    llm_call=call_deepseek,  # 你的LLM调用函数
    tools={
        "search": search_web,
        "calculate": calculate,
        "get_weather": get_weather,
    }
)

result = agent.run("北京今天天气怎么样？如果温度超过20度，算一下30%折扣后1000元是多少钱")
print(json.dumps(result, ensure_ascii=False, indent=2))
```

**关键理解：**
- ReAct = 思考(Action) + 行动(Action) + 观察(Observation) 的循环
- Agent的本质是"LLM在循环中自己决定下一步做什么"
- Token消耗主要在中间过程（Thought/Action/Observation），所以Agent比单次问答贵很多

---

### Day 38-39：LangChain Agent深度使用

```python
# LangChain的Agent实现（理解内部原理后，用框架写）

# 1. 定义工具
from langchain_core.tools import tool

@tool
def search(query: str) -> str:
    """在知识库中搜索信息。输入搜索关键词。"""
    results = vectorstore.similarity_search(query, k=3)
    return "\n\n".join(f"[{i+1}] {r.page_content[:200]}" for i, r in enumerate(results))

@tool
def get_current_time() -> str:
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def run_python(code: str) -> str:
    """执行Python代码，返回执行结果。用于计算或数据处理。"""
    import io, sys
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        exec(code)
        return buffer.getvalue()
    except Exception as e:
        return f"执行错误: {e}"
    finally:
        sys.stdout = old_stdout

tools = [search, get_current_time, run_python]

# 2. 绑定工具到LLM
llm_with_tools = llm.bind_tools(tools)

# 3. 创建Agent
from langgraph.prebuilt import create_react_agent

agent_executor = create_react_agent(
    llm, tools,
    # 可自定义System Prompt
    state_modifier="你是技术助手，遇到计算问题用run_python工具"
)

# 4. 运行Agent
result = agent_executor.invoke({
    "messages": [HumanMessage(content="搜索一下Java 21的新特性，然后统计有几个")]
})

# 查看中间步骤（面试要能说清楚每一步做了什么）
for msg in result["messages"]:
    if isinstance(msg, AIMessage):
        if msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"  → 调用工具：{tc['name']}({tc['args']})")
        if msg.content:
            print(f"  → 模型回复：{msg.content}")
    elif isinstance(msg, ToolMessage):
        print(f"  → 工具返回：{msg.content[:100]}...")
```

---

### Day 40-41（周末）：Agent项目——智能运维助手

**项目：DevOps-Agent —— 用Agent管理服务器**

```python
# 项目亮点：这是面试官最感兴趣的"有实际场景的Agent"

# 场景：运维人员用自然语言管理服务器
# "检查一下服务器状态，如果磁盘超过80%就清理日志"

tools = [
    # 模拟服务器管理工具
    {
        "name": "check_disk",
        "description": "检查磁盘使用率",
        "func": lambda: "磁盘使用率: /dev/sda1 85%, /dev/sdb1 45%"
    },
    {
        "name": "check_service",
        "description": "检查服务运行状态",
        "func": lambda svc: f"服务{svc}: 运行中"
    },
    {
        "name": "clean_logs",
        "description": "清理日志文件",
        "func": lambda path: f"已清理{path}，释放2.3GB"
    },
    {
        "name": "restart_service",
        "description": "重启指定服务",
        "func": lambda svc: f"服务{svc}已重启"
    },
]

agent = SimpleReActAgent(call_deepseek, tools)
result = agent.run("检查服务器状态，磁盘超过80%就清理/var/log下的日志")
```

**简历写法：**
> 基于ReAct模式实现智能运维Agent，支持自然语言驱动的服务器监控与自动化运维。Agent能自主规划运维任务、调用工具链、处理异常，将运维操作从命令行降维到对话交互。

---

## Week 7：LangGraph——现代Agent开发标准

> LangGraph是2024-2025年Agent开发的主流方案，正在取代LangChain的Agent模块

### Day 42-43：LangGraph核心概念

```python
# LangGraph思想：Agent = 状态图（State Graph）
# 类比：你的Java工作流引擎（Activiti/Flowable），但有LLM做决策

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

# 1. 定义State（状态——类比Java工作流的流程变量）
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]  # 消息列表，operator.add表示追加
    next_step: str                            # 下一步动作

# 2. 定义Node（节点——每个节点是一个处理函数）
def chatbot(state: AgentState):
    """LLM回复节点"""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def search_tool(state: AgentState):
    """搜索工具节点"""
    last_message = state["messages"][-1]
    query = last_message.content
    results = vectorstore.similarity_search(query)
    return {"messages": [f"搜索结果：{results[0].page_content[:200]}"]}

# 3. 定义路由（条件边——LLM决定走哪条路）
def router(state: AgentState):
    """决定下一步去哪个节点"""
    last_message = state["messages"][-1]
    if "搜索" in last_message.content:
        return "search"
    return "end"

# 4. 构建图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("chatbot", chatbot)
workflow.add_node("search", search_tool)

# 设置入口
workflow.set_entry_point("chatbot")

# 添加边
workflow.add_conditional_edges(
    "chatbot",
    router,
    {
        "search": "search",
        "end": END,
    }
)
workflow.add_edge("search", "chatbot")  # 搜索完回到chatbot

# 5. 编译运行
app = workflow.compile()
result = app.invoke({"messages": [HumanMessage(content="帮我搜索一下FastAPI的文档")]})
```

### Day 44-45：LangGraph进阶

```python
# 1. 带记忆的Agent（Checkpoint）
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# 多轮对话（thread_id区分不同会话）
config = {"configurable": {"thread_id": "user-123"}}

app.invoke({"messages": [HumanMessage(content="我叫张三")]}, config)
app.invoke({"messages": [HumanMessage(content="我叫什么？")]}, config)
# → "你叫张三"（因为有checkpoint记忆）

# 2. 并行节点
# 问题拆成多个子任务并行执行
workflow.add_node("subtask_a", handler_a)
workflow.add_node("subtask_b", handler_b)
workflow.add_node("merge", merge_handler)

# 从chatbot分叉到两个子任务
workflow.add_conditional_edges("chatbot", splitter, {
    "a": "subtask_a",
    "b": "subtask_b",
})
# 两个都完成后到merge
workflow.add_edge("subtask_a", "merge")
workflow.add_edge("subtask_b", "merge")

# 3. 人工审批（Human-in-the-Loop）
workflow.add_node("review", human_review_node)
# 某步骤需要人工确认才能继续

# 4. 流式输出
for event in app.stream(
    {"messages": [HumanMessage(content="复杂任务...")]},
    config,
    stream_mode="values"  # 或 "updates"
):
    # 每个节点执行完触发一次
    last_msg = event["messages"][-1]
    print(f"[{event.get('next_step', '')}] {last_msg}")
```

### Day 46-47（周末）：LangGraph实战项目

**项目：CodeReview-Agent —— 自动代码审查Agent**

```
状态图设计：
┌─────────┐    ┌─────────────┐    ┌──────────┐    ┌──────────┐
│ 接收PR  │ → │ 语法检查    │ → │ 代码规范  │ → │ 安全扫描  │
└─────────┘    └─────────────┘    └──────────┘    └──────────┘
                                        │                │
                                        ▼                ▼
                              ┌──────────────────────────────┐
                              │     合并审查结果              │
                              └──────────────┬───────────────┘
                                             ▼
                              ┌──────────────────────────────┐
                              │     生成Review报告            │
                              └──────────────────────────────┘
```

**技术要点（LangGraph体现）：**
- StateGraph管理审查流程
- 语法检查 + 规范检查用并行节点（提升效率）
- 安全扫描是conditional：Java/Go代码检查，前端代码跳过
- Checkpoint保存审查历史，支持增量审查

---

## Week 8：Function Calling深度 + Multi-Agent概念

### Day 48-49：OpenAI Function Calling深入

```python
# Function Calling = LLM告诉你要调哪个函数 + 传什么参数
# 类比：用户在聊天框里说"帮我查北京天气"
#       LLM输出 → {function: "get_weather", arguments: {city: "北京"}}
#       后端拿到这个JSON，调用get_weather("北京")，结果再送回LLM

# 定义Tool的JSON Schema（OpenAI格式）
tools_definition = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "查询MySQL数据库",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL查询语句，仅支持SELECT"
                    },
                    "database": {
                        "type": "string",
                        "enum": ["users", "orders", "products"],
                        "description": "目标数据库"
                    }
                },
                "required": ["sql", "database"]
            }
        }
    }
]

# Function Calling的本质理解：
# 1. 你定义工具的"接口签名"（像Java的interface）
# 2. LLM根据用户意图决定调用哪个工具、传什么参数
# 3. 你执行工具，把结果返回给LLM
# 4. LLM用自然语言把结果呈现给用户

# 面试常见问题：
# Q: Function Calling和普通API调用有什么区别？
# A: 普通API是程序员写死调用逻辑，Function Calling是LLM动态决定何时调用、怎么调用
```

### Day 50-51：Multi-Agent入门

```python
# 场景：一个Agent不够，需要多个Agent分工协作
# 类比：后端微服务架构——每个服务专注一件事

# 方案1：LangGraph多Agent（推荐）
from langgraph.graph import StateGraph

# 定义不同角色的Agent
planner_agent = create_react_agent(llm, [task_breakdown_tool])
coder_agent = create_react_agent(llm, [code_generate_tool, code_test_tool])
reviewer_agent = create_react_agent(llm, [code_review_tool])

# 用LangGraph编排
# Planner拆解任务 → Coder实现 → Reviewer检查 → Coder修复 → 输出

# 方案2：CrewAI（快速上手）
from crewai import Agent, Task, Crew

planner = Agent(
    role="技术规划师",
    goal="将用户需求拆解为可执行的技术任务",
    backstory="你是拥有10年经验的架构师...",
    llm=llm,
)

coder = Agent(
    role="程序员",
    goal="编写高质量的功能代码",
    backstory="你精通Python和Java...",
    llm=llm,
)

task1 = Task(description="用户需要一个用户注册功能...", agent=planner)
task2 = Task(description="根据规划编写代码...", agent=coder)

crew = Crew(agents=[planner, coder], tasks=[task1, task2])
result = crew.kickoff()
```

### Day 52-53：综合实战——Multi-Agent协作系统

**项目：Research-Agent —— 市场调研多Agent系统**

```
用户输入："调研2024年国内AI Agent赛道"
        │
        ▼
┌───────────────────┐
│  Planner Agent    │ → 拆解为：①收集行业报告 ②分析竞品 ③市场规模 ④输出报告
└───────┬───────────┘
        │ 分发任务
    ┌───┼───┐
    ▼   ▼   ▼
┌────┐┌────┐┌────┐
│搜集││分析││比较│  三个Agent并行工作
└──┬─┘└──┬─┘└──┬─┘
   │     │     │
   └────┼─────┘
        ▼
┌───────────────────┐
│  Writer Agent     │ → 整合信息，生成调研报告
└───────────────────┘
```

**简历写法：**
> 基于LangGraph实现多Agent协作系统，采用DAG任务编排，支持Agent间异步消息通信。规划Agent负责任务拆解，执行Agent并行处理子任务，审查Agent把关输出质量。系统可扩展到任意数量的Agent节点。

### Day 54-56（最后冲刺）：项目打磨 + 阶段总结

1. **升级所有项目到GitHub**，重点是CodeReview-Agent和Research-Agent
2. **录屏演示**（如果没有前端，用终端录屏也行）
3. **写第二阶段总结博客**
4. **检查清单：**
   - [ ] 能解释ReAct循环的每一步
   - [ ] LangGraph的StateGraph/Node/Edge/ConditionalEdge能用熟
   - [ ] Function Calling机制理解透彻
   - [ ] 手写过Agent循环（不依赖框架）
   - [ ] RAG全链路（多路召回+重排序+混合检索）掌握
   - [ ] Multi-Agent概念能说清楚

---

## 第二阶段总结

**完成标志：** 能独立用LangGraph构建多工具Agent，理解Agent底层原理

**核心能力（面试能答）：**
1. Agent的本质是什么？（LLM在循环中自主决策+调用工具）
2. ReAct vs Plan-Execute区别？
3. Tool怎么定义和注册？
4. Agent如何控制Token消耗？（限制步数、工具调用次数、上下文裁剪）
5. 多Agent怎么通信？（共享State、消息总线、Chain调用）
