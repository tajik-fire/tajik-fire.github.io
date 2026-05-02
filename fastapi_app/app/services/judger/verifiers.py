
from typing import Tuple, Optional
import re


class Verifier:
    
    
    @staticmethod
    def normalize_output(output: str) -> str:
        

        lines = output.rstrip().split('\n')
        normalized_lines = [line.rstrip() for line in lines]
        return '\n'.join(normalized_lines)
    
    @staticmethod
    def compare_outputs(
        actual: str,
        expected: str,
        ignore_whitespace: bool = True,
        ignore_case: bool = False
    ) -> Tuple[bool, Optional[str]]:
        
        if ignore_whitespace:
            actual = Verifier.normalize_output(actual)
            expected = Verifier.normalize_output(expected)
        
        if ignore_case:
            actual = actual.lower()
            expected = expected.lower()
        
        if actual == expected:
            return True, None
        

        actual_lines = actual.split('\n')
        expected_lines = expected.split('\n')
        

        min_len = min(len(actual_lines), len(expected_lines))
        for i in range(min_len):
            if actual_lines[i] != expected_lines[i]:
                return False, f"Wrong answer at line {i + 1}"
        

        if len(actual_lines) < len(expected_lines):
            return False, f"Output is too short (expected {len(expected_lines)} lines, got {len(actual_lines)})"
        else:
            return False, f"Output is too long (expected {len(expected_lines)} lines, got {len(actual_lines)})"
    
    @staticmethod
    def check_special_judge(
        actual: str,
        expected: str,
        input_data: str
    ) -> Tuple[bool, Optional[str]]:
        

        return Verifier.compare_outputs(actual, expected)
    
    @staticmethod
    def validate_output_format(
        output: str,
        expected_lines: int = None,
        expected_tokens: int = None
    ) -> Tuple[bool, Optional[str]]:
        
        lines = output.strip().split('\n') if output.strip() else []
        tokens = output.split()
        
        if expected_lines is not None and len(lines) != expected_lines:
            return False, f"Expected {expected_lines} lines, got {len(lines)}"
        
        if expected_tokens is not None and len(tokens) != expected_tokens:
            return False, f"Expected {expected_tokens} tokens, got {len(tokens)}"
        
        return True, None
