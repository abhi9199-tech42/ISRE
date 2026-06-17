import time
import os

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class ResourceMonitor:
    """
    Monitors system resources to support graceful degradation.
    Falls back to basic estimation if psutil is not available.
    Requirement 7.4, 7.5.
    """
    
    def __init__(self, memory_threshold_mb: float = 1000.0):
        self.memory_threshold = memory_threshold_mb
        self._process = None
        if HAS_PSUTIL:
            try:
                self._process = psutil.Process(os.getpid())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self._process = None

    def get_memory_usage(self) -> float:
        """Returns memory usage in MB."""
        if self._process:
            try:
                return self._process.memory_info().rss / (1024 * 1024)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        # Fallback: estimate based on Python's resource module
        try:
            import resource
            usage = resource.getrusage(resource.RUSAGE_SELF)
            return usage.ru_maxrss / 1024  # Convert KB to MB on Linux
        except (ImportError, AttributeError):
            # Windows fallback: return 0 (no memory tracking)
            return 0.0

    def is_resource_constrained(self) -> bool:
        return self.get_memory_usage() > self.memory_threshold

    def get_status(self) -> dict:
        return {
            "timestamp": time.time(),
            "memory_mb": self.get_memory_usage(),
            "constrained": self.is_resource_constrained(),
            "psutil_available": HAS_PSUTIL
        }
