from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from pathlib import Path
from typing import List, Tuple

from config_handlers.app_info_config_handler import AppInfoConfigHandler
from config_handlers.entity_set_models_config_handler import (
    EntitySetModel,
    EntitySetModelsConfigHandler,
    SupportedModel
)

import base64
import html
import random

import requests
import streamlit as st


@st.cache_resource
def _load_app_info_config() -> AppInfoConfigHandler:
    """
    Load application information configuration from the AppInfoConfigHandler.

    :return: An instance of AppInfoConfigHandler containing application information configuration.
    """
    return AppInfoConfigHandler.load_from_file()

@st.cache_resource
def _load_entity_set_models_config() -> EntitySetModelsConfigHandler:
    """
    Load Entity Set Models configuration from the EntitySetModelsConfigHandler.

    :return: An instance of EntitySetModelsConfigHandler containing entity set models configuration.
    """
    return EntitySetModelsConfigHandler.load_from_file()

def _get_app_name() -> str:
    """
    Get the application name from the application information configuration.

    :return: The application name as a string.
    """
    app_info_config_handler = _load_app_info_config()
    return app_info_config_handler.app_name

def _get_app_version() -> str:
    """
    Get the application version from the application information configuration.

    :return: The application version as a string.
    """
    app_info_config_handler = _load_app_info_config()
    return app_info_config_handler.app_version

def _get_app_short_description() -> str:
    """
    Get the application short description from the application information configuration.

    :return: The application short description as a string.
    """
    app_info_config_handler = _load_app_info_config()
    return app_info_config_handler.app_short_description

def _get_backend_url() -> str:
    """
    Get the backend API URL from the application information configuration.

    :return: The backend API URL as a string.
    """
    app_info_config_handler = _load_app_info_config()
    return app_info_config_handler.backend_url

def _get_entity_set_info() -> str:
    """
    Get the entity set information from the application information configuration.

    :return: The entity set information as a string.
    """
    app_info_config_handler = _load_app_info_config()
    return app_info_config_handler.entity_set_info

def _get_label_type_info() -> str:
    """
    Get the label type information from the application information configuration.

    :return: The label type information as a string.
    """
    app_info_config_handler = _load_app_info_config()
    return app_info_config_handler.label_type_info

def _get_supported_models_info() -> str:
    """
    Get the supported models information from the application information configuration.

    :return: The supported models information as a string.
    """
    app_info_config_handler = _load_app_info_config()
    return app_info_config_handler.supported_models_info

def _get_entity_sets() -> List[EntitySetModel]:
    """
    Get available entity sets from the entity set models configuration.

    :return: A list of entity sets.
    """
    entity_set_models_config_handler = _load_entity_set_models_config()
    return entity_set_models_config_handler.entity_sets

def _get_entity_set_ids() -> List[str]:
    """
    Get IDs of all available entity sets.

    :return: A list of entity set IDs.
    """
    entity_sets = _get_entity_sets()
    return [es.entity_set_id for es in entity_sets]

def _get_entity_set_details(entity_set_id: str) -> EntitySetModel:
    """
    Get details of a specific entity set by ID.
    
    :param entity_set_id: The ID of the entity set.
    :return: An instance of EntitySetModel containing details of the entity set.
    """
    entity_sets = _get_entity_sets()
    for es in entity_sets:
        if es.entity_set_id == entity_set_id:
            return es
    raise ValueError(f"Entity set '{entity_set_id}' not found.")

def _get_supported_model_ids(entity_set_id: str) -> List[str]:
    """
    Get supported model IDs for a specific entity set.
    
    :param entity_set_id: The ID of the entity set.
    :return: A list of supported model IDs.
    """
    entity_sets = _get_entity_sets()
    for es in entity_sets:
        if es.entity_set_id == entity_set_id:
            return [sm.model_id for sm in es.supported_models]
    raise ValueError(f"Entity set '{entity_set_id}' not found.")

def _get_supported_model_details(entity_set_id: str, model_id: str) -> SupportedModel:
    """
    Get details of a specific supported model within a specific entity set.

    :param entity_set_id: The ID of the entity set.
    :param model_id: The ID of the model.
    :return: An instance of SupportedModel containing details of the supported model.
    """
    es = _get_entity_set_details(entity_set_id)
    for sm in es.supported_models:
        if sm.model_id == model_id:
            return sm
    raise ValueError(f"Supported model '{model_id}' not found in entity set '{entity_set_id}'.")

def _set_defaults() -> None:
    """
    Set default values for the Streamlit app.
    
    :return: None
    """
    if "entity_set_id" not in st.session_state:
        st.session_state["entity_set_id"] = "grascco"
    if "label_type" not in st.session_state:
        st.session_state["label_type"] = "Coarse-grained"
    if "model_id" not in st.session_state:
        st.session_state["model_id"] = "xlm-roberta-large"
    if "input_text_area" not in st.session_state:
        st.session_state["input_text_area"] = ""
    if "processed_data" not in st.session_state:
        st.session_state["processed_data"] = None

