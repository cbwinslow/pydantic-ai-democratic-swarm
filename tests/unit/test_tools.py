"""Tests for standard tools."""

import pytest
import tempfile
from pathlib import Path

from pydantic_ai_swarm.tools.standard import (
    FileReaderTool,
    WebScraperTool,
    DataValidatorTool,
    TextProcessorTool,
    CodeAnalyzerTool,
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestFileReaderTool:
    """Test cases for FileReaderTool."""
    
    async def test_file_reader_creation(self):
        """Test file reader tool can be created."""
        tool = FileReaderTool()
        assert tool.name == "file_reader"
        assert "file_reader" in tool.description.lower()
    
    async def test_read_existing_file(self, tmp_path):
        """Test reading an existing file."""
        # Create a temporary file
        test_file = tmp_path / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)
        
        tool = FileReaderTool()
        result = await tool.execute({"path": str(test_file)})
        
        assert result.success
        assert result.data["content"] == test_content
        assert result.data["path"] == str(test_file)
    
    async def test_read_nonexistent_file(self):
        """Test reading a file that doesn't exist."""
        tool = FileReaderTool()
        result = await tool.execute({"path": "/nonexistent/file.txt"})
        
        assert not result.success
        assert "not found" in result.error.lower()
    
    async def test_read_file_without_path(self):
        """Test reading without providing path parameter."""
        tool = FileReaderTool()
        result = await tool.execute({})
        
        assert not result.success
        assert "missing" in result.error.lower()
    
    async def test_file_size_limit(self, tmp_path):
        """Test file size limit enforcement."""
        # Create a large file
        test_file = tmp_path / "large.txt"
        large_content = "x" * (2 * 1024 * 1024)  # 2MB
        test_file.write_text(large_content)
        
        tool = FileReaderTool()
        result = await tool.execute({
            "path": str(test_file),
            "max_size": 1024 * 1024  # 1MB limit
        })
        
        assert not result.success
        assert "too large" in result.error.lower()
    
    async def test_compatible_agents(self):
        """Test compatible agents list."""
        tool = FileReaderTool()
        agents = tool.compatible_agents
        
        assert "content_agent" in agents
        assert "code_agent" in agents


@pytest.mark.unit
@pytest.mark.asyncio
class TestDataValidatorTool:
    """Test cases for DataValidatorTool."""
    
    async def test_validator_creation(self):
        """Test validator tool can be created."""
        tool = DataValidatorTool()
        assert tool.name == "data_validator"
    
    async def test_validate_correct_data(self):
        """Test validating correct data."""
        tool = DataValidatorTool()
        
        data = {
            "name": "Test",
            "age": 25,
            "active": True,
        }
        schema = {
            "name": str,
            "age": int,
            "active": bool,
        }
        
        result = await tool.execute({
            "data": data,
            "schema": schema,
        })
        
        assert result.success
        assert result.data["valid"] is True
        assert len(result.data["errors"]) == 0
    
    async def test_validate_incorrect_data(self):
        """Test validating incorrect data."""
        tool = DataValidatorTool()
        
        data = {
            "name": "Test",
            "age": "invalid",  # Should be int
        }
        schema = {
            "name": str,
            "age": int,
        }
        
        result = await tool.execute({
            "data": data,
            "schema": schema,
        })
        
        assert not result.success
        assert result.data["valid"] is False
        assert len(result.data["errors"]) > 0
    
    async def test_validate_missing_fields(self):
        """Test validation with missing fields."""
        tool = DataValidatorTool()
        
        data = {"name": "Test"}
        schema = {
            "name": str,
            "age": int,
            "email": str,
        }
        
        result = await tool.execute({
            "data": data,
            "schema": schema,
        })
        
        assert not result.success
        assert "missing" in str(result.data["errors"]).lower()


