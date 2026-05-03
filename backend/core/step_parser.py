import re
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Callable


@dataclass
class ParsedStep:
    raw: str
    operation: str
    params: Dict = field(default_factory=dict)
    target: Optional[str] = None
    value: Optional[str] = None


class StepParser:
    OPERATIONS: Dict[str, List[str]] = {
        'open': ['打开', '访问', 'goto', 'navigate'],
        'input': ['输入', '填写', 'type', 'enter'],
        'click': ['点击', 'click', 'press'],
        'search': ['搜索', 'search'],
        'verify': ['验证', '检查', 'verify', 'assert'],
        'wait': ['等待', 'wait'],
        'scroll': ['滚动', 'scroll'],
        'hover': ['悬停', 'hover'],
    }
    
    URL_ALIASES = {
        '百度': 'https://www.baidu.com',
        '淘宝': 'https://www.taobao.com',
        '京东': 'https://www.jd.com',
        'b站': 'https://www.bilibili.com',
        'bilibili': 'https://www.bilibili.com',
    }
    
    def __init__(self):
        self._extractors: Dict[str, Callable] = {
            'open': self._extract_url,
            'input': self._extract_input_content,
            'click': self._extract_click_target,
            'search': self._extract_search_keyword,
            'verify': self._extract_verify_content,
            'wait': self._extract_wait_duration,
            'scroll': self._extract_scroll_params,
            'hover': self._extract_hover_target,
        }
    
    def parse(self, step: str) -> ParsedStep:
        operation = self._detect_operation(step)
        params = self._extract_params(step, operation)
        return ParsedStep(
            raw=step,
            operation=operation,
            params=params,
            target=params.get('target'),
            value=params.get('value'),
        )
    
    def _detect_operation(self, step: str) -> str:
        step_lower = step.lower()
        for op, keywords in self.OPERATIONS.items():
            for keyword in keywords:
                if keyword in step_lower or keyword in step:
                    return op
        return 'unknown'
    
    def _extract_params(self, step: str, operation: str) -> Dict:
        extractor = self._extractors.get(operation, lambda s: {})
        return extractor(step)
    
    def _extract_url(self, step: str) -> Dict:
        url_match = re.search(r'https?://[^\s]+', step)
        if url_match:
            return {'url': url_match.group()}
        
        for alias, url in self.URL_ALIASES.items():
            if alias in step.lower():
                return {'url': url}
        
        return {'url': ''}
    
    def _extract_input_content(self, step: str) -> Dict:
        patterns = [
            r'在(.+?)中输入[：:]\s*(.+)',
            r'输入[：:]\s*(.+)',
            r'填写[：:]\s*(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, step)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    return {'target': groups[0].strip(), 'value': groups[1].strip()}
                elif len(groups) == 1:
                    return {'target': 'default', 'value': groups[0].strip()}
        
        quoted = re.search(r'["\']([^"\']+)["\']', step)
        if quoted:
            return {'target': 'default', 'value': quoted.group(1)}
        
        return {'target': 'default', 'value': ''}
    
    def _extract_click_target(self, step: str) -> Dict:
        patterns = [
            r'点击["\']?([^"\']+)["\']?',
            r'click\s+["\']?([^"\']+)["\']?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, step, re.IGNORECASE)
            if match:
                target = match.group(1).strip()
                return {'target': target}
        
        return {'target': ''}
    
    def _extract_search_keyword(self, step: str) -> Dict:
        patterns = [
            r'搜索["\']([^"\']+)["\']',
            r'搜索[：:]\s*(.+)',
            r'search\s+["\']?([^"\']+)["\']?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, step, re.IGNORECASE)
            if match:
                return {'keyword': match.group(1).strip()}
        
        return {'keyword': ''}
    
    def _extract_verify_content(self, step: str) -> Dict:
        patterns = [
            r'验证.*?包含["\']?([^"\']+)["\']?',
            r'检查.*?包含["\']?([^"\']+)["\']?',
            r'验证[：:]\s*(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, step)
            if match:
                return {'expected': match.group(1).strip()}
        
        return {'expected': ''}
    
    def _extract_wait_duration(self, step: str) -> Dict:
        match = re.search(r'等待(\d+)秒?', step)
        if match:
            return {'duration': int(match.group(1))}
        return {'duration': 1}
    
    def _extract_scroll_params(self, step: str) -> Dict:
        direction = 'down'
        if '上' in step or 'top' in step.lower():
            direction = 'up'
        elif '下' in step or 'bottom' in step.lower():
            direction = 'down'
        return {'direction': direction}
    
    def _extract_hover_target(self, step: str) -> Dict:
        match = re.search(r'悬停[于在]?["\']?([^"\']+)["\']?', step)
        if match:
            return {'target': match.group(1).strip()}
        return {'target': ''}