def _get_base_css() -> str:
    """
    Generate the base CSS styles for the application.

    :return: A string containing the CSS styles.
    """
    return """
    <style>

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    
    :root {
        --decorated-output-bg: white;
        --decorated-output-text: black;
        --code-color: black;
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --decorated-output-bg: black;
            --decorated-output-text: white;
            --code-color: wheat;
        }
    }
    body.theme-dark {
        --decorated-output-bg: black;
        --decorated-output-text: white;
        --code-color: wheat;
    }

    .label-extra { 
        padding: 2px 6px; 
        border-radius: 5px; 
        color: black; 
    }
        
    .label-token { 
        background-color: wheat !important; 
        text-decoration: line-through; 
    }

    .circle-number {
        display: inline-block;
        width: 40px;
        height: 40px;
        line-height: 33px;
        text-align: center;
        border-radius: 50%;
        border: 2px solid gray;
        font-size: 20px;
        font-weight: bold;
        color: gray;
        margin: 5px 0px;
    }
    
    .decorated-output-div {
        padding: 10px;
        margin-bottom: 15px;
        border: 1px solid #ddd;
        border-radius: 6px;
        background-color: var(--decorated-output-bg);
        color: var(--decorated-output-text);
        line-height: 2.1;
    }
    
    div[data-testid="stCode"] pre {
        border: 1px solid #ddd !important;
        font-family: Arial, sans-serif !important;
        font-size: 16px !important;
        background-color: transparent !important;
        color: var(--code-color) !important;
    }
        
    hr {
        border: none !important;
        border-top: 2px dashed gray !important;
        margin: 20px 0 !important;
        opacity: 1 !important;
    }

    h1, [data-testid="stMarkdownContainer"] h1 {
        font-size: 1.9rem !important;
    }
    
    </style>
    """

def _get_base64_encoded_image(image_path: Path) -> str:
    """
    Get the base64 encoded string of an image.
    
    :param image_path: Path to the image file.
    :return: Base64 encoded string of the image.
    """
    if image_path.exists():
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def _get_markup_for_site_top_section() -> str:
    """
    Generate HTML markup for the top section of the site with logo, title, 
    version, built by and contact information.

    :return: A string containing the HTML markup for the top section.
    """
    return f"""
        <div style='display: flex; align-items: center; justify-content: space-between; gap: 20px; margin-bottom: 30px; flex-wrap: wrap;'>
            <div style='display: flex; align-items: center; gap: 15px; min-width: 300px;'>
                <div style='flex-shrink: 0;'>
                    <img src='data:image/png;base64,{_get_base64_encoded_image(Path("logo.png"))}' width='80' style='display: block;'>
                </div>
                <div style='display: flex; flex-direction: column; justify-content: center;'>
                    <div style='margin: 0; font-size: 1.9rem; font-weight: bold; line-height: 1.2;'>{_get_app_name()}</div>
                    <p style='font-size: 0.75rem; margin: 0; color: #666; line-height: 1.2;'>
                        {_get_app_short_description()}
                    </p>
                    <p style='font-size: 0.75rem; margin: 0; color: #666; line-height: 1.2;'>
                        Version: {_get_app_version()}
                    </p>
                </div>
            </div>
            <div style='text-align: right; min-width: 200px; margin-left: auto;'>
                <p style='font-size: 0.85rem; margin: 2px 0; color: #666;'>
                    Built with ❤️ by
                </p>
                <div style='display: flex; align-items: center; justify-content: flex-end; gap: 8px; margin: 2px 0;'>
                    <img src='data:image/png;base64,{_get_base64_encoded_image(Path("calgo_lab_logo.png"))}' style='height: 1rem; width: auto; display: block;'>
                    <p style='font-size: 1rem; font-weight: bold; margin: 0;'>
                        Cognitive Algorithms Lab
                    </p>
                </div>
                <p style='font-size: 0.8rem; margin: 2px 0;'>
                    🌐 <a href='https://calgo-lab.de' target='_blank' style='color: #1f77b4; text-decoration: none;'>
                        www.calgo-lab.de
                    </a>
                </p>
            </div>
        </div>
        <hr style='
            height: 3px;
            border: none;
            background: linear-gradient(90deg, #00CED1 0%, #FFD700 100%);
            margin: 20px 0 30px 0;
            opacity: 1 !important;
        '>
        """

@st.dialog("What is an Entity Set?")
def _show_entity_set_info() -> None:
    """
    Show entity set information in a dialog.

    :return: None
    """
    st.markdown(_get_entity_set_info(), unsafe_allow_html=True)

