# LLM OCR Package

LLM-powered OCR evaluation and correction package that supports multiple language models for OCR processing and text correction tasks.

## Features

- **Multi-Provider LLM Support**: Claude, GPT-4, Gemini, and Together AI
- **Multiple Processing Modes**: Single-line, sliding window, and full-page OCR
- **Evaluation**: Character accuracy, word accuracy, case preservation, and error analysis
- **OCR Correction**: LLM-based text correction with configurable output formats
- **ALTO XML Support**: Process ALTO XML files with corresponding images
- **Detailed Metrics**: Extensive evaluation metrics with error pattern analysis
- **Workflow Management**: Complete pipeline orchestration with result tracking

## Installation

### From source

```bash
git clone https://github.com/mary-lev/llm-ocr.git
cd llm-ocr
pip install -e .
```

### Development installation

```bash
git clone https://github.com/mary-lev/llm-ocr.git
cd llm-ocr
pip install -e ".[dev]"
```

## Quick Start

### 1. Set up API keys

Copy the `.env.template` file and fill in your API key values:

```bash
cp .env.template .env
# Edit .env and add your API key values
```

The following environment variables must be set in your `.env` file:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`
- `TOGETHER_API_KEY`
- `DEEP_SEEK_API_KEY`
- `DEEPINFRA_API_KEY`

### 2. Basic usage

```python
from llm_ocr.workflow import OCRPipelineWorkflow
from llm_ocr.models import ProcessingMode
from llm_ocr.prompts.prompt import PromptVersion

# Initialize workflow
workflow = OCRPipelineWorkflow(
    id="document_001",
    folder="ground_truth",  # Contains .xml, .jpeg files
    ocr_model_name="claude-3-7-sonnet-20250219",
    modes=[ProcessingMode.FULL_PAGE],
    prompt_version=PromptVersion.V3
)

# Run complete pipeline
results = workflow.run_pipeline()

# Or run individual steps
workflow.run_ocr()
workflow.evaluate_ocr()
workflow.run_correction()
workflow.evaluate_correction()
```

## Architecture

### Core Components

- **Pipelines** (`llm_ocr/pipelines/`): OCR and correction processing workflows
- **LLM Models** (`llm_ocr/llm/`): Multi-provider LLM support with unified interface
- **Prompts** (`llm_ocr/prompts/`): Modular prompt generation with version control and context enrichment
- **Evaluators** (`llm_ocr/evaluators/`): Comprehensive metrics and evaluation framework
- **Processors** (`llm_ocr/processors/`): Input format handling (ALTO XML)
- **Workflow** (`llm_ocr/workflow.py`): Main orchestration and result management

### Processing Modes

- **SINGLE_LINE**: Process each text line individually
- **SLIDING_WINDOW**: Process lines with context window
- **FULL_PAGE**: Process entire page at once

### Supported Models

- **Claude**: Anthropic's Claude models (3.5 Sonnet, etc.)
- **GPT-4**: OpenAI's GPT-4 models
- **Gemini**: Google's Gemini models
- **Together AI**: Various open-source models via Together

## Prompt System

The package features a modular prompt generation system that allows for flexible experimentation with different prompt strategies and automatic context enrichment.

### Prompt Versions

Different prompt versions are available for various use cases and languages:

- **V1**: Basic OCR prompts without additional context
- **V2**: Enhanced with historical book metadata (year, title)
- **V3**: Advanced context with improved instructions
- **V4**: Russian language optimized prompts

```python
from llm_ocr.prompts.prompt import PromptVersion

# Use different prompt versions
workflow = OCRPipelineWorkflow(
    id="document_001",
    folder="ground_truth",
    ocr_model_name="claude-3-7-sonnet-20250219",
    prompt_version=PromptVersion.V2,  # Will include book metadata context
    modes=[ProcessingMode.FULL_PAGE]
)
```

### Prompt Types and Modes

The system supports different output formats and processing modes:

```python
from llm_ocr.prompts.prompt_builder import PromptBuilder, PromptType, PromptVersion

builder = PromptBuilder()

# Structured JSON output for single line processing
structured_prompt = builder.build_prompt(
    mode="single_line",
    prompt_type=PromptType.STRUCTURED,  # JSON format
    version=PromptVersion.V3
)

# Simple text output for full page processing
simple_prompt = builder.build_prompt(
    mode="full_page", 
    prompt_type=PromptType.SIMPLE,  # Plain text format
    version=PromptVersion.V1
)
```

### Automatic Metadata Enrichment

When document metadata is available, prompts can be automatically enriched with context:

```python
from llm_ocr.prompts.prompt_builder import PromptBuilder, PromptType, PromptVersion

builder = PromptBuilder()

# Automatic enrichment using document ID
enriched_prompt = builder.build_prompt(
    mode="single_line",
    prompt_type=PromptType.STRUCTURED,
    version=PromptVersion.V2,
    document_id="historical_doc_001"  # Auto-loads book metadata
)

