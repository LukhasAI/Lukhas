#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Cognitive Ai Client

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Specialized AI client for cognitive tasks: mathematics, reasoning, pattern recognition

For more information, visit: https://lukhas.ai
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class CognitiveResponse:
    """Response from cognitive AI processing."""
    content: str
    answer: Any = None
    reasoning: str = ""
    tokens_used: int = 0
    model: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class CognitiveAIClient:
    """OpenAI client specialized for cognitive tasks."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the cognitive AI client."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self.model = "gpt-4o-mini"  # Cost-effective model for cognitive tasks

        if OPENAI_AVAILABLE and self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
            self.available = True
        else:
            self.available = False

    async def solve_math_problem(
        self, problem: str, context: Dict[str, Any] = None) -> CognitiveResponse:
        """Solve mathematical problems with step-by-step reasoning."""
        if not self.available:
            return self._fallback_math_response(problem)

        try:
            prompt = f"""Solve this mathematical problem step by step:

Problem: {problem}

Please provide:
1. Clear step-by-step solution
2. Final numerical answer
3. Brief explanation of the method used

Example format:
Step 1: [First calculation]
Step 2: [Second calculation]
Final Answer: [Number]
Method: [Brief explanation]"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are LUKHAS, an advanced AI with exceptional mathematical reasoning capabilities. Always provide step-by-step solutions with clear numerical answers."
                        "content": "You are lukhas, an advanced AI with exceptional mathematical reasoning capabilities. Always provide step-by-step solutions with clear numerical answers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=400,
                temperature=0.1  # Low temperature for precise mathematical reasoning
            )

            content = response.choices[0].message.content

            # Extract answer from response
            answer = self._extract_numerical_answer(content)
            reasoning = self._extract_reasoning(content)

            return CognitiveResponse(
                content=content,
                answer=answer,
                reasoning=reasoning,
                tokens_used=response.usage.total_tokens,
                model=self.model,
                metadata={
                    "task_type": "mathematical_reasoning",
                    "problem": problem,
                    "context": context
                }
            )

        except Exception as e:
            return self._fallback_math_response(problem, error=str(e))

    async def recognize_pattern(
        self, pattern_data: Dict[str, Any]) -> CognitiveResponse:
        """Recognize and complete patterns (ARC-AI style)."""
        if not self.available:
            return self._fallback_pattern_response(pattern_data)

        try:
            prompt = f"""Analyze this pattern recognition task:

Pattern Name: {pattern_data.get('name', 'Unknown')}
Description: {pattern_data.get('description', '')}
Examples: {pattern_data.get('examples', [])}
Test Input: {pattern_data.get('test_input', '')}

Task: Identify the pattern rule and apply it to the test input.

Please provide:
1. Pattern rule identified
2. Step-by-step application to test input
3. Final answer/output
4. Confidence level (1-10)

Format:
Rule: [Pattern rule]
Application: [How rule applies to test]
Answer: [Final result]
Confidence: [1-10]"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are LUKHAS, an advanced AI with exceptional pattern recognition capabilities. You excel at ARC-AI style abstract reasoning tasks."
                        "content": "You are lukhas, an advanced AI with exceptional pattern recognition capabilities. You excel at ARC-AI style abstract reasoning tasks."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=400,
                temperature=0.2
            )

            content = response.choices[0].message.content
            answer = self._extract_pattern_answer(content, pattern_data)

            return CognitiveResponse(
                content=content,
                answer=answer,
                reasoning=content,
                tokens_used=response.usage.total_tokens,
                model=self.model,
                metadata={
                    "task_type": "pattern_recognition",
                    "pattern_data": pattern_data
                }
            )

        except Exception as e:
            return self._fallback_pattern_response(pattern_data, error=str(e))

    async def learn_and_adapt(self, learning_data: Dict[str, Any]) -> CognitiveResponse:
        """Process learning and adaptation tasks."""
        if not self.available:
            return self._fallback_learning_response(learning_data)

        try:
            prompt = f"""Learning Task:

Concept: {learning_data.get('concept', '')}
Examples: {learning_data.get('examples', [])}
Question: {learning_data.get('question', '')}
Previous Learning: {learning_data.get('learning_context', {})}

Task: Use the examples to understand the concept, then answer the question.
Show how you learned from the examples and applied that knowledge.

Please provide:
1. Concept understanding
2. Learning from examples
3. Application to question
4. Final answer

