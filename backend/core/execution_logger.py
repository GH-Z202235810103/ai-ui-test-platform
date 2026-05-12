from datetime import datetime
from typing import List, Optional


class ExecutionLogger:
    LEVELS = {
        'minimal': 0,
        'normal': 1,
        'verbose': 2,
        'debug': 3,
    }
    
    def __init__(self, headless: bool = False, level: str = 'normal'):
        self.headless = headless
        self.level = self.LEVELS.get(level, 1)
        self._logs: List[str] = []
        self._start_time = datetime.now()
    
    def log(self, message: str, category: str = 'info', importance: int = 1) -> None:
        effective_level = 0 if self.headless else self.level
        
        if importance <= effective_level:
            entry = self._format_entry(message, category)
            self._logs.append(entry)
            print(entry)
    
    def log_screenshot(self, name: str, action: str) -> None:
        if self.headless:
            return
        self.log(f"截图: {name} ({action})", category='screenshot', importance=1)
    
    def log_element_located(self, by: str, value: str) -> None:
        if self.headless:
            return
        self.log(f"元素定位: {by}={value}", category='element', importance=2)
    
    def log_step(self, step_num: int, step_desc: str) -> None:
        self.log(f"步骤 {step_num}: {step_desc}", category='step', importance=0)
    
    def log_success(self, message: str) -> None:
        self.log(f"[OK] {message}", category='success', importance=0)

    def log_error(self, message: str) -> None:
        self.log(f"[ERROR] {message}", category='error', importance=0)

    def log_warning(self, message: str) -> None:
        self.log(f"[WARNING] {message}", category='warning', importance=0)
    
    def get_logs(self) -> List[str]:
        return self._logs.copy()
    
    def clear(self) -> None:
        self._logs.clear()
    
    def get_duration(self) -> str:
        duration = datetime.now() - self._start_time
        return str(duration).split('.')[0]
    
    def _format_entry(self, message: str, category: str) -> str:
        timestamp = datetime.now().strftime('%H:%M:%S')
        return f"[{timestamp}] [{category}] {message}"
