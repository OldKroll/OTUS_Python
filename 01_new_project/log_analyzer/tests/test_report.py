import os

from src.log_analyzer import (
    _calculate_stat,
    _find_newest_log,
    _get_prepared_data,
    _write_report,
)

_config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "01_new_project/log_analyzer/src/reports",
    "LOG_DIR": "01_new_project/log_analyzer/src/log",
    "SCRIPT_LOG_FILE": None,
    "ERROR_RATE": 51,
}


def test_create_report() -> None:
    """test_create_report"""
    log = _find_newest_log(_config)
    assert log.filename == "nginx-access-ui.log-20170630.gz"
    raw_data = _get_prepared_data(log, _config)
    assert raw_data.total_urls_count == 2613659
    report = _calculate_stat(
        raw_data.total_urls_count,
        raw_data.total_request_time,
        raw_data.urls_stat,
        _config,
    )
    assert report[0]["time_avg"], 62.995
    _write_report(report, log, _config)
    assert f"report-{log.date}.html" in os.listdir(_config["REPORT_DIR"])
