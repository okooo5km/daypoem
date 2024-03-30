#!/usr/bin/env python3
import os
import re
import csv
import json
import typer
import openai
import requests
import pkg_resources
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from prettytable import PrettyTable
from datetime import datetime, timedelta

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
first_day_str = os.getenv("FIRST_DAY", "2023-10-16")
first_day = datetime.strptime(first_day_str, "%Y-%m-%d")
base_dir_str = os.getenv("BASE_DIR", (Path.home() / "Desktop").as_posix())
base_dir = Path(base_dir_str) / "AI 画诗"

data_path = pkg_resources.resource_filename(__name__, 'data/poems.csv')

summary_prompt = """我是一名男士，你是我的小红书文案撰写助手，对我提供的 json 数据格式的古诗词内容进行分析理解，最终会总结一句话分享，你需要把自己当做读者提出切题且值得思考的问题（也就是第一人称），尽量是非常简短和富有文采的一句话！同时生成一个以“AI画诗《{诗的题目}》开头的文案标题，小红书标题不能超过 20 个中文汉字，要求吸人眼球且符合小红书文案风格，如果可能的话一句话和标题中也配上贴切的 emoji，同时凝练出可以使用的话题关键词，比如#唐诗 #月亮 #思念 #爱情 ...；另外根据我提供的赏析内容，写一段贴合原赏析内容且富有文采和哲理的赏析。综上，整体输出的内容为 json 字符串本身就好，不要使用 markdown 语法，形如:
{
    "标题": "",
    "一句话": "",
    "赏析": "",
    "话题": ""
}"""


def parse_poem_info(url):

    html_content = ""

    poem_id = re.search(r"shiwenv_(\w+)\.aspx", url).group(1)

    # 发送 HTTP 请求
    response = requests.get(url)

    # 检查请求是否成功
    if response.status_code == 200:
        # 返回网页的 HTML 内容
        html_content = response.text
    else:
        print(
            f"Failed to fetch the webpage. Status code: {response.status_code}")
        return None

    # Initialize BeautifulSoup object
    soup = BeautifulSoup(html_content, 'html.parser')

    # Initialize the JSON object to hold the data
    poem_data = {}

    # Extract poem content
    zhengwen_id = f"zhengwen{poem_id}"
    zhengwen_div = soup.find('div', {'id': zhengwen_id})

    # Title, Author and Content
    poem_data["题目"] = zhengwen_div.h1.text.strip()
    author_info = zhengwen_div.p.text.strip().split("〔")
    poem_data["作者"] = {
        "姓名": author_info[0],
        "朝代": author_info[1].rstrip("〕"),
    }
    poem_data["诗句"] = zhengwen_div.find('div').text.strip()

    # Translation and Notes
    yiwen_div = soup.find('span', string="译文及注释")
    if not yiwen_div:
        yiwen_div = soup.find('span', string="注解及译文")

    if not yiwen_div:
        poem_data["译文"] = ""
        poem_data["注释"] = ""
    else:
        yishang_div = yiwen_div.find_parent(
            'div', {'class': 'contyishang'})
        yishang_ps = yishang_div.find_all('p')
        poem_data["译文"] = yishang_ps[0].text.strip().replace("译文", "")
        if len(yishang_ps) > 1:
            poem_data["注释"] = yishang_ps[1].text.strip()
        else:
            poem_data["注释"] = ""
        if poem_data["注释"].endswith("展开阅读全文 ∨"):
            poem_data["注释"] = poem_data["注释"][:poem_data["注释"].rfind("。")+1]

    # Appreciation
    shangxi_span = soup.find('span', string="赏析")
    if not shangxi_span:
        shangxi_span = soup.find('span', string="评析")
    if shangxi_span:
        shangxi_div = shangxi_span.find_parent('div')
        shangxi_content = [p.text.strip()
                           for p in shangxi_div.find_next_siblings('p')]
        poem_data["赏析"] = "\n".join(
            shangxi_content)
        if poem_data["赏析"].endswith("展开阅读全文 ∨"):
            poem_data["赏析"] = poem_data["赏析"][:poem_data["赏析"].rfind("。")+1]

    # Creation background
    chuangzuo_span = soup.find('span', string="创作背景")
    if chuangzuo_span:
        chuangzuo_div = chuangzuo_span.find_parent('div')
        chuangzuo_content = [p.text.strip()
                             for p in chuangzuo_div.find_next_siblings('p')]
        poem_data["创作背景"] = "\n".join(chuangzuo_content)

    # Author details
    poem_data["作者"]["介绍"] = ""
    zuozhe_parent_div = soup.find('div', {'class': 'sonspic'})
    if zuozhe_parent_div:
        zuozhe_div = zuozhe_parent_div.find(
            'div', {'class': 'cont'})
        for p in zuozhe_div.find_all('p'):
            poem_data["作者"]["介绍"] += p.text.strip()
        # 删除形如 "► 439篇诗文　► 585条名句" 的字符串
        poem_data["作者"]["介绍"] = re.sub(
            r"► \d+篇诗文　► \d+条名句", "", poem_data["作者"]["介绍"])

    return poem_data


