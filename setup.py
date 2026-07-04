'''
  @ Date: 2026-07-03
  @ Author: 明哥升级版
  @ Description: 升级后的 setup.py - 版本号更新 + 完善依赖
'''
from setuptools import setup, find_packages

# 读取 README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 核心依赖（避免读取requirements.txt导致的CI问题）
core_requirements = [
    'numpy>=1.24.0',
    'scipy>=1.11.0',
    'opencv-python>=4.8.0',
    'torch>=2.1.0',
    'torchvision>=0.16.0',
    'tqdm>=4.66.0',
    'pyyaml>=6.0.1',
    'yacs>=0.1.8',
    'tabulate>=0.9.0',
    'termcolor>=2.3.0',
    'setuptools>=69.0.0',
]

setup(
    name='easymocap',
    version='1.0.0',  # ✅ 升级版本号
    author='Qing Shuai',
    author_email='s_q@zju.edu.cn',
    description='Easy Human Motion Capture Toolbox - 大模型支持下的动作捕捉与视觉合成系统',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/zju3dv/EasyMocap',
    packages=find_packages(exclude=['tests', 'tests.*']),
    python_requires='>=3.10',
    install_requires=core_requirements,
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.7.0',
            'flake8>=6.1.0',
            'mypy>=1.5.0',
            'isort>=5.12.0',
        ],
        'llm': [
            'openai>=1.3.0',
            'anthropic>=0.18.0',
            'langchain>=0.1.0',
            'tiktoken>=0.5.0',
        ],
        'vlm': [
            'segment-anything>=1.0',
            'groundingdino-py>=0.1.0',
            'transformers>=4.35.0',
        ],
        'aigc': [
            'diffusers>=0.24.0',
            'controlnet-aux>=0.0.7',
            'xformers>=0.0.23',
        ],
    },
    entry_points={
        'console_scripts': [
            'emc=apps.mocap.run:main_entrypoint',
            'mocap-server=apps.api.server:main',  # ✅ 新增API服务器入口
            'mocap-llm=easymocap.llm.cli:main',    # ✅ 新增LLM CLI入口
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Image Recognition',
    ],
)