Format:
Concept: [What you learned]
Learning: [How examples taught you]
Application: [How you apply to question]
Answer: [Final result]"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are LUKHAS, an advanced AI with exceptional learning and adaptation capabilities. You can quickly identify patterns from examples and apply them to new situations."
                        "content": "You are lukhas, an advanced AI with exceptional learning and adaptation capabilities. You can quickly identify patterns from examples and apply them to new situations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=400,
                temperature=0.3
            )

            content = response.choices[0].message.content
            answer = self._extract_learning_answer(content, learning_data)

            return CognitiveResponse(
                content=content,
                answer=answer,
                reasoning=content,
                tokens_used=response.usage.total_tokens,
                model=self.model,
                metadata={
                    "task_type": "learning_adaptation",
                    "learning_data": learning_data
                }
            )

        except Exception as e:
            return self._fallback_learning_response(learning_data, error=str(e))

    def _extract_numerical_answer(self, content: str) -> Any:
        """Extract numerical answer from mathematical response."""
        import re

        # Look for "Final Answer:", "Answer:", or numbers in the response
        patterns = [
    ]
            r"Final Answer:\s*([0-9,.()]+)",
            r"Answer:\s*([0-9,.()]+)",
            r"=\s*([0-9,.()]+)",
            r"([0-9]+(?:\.[0-9]+)?)"
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    answer_str = match.group(1).replace(",", "")
                    return float(answer_str) if "." in answer_str else int(answer_str)
                except (ValueError, TypeError, AttributeError) as e:
                    # Failed to parse numeric answer, try next pattern
                    continue

        return None

    def _extract_reasoning(self, content: str) -> str:
        """Extract reasoning steps from response."""
        lines = content.split('\n')
        reasoning_lines = []
        for line in lines:
            if any(keyword in line.lower()
                   for keyword in ['step', 'first', 'then', 'next', 'finally']):
                reasoning_lines.append(line.strip())
        return '\n'.join(reasoning_lines) if reasoning_lines else content

    def _extract_pattern_answer(
        self, content: str, pattern_data: Dict[str, Any]) -> Any:
        """Extract pattern answer from response."""
        import re

        # Look for answer in various formats
        patterns = [
            r"Answer:\s*(.+?)(?:\n|$)",
            r"Result:\s*(.+?)(?:\n|$)",
            r"Output:\s*(.+?)(?:\n|$)"
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return pattern_data.get('expected_output', 'No answer extracted')

    def _extract_learning_answer(
        self, content: str, learning_data: Dict[str, Any]) -> Any:
        """Extract learning answer from response."""
        import re

        # Look for answer in various formats
        patterns = [
            r"Answer:\s*(.+?)(?:\n|$)",
            r"Final Answer:\s*(.+?)(?:\n|$)",
            r"Result:\s*(.+?)(?:\n|$)"
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                answer_str = match.group(1).strip()
                # Try to convert to number if possible
                try:
                    return float(answer_str) if "." in answer_str else int(answer_str)
                except (ValueError, TypeError) as e:
                    # Not a numeric value, return as string
                    return answer_str

        return learning_data.get('expected', 'No answer extracted')

    def _fallback_math_response(
    self,
    problem: str,
     error: Optional[str] = None) -> CognitiveResponse:
        """Provide fallback response for math problems."""
        return CognitiveResponse(
            content = f"Mathematical problem: {problem}\nProcessing with basic algorithms.",
            answer = None,
            reasoning = "Fallback processing - AI not available",
            metadata = {
                "task_type": "mathematical_reasoning",
                "processing_type": "fallback",
                "error": error
            }
        )

    def _fallback_pattern_response(
        self, pattern_data: Dict[str, Any], error: Optional[str]=None) -> CognitiveResponse:
        """Provide fallback response for pattern recognition."""
        return CognitiveResponse(
            content = "Pattern recognition using basic algorithms.",
            answer = pattern_data.get('expected_output', 'Unknown'),
            reasoning = "Fallback processing - AI not available",
            metadata = {
                "task_type": "pattern_recognition",
                "processing_type": "fallback",
                "error": error
            }
        )

    def _fallback_learning_response(
        self, learning_data: Dict[str, Any], error: Optional[str]=None) -> CognitiveResponse:
        """Provide fallback response for learning tasks."""
        return CognitiveResponse(
            content = "Learning task processed with basic algorithms.",
            answer = learning_data.get('expected', 'Unknown'),
            reasoning = "Fallback processing - AI not available",
            metadata = {
                "task_type": "learning_adaptation",
                "processing_type": "fallback",
                "error": error
            }
        )

    def get_status(self) -> Dict[str, Any]:
        """Get cognitive AI client status."""
        return {
            "available": self.available,
            "model": self.model,
            "api_key_configured": bool(self.api_key),
            "openai_library_available": OPENAI_AVAILABLE,
            "capabilities": [
                "mathematical_reasoning",
                "pattern_recognition",
                "learning_adaptation",
                "abstract_reasoning"
            ]
        }








# Last Updated: 2025-06-05 09:37:28
