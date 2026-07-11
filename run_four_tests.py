import sys
import run_all_tests
import asyncio

four_tests = [
    t for t in run_all_tests.tests if t[0] in [
        "layer4_test_1",
        "layer4_test_2",
        "layer4_test_3",
        "layer4_rate_limit_mock"
    ]
]
run_all_tests.tests = four_tests

if __name__ == "__main__":
    asyncio.run(run_all_tests.main())
