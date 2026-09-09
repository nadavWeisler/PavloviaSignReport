import base64
import json
from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest
from PIL import Image


@pytest.fixture
def png_data_uri() -> str:
    image = Image.new("RGB", (10, 10), color=(255, 0, 0))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{encoded}"


@pytest.fixture
def sample_dataframe(png_data_uri: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": ["participant/1", "participant:2"],
            "name": ["Alice", "Bob"],
            "amount": [25, 30.5],
            "completed": [True, False],
            "sign": [png_data_uri, png_data_uri],
        }
    )


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_csv(tmp_path: Path, sample_dataframe: pd.DataFrame) -> Path:
    path = tmp_path / "participants.csv"
    sample_dataframe.to_csv(path, index=False)
    return path


@pytest.fixture
def sample_config(tmp_path: Path) -> Path:
    config = {
        "document": {
            "title": "Configured Report",
            "summary_filename": "summary-output.docx",
            "output_filename_template": "report-{safe_id}.docx",
            "document_intro": "Hello {name}",
            "image_width": 1.0,
            "image_height": 1.0,
            "table_image_width": 0.8,
            "table_image_height": 0.8,
        },
        "columns": [
            {"name": "name", "display_name": "Name", "type": "string"},
            {"name": "amount", "display_name": "Amount", "type": "number"},
            {
                "name": "completed",
                "display_name": "Completed",
                "type": "boolean",
                "true_text": "Done",
                "false_text": "Pending",
            },
            {"name": "sign", "display_name": "Signature", "type": "image"},
        ],
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path
