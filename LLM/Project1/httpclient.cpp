#include <curl/curl.h>    
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "json11.hpp"

//关于POST请求相关的结构体和函数
typedef struct {
    std::string body;
    size_t bodySize;
} stResponse;

typedef struct {
    std::string header;
    size_t headerSize;
} stResponseHeader;

size_t responseBodyCallback(void* ptr, size_t size, size_t nmemb, void* stream) {
    stResponse* pResponse = (stResponse*)stream;
    pResponse->body.append((char*)ptr, size * nmemb);
    pResponse->bodySize = size * nmemb;
    return size * nmemb;
}

size_t responseHeaderCallback(void* ptr, size_t size, size_t nmemb, void* stream) {
    stResponseHeader* pResponseHeader = (stResponseHeader*)stream;
    pResponseHeader->header.append((char*)ptr, size * nmemb);
    pResponseHeader->headerSize = size * nmemb;
    return size * nmemb;
}
//——————————————————————————————————

//函数声明
void http_post_generate(char post_data[5096], json11::Json::array* context);
void http_post_chat(char post_data[5096]);

//现在所实现的功能：能够有记忆的进行对话
int main() {
    std::cout << "Put 1 to exit" << std::endl;
    char postData[5096];    //存储POST的参数内容
    std::string propt_str;  //存储客户想要向大模型询问的内容
    json11::Json::array context;
    json11::Json post_body; //JSON格式的POST参数内容

    while (1) {
        std::getline(std::cin, propt_str);
        if (!strcmp(propt_str.c_str(), "1"))break;
        //JSON对象的定义必须在给定prpt_str之后，因为库定义的为const
        post_body = json11::Json::object{
		    { "model", "llama3.1" },    //选择的大模型
		    { "prompt", propt_str},    //向大模型询问的内容
		    { "stream", false },        //以非流式（不必在意的参数）
			{"context",context},        //为了实现短暂的对话记忆
        };
        strcpy_s(postData, post_body.dump().c_str());
        std::cout << postData << std::endl;
        http_post_generate(postData,&context);
    }




    return 0;
}



void http_post_generate(char post_data[5096], json11::Json::array* context) {       //generate API的调用函数，context用来保存短暂的对话记忆
    std::string readBuffer;
    stResponse response;
    stResponseHeader responseHeader;

    // 初始化所有可能的调用
    curl_global_init(CURL_GLOBAL_ALL);


    CURL* curl = curl_easy_init();

    // 设置url
    curl_easy_setopt(curl, CURLOPT_URL, "http://222.20.126.129:11434/api/generate");

    // 设置post请求，不设置或设置为0则为get请求
    curl_easy_setopt(curl, CURLOPT_POST, 1);
    // 设置post请求体
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, post_data);
    // 设置post请求体大小
    curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, strlen(post_data));

    // 设置http请求头
    curl_slist* headerList = NULL;
    headerList = curl_slist_append(headerList, "Content-Type: application/json");
    headerList = curl_slist_append(headerList, "flag: libcurl");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headerList);

    // 设置不校验证书，https请求时使用
    curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0);
    curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, 0);

    // 设置回调函数获取响应体数据
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, responseBodyCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void*)&response);

    // 设置回调函数获取响应头数据
    curl_easy_setopt(curl, CURLOPT_HEADERFUNCTION, responseHeaderCallback);
    curl_easy_setopt(curl, CURLOPT_HEADERDATA, (void*)&responseHeader);

    // 超时时间
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 30);

    // 执行请求
    CURLcode res = curl_easy_perform(curl);

    // 检查错误
    if (res == CURLE_OK) {
        // 获取状态码
        int responseCode = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &responseCode);
        std::cout << "code : " << responseCode << std::endl;

        //调试信息
        //std::cout << "responseHeader size : " << responseHeader.headerSize << std::endl;
        //std::cout << "responseHeader header : " << responseHeader.header.c_str() << std::endl;

        //std::cout << "response size : " << response.bodySize << std::endl;
        //std::cout << "response body : " << response.body.c_str() << std::endl;

        //将response body转化为JSON对象
        std::string err;
        json11::Json mJson = json11::Json::parse(response.body.c_str(), err);

        std::cout << "AI response :" << mJson["response"].string_value()<<std::endl;
        *context = mJson["context"].array_items();
    }
    else {
        std::cout << curl_easy_strerror(res) << std::endl;
    }

    curl_slist_free_all(headerList);

    // 清理
    curl_easy_cleanup(curl);
}

void http_post_chat(char post_data[5096]) { //暂时用不到的接口
    std::string readBuffer;
    stResponse response;
    stResponseHeader responseHeader;

    // 初始化所有可能的调用
    curl_global_init(CURL_GLOBAL_ALL);


    CURL* curl = curl_easy_init();

    // 设置url
    curl_easy_setopt(curl, CURLOPT_URL, "http://222.20.126.129:11434/api/chat");

    // 设置post请求，不设置或设置为0则为get请求
    curl_easy_setopt(curl, CURLOPT_POST, 1);
    // 设置post请求体
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, post_data);
    // 设置post请求体大小
    curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, strlen(post_data));

    // 设置http请求头
    curl_slist* headerList = NULL;
    headerList = curl_slist_append(headerList, "Content-Type: application/json");
    headerList = curl_slist_append(headerList, "flag: libcurl");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headerList);

    // 设置不校验证书，https请求时使用
    curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0);
    curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, 0);

    // 设置回调函数获取响应体数据
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, responseBodyCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void*)&response);

    // 设置回调函数获取响应头数据
    curl_easy_setopt(curl, CURLOPT_HEADERFUNCTION, responseHeaderCallback);
    curl_easy_setopt(curl, CURLOPT_HEADERDATA, (void*)&responseHeader);

    // 超时时间
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 30);

    // 执行请求
    CURLcode res = curl_easy_perform(curl);

    // 检查错误
    if (res == CURLE_OK) {
        // 获取状态码
        int responseCode = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &responseCode);
        std::cout << "code : " << responseCode << std::endl;

        //调试信息
        //std::cout << "responseHeader size : " << responseHeader.headerSize << std::endl;
        //std::cout << "responseHeader header : " << responseHeader.header.c_str() << std::endl;

        //std::cout << "response size : " << response.bodySize << std::endl;
        //std::cout << "response body : " << response.body.c_str() << std::endl;

        //将response body转化为JSON对象
        std::string err;
        json11::Json mJson = json11::Json::parse(response.body.c_str(), err);

        std::cout << "AI response :" << mJson["response"].string_value();
    }
    else {
        std::cout << curl_easy_strerror(res) << std::endl;
    }

    curl_slist_free_all(headerList);

    // 清理
    curl_easy_cleanup(curl);
}
