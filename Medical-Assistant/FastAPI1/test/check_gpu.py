"""
GPU 环境验证脚本
用于检查 GPU 是否可用以及 PyTorch 是否正确配置了 CUDA 支持
"""
import sys
import torch


def check_gpu_environment():
    """检查 GPU 环境配置"""
    print("=" * 60)
    print("GPU 环境检查")
    print("=" * 60)
    
    # 检查 PyTorch 版本
    print(f"\n1. PyTorch 版本: {torch.__version__}")
    
    # 检查 CUDA 是否可用
    cuda_available = torch.cuda.is_available()
    print(f"2. CUDA 是否可用: {cuda_available}")
    
    if cuda_available:
        # 获取 CUDA 版本
        print(f"3. CUDA 版本: {torch.version.cuda}")
        
        # 获取 cuDNN 版本
        print(f"4. cuDNN 版本: {torch.backends.cudnn.version()}")
        
        # 获取 GPU 数量
        gpu_count = torch.cuda.device_count()
        print(f"5. 可用 GPU 数量: {gpu_count}")
        
        # 获取每个 GPU 的详细信息
        for i in range(gpu_count):
            print(f"\n6.{i+1} GPU {i} 信息:")
            print(f"   - 名称: {torch.cuda.get_device_name(i)}")
            print(f"   - 计算能力: {torch.cuda.get_device_capability(i)}")
            
            # 获取内存信息
            total_memory = torch.cuda.get_device_properties(i).total_mem / (1024**3)
            print(f"   - 总内存: {total_memory:.2f} GB")
        
        # 尝试在 GPU 上创建一个简单的张量
        try:
            x = torch.tensor([1.0, 2.0, 3.0]).cuda()
            print(f"\n7. GPU 张量测试: 成功 (张量值: {x})")
        except Exception as e:
            print(f"\n7. GPU 张量测试: 失败 - {e}")
            return False
            
    else:
        print("\n⚠️  警告: CUDA 不可用，将使用 CPU 运行")
        print("   可能的原因:")
        print("   - 没有安装 NVIDIA 驱动")
        print("   - 没有安装 CUDA Toolkit")
        print("   - PyTorch 不是 CUDA 版本")
        print("   - Docker 容器没有正确配置 GPU 访问")
        return False
    
    print("\n" + "=" * 60)
    print("✅ GPU 环境检查完成 - 一切正常!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = check_gpu_environment()
    sys.exit(0 if success else 1)
