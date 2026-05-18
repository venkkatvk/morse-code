"""
Production Quality Assurance Test Suite for Morse Interpreter Engine
-------------------------------------------------------------------
Validates syntactic guardrails, tool dispatching orchestration, 
and fault-tolerant graceful degradation thresholds.
"""

import pytest
from pydantic_ai import capture_run_messages
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.function import FunctionModel

from app.translator import translate_morse_pipeline, validate_morse_input, morse_agent
from app.schemas import TranslationResponse


# =====================================================================
# GATEWAY GUARDRAIL TESTING (Day 2 Validation Gates)
# =====================================================================

def test_validate_morse_input_malformed_alphanumeric():
    """
    Gateway Level Verification:
    Validates that raw, un-encoded alphanumeric text is blocked instantly 
    by our regex pattern before consuming downstream AI tokens.
    """
    malformed_input = "HELLO WORLD"
    
    with pytest.raises(ValueError) as exc_info:
        validate_morse_input(malformed_input)
        
    assert "Input contains invalid characters for Morse code" in str(exc_info.value)


def test_validate_morse_input_empty_payload():
    """
    Gateway Level Verification:
    Ensures blank or whitespace-only inputs are dropped immediately.
    """
    with pytest.raises(ValueError, match="Morse code input cannot be empty."):
        validate_morse_input("   ")


# =====================================================================
# TOOL EXECUTION & SCHEMA COMPLIANCE TESTING (Day 1 & Day 3 Agents)
# =====================================================================

def test_valid_morse_stream_triggers_tool_and_returns_contract():
    """
    Happy Path Orchestration:
    Injects TestModel to bypass real API hits. Verifies that a pristine 
    Morse string seamlessly triggers the internal dictionary tool lookup, 
    and wraps the resulting data into our strict TranslationResponse schema.
    """
    valid_morse = ".... . .-.. .-.. --- / .-- --- .-. .-.. -.."
    
    # Override live model with the deterministic procedural TestModel stub
    with morse_agent.override(model=TestModel()):
        # Capture the underlying telemetry stream messages exchanged during execution
        with capture_run_messages() as message_logs:
            response = translate_morse_pipeline(valid_morse)
            
            # 1. Assert compliance with our structural Pydantic contract
            assert isinstance(response, TranslationResponse)
            
            # 2. Verify that message frames exist, proving the engine executed
            assert len(message_logs) > 0
            
            # 3. Scan the trace logs to guarantee tool integration occurred
            has_tool_call = any(
                any(part.part_kind == 'tool-call' for part in msg.parts)
                for msg in message_logs if hasattr(msg, 'parts')
            )
            assert has_tool_call, "The agent failed to trigger the dictionary lookup tool!"


# =====================================================================
# FAULT TOLERANCE & GRACEFUL DEGRADATION TESTING (Day 5 Resilience)
# =====================================================================

def test_graceful_fallback_on_api_timeout_exception():
    """
    Resilience Verification:
    Simulates a catastrophic OpenAI API timeout or network termination event 
    by injecting an exploding FunctionModel. Assures that our pipeline catches 
    the blast, falls back to the local dictionary lookup, and returns a cleanly 
    structured response marked with low confidence.
    """
    valid_morse = ".... . .-.. .-.. ---"  # Spells "HELLO"
    
    # 1. Craft a poisoned model function that explicitly throws a runtime network error
    def exploding_network_adapter(messages, info):
        raise RuntimeError("OpenAI API Connection Timeout (Simulated Carrier Loss)")
        
    # 2. Inject the poisoned model into the pipeline's runtime instance
    with morse_agent.override(model=FunctionModel(exploding_network_adapter)):
        # Execute pipeline—if error handling is broken, the test will crash here!
        response = translate_morse_pipeline(valid_morse)
        
        # 3. Assert that the system degraded gracefully rather than throwing a 500
        assert isinstance(response, TranslationResponse)
        assert "[FALLBACK LOGIC]:" in response.translated_text
        assert "HELLO" in response.translated_text
        assert response.confidence_score == 0.10
        assert response.is_corrupted is True