def _format_entity_set_display_name(entity_set_id: str) -> str:
    """
    Format the display name for a given entity set ID.
    
    :param entity_set_id: The ID of the entity set.
    :return: A formatted display name for the entity set.
    """
    es = _get_entity_set_details(entity_set_id)
    if es:
        return f"{("+").join(es.corpus_doctypes)} / {es.corpus_name}"
    return entity_set_id

def _update_entity_set_id() -> None:
    """
    Update the entity set ID in the session state and reset related fields.

    :return: None
    """
    st.session_state["entity_set_id"] = st.session_state["entity_set_radio"]
    st.session_state["label_type"] = "Coarse-grained"
    st.session_state["model_id"] = _get_supported_model_ids(st.session_state["entity_set_id"])[0]
    st.session_state["processed_data"] = None

@st.dialog("What are Label Types?")
def _show_label_type_info() -> None:
    """
    Show label type information in a dialog.

    :return: None
    """
    st.markdown(_get_label_type_info(), unsafe_allow_html=True)

def _format_model_id_display_name(model_id: str) -> str:
    """
    Format the display name for a given model ID for a selected entity set.
    
    :param model_id: The ID of the model.
    :return: A formatted display name for the model.
    """
    entity_set_id = st.session_state["entity_set_id"]
    sm = _get_supported_model_details(entity_set_id, model_id)
    if sm:
        return f"{sm.model_type}.{sm.model_name}"
    return model_id

def _update_model_id() -> None:
    """
    Update the model ID in the session state and reset related fields.

    :return: None
    """
    st.session_state["model_id"] = st.session_state["supported_models_radio"]
    st.session_state["processed_data"] = None

def _update_label_type() -> None:
    """
    Update the label type in the session state and reset related fields.

    :return: None
    """
    st.session_state["label_type"] = st.session_state["label_type_radio"]
    st.session_state["processed_data"] = None

@st.dialog("What are Supported Models?")
def _show_supported_models_info() -> None:
    """
    Show supported models information in a dialog.

    :return: None
    """
    st.markdown(_get_supported_models_info(), unsafe_allow_html=True)

def _hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """
    Convert hex color to RGBA with specified alpha.
    
    :param hex_color: Hex color string (e.g., "#9C27B0")
    :param alpha: Alpha value between 0 and 1
    :return: RGBA string (e.g., "rgba(156, 39, 176, 0.9)")
    """
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"

def _get_label_colors(entity_set_id: str, label_id: str) -> Tuple[str, str]:
    """
    Get background and border colors for a specific label.
    
    :param entity_set_id: The entity set identifier
    :param label_id: The label identifier
    :return: Tuple of (background_color, border_color)
    """
    es = _get_entity_set_details(entity_set_id)
    
    for root_label in es.entity_set_labels:
        if root_label.id == label_id:
            return (
                root_label.background_color or "#F3E5F5",
                root_label.border_color or "#E1BEE7"
            )
        
        for idx, fg_label in enumerate(root_label.fine_grained):
            if fg_label.id == label_id:
                if fg_label.id == root_label.id or len(root_label.fine_grained) == 1:
                    return (
                        root_label.background_color or "#F3E5F5",
                        root_label.border_color or "#E1BEE7"
                    )
                
                if fg_label.background_color and fg_label.border_color:
                    return (fg_label.background_color, fg_label.border_color)
                
                alpha_reduction = 0.07 * (idx + 1)
                bg_alpha = max(0.25, 1.0 - alpha_reduction)
                border_alpha = max(0.25, 1.0 - alpha_reduction)
                
                root_bg = root_label.background_color or "#F3E5F5"
                root_border = root_label.border_color or "#E1BEE7"

                return (
                    _hex_to_rgba(root_bg, bg_alpha),
                    _hex_to_rgba(root_border, border_alpha)
                )
    return ("#F3E5F5", "#E1BEE7")

def _get_markup_for_label_legends() -> str:
    """
    Generate HTML markup for label legends based on the current entity set and label type.
    
    :return: A string containing the HTML markup for the label legends.
    """
    entity_set_id = st.session_state["entity_set_id"]
    label_type = st.session_state["label_type"]
    
    es = _get_entity_set_details(entity_set_id)

    labels: List[str] = list()
    if label_type == "Fine-grained":
        labels = [fg_label.id for root_label in es.entity_set_labels for fg_label in root_label.fine_grained]
    elif label_type == "Coarse-grained":
        labels = [root_label.id for root_label in es.entity_set_labels]
    
    html_parts = []
    for label in labels:
        bg_color, border_color = _get_label_colors(entity_set_id, label)
        html_parts.append(
            f'<span class="label-extra" style="background-color: {bg_color}; border: 2px solid {border_color};">{label}</span>'
        )
    
    return " ".join(html_parts)

