# daypoem

从指定日期（默认为 `2023年10月16日`）开始，每日抽取一首诗并生成小红书文案。并在指定目录下（默认为 `$HOME/Downloads/AI 画诗`）下生成唐诗的目录及数据。

- poem.json: 唐诗数据
- 小红书.txt: 小红书文案

## 安装

```bash
git clone https://github.com/okooo5km/daypoem && cd daypoem
pip3 install .
```

这样 daypoem 就可以运行了。在运行之前需要声明 OpenAI 的 API Key 的环境变量：

```bash
export OPENAI_API_KEY=xxx
```

## 配置

可以通过环境变量修改默认的起始日期和唐诗数据保存目录：

```bash
export FIRST_DAY=2023-10-16
export BASE_DIR=/Users/5km/Downloads
```

## 使用

### 基本用法

```bash
➜ daypoem --help

 Usage: daypoem [OPTIONS]

╭─ Options ────────────────────────────────────────────────────────────╮
│ --url                    TEXT     The URL of the poem to scrape.     │
│                                   [default: None]                    │
│ --xhs       --no-xhs              Generate an xiaohongshu note       │
│                                   [default: no-xhs]                  │                   │
│ --offset                 INTEGER  The number of days to offset from  │
│                                   today.                             │
│                                   [default: 0]                       │
│ --list      --no-list             List all diary information.        │
│                                   [default: no-list]                 │
│ --help                            Show this message and exit.        │
╰──────────────────────────────────────────────────────────────────────╯

```

### 查看唐诗三百首的列表

```bash
daypoem --list
```

### 获取诗

```bash
# 获取今天的唐诗
daypoem
# 获取昨天的唐诗
daypoem --offset -1
# 获取明天的唐诗
daypoem --offset 1
```

### 获取唐诗并生成文案

```bash
daypoem --xhs
```