# Manual context variables
manual_prompt = builder.build_prompt(
    mode="sliding_window",
    prompt_type=PromptType.STRUCTURED, 
    version=PromptVersion.V2,
    book_title="История государства Российского",
    book_year="1767"
)
```

### Custom Prompt Configuration

For advanced users, prompts can be fully customized via JSON configuration:

```python
# Create custom prompt builder with custom config
custom_builder = PromptBuilder(
    config_path="path/to/custom_prompts.json",
    metadata_path="path/to/document_metadata.json"
)

# Use convenience functions for common cases
from llm_ocr.prompts.prompt_builder import get_prompt, PromptType, PromptVersion

prompt = get_prompt(
    mode="correction",
    prompt_type=PromptType.SIMPLE,
    version=PromptVersion.V4,
    book_title="Тестовая книга"
)
```

### Prompt Configuration Format

Custom prompt configurations use JSON format with modular components:

```json
{
  "components": {
    "base_ocr": "Extract OCR text from 18th century Russian book",
    "orthography": "Preserve ѣ, Ѳ, ѳ, ѵ, ъ characters",
    "json_format": "Respond with JSON: {\"line\": \"text\"}"
  },
  "context_enrichment": {
    "v1": "",
    "v2": " from {book_year} book \"{book_title}\"",
    "v3": " processing \"{book_title}\" ({book_year})",
    "v4": " обрабатываете \"{book_title}\" {book_year} года"
  },
  "mode_instructions": {
    "single_line": "Process single line",
    "sliding_window": "Process sliding window", 
    "full_page": "Process full page",
    "correction": "Correct OCR text"
  }
}
```

## Configuration

### Model Configuration

```python
from llm_ocr.config import ModelConfig

config = ModelConfig(
    max_tokens=2048,
    temperature=0.0,
    sliding_window_size=3,
    batch_size=10
)
```

### Evaluation Configuration

```python
from llm_ocr.config import EvaluationConfig

eval_config = EvaluationConfig(
    use_char_accuracy=True,
    use_word_accuracy=True,
    use_old_char_preservation=True,
    include_detailed_analysis=True
)
```

## Data Format

### Input Requirements

Your data folder should contain:

- `{id}.xml`: ALTO XML file with text coordinates
- `{id}.jpeg`: Corresponding image file
- `{id}.txt`: Ground truth text (optional, for evaluation)

### Output Format

Results are saved as JSON files with complete metrics and analysis:

```json
{
  "document_info": {
    "document_name": "document_001",
    "timestamp": "20250124_143022"
  },
  "models": {
    "claude-3-7-sonnet-20250219": {
      "ocr_results": {
        "fullpage": {
          "lines": [...],
          "metrics": {...}
        }
      },
      "correction_results": {
        "original_ocr_text": "...",
        "corrected_text": "...",
        "metrics": {...}
      }
    }
  }
}
```

## Advanced Usage

### Custom Model Integration

```python
from llm_ocr.llm.base import BaseOCRModel

class CustomOCRModel(BaseOCRModel):
    def process_single_line(self, image_base64: str):
        # Implement single line processing
        pass

    def process_full_page(self, page_image_base64: str, id: str):
        # Implement full page processing
        pass

    def correct_text(self, text: str, image_base64: str):
        # Implement text correction
        pass
```

### Batch Processing

```python
from llm_ocr.workflow import run_multi_model_workflow

results = run_multi_model_workflow(
    xml_path="data/document.xml",
    image_path="data/document.jpeg",
    ground_truth_path="data/document.txt",
    model_names=["claude-3-7-sonnet-20250219", "gpt-4o-2024-08-06"],
    output_dir="results"
)
```

## Development

### Environment Setup

```bash
# Clone and set up development environment
git clone https://github.com/mary-lev/llm-ocr.git
cd llm-ocr

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests with coverage
pytest

# Or use the custom test runner
python run_tests.py

# Run specific test files
pytest tests/unit/test_metrics.py
pytest tests/integration/test_basic_workflow.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=llm_ocr --cov-report=html
```

**Note**: Always activate the virtual environment before running tests to avoid dependency conflicts.

### Code Quality

```bash
# Activate virtual environment first
source venv/bin/activate

# Format code
python -m black llm_ocr/
python -m isort llm_ocr/

# Lint code
python -m ruff check llm_ocr/

# Type checking (requires Python 3.10+ target)
python -m mypy llm_ocr/ --python-version=3.10

# Run all quality checks
python run_tests.py  # Includes tests + quality checks
```

### Pre-commit Hooks

This project uses pre-commit hooks to maintain code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Set up development environment: `source venv/bin/activate && pip install -e ".[dev]"`
4. Make your changes and add tests
5. Run the test suite: `pytest` or `python run_tests.py`
6. Ensure code quality: `pre-commit run --all-files`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this package in your research, please cite:

```bibtex
@software{llm_ocr_package,
  title = {LLM OCR: Multi-Provider OCR Evaluation and Correction},
  author = {Maria Levchenko},
  year = {2025},
  url = {https://github.com/mary-lev/llm-ocr}
}
```
