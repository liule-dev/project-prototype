import base64
import traceback
from typing import List, Dict, Any
import io
import dotenv
import pandas as pd
import uvicorn
from langchain.agents import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from fastapi import WebSocket, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import matplotlib.pyplot as plt
api_key=dotenv.get_key(dotenv.find_dotenv(),"api_key")
base_url=dotenv.get_key(dotenv.find_dotenv(),"base_url")



app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)



# 封装数据分析工具
@tool
def get_columns() -> str:
    """获取数据集的列名"""
    return ", ".join(df.columns)


@tool
def describe_column(column_name: str) -> str:
    """描述指定列的统计信息"""
    if column_name not in df.columns:
        return f"列 {column_name} 不存在。"
    desc = df[column_name].describe().to_string()
    return desc


@tool
def correlation(columns: str) -> str:
    """计算两列之间的相关系数
    columns: 姓名,年龄,爱好,专业
    """
    cols = [c.strip() for c in columns.split(',')]#将输入的列名字符串按逗号分割，并使用 strip() 去除每个列名前后的空格，生成一个清洗后的列名列表 cols。
    for col in cols:
        if col not in df.columns:
            return f"列 {col} 不存在。"
    return df[cols].corr().to_string()#如果所有列都存在，则使用 df[cols] 选取指定列，调用 corr() 方法计算相关系数矩阵，并通过 to_string() 转换为易读的字符串格式返回。

global image
image = None
@tool
def plot_column(column_name: str):
    """绘制指定列的直方图"""
    if column_name not in df.columns:
        return f"列 {column_name} 不存在。"

    try:
        # 创建图形并绘制直方图
        fig, ax = plt.subplots()
        df[column_name].plot.hist(ax=ax)

        # 保存到内存缓冲区
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # 转换为base64
        global image
        image = base64.b64encode(buf.read()).decode()
        buf.close()
        # 清理资源
        plt.close(fig)

        return "图表已生成"
    except Exception as e:
        return f"绘图失败: {str(e)}"

df = None
# 判断函数
def ensure_df_loaded():
    global df
    return df is not None

g=0
def try_transport_database(b64_data: str):
    global df
    try:
        decoded_bytes = base64.b64decode(b64_data)
    except Exception as e:
        return f"数据文件解码失败 :{e}"
    try:
        df = pd.read_csv(io.BytesIO(decoded_bytes))
        return df
    except Exception as e:
        pass
    try:
        df = pd.read_excel(io.BytesIO(decoded_bytes))
        return df
    except Exception as e:
        df = None
        return f"无法识别数据格式文件  csv 和 excel 均解析失败"

model = ChatOpenAI(
        model='qwen3-vl-plus',
        api_key=api_key,
        base_url=base_url,
        streaming=True  # 开启流式输出
    )


tools = [get_columns, describe_column, correlation,plot_column]#

prompt = '''
           你是一个数据分析智能体，使用提供的工具来分析一个DataFrame,工具的输出非常的重要,当用户提出数据分析问题时，你应该尽可能的调用工具来获得准确的信息。
            1.如果用户未让绘图则只分析不要绘图，如果用户提示绘图则先调用列分析工具再把列分析工具输出给plot_column工具绘制图表
            
            You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
        '''

agent = create_react_agent(
        llm=model,
        tools=tools,
        prompt=PromptTemplate.from_template(prompt)
    )

   # 并把查找上面最相似的文件的DataFrame返回在content字段，与上面的1用逗号分割
prompt1 = '''
        1.你是一个数据处理助手，分析用户是否需要对文件分析或绘图，如果需要智能体content字段返回数字1
'''

# agent1 不需要工具，直接使用 model
# agent1 = create_react_agent(
#     llm=model,
#     prompt=PromptTemplate.from_template(prompt1),
# )

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        print('websocket 链接成功...')
        global df  # 声明全局变量
        global g
        history: List[Dict[str, Any]] = []
        try:
            while True:
                data = await websocket.receive_json()
                question = data.get("question").strip()
                imageBase64 = data.get("imageBase64")
                datafilebase64 = data.get("datafileBase64")

                if not question and not imageBase64 and not datafilebase64:
                    await websocket.send_json({
                        "event": "错误",
                        "message": "请输入问题或图片"
                    })
                    continue

                content: List[Dict[str, Any]] = []

                if datafilebase64:
                    ddd=try_transport_database(datafilebase64)
                    history.append({"role": "user", "content": ddd})

                if question:
                    content.append({
                        "type": "text",
                        "text": question
                    })
                if imageBase64:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{imageBase64}"}
                    })
                    history.append({"role": "user", "content": content})


                await websocket.send_json({"event": "start"})

                try:
                    if imageBase64:
                        messages_llm = history + [{"role": "user", "content": content}]
                        full_data = " "
                        async for chunk in model.astream(messages_llm):
                            delta = chunk.content or ""
                            if not delta:
                                continue
                            full_data += delta
                            await websocket.send_json({"event": "delta", "text": delta})
                        await websocket.send_json({"event": "end", "text": full_data})
                        history.append({"role": "user", "content": content})
                        history.append({"role": "assistant", "content": [{"type": "text", "text": full_data}]})
                    elif question and ensure_df_loaded() or question and g==1:
                        answer = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
                        try:
                            result = answer["messages"][-1].content
                        except Exception as e:
                            result = str(answer)
                        full_text = ""
                        for i in range(0, len(result), 30):
                            delta = result[i:i + 30]
                            full_text += delta
                            await websocket.send_json({'event': 'delta', 'text': delta})
                        df = None
                        g=0
                        await websocket.send_json({'event': 'end', 'text': full_text,"image": image})
                        history.append({"role": "user", "content": [{"type": "text", "text": question}]})
                        history.append({"role": "assistant", "content": [{"type": "text", "text": full_text}]})
                    elif question:
                        messages_llm = history + [
                            {"role": "user", "content": content or [{"type": "text", "text": question or "你好"}]}]
                        full_data = ""
                        async for chunk in model.astream(messages_llm):
                            delta = chunk.content or ""
                            if not delta:
                                continue
                            full_data += delta
                            await websocket.send_json({"event": "delta", "text": delta})
                        await websocket.send_json({"event": "end", "text": full_data})
                        history.append({"role": "user", "content": [{"type": "text", "text": question}]})
                        history.append({"role": "assistant", "content": [{"type": "text", "text": full_data}]})

                except Exception as e:
                    traceback.print_exc()
                    print(f"模型调用出错: {str(e)}")
                    await websocket.send_json({
                        'event': 'error',
                        'message': f'模型调用出错: {str(e)}'
                    })

        except Exception as e:
            print("WebSocket连接已断开")


if __name__ == "__main__":
    uvicorn.run(app,port=8080)




