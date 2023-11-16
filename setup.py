from setuptools import setup, find_packages

setup(
    name='daypoem',  # 项目名称
    version='1.0.0',  # 项目版本
    packages=find_packages(),  # 自动查找项目中的包
    include_package_data=True,
    install_requires=[
        'typer',         # 用于创建命令行接口
        'openai',        # 用于访问 OpenAI 相关服务
        'requests',      # 用于发送 HTTP 请求
        'beautifulsoup4',  # 用于解析 HTML 和 XML 文件
        'python-dotenv',  # 用于加载 .env 文件中的环境变量
        'prettytable',   # 用于创建格式化的表格输出
    ],
    entry_points={
        'console_scripts': [
            'daypoem=daypoem.main:main',  # "daypoem" 是命令行工具的名称
        ],
    }
)
