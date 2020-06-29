# AutomatedParaphrase

## 原项目链接

https://github.com/AudayBerro/automatedParaphrase

## 配置环境

```shell
# 安装依赖
pip install -r requirements.txt -q
# 下载en_core_web_lg
python -m spacy download en_core_web_lg
```

## 文件处理

在项目目录下创建results文件夹

## 使用方法

在dataset文件夹里放txt文件，里面数据为每行一条

文件名用于-f参数

```shell
python main.py -f file_name.txt
```

## 输出

输出的结果会添加到result/paraphrases.txt