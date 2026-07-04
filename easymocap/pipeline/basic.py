'''
  @ Date: 2026-07-03
  @ Author: 明哥升级版
  @ Description: 升级后的 pipeline/basic.py - 添加类型注解、错误处理和大模型集成
'''
from typing import Optional, Dict, Any, Tuple
import numpy as np
import logging

from ..pyfitting import optimizeShape, optimizePose2D, optimizePose3D
from ..mytools import Timer
from ..dataset import CONFIG
from .weight import load_weight_pose, load_weight_shape
from .config import Config
from ..logging_config import setup_logging, get_logger

# 配置日志
setup_logging()
logger = get_logger(__name__)

# 可选导入LLM和VLM模块
try:
    from ..llm import LLMService, get_llm_service
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.debug("LLM模块不可用")

try:
    from ..vlm import VLMService, get_vlm_service
    VLM_AVAILABLE = True
except ImportError:
    VLM_AVAILABLE = False
    logger.debug("VLM模块不可用")

try:
    from ..performance import PerformanceOptimizer, CacheManager
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False
    logger.debug("性能优化模块不可用")


def multi_stage_optimize(
    body_model: Any,
    params: Dict[str, Any],
    kp3ds: np.ndarray,
    kp2ds: Optional[np.ndarray] = None,
    bboxes: Optional[np.ndarray] = None,
    Pall: Optional[np.ndarray] = None,
    weight: Optional[Dict[str, float]] = None,
    cfg: Optional[Any] = None
) -> Dict[str, Any]:
    """
    多阶段优化流程
    
    Args:
        body_model: SMPL/SMPL-X人体模型
        params: 模型参数字典
        kp3ds: 3D关键点，形状为 (nFrames, nJoints, 3+)
        kp2ds: 2D关键点，形状为 (nFrames, nViews, nJoints, 3)，可选
        bboxes: 边界框，形状为 (nFrames, nViews, 5)，可选
        Pall: 投影矩阵，可选
        weight: 损失权重字典
        cfg: 配置对象
    
    Returns:
        优化后的参数字典
    
    Raises:
        ValueError: 输入数据格式错误
        RuntimeError: 优化失败
    """
    if weight is None:
        weight = {}
    
    if cfg is None:
        raise ValueError("配置对象 cfg 不能为空")
    
    try:
        # 阶段1: 优化全局旋转和平移
        with Timer('Optimize global RT'):
            cfg.OPT_R = True
            cfg.OPT_T = True
            # 禁用smooth_body以避免与k3d数据项冲突
            saved_smooth_body = weight.get('smooth_body', 0.)
            weight['smooth_body'] = 0.
            params = optimizePose3D(body_model, params, kp3ds, weight=weight, cfg=cfg)
            weight['smooth_body'] = saved_smooth_body
        
        # 阶段2: 优化3D姿态
        with Timer(f'Optimize 3D Pose/{kp3ds.shape[0]} frames'):
            cfg.OPT_POSE = True
            cfg.ROBUST_3D = False
            params = optimizePose3D(body_model, params, kp3ds, weight=weight, cfg=cfg)
            
            # 可选：启用鲁棒3D优化
            # if cfg.get('robust_3d', False):
            #     cfg.ROBUST_3D = True
            #     params = optimizePose3D(body_model, params, kp3ds, weight=weight, cfg=cfg)
            
            # 优化手部（SMPLH/SMPLX）
            if cfg.model in ['smplh', 'smplx']:
                cfg.OPT_HAND = True
                params = optimizePose3D(body_model, params, kp3ds, weight=weight, cfg=cfg)
            
            # 优化表情（SMPLX）
            if cfg.model == 'smplx':
                cfg.OPT_EXPR = True
                params = optimizePose3D(body_model, params, kp3ds, weight=weight, cfg=cfg)
        
        # 阶段3: 优化2D姿态（如果有2D数据）
        if kp2ds is not None and bboxes is not None:
            with Timer(f'Optimize 2D Pose/{kp3ds.shape[0]} frames'):
                # bboxes => (nFrames, nViews, 5), keypoints2d => (nFrames, nViews, nJoints, 3)
                params = optimizePose2D(body_model, params, bboxes, kp2ds, Pall, weight=weight, cfg=cfg)
        
        return params
        
    except Exception as e:
        logger.error(f"多阶段优化失败: {e}")
        raise RuntimeError(f"优化过程出错: {e}") from e


