import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from ..config import ModelConfig


class BaseOCRModel(ABC):
    """Base abstract class for OCR language models."""

    def __init__(self, model_name: str):
        self.config = ModelConfig
        self.model_name = model_name
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def process_single_line(self, prompt: str, image_base64: str) -> Dict[str, Any]:
        """Process a single line image with pre-built prompt.

        Args:
            prompt: The formatted prompt text
            image_base64: Base64 encoded image string

        Returns:
            Parsed JSON response as dict
        """
        pass

    @abstractmethod
    def process_sliding_window(
        self, prompt: str, images_base64: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Process a window of line images with pre-built prompt.

        Args:
            prompt: The formatted prompt text
            images_base64: List of base64 encoded image strings

        Returns:
            Parsed JSON response as dict or None if failed
        """
        pass

    @abstractmethod
    def process_full_page(self, prompt: str, page_image_base64: str) -> str:
        """Process a full page image with pre-built prompt.

        Args:
            prompt: The formatted prompt text
            page_image_base64: Base64 encoded page image string

        Returns:
            Extracted text or JSON string
        """
        pass

    @abstractmethod
    def correct_text(self, prompt: str, text: str, image_base64: str) -> str:
        """Correct OCR text with pre-built prompt.

        Args:
            prompt: The formatted prompt text
            text: OCR text to correct
            image_base64: Base64 encoded image for context

        Returns:
            Corrected text
        """
        pass

    def _extract_json_from_response(self, response_text: str) -> Union[Dict[Any, Any], List[Any]]:
        """
        Extract JSON object or array from model response that may include additional text,
        markdown formatting, or code blocks.
        Args:
            response_text: The text response from the model
        Returns:
            Parsed JSON as dict or list

        Raises:
            ValueError: If no valid JSON is found
        """
        # First, try direct JSON parsing
        try:
            result = json.loads(response_text)
            if not isinstance(result, (dict, list)):
                raise ValueError("JSON root is not an object or array")
            return result
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            markdown_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
            markdown_matches = re.findall(markdown_pattern, response_text)

            if markdown_matches:
                for match in markdown_matches:
                    try:
                        result = json.loads(match)
                        if not isinstance(result, (dict, list)):
                            raise ValueError("JSON root is not an object or array")
                        return result
                    except json.JSONDecodeError:
                        continue  # Try next match if available

            # If no markdown blocks found or none contained valid JSON,
            # fall back to the original bracket-based extraction
            try:
                # Check if response contains an array
                if "[" in response_text and "]" in response_text:
                    json_start = response_text.find("[")
                    json_end = response_text.rfind("]") + 1
                # Check if response contains an object
                elif "{" in response_text and "}" in response_text:
                    json_start = response_text.find("{")
                    json_end = response_text.rfind("}") + 1
                else:
                    raise ValueError("No JSON object/array found in response")

                if json_start == -1 or json_end <= 0:
                    raise ValueError("No JSON object/array found in response")

                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
                if not isinstance(result, (dict, list)):
                    raise ValueError("JSON root is not an object or array")
                return result

            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parsing error: {str(e)}")
                self.logger.debug(f"Response text: {response_text}")
                raise
            except Exception as e:
                self.logger.error(f"Error extracting JSON from response: {str(e)}")
                self.logger.debug(f"Response text: {response_text}")
                raise