@pytest.mark.unit
@pytest.mark.asyncio
class TestTextProcessorTool:
    """Test cases for TextProcessorTool."""
    
    async def test_processor_creation(self):
        """Test text processor tool can be created."""
        tool = TextProcessorTool()
        assert tool.name == "text_processor"
    
    async def test_tokenize_text(self):
        """Test text tokenization."""
        tool = TextProcessorTool()
        
        text = "Hello world this is a test"
        result = await tool.execute({
            "text": text,
            "operation": "tokenize",
        })
        
        assert result.success
        assert result.data["operation"] == "tokenize"
        assert result.data["token_count"] == 6
        assert "tokens" in result.data
    
    async def test_word_count(self):
        """Test word count operation."""
        tool = TextProcessorTool()
        
        text = "Hello world. This is a test. Testing one two three."
        result = await tool.execute({
            "text": text,
            "operation": "word_count",
        })
        
        assert result.success
        assert result.data["word_count"] > 0
        assert result.data["sentence_count"] > 0
        assert "character_count" in result.data
    
    async def test_summarize_text(self):
        """Test text summarization."""
        tool = TextProcessorTool()
        
        # Create a long text
        words = ["word" + str(i) for i in range(150)]
        text = " ".join(words)
        
        result = await tool.execute({
            "text": text,
            "operation": "summarize",
        })
        
        assert result.success
        assert "summary" in result.data
        assert result.data["summary_length"] <= 100
    
    async def test_extract_keywords(self):
        """Test keyword extraction."""
        tool = TextProcessorTool()
        
        text = "Python programming language Python development testing Python code"
        result = await tool.execute({
            "text": text,
            "operation": "extract_keywords",
        })
        
        assert result.success
        assert "keywords" in result.data
        assert len(result.data["keywords"]) > 0
    
    async def test_invalid_operation(self):
        """Test invalid operation handling."""
        tool = TextProcessorTool()
        
        result = await tool.execute({
            "text": "test",
            "operation": "invalid_operation",
        })
        
        assert not result.success
        assert "unknown operation" in result.error.lower()
    
    async def test_missing_text(self):
        """Test operation without text."""
        tool = TextProcessorTool()
        
        result = await tool.execute({
            "operation": "tokenize",
        })
        
        assert not result.success
        assert "missing" in result.error.lower()


@pytest.mark.unit
@pytest.mark.asyncio
class TestCodeAnalyzerTool:
    """Test cases for CodeAnalyzerTool."""
    
    async def test_analyzer_creation(self):
        """Test code analyzer tool can be created."""
        tool = CodeAnalyzerTool()
        assert tool.name == "code_analyzer"
    
    async def test_analyze_python_code(self):
        """Test analyzing Python code."""
        tool = CodeAnalyzerTool()
        
        code = """
def hello_world():
    # This is a comment
    print("Hello, World!")
    return True

# TODO: Add more features
"""
        
        result = await tool.execute({
            "code": code,
            "language": "python",
        })
        
        assert result.success
        assert result.data["language"] == "python"
        assert "metrics" in result.data
        assert "total_lines" in result.data["metrics"]
        assert "code_lines" in result.data["metrics"]
        assert "comment_lines" in result.data["metrics"]
    
    async def test_detect_todo_comments(self):
        """Test detection of TODO comments."""
        tool = CodeAnalyzerTool()
        
        code = "# TODO: Fix this bug\nprint('test')"
        result = await tool.execute({
            "code": code,
            "language": "python",
        })
        
        assert result.success
        assert len(result.data["issues"]) > 0
        assert any("TODO" in str(issue) for issue in result.data["issues"])
    
    async def test_large_file_detection(self):
        """Test detection of large files."""
        tool = CodeAnalyzerTool()
        
        # Create a large code file
        lines = ["print('line')" for _ in range(1500)]
        code = "\n".join(lines)
        
        result = await tool.execute({
            "code": code,
            "language": "python",
        })
        
        assert result.success
        assert len(result.data["issues"]) > 0
        assert any("long" in str(issue).lower() for issue in result.data["issues"])
    
    async def test_missing_code(self):
        """Test analyzer without code."""
        tool = CodeAnalyzerTool()
        
        result = await tool.execute({
            "language": "python",
        })
        
        assert not result.success
        assert "missing" in result.error.lower()
    
    async def test_compatible_agents(self):
        """Test compatible agents for code analyzer."""
        tool = CodeAnalyzerTool()
        agents = tool.compatible_agents
        
        assert "code_agent" in agents
        assert "security_agent" in agents
        assert "testing_agent" in agents


@pytest.mark.integration
@pytest.mark.asyncio
class TestToolsIntegration:
    """Integration tests for tools."""
    
    async def test_file_to_text_processor_pipeline(self, tmp_path):
        """Test pipeline: file reader -> text processor."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello world this is a test document")
        
        # Read file
        file_tool = FileReaderTool()
        file_result = await file_tool.execute({"path": str(test_file)})
        assert file_result.success
        
        # Process text
        text_tool = TextProcessorTool()
        text_result = await text_tool.execute({
            "text": file_result.data["content"],
            "operation": "word_count",
        })
        assert text_result.success
        assert text_result.data["word_count"] == 7
    
    async def test_multiple_tools_same_data(self):
        """Test multiple tools on the same data."""
        code = "def test():\n    return True"
        
        # Analyze code
        analyzer = CodeAnalyzerTool()
        analyze_result = await analyzer.execute({
            "code": code,
            "language": "python",
        })
        assert analyze_result.success
        
        # Process as text
        text_tool = TextProcessorTool()
        text_result = await text_tool.execute({
            "text": code,
            "operation": "tokenize",
        })
        assert text_result.success
