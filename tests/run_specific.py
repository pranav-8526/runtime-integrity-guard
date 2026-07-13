import asyncio
from run_all_tests import run_test

async def main():
    await run_test("layer4_test_1", "layer4_test_1", "BLOCK", "T6_SemanticInjection")
    await run_test("layer4_test_2", "layer4_test_2", "BLOCK", "T6_SemanticInjection")
    await run_test("layer4_test_3", "layer4_test_3", "BLOCK", "T6_SemanticInjection")
    await run_test("layer4_rate_limit_mock", "layer4_rate_limit_mock", "ALLOW_DEGRADED", "T6_SemanticInjection")

if __name__ == "__main__":
    asyncio.run(main())