def get_poems() -> list:

    poems = []

    with open(data_path, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 跳过标题行
        for row in reader:
            poem = {
                "序号": row[0],
                "题目": row[1],
                "作者": row[2],
                "类型": row[3],
                "链接": row[4]
            }
            poems.append(poem)

    return poems


def get_poem(offset=0):
    poems = get_poems()
    index = (datetime.today() - first_day).days + offset
    return poems[index]


def generate_xhs_note_with_emoji(poem_info):
    template = """{小红书[标题]}

📜《{题目}》 by {作者[姓名]} - {作者[朝代]}🌟
    
🍃 诗句 🍃
{诗句}

📚 译文 📚
{译文}

🔍 赏析 🔍
{小红书[赏析]}

💬 一言 💬
{小红书[一句话]}

#AI #AI画诗 #AI绘画 #AIGC #水墨画 {小红书[话题]}
"""

    # 对于多行文本进行缩进处理
    for key in ['译文', '注释']:
        poem_info[key] = poem_info[key].replace('\n', '\n  ')

    return template.format(**poem_info)


def daypoem(
    url: str = typer.Option(None, help="The URL of the poem to scrape."),
    xhs: bool = typer.Option(False, help="Generate an xiaohongshu note"),
    offset: int = typer.Option(
        0, help="The number of days to offset from today."),
    list: bool = typer.Option(False, help="List all diary information."),
):
    if list:
        table = PrettyTable()
        table.field_names = ["序号", "题目", "作者", "类型", "链接"]
        for poem in get_poems():
            table.add_row(
                [poem['序号'], poem['题目'], poem['作者'], poem['类型'], poem['链接']])
        print(table)
        return

    if not url:
        url = get_poem(offset=offset)["链接"]

    poem_info = parse_poem_info(url)

    xhs_content = ""
    if poem_info:
        print()
        print(json.dumps(poem_info, ensure_ascii=False, indent=4))

        if xhs:
            print("\n🚀 summarying ... \n")
            completion = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": summary_prompt},
                    {"role": "user", "content": json.dumps(
                        poem_info, ensure_ascii=False)}
                ]
            )

            xhs_dict = {
                "标题": "",
                "一句话": "",
                "赏析": "",
                "话题": ""
            }
            content_json = json.loads(completion.choices[0].message.content)
            if content_json:
                xhs_dict.update(content_json)

            poem_info["小红书"] = xhs_dict
            xhs_content = generate_xhs_note_with_emoji(poem_info)

            print(xhs_content)

            poem_info["小红书"]["文案"] = xhs_content

        min_days_offset = (first_day - datetime.today()).days
        days_offset = offset if offset >= min_days_offset else min_days_offset
        poem_date = datetime.today() + timedelta(days=days_offset)

        date_str = poem_date.strftime("%Y%m%d")
        dir_name = f'{date_str}《{poem_info["题目"]}》'
        dir_path = base_dir / dir_name
        if not dir_path.exists():
            dir_path.mkdir()
        file_path = dir_path / "小红书.txt"
        with file_path.open("w", encoding="utf-8") as f:
            f.write(xhs_content)
        poem_info_file_path = dir_path / "poem_info.json"
        json.dump(poem_info, poem_info_file_path.open(
            "w", encoding="utf-8"), indent=4, ensure_ascii=False)

        # 打开文件夹
        os.system(f"open {dir_path.as_uri()}")
        # poem_info echo 到系统剪切板
        pretty_poem_info = json.dumps(poem_info, ensure_ascii=False, indent=4)
        os.system(f"echo '{pretty_poem_info}' | pbcopy")

    else:
        print("Failed to fetch the webpage.")


def main():
    typer.run(daypoem)


if __name__ == "__main__":
    main()