def multi_stage_optimize2d(
    body_model: Any,
    params: Dict[str, Any],
    kp2ds: np.ndarray,
    bboxes: np.ndarray,
    Pall: np.ndarray,
    weight: Optional[Dict[str, float]] = None,
    args: Optional[Any] = None
) -> Dict[str, Any]:
    """
    仅使用2D数据的多阶段优化
    
    Args:
        body_model: 人体模型
        params: 模型参数
        kp2ds: 2D关键点
        bboxes: 边界框
        Pall: 投影矩阵
        weight: 损失权重
        args: 命令行参数
    
    Returns:
        优化后的参数
    """
    if weight is None:
        weight = {}
    
    cfg = Config(args)
    cfg.device = body_model.device
    cfg.model = body_model.model_type
    
    try:
        # 阶段1: 优化全局旋转和平移
        with Timer('Optimize global RT'):
            cfg.OPT_R = True
            cfg.OPT_T = True
            saved_smooth_body = weight.get('smooth_body', 0.)
            weight['smooth_body'] = 0.
            params = optimizePose2D(body_model, params, bboxes, kp2ds, Pall, weight=weight, cfg=cfg)
            weight['smooth_body'] = saved_smooth_body
        
        # 阶段2: 优化2D姿态和形状
        with Timer(f'Optimize 2D Pose/{kp2ds.shape[0]} frames'):
            cfg.OPT_POSE = True
            cfg.OPT_SHAPE = True
            params = optimizePose2D(body_model, params, bboxes, kp2ds, Pall, weight=weight, cfg=cfg)
        
        return params
        
    except Exception as e:
        logger.error(f"2D优化失败: {e}")
        raise RuntimeError(f"2D优化过程出错: {e}") from e


def smpl_from_keypoints3d2d(
    body_model: Any,
    kp3ds: np.ndarray,
    kp2ds: np.ndarray,
    bboxes: np.ndarray,
    Pall: np.ndarray,
    config: Dict[str, Any],
    args: Any,
    weight_shape: Optional[Dict[str, float]] = None,
    weight_pose: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    从3D和2D关键点拟合SMPL模型
    
    Args:
        body_model: SMPL/SMPL-X模型
        kp3ds: 3D关键点
        kp2ds: 2D关键点
        bboxes: 边界框
        Pall: 投影矩阵
        config: 数据集配置
        args: 命令行参数
        weight_shape: 形状优化权重
        weight_pose: 姿态优化权重
    
    Returns:
        拟合后的SMPL参数
    """
    model_type = body_model.model_type
    params_init = body_model.init_params(nFrames=1)
    
    # 加载形状权重
    if weight_shape is None:
        weight_shape = load_weight_shape(model_type, args.opts)
    
    try:
        # 优化形状
        if model_type in ['smpl', 'smplh', 'smplx']:
            # 使用前14个肢体优化形状（不使用nose, neck）
            params_shape = optimizeShape(
                body_model, params_init, kp3ds,
                weight_loss=weight_shape,
                kintree=CONFIG['body15']['kintree'][1:]
            )
        else:
            params_shape = optimizeShape(
                body_model, params_init, kp3ds,
                weight_loss=weight_shape,
                kintree=config['kintree']
            )
        
        # 初始化姿态参数
        cfg = Config(args)
        cfg.device = body_model.device
        params = body_model.init_params(nFrames=kp3ds.shape[0])
        params['shapes'] = params_shape['shapes'].copy()
        
        # 加载姿态权重
        if weight_pose is None:
            weight_pose = load_weight_pose(model_type, args.opts)
        
        # 多阶段优化
        params = multi_stage_optimize(
            body_model, params, kp3ds, kp2ds, bboxes, Pall, weight_pose, cfg
        )
        
        return params
        
    except Exception as e:
        logger.error(f"SMPL拟合失败: {e}")
        raise RuntimeError(f"SMPL拟合过程出错: {e}") from e


def smpl_from_keypoints3d(
    body_model: Any,
    kp3ds: np.ndarray,
    config: Dict[str, Any],
    args: Any,
    weight_shape: Optional[Dict[str, float]] = None,
    weight_pose: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    仅从3D关键点拟合SMPL模型
    
    Args:
        body_model: SMPL/SMPL-X模型
        kp3ds: 3D关键点
        config: 数据集配置
        args: 命令行参数
        weight_shape: 形状优化权重
        weight_pose: 姿态优化权重
    
    Returns:
        拟合后的SMPL参数
    """
    model_type = body_model.model_type
    params_init = body_model.init_params(nFrames=1)
    
    # 加载形状权重
    if weight_shape is None:
        weight_shape = load_weight_shape(model_type, args.opts)
    
    try:
        # 优化形状
        if model_type in ['smpl', 'smplh', 'smplx']:
            params_shape = optimizeShape(
                body_model, params_init, kp3ds,
                weight_loss=weight_shape,
                kintree=CONFIG['body15']['kintree'][1:]
            )
        else:
            params_shape = optimizeShape(
                body_model, params_init, kp3ds,
                weight_loss=weight_shape,
                kintree=config['kintree']
            )
        
        # 初始化姿态参数
        cfg = Config(args)
        cfg.device = body_model.device
        cfg.model_type = model_type
        params = body_model.init_params(nFrames=kp3ds.shape[0])
        params['shapes'] = params_shape['shapes'].copy()
        
        # 加载姿态权重
        if weight_pose is None:
            weight_pose = load_weight_pose(model_type, args.opts)
        
        # 多阶段优化（仅3D）
        params = multi_stage_optimize(
            body_model, params, kp3ds, None, None, None, weight_pose, cfg
        )
        
        return params
        
    except Exception as e:
        logger.error(f"SMPL拟合失败: {e}")
        raise RuntimeError(f"SMPL拟合过程出错: {e}") from e
