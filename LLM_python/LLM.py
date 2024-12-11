import json
import requests

# 定义API的URL
API_URL = "http://222.20.126.129:11434/api/generate"

# 模拟的函数来生成请求数据
def http_post_generate(post_data, context):
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "flag": "libcurl",
        "Accept-Encoding": "gzip, deflate, br"
    }

    # 发起POST请求
    response = requests.post(API_URL, headers=headers, data=post_data)
    
    # 如果请求成功，处理返回的数据
    if response.status_code == 200:
        print(f"code: {response.status_code}")
        response_json = response.json()

        # 打印调试信息
        print(f"AI response: {response_json['response']}")

        # 更新上下文
        context[:] = response_json["context"]  # 更新context
        return response_json['response']
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


# 转换为UTF-8的函数
def to_utf8(input_str):
    return input_str.encode('utf-8').decode('utf-8')


# 主函数
def main():
    # print("Put 1 to exit")

    # 输入提示词和问题
    hint_for_judge_str="\n上述的信息能够转化为日程信息吗，如果能回复\"Yes\",否则回复\"No\"。"
    # hint_for_judge_str="打印上述的信息"
    # hint_str = "接下来我将给你发送日志信息，首先请找出具体时间、地点和重要内容，且重要内容要比较详细，回复的具体格式如下“时间:时间信息\n地点:地点信息\n重要内容:内容信息\nEND。如果是线上的将地点替换为会议号或其它相关链接且链接的含义或者内容要写明。如果没有指出地址、时间可以空着。"
    hint_str = "分析发给你的信息，回复的具体格式:\"具体时间：具体时间如几点几分、早上还是晚上\n地点:地点信息\n内容（若无可省略）:内容信息\nEND\"。如果是线上的将地点替换为会议号或其它相关链接且链接的含义或者内容要写明。\n"
    hint_of_data="分析发给你的信息，识别其中的年月日若无年或月可省略，回复格式为：\"xx年xx月xx日，比如2021年3月4日\";若无年月日则识别例如\"今天\"\"明天\"\"后天\"的字并直接回复"
    propt_str = input("请输入您的问题：")  # 获取用户输入的问题

    # 定义上下文
    context = []

    # # 使用用户输入的问题进行后续处理
    # post_body = {
    #     "model": "llama3.1",  # 选择的大模型
    #     "prompt": propt_str,  # 转换输入问题为UTF-8
    #     "stream": False,  # 以非流式（不必在意的参数）
    #     "context": context  # 用于保存对话的上下文
    # }

    # # 将请求体转为JSON格式
    # post_data = json.dumps(post_body, ensure_ascii=False).encode('utf-8')

    # # 分析日志信息API
    # http_post_generate(post_data, context)

    hint_for_judge_str=propt_str+hint_for_judge_str
    # print(hint_for_judge_str)
    # 准备POST请求体的内容
    post_body = {
        "model": "llama3.1",  # 选择的大模型
        "prompt": hint_for_judge_str,  # 转换提示词为UTF-8
        "stream": False,  # 以非流式（不必在意的参数）
        "context": context  # 用于保存对话的上下文
    }

    # 将请求体转为JSON格式
    post_data = json.dumps(post_body, ensure_ascii=False).encode('utf-8')

    # 调用API
    judge=http_post_generate(post_data, context)





    if judge[:3]=="Yes":
        # 准备POST请求体的内容
        # hint_str+=propt_str
        post_body = {
            "model": "llama3.1",  # 选择的大模型
            "prompt": hint_str,  # 转换提示词为UTF-8
            "stream": False,  # 以非流式（不必在意的参数）
            "context": context  # 用于保存对话的上下文
        }

        # 将请求体转为JSON格式
        post_data = json.dumps(post_body, ensure_ascii=False).encode('utf-8')

        # 调用API
        http_post_generate(post_data, context)

        # 获取日期信息，为了保存日程
        post_body = {
            "model": "llama3.1",  # 选择的大模型
            "prompt": hint_of_data,  # 转换提示词为UTF-8
            "stream": False,  # 以非流式（不必在意的参数）
            "context": context  # 用于保存对话的上下文
        }

        # 将请求体转为JSON格式
        post_data = json.dumps(post_body, ensure_ascii=False).encode('utf-8')

        # 调用API
        http_post_generate(post_data, context)
    else:
        print("不是日志信息")

if __name__ == "__main__":
    main()
