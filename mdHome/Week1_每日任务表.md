# 第一周：Python急速上手 + LLM初体验（每日任务表）

> 每天学习时长：4-5小时。上午输入，下午输出，晚上复习。
> 善用Java基础做对比，不要从头学语法，对比着学最快。

---

## Day 1（周一）：Python环境 + 基础语法（变量→函数）

### 上午 2h（看 + 跟着敲）

1. **环境搭建**（30min）
   ```bash
   # 安装Python 3.11+（不要装3.13最新，部分库不兼容）
   # Windows直接官网下载安装，勾选"Add Python to PATH"
   
   # 验证
   python --version
   pip --version
   
   # 创建虚拟环境（类比Maven的local repo）
   python -m venv venv
   # Windows激活：venv\Scripts\activate
   # Mac/Linux：source venv/bin/activate
   
   # 安装常用包
   pip install jupyter ipython requests httpx
   ```

2. **变量与基础类型**（30min）
   - 看 [廖雪峰Python教程 1-4章](https://www.liaoxuefeng.com/wiki/1016959663602400)
   - 对照Java理解：

   | Java | Python |
   |------|--------|
   | `int x = 10; String s = "hi";` | `x = 10; s = "hi"` |
   | `final int X = 10;` | 约定大写作常量 `MAX_SIZE = 100` |
   | `Integer.parseInt("10")` | `int("10")` |
   | `x == 10` (基本类型)  `s.equals("hi")` | `x == 10` `s == "hi"` (都OK) |

3. **list/dict/tuple/set**（30min）
   - 这是你未来每天都要用的，重点练

   ```python
   # list → Java的 ArrayList
   nums = [1, 2, 3]
   nums.append(4)         # add()
   nums[0]                # get(0)
   nums[-1]               # 最后一个，Python独有
   nums[1:3]              # 切片：[2, 3]，Python独有
   [x*2 for x in nums]    # 列表推导式，必会
   
   # dict → Java的 HashMap<String, Object>
   user = {"name": "张三", "age": 21}
   user["name"]           # get("name")
   user.get("email", "")  # 带默认值
   {k: v for k, v in user.items() if k != "age"}  # 字典推导式
   
   # tuple → 不可变列表，常用于函数返回多值
   point = (3, 4)
   x, y = point           # 解包，Python独有
   
   # set → Java的 HashSet
   tags = {"python", "java", "ai"}
   tags.add("agent")
   ```

4. **控制流**（30min）
   ```python
   # if-elif-else（注意冒号和缩进）
   if score >= 90:
       grade = "A"
   elif score >= 80:
       grade = "B"
   else:
       grade = "C"
   
   # for —— Python的for直接遍历，不像Java的fori
   for i, item in enumerate(items):   # 同时拿索引和值
       print(f"{i}: {item}")
   
   for k, v in user.items():          # 遍历字典
       print(f"{k}={v}")
   
   # while（和Java一样）
   # 没有 do-while
   ```

### 下午 2h（动手写）

**练习题目（必须手写，不要复制）：**

1. 写一个函数 `group_by_age(users: list[dict]) -> dict[str, list]`，把用户按年龄段分组
2. 用列表推导式生成100以内的所有质数
3. 统计一段文本中每个单词出现的次数，返回top10
4. 实现一个简单的LRU缓存类（用dict + list，不查资料试试）

> 每道题控制在20-30分钟，写不出来就查，但查完要手写一遍。

### 晚上 1h（复习）
- 把今天遇到的Python和Java不同点记到笔记里
- 逛逛GitHub trending的Python项目，感受一下Python代码风格

---

## Day 2（周二）：函数 + 面向对象 + 文件IO

### 上午 2h

1. **函数进阶**（45min）
   ```python
   # 默认参数 / 关键字参数 / 可变参数
   def create_user(name, age=18, **kwargs):
       """**kwargs → 接收任意多关键字参数，打包成dict"""
       user = {"name": name, "age": age}
       user.update(kwargs)
       return user
   
   create_user("张三", city="北京", job="学生")
   # → {"name": "张三", "age": 18, "city": "北京", "job": "学生"}
   
   # lambda（匿名函数，类比Java的 (x)->x*2）
   sorted(users, key=lambda u: u["age"], reverse=True)
   
   # 装饰器——Java的AOP！
   import time
   def timer(func):
       def wrapper(*args, **kwargs):
           start = time.time()
           result = func(*args, **kwargs)
           print(f"{func.__name__} 耗时 {time.time()-start:.2f}s")
           return result
       return wrapper
   
   @timer
   def slow_func():
       time.sleep(1)
   ```

2. **面向对象**（45min）
   ```python
   # Python的OOP比Java简洁但规则不同
   class Agent:
       # 类变量 → Java的 static 变量
       model = "gpt-4"
       
       def __init__(self, name, tools=None):
           # __init__ → 构造函数，self → this（必须显式写）
           self.name = name            # 实例变量
           self.tools = tools or []    # 默认空列表的Python写法
       
       def add_tool(self, tool):
           """实例方法"""
           self.tools.append(tool)
       
       @classmethod
       def from_config(cls, config):
           """类方法 → Java的静态工厂方法"""
           return cls(config["name"], config.get("tools"))
       
       @staticmethod
       def validate_tool(tool):
           """静态方法 → Java的 static 方法"""
           return "name" in tool and "func" in tool
       
       def __str__(self):
           """类似Java的 toString()"""
           return f"Agent({self.name}, tools={len(self.tools)})"
   
   # 继承
   class CoderAgent(Agent):
       def __init__(self, name, language="python"):
           super().__init__(name, tools=["code_executor"])
           self.language = language
   ```

3. **文件IO与异常**（30min）
   ```python
   # with语句 → Java的 try-with-resources
   with open("data.txt", "r", encoding="utf-8") as f:
       content = f.read()
   
   # 逐行读（大文件）
   with open("big_file.txt") as f:
       for line in f:
           process(line)
   
   # JSON读写——日常最高频操作
   import json
   with open("config.json", "w") as f:
       json.dump(data, f, ensure_ascii=False, indent=2)
   data = json.load(open("config.json"))
   
   # 异常
   try:
       result = risky_operation()
   except ValueError as e:
       print(f"参数错误: {e}")
   except Exception as e:
       print(f"未知错误: {e}")
   finally:
       cleanup()
   ```

### 下午 2h

**练习题目：**

1. 写一个`@retry(max_attempts=3, delay=1)`装饰器，函数失败后自动重试
2. 定义一个`Tool`基类和`SearchTool`、`CalculatorTool`子类，各有`execute()`方法
3. 读取一个JSON配置文件，解析后用Python类的形式管理配置（Config类）
4. 递归遍历一个目录，统计所有`.py`文件的总行数

### 晚上 1h
- 整理OOP对比表（Java vs Python）
- 想想：Spring的`@Transactional`和Python装饰器是不是一个思路？

---

## Day 3（周三）：异步编程（Agent核心能力）

> Java的线程/CompletableFuture你熟，但Python的async是另一套逻辑。
> 核心理解：**async ≠ 多线程，async = 单线程协作式并发**

### 上午 2h

1. **理解async/await**（1h）
   ```python
   import asyncio
   
   # 同步版本
   def fetch_url(url):
       print(f"开始请求 {url}")
       time.sleep(1)   # 模拟IO等待——整个线程卡住
       print(f"完成 {url}")
       return f"data from {url}"
   
   # 异步版本
   async def fetch_url_async(url):
       print(f"开始请求 {url}")
       await asyncio.sleep(1)   # 让出控制权，不阻塞
       print(f"完成 {url}")
       return f"data from {url}"
   
   # 并发的威力
   async def main():
       urls = [f"https://api{i}.com" for i in range(10)]
       
       # 同步：10秒（一个一个来）
       # 异步：1秒（10个请求同时发出）
       results = await asyncio.gather(
           *[fetch_url_async(url) for url in urls]
       )
       return results
   
   asyncio.run(main())
   ```

   **理解要点：**
   - `async def` 定义的是一个协程（coroutine）
   - `await` = "我要等这个IO完成，但在等待期间你可以干别的"
   - `asyncio.gather()` = 同时发起多个协程
   - 类比Java的`CompletableFuture.allOf()`，但Python是单线程的

2. **asyncio实战**（1h）
   ```python
   # Task：轻量级"线程"
   async def worker(name, queue):
       while True:
           task = await queue.get()
           if task is None:   # 结束信号
               break
           print(f"{name} 处理 {task}")
           await asyncio.sleep(0.5)
   
   async def producer(queue):
       for i in range(10):
           await queue.put(f"任务{i}")
           await asyncio.sleep(0.1)
       for _ in range(3):
           await queue.put(None)  # 通知worker结束
   
   # aiohttp：异步HTTP客户端（LLM API调用的基础）
   import aiohttp
   async def call_llm(prompt):
       async with aiohttp.ClientSession() as session:
           async with session.post(
               "https://api.openai.com/v1/chat/completions",
               headers={"Authorization": f"Bearer {api_key}"},
               json={
                   "model": "gpt-4",
                   "messages": [{"role": "user", "content": prompt}]
               }
           ) as resp:
               return await resp.json()
   ```

   资源：[Real Python Async IO文章](https://realpython.com/async-io-python/) —— 必读

### 下午 2h

**练习题目：**

1. 用`asyncio`写一个简单的并发爬虫，爬3个网页（用`aiohttp`）
2. 实现一个`Semaphore`限流的异步请求器（最多5个并发）
3. 模拟：10个用户同时请求AI对话，用`asyncio.gather`处理，统计总耗时
4. 比较同步版和异步版的性能差距

### 晚上 1h
- 画一张图：asyncio事件循环怎么工作的
- 对比Java的线程池模型和Python协程模型的优劣

---

## Day 4（周四）：Python核心模块 + FastAPI速成

### 上午 2h

1. **常用标准库速览**（30min）
   ```python
   # collections —— 高级数据结构
   from collections import defaultdict, Counter, deque, OrderedDict
   Counter(["a","b","a","c","a"])    # → {"a":3, "b":1, "c":1}
   defaultdict(list)                  # 访问不存在的key自动创建空list
   
   # itertools —— 迭代器工具
   from itertools import chain, groupby, product, combinations
   chain([1,2], [3,4])               # → [1,2,3,4]
   
   # functools —— 函数工具
   from functools import lru_cache, partial, reduce
   
   @lru_cache(maxsize=128)            # 自动缓存函数结果
   def fib(n):
       return n if n < 2 else fib(n-1) + fib(n-2)
   
   # dataclasses —— 数据类（Java的 @Data / record）
   from dataclasses import dataclass, field
   
   @dataclass
   class Message:
       role: str           # "user" / "assistant" / "system"
       content: str
       created_at: float = field(default_factory=time.time)
   ```

2. **FastAPI核心**（1.5h）
   ```python
   # app.py
   from fastapi import FastAPI, HTTPException, Depends
   from pydantic import BaseModel, Field
   from typing import Optional
   
   app = FastAPI(title="Agent服务", version="1.0")
   
   # --- 数据模型（Pydantic）---
   class ChatRequest(BaseModel):
       """请求体，类比Java的 @RequestBody DTO"""
       message: str = Field(..., min_length=1, max_length=4000)
       history: list[dict] = []
       temperature: float = Field(default=0.7, ge=0, le=2.0)
   
   class ChatResponse(BaseModel):
       reply: str
       tokens_used: int
       model: str
   
   # --- 依赖注入（类比Spring的 @Autowired）---
   def get_api_key():
       """可以从环境变量/配置中心/数据库读取"""
       return "sk-xxx"
   
   # --- 路由 ---
   @app.get("/")
   async def root():
       """健康检查"""
       return {"status": "ok", "service": "Agent"}
   
   @app.post("/chat", response_model=ChatResponse)
   async def chat(req: ChatRequest, api_key: str = Depends(get_api_key)):
       """对话接口"""
       # 模拟调用LLM（后续替换为真实调用）
       reply = f"你说: {req.message}。我是Agent回复"
       return ChatResponse(
           reply=reply,
           tokens_used=len(req.message) // 4,
           model="gpt-4"
       )
   
   # --- 流式输出（SSE，Agent开发高频需求）---
   import asyncio
   from fastapi.responses import StreamingResponse
   
   @app.post("/chat/stream")
   async def chat_stream(req: ChatRequest):
       """流式对话——像ChatGPT那样一个字一个字出"""
       async def generate():
           words = f"这是对「{req.message}」的回复...".split()
           for word in words:
               yield f"data: {word}\n\n"
               await asyncio.sleep(0.1)
           yield "data: [DONE]\n\n"
       
       return StreamingResponse(
           generate(),
           media_type="text/event-stream"
       )
   
   # 启动：uvicorn app:app --reload
   ```

   **对比Spring Boot：**
   | Spring Boot | FastAPI |
   |-------------|---------|
   | `@RestController` | `@app.get/post` |
   | `@RequestBody` | `req: ChatRequest`（Pydantic自动校验） |
   | `@Autowired` | `Depends()` |
   | `@ExceptionHandler` | `@app.exception_handler()` |
   | AOP切面 | Middleware |
   | application.yml | Pydantic Settings |

### 下午 2h

**动手项目：第一个API服务**

搭建一个"天气助手"雏形：
```python
# 要求：
# 1. POST /weather 输入城市名，返回模拟天气信息
# 2. POST /advice 输入城市名，基于天气给出穿衣建议（模拟LLM）
# 3. GET /history 查看历史查询记录（存内存list即可）
# 4. 用Pydantic做请求/响应校验
# 5. 能通过 http://127.0.0.1:8000/docs 看到自动生成的Swagger文档
```

### 晚上 1h
- 用FastAPI的`/docs`页面体会Swagger自动生成
- 想想：这和你的Java项目里写Swagger注解有什么不同？

---

## Day 5（周五）：LLM API调用 + Prompt初探

### 上午 2h

1. **OpenAI API调用（兼容格式）**（1h）
   ```python
   import openai
   
   # 用OpenAI兼容接口调用（国内模型基本都兼容这个格式）
   client = openai.AsyncOpenAI(
       api_key="your-api-key",
       base_url="https://api.deepseek.com/v1"  # 以DeepSeek为例
       # base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 通义千问
   )
   
   # 同步调用
   response = client.chat.completions.create(
       model="deepseek-chat",
       messages=[
           {"role": "system", "content": "你是一个Java专家"},
           {"role": "user", "content": "解释Java的volatile关键字"}
       ],
       temperature=0.7,
       max_tokens=1000
   )
   print(response.choices[0].message.content)
   
   # 流式调用（SSE实现的基础）
   stream = client.chat.completions.create(
       model="deepseek-chat",
       messages=[{"role": "user", "content": "写一首诗"}],
       stream=True
   )
   for chunk in stream:
       if chunk.choices[0].delta.content:
           print(chunk.choices[0].delta.content, end="", flush=True)
   ```

2. **统一调用封装**（1h）
   ```python
   # 封装一个多模型调用工具——用你Java写Service层的思路
   from enum import Enum
   from dataclasses import dataclass
   
   class ModelProvider(Enum):
       OPENAI = "openai"
       DEEPSEEK = "deepseek"
       QWEN = "qwen"
       ZHIPU = "zhipu"
   
   @dataclass
   class LLMConfig:
       provider: ModelProvider
       api_key: str
       model: str
       base_url: str
   
   class LLMClient:
       """统一LLM调用客户端——类比Java的Service"""
       
       def __init__(self):
           self._clients: dict[str, openai.AsyncOpenAI] = {}
       
       def register(self, name: str, config: LLMConfig):
           self._clients[name] = openai.AsyncOpenAI(
               api_key=config.api_key,
               base_url=config.base_url
           )
       
       async def chat(self, client_name: str, messages: list[dict],
                      temperature=0.7, stream=False):
           client = self._clients[client_name]
           return await client.chat.completions.create(
               model="gpt-4",  # 可以按config来
               messages=messages,
               temperature=temperature,
               stream=stream
           )
       
       async def chat_with_prompt(self, client_name: str,
                                   system_prompt: str,
                                   user_input: str) -> str:
           """最常用的调用模式：系统提示词 + 用户输入"""
           response = await self.chat(client_name, [
               {"role": "system", "content": system_prompt},
               {"role": "user", "content": user_input}
           ])
           return response.choices[0].message.content
   ```

### 下午 2h

**动手：提示词实验**

1. 用同一个问题测试3种Prompt策略，对比效果：
   ```python
   question = "设计一个学生选课系统的数据库表结构"
   
   # Prompt 1：直接问
   # Prompt 2：设定角色（你是资深DBA）+ Few-shot示例
   # Prompt 3：Chain-of-Thought（请一步步思考，先分析需求，再设计表...）
   ```

2. 实现一个简单的Prompt模板管理：
   ```python
   class PromptManager:
       """Prompt模板管理——类比Java的模板引擎"""
       templates = {
           "code_review": "你是一个资深{language}程序员，请review以下代码：\n{code}",
           "sql_generator": "根据以下需求生成SQL：{requirement}\n数据库是{db_type}",
       }
       
       def render(self, name: str, **kwargs) -> str:
           return self.templates[name].format(**kwargs)
   ```

### 晚上 1h
- 注册DeepSeek API（有免费额度）或智谱GLM（有免费token）
- 实际调通一次API调用，体验流式输出
- 注册链接：https://platform.deepseek.com/ 或 https://open.bigmodel.cn/

---

## Day 6（周六）：项目实战——个人AI对话服务

> 周末全天投入，今天做一个完整的小项目收尾第一周

### 项目：MiniChat —— 个人AI对话服务

**功能需求：**
- [ ] FastAPI后端，支持POST对话（非流式+流式两种）
- [ ] 支持多轮对话（带上下文历史）
- [ ] 支持切换不同模型（至少接入2个：DeepSeek + 通义千问）
- [ ] 简单的前端页面（HTML一个文件搞定，ChatGPT风格的聊天框）
- [ ] 对话历史存SQLite（用Python自带模块）

**架构：**
```
前端(HTML/CSS/JS) ──SSE──> FastAPI ──> LLMClient ──> DeepSeek/千问
                              │
                         SQLite (历史记录)
```

**分步实现（每步1-1.5小时，全天5-6小时）：**

**Step 1：项目骨架（1h）**
```
minichat/
├── main.py          # FastAPI入口 + 路由
├── llm_client.py    # 多模型调用封装（用Day5的代码）
├── models.py        # Pydantic数据模型
├── db.py            # SQLite操作
├── static/
│   └── index.html   # 前端聊天界面
└── prompts.py       # Prompt模板
```

**Step 2：后端API（2h）**
- `/chat` — 普通对话
- `/chat/stream` — 流式对话（SSE）
- `/history` — 获取历史
- `/models` — 列出可用模型

**Step 3：前端页面（1.5h）**
```html
<!-- 简易聊天界面，ChatGPT风格 -->
<!-- 支持：输入框、发送按钮、流式显示消息、切换模型 -->
```

**Step 4：测试 + 优化（1h）**
- 跑通完整链路
- 处理异常（API超时、网络错误）
- 加上简单的日志

### 晚上 1h
- 把MiniChat项目推到GitHub（这是你的第一个AI项目）
- 写好README：功能介绍、技术栈、如何运行、截图
- 复盘：这周哪些概念还不清楚？记下来下周查

---

## Day 7（周日）：周复盘 + 查漏补缺

### 上午 2h：复习巩固

1. **过一遍Day1-6的核心代码**，看是否能独立重写
2. **重点检查**：
   - async/await用熟了吗？
   - FastAPI的路由、依赖注入、中间件会写吗？
   - Pydantic的Field校验会用吗？
   - LLM API调用流程清楚吗？

3. **完成MiniChat的收尾**（如果周六没做完）

### 下午 2h：预习下周

1. **浏览下周要学的内容**：
   - LangChain基础（Chain、PromptTemplate、LLM）
   - PDF文档处理（PyPDF2、LangChain Document Loader）
   - ChromaDB向量数据库
2. **安装需要的包**：
   ```bash
   pip install langchain langchain-openai langchain-community
   pip install chromadb pypdf2 tiktoken
   ```

### 晚上 1h：输出周报
- 写一篇学习笔记（发CSDN/掘金/知乎都可以，开始建立你的技术博客）
- 标题示例：《Java后端转AI开发第一周：Python速成复盘》

---

## Week 1 检查清单

| 技能点 | 自评（1-5） | 不会的话回看 |
|--------|------------|-------------|
| Python基础语法熟练（list/dict/类/装饰器） | /5 | Day1-2 |
| async/await异步编程 | /5 | Day3 |
| FastAPI写RESTful接口 | /5 | Day4 |
| Pydantic数据校验 | /5 | Day4 |
| LLM API调用（同步+流式） | /5 | Day5 |
| Prompt Engineering基础 | /5 | Day5 |
| SSE流式输出 | /5 | Day4 |
| 独立完成一个MiniChat项目 | Y/N | Day6 |

> 全部达到3分以上即可进入第二周。有1-2分的项目，下周抽空补。

---

## 下周预告

**Week 2 核心：**
- LangChain快速入门（Chain、Prompt、LLM三大件）
- 文档处理（用LangChain的Document Loader）
- ChromaDB向量数据库入门
- 实现第一个RAG问答Demo

> 第一周重在"换语言"（Java→Python），第二周开始才是Agent开发的真正内容。加油！
