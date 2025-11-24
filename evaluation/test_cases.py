"""
Test cases for business analytics agent evaluation.

Defines test scenarios with expected outcomes for automated testing.
"""

import os

# Base directory for test data
TEST_DATA_DIR = "data"


# Test case definitions
TEST_CASES = [
    {
        "name": "normal_operations",
        "description": "Baseline test with one anomaly",
        "csv_file": os.path.join(TEST_DATA_DIR, "sample_business_metrics.csv"),
        "expected_anomalies": 1,
        "expected_recommendations_min": 3,
        "expected_severity": "HIGH",
        "threshold": 0.85  # Minimum score to pass
    },
    {
        "name": "no_anomalies",
        "description": "Normal metrics without anomalies",
        "csv_file": os.path.join(TEST_DATA_DIR, "normal_metrics.csv"),
        "expected_anomalies": 0,
        "expected_recommendations_min": 1,  # Still generate baseline recommendations
        "expected_severity": "LOW",
        "threshold": 0.90  # Higher threshold for simpler case
    },
    {
        "name": "multiple_anomalies",
        "description": "Volatile metrics with multiple anomalies",
        "csv_file": os.path.join(TEST_DATA_DIR, "volatile_metrics.csv"),
        "expected_anomalies": 2,  # At least 2
        "expected_recommendations_min": 4,
        "expected_severity": "HIGH",
        "threshold": 0.82  # Slightly lower for complex case
    }
]


# Edge case definitions
EDGE_CASES = [
    {
        "name": "empty_csv",
        "description": "Empty CSV file",
        "csv_content": "date,revenue,costs,customers\n",
        "expected_error": True,
        "error_type": "data_loading_error"
    },
    {
        "name": "missing_columns",
        "description": "CSV with missing required columns",
        "csv_content": "date,revenue\n2024-01-01,50000\n",
        "expected_error": True,
        "error_type": "validation_error"
    },
    {
        "name": "invalid_data_types",
        "description": "Non-numeric values in numeric columns",
        "csv_content": "date,revenue,costs,customers\n2024-01-01,invalid,30000,150\n",
        "expected_error": True,
        "error_type": "data_type_error"
    }
]


def get_test_case(name: str):
    """Get test case by name."""
    for test_case in TEST_CASES:
        if test_case["name"] == name:
            return test_case
    return None


def get_all_test_case_names():
    """Get list of all test case names."""
    return [tc["name"] for tc in TEST_CASES]
