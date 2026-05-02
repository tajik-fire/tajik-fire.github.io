
import pytest
from app.services.judger.verifiers import Verifier


class TestVerifier:
    
    
    def test_exact_match(self):
        
        actual = "5\n"
        expected = "5\n"
        is_correct, error = Verifier.compare_outputs(actual, expected)
        assert is_correct is True
        assert error is None
    
    def test_whitespace_insensitive(self):
        
        actual = "5  \n"
        expected = "5\n"
        is_correct, error = Verifier.compare_outputs(actual, expected, ignore_whitespace=True)
        assert is_correct is True
    
    def test_case_insensitive(self):
        
        actual = "Hello\n"
        expected = "hello\n"
        is_correct, error = Verifier.compare_outputs(actual, expected, ignore_case=True)
        assert is_correct is True
    
    def test_wrong_answer_line_diff(self):
        
        actual = "5\n"
        expected = "6\n"
        is_correct, error = Verifier.compare_outputs(actual, expected)
        assert is_correct is False
        assert "line 1" in error.lower() or "wrong" in error.lower()
    
    def test_output_too_short(self):
        
        actual = "5\n"
        expected = "5\n6\n"
        is_correct, error = Verifier.compare_outputs(actual, expected)
        assert is_correct is False
        assert "short" in error.lower()
    
    def test_output_too_long(self):
        
        actual = "5\n6\n7\n"
        expected = "5\n"
        is_correct, error = Verifier.compare_outputs(actual, expected)
        assert is_correct is False
        assert "long" in error.lower()
    
    def test_multiline_correct(self):
        
        actual = "1\n2\n3\n"
        expected = "1\n2\n3\n"
        is_correct, error = Verifier.compare_outputs(actual, expected)
        assert is_correct is True
    
    def test_multiline_wrong(self):
        
        actual = "1\n2\n3\n"
        expected = "1\n3\n3\n"
        is_correct, error = Verifier.compare_outputs(actual, expected)
        assert is_correct is False
        assert "line 2" in error.lower()
    
    def test_empty_output(self):
        
        actual = ""
        expected = "5\n"
        is_correct, error = Verifier.compare_outputs(actual, expected)
        assert is_correct is False
    
    def test_normalize_output(self):
        
        output = "  5  \n  6  \n  "
        normalized = Verifier.normalize_output(output)
        assert normalized == "  5\n  6"
    
    def test_validate_format_lines(self):
        
        output = "1\n2\n3\n"
        is_valid, error = Verifier.validate_output_format(output, expected_lines=3)
        assert is_valid is True
        
        is_valid, error = Verifier.validate_output_format(output, expected_lines=2)
        assert is_valid is False
    
    def test_validate_format_tokens(self):
        
        output = "1 2 3\n"
        is_valid, error = Verifier.validate_output_format(output, expected_tokens=3)
        assert is_valid is True
        
        is_valid, error = Verifier.validate_output_format(output, expected_tokens=2)
        assert is_valid is False


class TestLanguageConfig:
    
    
    def test_supported_languages(self):
        
        from app.services.judger.languages import SUPPORTED_LANGUAGES, is_supported
        
        assert "python3" in SUPPORTED_LANGUAGES
        assert "cpp17" in SUPPORTED_LANGUAGES
        assert "java11" in SUPPORTED_LANGUAGES
        assert len(SUPPORTED_LANGUAGES) == 3
    
    def test_is_supported(self):
        
        from app.services.judger.languages import is_supported
        
        assert is_supported("python3") is True
        assert is_supported("cpp17") is True
        assert is_supported("java11") is True
        assert is_supported("c") is False
        assert is_supported("rust") is False
    
    def test_get_language_config(self):
        
        from app.services.judger.languages import get_language_config
        
        python_config = get_language_config("python3")
        assert python_config is not None
        assert python_config.name == "Python 3"
        assert python_config.extension == ".py"
        assert python_config.compile_cmd is None
        assert python_config.time_multiplier == 2.0
        
        cpp_config = get_language_config("cpp17")
        assert cpp_config is not None
        assert cpp_config.name == "C++17"
        assert cpp_config.extension == ".cpp"
        assert cpp_config.compile_cmd is not None
        assert cpp_config.time_multiplier == 1.0
        
        java_config = get_language_config("java11")
        assert java_config is not None
        assert java_config.name == "Java 11"
        assert java_config.extension == ".java"
        assert java_config.time_multiplier == 2.0
        assert java_config.memory_multiplier == 2.0
    
    def test_unsupported_language(self):
        
        from app.services.judger.languages import get_language_config
        
        config = get_language_config("cobol")
        assert config is None