def _use_example_text() -> None:
    """
    Set a random example text as input.

    :return: None
    """
    es = _get_entity_set_details(st.session_state["entity_set_id"])
    example_texts = es.sample_texts

    if example_texts:
        st.session_state["input_text_area"] = random.choice(example_texts)
        st.session_state["processed_data"] = None

def _process_text() -> None:
    """
    Process the input text by calling the API and storing the result.

    :return: None
    """
    input_text_value = st.session_state.get("input_text_area", "").strip()

    if not input_text_value:
        st.warning("Please enter text before processing.")
        return
    
    payload = {
        "entity_set_id": st.session_state["entity_set_id"],
        "model_id": st.session_state["model_id"],
        "fine_grained": st.session_state["label_type"] == "Fine-grained",
        "input_texts": [input_text_value]
    }

    try:
        url = f"{_get_backend_url()}/api/predict/detect_entities"
        response = requests.post(url, json=payload)
        response.raise_for_status()
        st.session_state["processed_data"] = response.json()
    except requests.exceptions.RequestException as request_exception:
        st.error(f"API Error: {request_exception}")
        st.session_state["processed_data"] = None

def _render_annotated_output(entities, output_text) -> None:
    """
    Render the annotated output with colored labels.
    
    :param entities: List of entity dictionaries
    :param output_text: The text to display
    :return: None
    """
    entity_set_id = st.session_state["entity_set_id"]
    decorated_output = ""
    prev_end = 0
    
    for entity in entities:
        label = entity["Label"]
        token = entity["Token"]

        start_idx = output_text.find(token, prev_end)

        if start_idx != -1:
            decorated_output += html.escape(output_text[prev_end: start_idx])
            bg_color, border_color = _get_label_colors(entity_set_id, label)
            decorated_output += (
                f'<span class="label-extra label-token" style="background-color: {bg_color}; border: 2px solid {border_color};">'
                f'{html.escape(token)}</span> '
            )
            decorated_output += (
                f'<span class="label-extra" style="background-color: {bg_color}; border: 2px solid {border_color};">'
                f'{html.escape(label)}</span>'
            )
            prev_end = start_idx + len(token)

    decorated_output += html.escape(output_text[prev_end:])
    decorated_output = decorated_output.replace("\n", "<br>")

    st.markdown(
        f'<div class="decorated-output-div">{decorated_output}</div>',
        unsafe_allow_html=True
    )

def _display_processed_output() -> None:
    """
    Display the processed API output with annotations.

    :return: None
    """
    if not st.session_state.get("processed_data"):
        return

    output_items = st.session_state["processed_data"]["output"]
    st.subheader("Annotated Output")
    for _, output_item in enumerate(output_items):
        entities = output_item
        output_text = st.session_state.get("input_text_area", "")
        _render_annotated_output(entities, output_text)
        st.divider()



def main() -> None:
    """
    Main function to run the Streamlit app.

    :return: None
    """
    _load_app_info_config()
    _load_entity_set_models_config()

    st.set_page_config(page_title=_get_app_name(), page_icon="favicon.ico")
    
    _set_defaults()

    st.markdown(_get_base_css(), unsafe_allow_html=True)
    
    st.markdown(_get_markup_for_site_top_section(), unsafe_allow_html=True)

    st.button("💡 Entity Set", on_click=_show_entity_set_info)

    st.radio(
        "Entity Set:",
        options=_get_entity_set_ids(),
        index=_get_entity_set_ids().index(st.session_state["entity_set_id"]),
        format_func=_format_entity_set_display_name,
        horizontal=True,
        key="entity_set_radio",
        on_change=_update_entity_set_id,
        label_visibility="collapsed"
    )

    st.button("💡 Label Type", on_click=_show_label_type_info)

    st.radio(
        "Label Type:",
        options=["Fine-grained", "Coarse-grained"],
        index=["Fine-grained", "Coarse-grained"].index(st.session_state["label_type"]),
        horizontal=True,
        key="label_type_radio",
        on_change=_update_label_type,
        label_visibility="collapsed"
    )

    st.button("💡 Supported Models", on_click=_show_supported_models_info)

    st.radio(
        "Supported Models:",
        options=_get_supported_model_ids(st.session_state["entity_set_id"]),
        index=_get_supported_model_ids(st.session_state["entity_set_id"]).index(st.session_state["model_id"]),
        format_func=_format_model_id_display_name,
        horizontal=True,
        key="supported_models_radio",
        on_change=_update_model_id,
        label_visibility="collapsed"
    )

    st.markdown(
        f'<div class="decorated-output-div">{_get_markup_for_label_legends()}</div>',
        unsafe_allow_html=True
    )

    st.button("Use Example Text", on_click=_use_example_text)

    st.text_area(
        "Enter text here:",
        height=150,
        key="input_text_area"
    )

    st.button("Process", on_click=_process_text)

    _display_processed_output()

if __name__ == "__main__":
    main()