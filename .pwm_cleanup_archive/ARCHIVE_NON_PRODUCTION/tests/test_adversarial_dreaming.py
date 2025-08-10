from dream.engine.dream_engine import DreamEngine


def test_adversarial_dreaming():
    # Setup
    engine = DreamEngine()
    adversarial_parameters = {"ethical_challenge": "test"}

    # Action
    result = engine.run_adversarial_simulation(adversarial_parameters)

    # Assert
    assert result["response"] == "ethical challenge handled"
