const { createApp } = Vue;

createApp({
    data() {
        return {
            nlpDescription: '',
            testcases: [],
            selectedTestCase: null,
            executionResult: null,
            apiBaseUrl: 'http://localhost:8000'
        };
    },
    mounted() {
        this.loadTestCases();
        // 添加示例数据
        if (this.testcases.length === 0) {
            this.testcases = [
                {
                    id: '1',
                    name: '百度搜索测试',
                    description: '测试百度搜索功能的完整流程',
                    steps: ['打开百度首页', '输入搜索关键词', '点击搜索按钮', '验证搜索结果'],
                    status: 'passed',
                    created_at: new Date().toISOString()
                },
                {
                    id: '2', 
                    name: '用户登录测试',
                    description: '测试用户登录的成功和失败场景',
                    steps: ['访问登录页面', '输入正确凭证', '点击登录按钮', '验证登录成功'],
                    status: 'pending',
                    created_at: new Date().toISOString()
                }
            ];
        }
    },
    methods: {
        async loadTestCases() {
            try {
                const response = await fetch(`${this.apiBaseUrl}/testcases`);
                if (response.ok) {
                    this.testcases = await response.json();
                }
            } catch (error) {
                console.error('加载测试用例失败:', error);
            }
        },
        async generateFromNLP() {
            if (!this.nlpDescription.trim()) {
                alert('请输入测试描述');
                return;
            }
            
            try {
                const response = await fetch(`${this.apiBaseUrl}/generate-from-nlp`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ description: this.nlpDescription })
                });
                
                const result = await response.json();
                if (result.success) {
                    const newTestCase = {
                        id: Date.now().toString(),
                        name: `AI生成: ${this.nlpDescription.substring(0, 20)}...`,
                        description: this.nlpDescription,
                        steps: result.generated_steps,
                        status: 'pending',
                        created_at: new Date().toISOString()
                    };
                    
                    this.testcases.push(newTestCase);
                    this.nlpDescription = '';
                    alert('测试用例生成成功！');
                }
            } catch (error) {
                console.error('AI生成失败:', error);
                alert('生成失败，请检查后端服务');
            }
        },
        selectTestCase(testcase) {
            this.selectedTestCase = testcase;
            this.executionResult = null;
        },
        getStatusClass(status) {
            return `status-${status}`;
        },
        getStatusBadgeClass(status) {
            return `badge-${status}`;
        },
        async executeSingleTest() {
            if (!this.selectedTestCase) return;
            
            try {
                const response = await fetch(`${this.apiBaseUrl}/execute`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        testcase_id: this.selectedTestCase.id,
                        browser: 'chromium',
                        headless: false
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    this.selectedTestCase.status = 'running';
                    
                    // 模拟获取报告
                    setTimeout(async () => {
                        const reportResponse = await fetch(`${this.apiBaseUrl}/report/${result.execution_id}`);
                        const report = await reportResponse.json();
                        
                        this.executionResult = report;
                        this.selectedTestCase.status = report.status;
                    }, 2000);
                }
            } catch (error) {
                console.error('执行测试失败:', error);
            }
        },
        async runAllTests() {
            if (confirm('确定要执行所有测试用例吗？')) {
                alert('开始执行所有测试...（模拟功能）');
                // 这里可以遍历执行所有测试用例
            }
        },
        openRecorder() {
            alert('智能录制回放功能需要启动专门的录制服务');
            // 这里可以打开新的窗口或调用录制API
        }
    }
}).mount('#app');