import time
from dataclasses import dataclass
from typing import Any, Callable, Optional
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException,
    ElementNotInteractableException, StaleElementReferenceException
)


RETRYABLE_EXCEPTIONS = (
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    Exception,
)


@dataclass
class RetryResult:
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    attempts: int = 0


class RetryStrategy:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, backoff: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff = backoff
    
    def execute_with_retry(self, action: Callable, action_name: str = "操作") -> RetryResult:
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = action()
                return RetryResult(
                    success=True,
                    result=result,
                    attempts=attempt + 1
                )
            except RETRYABLE_EXCEPTIONS as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (self.backoff ** attempt)
                    time.sleep(delay)
        
        return RetryResult(
            success=False,
            error=last_error,
            attempts=self.max_retries
        )
    
    def execute_with_specific_exceptions(self, action: Callable, exceptions: tuple, action_name: str = "操作") -> RetryResult:
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = action()
                return RetryResult(
                    success=True,
                    result=result,
                    attempts=attempt + 1
                )
            except exceptions as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (self.backoff ** attempt)
                    time.sleep(delay)
        
        return RetryResult(
            success=False,
            error=last_error,
            attempts=self.max_retries
        )
