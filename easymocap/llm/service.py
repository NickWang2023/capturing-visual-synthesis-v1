'''
  @ Date: 2026-07-03
  @ Author: 明哥升级版
  @ Description: LLM服务模块 - 大模型集成（修复版）
'''
import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# 配置日志
logger = logging.getLogger(__name__)

# 可选导入openai
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai库未安装，LLM功能将不可用。请运行: pip install openai")


class TaskComplexityLevel(Enum):
    """任务复杂度级别"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


@dataclass
class TaskComplexity:
    """任务复杂度分析结果"""
    level: TaskComplexityLevel
    estimated_time: int  # 秒
    recommended_gpu: str
    priority: int  # 1-10
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "estimated_time": self.estimated_time,
            "recommended_gpu": self.recommended_gpu,
            "priority": self.priority
        }


@dataclass
class LLMConfig:
    """LLM配置"""
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """从环境变量加载配置"""
        return cls(
            api_key=os.getenv('OPENAI_API_KEY', ''),
            base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
            model=os.getenv('LLM_MODEL', 'gpt-4'),
            temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('LLM_MAX_TOKENS', '2000')),
            timeout=int(os.getenv('LLM_TIMEOUT', '60'))
        )


class LLMService:
    """
    大语言模型服务
    
    提供智能算力调度、参数生成、错误诊断等功能
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        初始化LLM服务
        
        Args:
            config: LLM配置，如果不提供则从环境变量加载
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai库未安装，请运行: pip install openai")
        
        self.config = config or LLMConfig.from_env()
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout
        )
        logger.info(f"LLM服务初始化完成，使用模型: {self.config.model}")
    
    def analyze_task_complexity(self, video_info: Dict[str, Any]) -> TaskComplexity:
        """
        使用LLM分析任务复杂度
        
        Args:
            video_info: 视频信息字典
        
        Returns:
            TaskComplexity对象
        """
        prompt = f"""分析以下视频处理任务的复杂度：
        
视频信息：
- 时长: {video_info.get('duration', 'unknown')}秒
- 分辨率: {video_info.get('resolution', 'unknown')}
- 帧率: {video_info.get('fps', 'unknown')}fps
- 人物数量: {video_info.get('person_count', 'unknown')}
- 场景类型: {video_info.get('scene_type', 'unknown')}

请返回JSON格式：
{{
    "level": "simple|medium|complex",
    "estimated_time": 预估处理时间(秒),
    "recommended_gpu": "A10|A100|multi-A100",
    "priority": 优先级(1-10)
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "你是动作捕捉任务调度专家。请只返回JSON格式的结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return TaskComplexity(
                level=TaskComplexityLevel(result['level']),
                estimated_time=result['estimated_time'],
                recommended_gpu=result['recommended_gpu'],
                priority=result['priority']
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"LLM返回的JSON解析失败: {e}")
            return TaskComplexity(
                level=TaskComplexityLevel.MEDIUM,
                estimated_time=300,
                recommended_gpu="A100",
                priority=5
            )
        except Exception as e:
            logger.error(f"任务复杂度分析失败: {e}")
            raise RuntimeError(f"无法分析任务复杂度: {e}") from e
    
    def generate_parameters(self, task_type: str, video_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用LLM自动生成处理参数
        """
        prompt = f"""为{task_type}任务生成最优处理参数：

视频信息：{json.dumps(video_info, ensure_ascii=False, indent=2)}

请生成JSON格式的参数配置。"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "你是动作捕捉参数优化专家。请只返回JSON格式的结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"参数生成失败: {e}")
            raise RuntimeError(f"无法生成参数: {e}") from e
    
    def diagnose_error(self, error_log: str) -> Dict[str, str]:
        """
        使用LLM诊断错误并提供修复建议
        """
        prompt = f"""分析以下错误日志并提供修复建议：

```
{error_log}
```

请返回JSON格式：
{{
    "error_type": "错误类型",
    "root_cause": "根本原因",
    "solution": "修复方案",
    "prevention": "预防措施"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "你是技术故障诊断专家。请只返回JSON格式的结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"错误诊断失败: {e}")
            raise RuntimeError(f"无法诊断错误: {e}") from e
    
    def chat(self, user_message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        智能对话接口
        """
        system_prompt = """你是大模型支持下的动作捕捉与视觉合成系统的AI助手。

你可以帮助用户：
1. 上传视频并进行动作捕捉
2. 调整处理参数
3. 查看处理进度和结果
4. 解答技术问题

请用简洁专业的语言回答用户问题。"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            messages.extend(history)
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"对话失败: {e}")
            raise RuntimeError(f"无法生成回复: {e}") from e


# 全局LLM服务实例
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取全局LLM服务实例"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def init_llm_service(config: Optional[LLMConfig] = None) -> LLMService:
    """初始化全局LLM服务"""
    global _llm_service
    _llm_service = LLMService(config)
    return _llm_service
