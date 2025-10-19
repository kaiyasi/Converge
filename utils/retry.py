"""
重試與錯誤恢復機制
- 指數退避重試
- Circuit Breaker 模式
- 錯誤恢復策略
"""
import time
import asyncio
import functools
from typing import Callable, Optional, Tuple, Type, Union
from enum import Enum
from utils.logger import get_logger

logger = get_logger(__name__)


class CircuitState(Enum):
    """斷路器狀態"""
    CLOSED = "closed"      # 正常狀態
    OPEN = "open"          # 斷開狀態
    HALF_OPEN = "half_open"  # 半開狀態


class CircuitBreaker:
    """斷路器模式實現"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        """
        初始化斷路器

        Args:
            failure_threshold: 失敗閾值
            recovery_timeout: 恢復超時時間 (秒)
            expected_exception: 預期的異常類型
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs):
        """
        通過斷路器調用函數

        Args:
            func: 要調用的函數
            *args: 位置參數
            **kwargs: 關鍵字參數

        Returns:
            函數返回值

        Raises:
            Exception: 當斷路器打開時拋出異常
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("斷路器進入半開狀態")
            else:
                raise Exception("斷路器已打開,拒絕請求")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    async def call_async(self, func: Callable, *args, **kwargs):
        """異步版本的斷路器調用"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("斷路器進入半開狀態")
            else:
                raise Exception("斷路器已打開,拒絕請求")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """檢查是否應該嘗試重置"""
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.recovery_timeout

    def _on_success(self):
        """成功時的處理"""
        if self.state == CircuitState.HALF_OPEN:
            logger.info("斷路器恢復正常")
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """失敗時的處理"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"斷路器已打開 (失敗次數: {self.failure_count})")

    def reset(self):
        """手動重置斷路器"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        logger.info("斷路器已手動重置")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    指數退避重試裝飾器

    Args:
        max_retries: 最大重試次數
        base_delay: 基礎延遲時間 (秒)
        max_delay: 最大延遲時間 (秒)
        exponential_base: 指數基數
        exceptions: 需要重試的異常類型
        on_retry: 重試時的回調函數

    Returns:
        裝飾器函數
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"重試失敗,已達最大次數 {max_retries}: {e}")
                        raise

                    delay = min(base_delay * (exponential_base ** (retries - 1)), max_delay)
                    logger.warning(f"執行失敗,{delay:.2f}秒後重試 ({retries}/{max_retries}): {e}")

                    if on_retry:
                        on_retry(retries, e)

                    time.sleep(delay)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"重試失敗,已達最大次數 {max_retries}: {e}")
                        raise

                    delay = min(base_delay * (exponential_base ** (retries - 1)), max_delay)
                    logger.warning(f"執行失敗,{delay:.2f}秒後重試 ({retries}/{max_retries}): {e}")

                    if on_retry:
                        on_retry(retries, e)

                    await asyncio.sleep(delay)

        # 判斷是否為異步函數
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


class ReconnectManager:
    """重連管理器"""

    def __init__(
        self,
        max_retries: int = 5,
        base_delay: float = 2.0,
        max_delay: float = 300.0
    ):
        """
        初始化重連管理器

        Args:
            max_retries: 最大重試次數 (0 表示無限重試)
            base_delay: 基礎延遲時間
            max_delay: 最大延遲時間
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retry_count = 0
        self.is_connected = False

    async def connect(
        self,
        connect_func: Callable,
        *args,
        **kwargs
    ) -> bool:
        """
        嘗試連接

        Args:
            connect_func: 連接函數
            *args: 位置參數
            **kwargs: 關鍵字參數

        Returns:
            是否連接成功
        """
        while self.max_retries == 0 or self.retry_count < self.max_retries:
            try:
                logger.info(f"嘗試連接... (第 {self.retry_count + 1} 次)")
                await connect_func(*args, **kwargs)
                self.is_connected = True
                self.retry_count = 0
                logger.info("連接成功")
                return True

            except Exception as e:
                self.retry_count += 1
                self.is_connected = False

                if self.max_retries > 0 and self.retry_count >= self.max_retries:
                    logger.error(f"連接失敗,已達最大重試次數: {e}")
                    return False

                delay = min(
                    self.base_delay * (2 ** (self.retry_count - 1)),
                    self.max_delay
                )
                logger.warning(f"連接失敗,{delay:.2f}秒後重試: {e}")
                await asyncio.sleep(delay)

        return False

    def reset(self):
        """重置重連狀態"""
        self.retry_count = 0
        self.is_connected = False


# 使用範例
if __name__ == '__main__':
    # 測試指數退避重試
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def unstable_function():
        import random
        if random.random() < 0.7:
            raise ConnectionError("連接失敗")
        return "成功"

    try:
        result = unstable_function()
        print(f"結果: {result}")
    except Exception as e:
        print(f"最終失敗: {e}")

    # 測試斷路器
    breaker = CircuitBreaker(failure_threshold=3)

    def failing_function():
        raise ValueError("測試錯誤")

    for i in range(10):
        try:
            breaker.call(failing_function)
        except Exception as e:
            print(f"調用 {i+1}: {e}, 斷路器狀態: {breaker.state.value}")
        time.sleep(1)
