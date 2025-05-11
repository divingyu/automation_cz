import logging
def pytest_runtest_makereport(item, call):
    # 获取测试阶段的日志内容
    if call.when == 'call':
        logs = []
        for handler in logging.getLogger().handlers:
            if hasattr(handler, 'captured_logs'):
                logs.extend(handler.captured_logs)
        
        # 将日志添加到 HTML 报告的额外信息中
        if logs:
            report = item._report
            report.sections.append(("Logs", "\n".join(logs)))