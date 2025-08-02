#!/usr/bin/env python3
"""
Test Common Cross-Domain Agents

Simple test to verify that common agents can be imported and instantiated correctly.
"""


def test_common_agents_import():
    """Test that all common agents can be imported"""
    print("Testing common agent imports...")

    try:
        from polyhegel.agents.common.agents import (
            CommonAnalysisLeader,
            StakeholderAnalysisFollower,
            TradeoffAnalysisFollower,
            RiskAssessmentFollower,
            ConsensusBuilderFollower,
            ScenarioPlanningFollower,
        )

        # Use the imports to avoid unused import warning
        agents = [
            CommonAnalysisLeader,
            StakeholderAnalysisFollower,
            TradeoffAnalysisFollower,
            RiskAssessmentFollower,
            ConsensusBuilderFollower,
            ScenarioPlanningFollower,
        ]
        print(f"✓ All {len(agents)} agent classes imported successfully")
        return True
    except Exception as e:
        print(f"✗ Agent import failed: {e}")
        return False


def test_common_agent_cards():
    """Test that all agent cards can be created"""
    print("Testing agent card creation...")

    try:
        from polyhegel.agents.common.cards import create_all_common_agent_cards

        cards = create_all_common_agent_cards()
        print(f"✓ Created {len(cards)} agent cards")

        for name, card in cards.items():
            print(f"  - {name}: {card.name}")

        return True
    except Exception as e:
        print(f"✗ Agent card creation failed: {e}")
        return False


def test_server_imports():
    """Test that server modules can be imported"""
    print("Testing server imports...")

    try:
        import polyhegel.servers.common.common_analysis_leader_server
        import polyhegel.servers.common.common_follower_server

        # Use the imports to avoid unused import warning
        servers = [
            polyhegel.servers.common.common_analysis_leader_server,
            polyhegel.servers.common.common_follower_server,
        ]
        print(f"✓ Server modules imported successfully ({len(servers)} modules)")
        return True
    except Exception as e:
        print(f"✗ Server import failed: {e}")
        return False


def test_common_techniques():
    """Test that common techniques are accessible"""
    print("Testing common techniques...")

    try:
        from polyhegel.techniques.common.techniques import ALL_TECHNIQUES

        print(f"✓ {len(ALL_TECHNIQUES)} common techniques available")

        for technique in ALL_TECHNIQUES:
            print(f"  - {technique.name} ({technique.technique_type.value})")

        return True
    except Exception as e:
        print(f"✗ Common techniques test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=== Testing Common Cross-Domain Agents ===\n")

    tests = [
        test_common_techniques,
        test_common_agents_import,
        test_common_agent_cards,
        test_server_imports,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()

    # Summary
    passed = sum(results)
    total = len(results)

    print("=== Test Results ===")
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✓ All tests passed! Common cross-domain agents are ready.")
        return 0
    else:
        print("✗ Some tests failed. Check output above.")
        return 1


if __name__ == "__main__":
    exit(main())
