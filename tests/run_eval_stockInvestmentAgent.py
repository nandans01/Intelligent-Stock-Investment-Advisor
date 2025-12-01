"""
Evaluation Runner for Stock Investment Agent
Runs the agent against the evaluation set and reports results
"""
import asyncio
import json
from datetime import datetime
from typing import List, Dict
import sys
import os

# Add the parent directory to the Python path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_investment_advisor.stockInvestmentAgent import root_agent
from google.adk.runners import InMemoryRunner
from google.adk.plugins.logging_plugin import (
    LoggingPlugin,
)
from eval_set_stockInvestmentAgent import (
    EVAL_SET,
    validate_response,
    get_eval_set_by_category,
    get_eval_set_statistics
)


class EvalRunner:
    """Runner for evaluating the Stock Investment Agent"""

    def __init__(self, agent, verbose: bool = True):
        self.agent = agent
        self.verbose = verbose
        self.results = []

    async def run_single_eval(self, test_case: dict) -> dict:
        """Run a single evaluation test case"""
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"Running Test: {test_case['id']} - {test_case['category']}")
            print(f"Input: {test_case['input']}")
            print(f"{'='*70}")

        try:
            runner = InMemoryRunner(agent=self.agent,
                                    plugins=[LoggingPlugin()])
            response = await runner.run_debug(test_case['input'])

            # Convert response to string if needed
            response_str = str(response)

            if self.verbose:
                print(f"\nResponse (first 500 chars):")
                print(f"{response_str[:500]}...")

            # Validate response
            validation_result = validate_response(response_str, test_case)
            validation_result["response"] = response_str
            validation_result["timestamp"] = datetime.now().isoformat()

            if self.verbose:
                status = "✓ PASSED" if validation_result["passed"] else "✗ FAILED"
                print(f"\nStatus: {status}")
                if not validation_result["passed"]:
                    print(f"Failed Criteria:")
                    for criterion in validation_result["failed_criteria"]:
                        print(f"  - {criterion}")

            return validation_result

        except Exception as e:
            error_result = {
                "test_id": test_case["id"],
                "category": test_case["category"],
                "input": test_case["input"],
                "passed": False,
                "failed_criteria": [f"Exception: {type(e).__name__}: {str(e)}"],
                "details": {"error": str(e)},
                "response": None,
                "timestamp": datetime.now().isoformat()
            }

            if self.verbose:
                print(f"\n✗ ERROR: {type(e).__name__}: {str(e)}")

            return error_result

    async def run_eval_set(self, test_cases: List[dict] = None, max_tests: int = None):
        """
        Run evaluation on a set of test cases

        Args:
            test_cases: List of test cases (defaults to full EVAL_SET)
            max_tests: Maximum number of tests to run (None = all)
        """
        if test_cases is None:
            test_cases = EVAL_SET

        if max_tests is not None:
            test_cases = test_cases[:max_tests]

        print("\n" + "="*70)
        print("STOCK INVESTMENT AGENT - EVALUATION RUN")
        print("="*70)
        print(f"Total tests to run: {len(test_cases)}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        self.results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] Processing {test_case['id']}...")
            result = await self.run_single_eval(test_case)
            self.results.append(result)

            # Brief pause between tests to avoid rate limits
            if i < len(test_cases):
                await asyncio.sleep(2)

        self._print_summary()
        return self.results

    def _print_summary(self):
        """Print summary of evaluation results"""
        print("\n" + "="*70)
        print("EVALUATION SUMMARY")
        print("="*70)

        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0

        print(f"\nOverall Results:")
        print(f"  Total Tests: {total}")
        print(f"  Passed: {passed} ({pass_rate:.1f}%)")
        print(f"  Failed: {failed} ({100-pass_rate:.1f}%)")

        # Breakdown by category
        category_stats = {}
        for result in self.results:
            cat = result["category"]
            if cat not in category_stats:
                category_stats[cat] = {"passed": 0, "failed": 0}
            if result["passed"]:
                category_stats[cat]["passed"] += 1
            else:
                category_stats[cat]["failed"] += 1

        print("\nResults by Category:")
        for category, stats in sorted(category_stats.items()):
            total_cat = stats["passed"] + stats["failed"]
            pass_rate_cat = (stats["passed"] / total_cat * 100) if total_cat > 0 else 0
            print(f"  {category}: {stats['passed']}/{total_cat} passed ({pass_rate_cat:.1f}%)")

        # Show failed tests
        if failed > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if not result["passed"]:
                    print(f"  ✗ {result['test_id']} - {result['category']}")
                    print(f"    Input: {result['input']}")
                    for criterion in result["failed_criteria"]:
                        print(f"      - {criterion}")

        print("\n" + "="*70)

    def save_results(self, filename: str = None):
        """Save evaluation results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"eval_results_{timestamp}.json"

        output = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r["passed"]),
            "failed": sum(1 for r in self.results if not r["passed"]),
            "results": self.results
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Results saved to: {filename}")
        return filename


async def run_quick_eval(max_tests: int = 5):
    """Run a quick evaluation with limited test cases"""
    print("\n🚀 Running QUICK EVALUATION (first 5 tests)")
    runner = EvalRunner(agent=root_agent, verbose=True)

    # Get diverse set of tests
    quick_tests = [
        EVAL_SET[0],   # SS_001 - Single stock
        EVAL_SET[5],   # MS_001 - Multi stock
        EVAL_SET[10],  # EC_001 - Edge case
        EVAL_SET[15],  # NV_001 - Name variation
        EVAL_SET[20],  # SEC_001 - Sector specific
    ]

    results = await runner.run_eval_set(quick_tests[:max_tests])
    runner.save_results("eval_results_quick.json")
    return results


async def run_category_eval(category: str):
    """Run evaluation on a specific category"""
    print(f"\n🎯 Running evaluation for category: {category}")
    runner = EvalRunner(agent=root_agent, verbose=True)

    test_cases = get_eval_set_by_category(category)
    if not test_cases:
        print(f"❌ No tests found for category: {category}")
        return None

    results = await runner.run_eval_set(test_cases)
    runner.save_results(f"eval_results_{category}.json")
    return results


async def run_full_eval():
    """Run full evaluation on all test cases"""
    print("\n🔬 Running FULL EVALUATION (all tests)")
    print("⚠️  This will take a while and consume API credits")

    response = input("Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Evaluation cancelled.")
        return None

    runner = EvalRunner(agent=root_agent, verbose=False)  # Less verbose for full run
    results = await runner.run_eval_set(EVAL_SET)
    runner.save_results("eval_results_full.json")
    return results


async def run_sample_eval():
    """Run evaluation on a representative sample"""
    print("\n📊 Running SAMPLE EVALUATION (representative sample)")
    runner = EvalRunner(agent=root_agent, verbose=True)

    # Get 2 tests from each category
    sample_tests = []
    categories_seen = {}
    for test in EVAL_SET:
        cat = test["category"]
        if cat not in categories_seen:
            categories_seen[cat] = 0
        if categories_seen[cat] < 2:
            sample_tests.append(test)
            categories_seen[cat] += 1

    results = await runner.run_eval_set(sample_tests)
    runner.save_results("eval_results_sample.json")
    return results


async def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("STOCK INVESTMENT AGENT - EVALUATION TOOL")
    print("="*70)

    # Show eval set statistics
    stats = get_eval_set_statistics()
    print(f"\nAvailable Tests: {stats['total_tests']}")
    print("\nCategories:")
    for category, breakdown in stats["category_breakdown"].items():
        print(f"  - {category}: {breakdown}")

    print("\n" + "="*70)
    print("SELECT EVALUATION MODE:")
    print("="*70)
    print("1. Quick Eval (5 diverse tests)")
    print("2. Sample Eval (2 tests per category)")
    print("3. Category Eval (specific category)")
    print("4. Full Eval (all tests)")
    print("5. Exit")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == "1":
        await run_quick_eval()
    elif choice == "2":
        await run_sample_eval()
    elif choice == "3":
        print("\nAvailable categories:")
        categories = set(test["category"] for test in EVAL_SET)
        for i, cat in enumerate(sorted(categories), 1):
            print(f"  {i}. {cat}")
        cat_choice = input("\nEnter category name: ").strip()
        if cat_choice in categories:
            await run_category_eval(cat_choice)
        else:
            print(f"❌ Invalid category: {cat_choice}")
    elif choice == "4":
        await run_full_eval()
    elif choice == "5":
        print("Exiting...")
    else:
        print(f"❌ Invalid choice: {choice}")


if __name__ == "__main__":
    asyncio.run(main())
