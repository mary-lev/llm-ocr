"""OpenAI OCR Model Implementation - Simplified without prompt logic."""

import logging
from typing import Any, Dict, List, Optional

from openai import OpenAI
from pydantic import BaseModel  # type: ignore

from llm_ocr.config import settings
from llm_ocr.llm.base import BaseOCRModel


# Pydantic models for response parsing
class Line(BaseModel):
    line: str


class LineGroup(BaseModel):
    lines: List[Line]


class Page(BaseModel):
    lines: List[Line]


class Page_with_Paragraphs(BaseModel):
    paragraphs: List[str]


class OpenAIOCRModel(BaseOCRModel):
    """OpenAI implementation of OCR language model."""

    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.logger = logging.getLogger(__name__)

    def process_single_line(self, prompt: str, image_base64: str) -> Dict[str, Any]:
        """Process a single line image with pre-built prompt."""

        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                            },
                        ],
                    },
                ],
                response_format=Line,
            )

            # Extract parsed response with proper typing
            parsed_result = completion.choices[0].message.parsed
            if parsed_result is None:
                self.logger.error("Parsed result is None")
                return {
                    "line": "",
                    "error": "No result",
                }
            result = parsed_result.model_dump()
            return result

        except Exception as e:
            self.logger.error(f"Error processing single line: {str(e)}")
            return {"line": "", "error": str(e)}

    def process_sliding_window(
        self, prompt: str, images_base64: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Process window of lines with pre-built prompt."""
        content: Any = []

        for img_base64 in images_base64:
            content.append(
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
            )

        content.append({"type": "text", "text": prompt})

        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": content},
                ],
                response_format=LineGroup,
            )

            # Extract parsed response with proper typing
            parsed_result = completion.choices[0].message.parsed
            if parsed_result is None:
                self.logger.error("Parsed result is None")
                return None

            if len(parsed_result.lines) == 1:
                # Return single line result
                line_result = parsed_result.lines[0].model_dump()
                return line_result
            else:
                # Return middle line for sliding window
                middle_idx = len(images_base64) // 2
                if middle_idx < len(parsed_result.lines):
                    line_result = parsed_result.lines[middle_idx].model_dump()
                    return line_result
                else:
                    return None

        except Exception as e:
            self.logger.error(f"Error processing sliding window: {str(e)}")
            return None

    def process_full_page(self, prompt: str, page_image_base64: str) -> str:
        """Process full page with pre-built prompt."""

        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{page_image_base64}"},
                            },
                        ],
                    },
                ],
                response_format=LineGroup,
            )

            # Extract parsed response with proper typing
            parsed_result = completion.choices[0].message.parsed
            if parsed_result is None:
                self.logger.error("Parsed result is None")
                return ""
            self.logger.info(f"Full page: {parsed_result}")
            extracted_lines = "\n".join([line.line for line in parsed_result.lines])
            self.logger.info(f"Extracted lines: {extracted_lines}")

            return extracted_lines

        except Exception as e:
            self.logger.error(f"Error processing full page: {str(e)}")
            return ""

    def correct_text(self, prompt: str, text: str, image_base64: str) -> str:
        """Correct OCR text with pre-built prompt."""

        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                            },
                        ],
                    },
                ],
                response_format=Line,
            )

            # Extract parsed response with proper typing
            parsed_result = completion.choices[0].message.parsed
            if parsed_result is None:
                self.logger.error("Parsed result is None")
                return text
            return parsed_result.line

        except Exception as e:
            self.logger.error(f"Error correcting text: {str(e)}")
            return text  # Return original on error
