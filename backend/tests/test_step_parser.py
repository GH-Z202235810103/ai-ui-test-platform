import pytest
import sys
sys.path.insert(0, 'backend')
from core.step_parser import StepParser, ParsedStep


class TestStepParser:
    def setup_method(self):
        self.parser = StepParser()
    
    def test_parse_open_url(self):
        result = self.parser.parse("打开https://www.baidu.com")
        assert result.operation == "open"
        assert result.params.get("url") == "https://www.baidu.com"
    
    def test_parse_open_with_keyword(self):
        result = self.parser.parse("打开百度")
        assert result.operation == "open"
        assert result.params.get("url") == "https://www.baidu.com"
    
    def test_parse_input(self):
        result = self.parser.parse("在搜索框中输入：人工智能")
        assert result.operation == "input"
        assert result.params.get("target") == "搜索框"
        assert result.params.get("value") == "人工智能"
    
    def test_parse_click(self):
        result = self.parser.parse("点击登录按钮")
        assert result.operation == "click"
        assert result.params.get("target") == "登录按钮"
    
    def test_parse_search(self):
        result = self.parser.parse("搜索\"Python教程\"")
        assert result.operation == "search"
        assert result.params.get("keyword") == "Python教程"
    
    def test_parse_verify(self):
        result = self.parser.parse("验证页面包含\"成功\"")
        assert result.operation == "verify"
        assert result.params.get("expected") == "成功"
    
    def test_parse_wait(self):
        result = self.parser.parse("等待3秒")
        assert result.operation == "wait"
        assert result.params.get("duration") == 3
    
    def test_parse_unknown(self):
        result = self.parser.parse("做一些未知操作")
        assert result.operation == "unknown"
    
    def test_parse_with_colon_variants(self):
        result1 = self.parser.parse("输入：测试内容")
        result2 = self.parser.parse("输入:测试内容")
        assert result1.operation == "input"
        assert result2.operation == "input"
