from __future__ import annotations

import uuid
import json
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import DEFAULT_EMBEDDING_MODEL, HUMAN_REVIEW_DISCLAIMER, MAX_FILE_SIZE_BYTES, OLLAMA_MODEL, REPORTS_DIR, TOP_K_RESULTS, UPLOAD_DIR
from src.contract_analyzer import ContractAnalyzer
from src.document_parser import DocumentParseError
from src.llm_client import is_llm_available, llm_provider
from src.logger import log_error
from src.report_generator import ReportGenerator
from ui.chat_view import render_chat_view
from ui.clause_view import render_clause_view
from ui.contract_analysis import render_contract_analysis
from ui.dashboard import render_dashboard
from ui.evidence_view import render_evidence_view
from ui.obligation_view import render_obligation_view
from ui.risk_view import render_risk_view
from ui.styles import apply_theme, empty_state, info_banner, page_header


st.set_page_config(
    page_title="AI Contract Review & Risk Analyzer",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Advanced AI-powered contract analysis and risk assessment platform."
    }
)


def show_disclaimer() -> None:
    """Display important disclaimer about human review."""
    st.warning("⚠️ " + HUMAN_REVIEW_DISCLAIMER)


def render_sidebar() -> str:
    """Render enhanced sidebar navigation and return selected page."""
    with st.sidebar:
        # Logo/Title section
        st.markdown(
            '''<div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid var(--border); margin-bottom: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚖️</div>
                <div style="font-size: 1.1rem; font-weight: 700;">Contract Analyzer</div>
                <div class="muted" style="font-size: 0.85rem; margin-top: 0.25rem;">AI-Powered Risk Assessment</div>
            </div>''',
            unsafe_allow_html=True
        )
        
        # Navigation pages
        st.markdown("### 📑 WORKSPACE")
        pages_config = [
            ("Dashboard", "📊", "Contract overview and risk summary"),
            ("Contract Analysis", "📋", "Detailed contract metadata"),
            ("Clauses", "📌", "Extract and analyze clauses"),
            ("Risk Analysis", "🔴", "Potential risks and issues"),
            ("Obligations", "✓", "Contractual obligations"),
            ("Evidence", "🔍", "Source-grounded findings"),
            ("Ask Contract", "💬", "Ask AI about contract"),
        ]
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        # Page selection with styled buttons
        page = st.radio(
            "Select view",
            options=[p[0] for p in pages_config],
            label_visibility="collapsed",
            format_func=lambda x: f"{next(p[1] for p in pages_config if p[0] == x)} {x}"
        )
        
        st.markdown("---")
        
        # Settings
        st.markdown("### ⚙️ SETTINGS")
        if st.button("Settings", use_container_width=True):
            page = "Settings"
        
        st.markdown("---")
        
        # AI Engine status
        st.markdown("### 🤖 AI ENGINE")
        provider = llm_provider()
        available = is_llm_available()
        
        status_color = "#2ed8b6" if available else "#ff5757"
        status_text = "Connected" if available else "Unavailable"
        status_icon = "✓" if available else "✗"
        
        st.markdown(
            f'''<div class="surface" style="background: linear-gradient(135deg, rgba(46, 216, 182, 0.05) 0%, rgba(46, 216, 182, 0.02) 100%); border-left: 4px solid {status_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div class="eyebrow">Provider</div>
                        <div style="color: var(--text);">{provider.upper()}</div>
                    </div>
                    <div style="font-size: 2rem; color: {status_color};">{status_icon}</div>
                </div>
                <div class="muted" style="font-size: 0.85rem; margin-top: 0.5rem;">Model: {OLLAMA_MODEL}</div>
                <div class="muted" style="font-size: 0.85rem;">Status: {status_text}</div>
            </div>''',
            unsafe_allow_html=True,
        )
        
        if provider == "ollama" and not available:
            info_banner(
                "Ollama Not Reachable",
                "Start Ollama locally or switch to OpenAI in the .env file.",
                "warning"
            )
        elif provider == "none":
            info_banner(
                "No Remote LLM Configured",
                "The app will operate in offline fallback mode.",
                "info"
            )
        
        st.markdown("---")
        
        # Export section (shown when contract is analyzed)
        analysis = st.session_state.get("analysis", {})
        if analysis and page != "Settings":
            st.markdown("### 📥 EXPORT")
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            report_path = REPORTS_DIR / f"{analysis['contract_id']}.pdf"
            try:
                ReportGenerator.generate_pdf_report(report_path, analysis)
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📄 PDF Report",
                        report_path.read_bytes(),
                        file_name="contract-review-report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                with col2:
                    st.download_button(
                        "📊 JSON Data",
                        json.dumps(analysis, ensure_ascii=False, indent=2),
                        file_name="contract-analysis.json",
                        mime="application/json",
                        use_container_width=True
                    )
            except (OSError, ValueError) as exc:
                log_error(f"Report generation failed: {exc}")
    
    return page


def main() -> None:
    apply_theme()
    
    # Initialize session state
    if "analysis" not in st.session_state:
        st.session_state.analysis = {}

    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Show disclaimer at the top
    show_disclaimer()
    
    # Get current analysis
    analysis = st.session_state.get("analysis", {})
    
    # Settings page
    if page == "Settings":
        page_header("Settings", "Configure application preferences", "⚙️ / SETTINGS")
        
        st.markdown("### 🔧 Runtime Configuration")
        provider = llm_provider()
        settings_data = [
            ["AI Provider", provider.title()],
            ["Model", OLLAMA_MODEL],
            ["Embedding Model", DEFAULT_EMBEDDING_MODEL],
            ["Retrieval Count", str(TOP_K_RESULTS)],
            ["Maximum Upload Size", "20 MB"],
            ["Ollama Status", "Connected" if is_llm_available() else "Unavailable"],
        ]
        settings_df = pd.DataFrame(settings_data, columns=["Setting", "Value"])
        st.dataframe(settings_df, hide_index=True, use_container_width=True)
        st.caption("ℹ️ Configuration is loaded from the project .env file. Secrets are never displayed.")
    
    # Dashboard page
    elif page == "Dashboard":
        if not analysis:
            # Upload section for new users
            page_header(
                "AI Contract Review & Risk Analyzer",
                "Analyze contracts in minutes with source-grounded AI review",
                "01 / UPLOAD"
            )
            
            st.markdown(
                '''<div class="surface" style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(0, 212, 255, 0.02) 100%); border-left: 4px solid var(--accent);">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">📄</div>
                    <h3>Upload Contract</h3>
                    <div class="muted">Drop your contract here or browse files</div>
                    <div class="muted" style="margin-top: 0.5rem;">PDF, DOCX, TXT · Maximum file size: 20 MB</div>
                </div>''',
                unsafe_allow_html=True,
            )
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload contract",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed" if not analysis else "visible"
        )
        
        if uploaded_file is not None:
            file_size_kb = len(uploaded_file.getvalue()) / 1024
            st.caption(f"📎 Selected: {Path(uploaded_file.name).name} · {file_size_kb:.1f} KB")
            
            if st.button("🚀 Analyze Contract", type="primary", use_container_width=True):
                try:
                    file_bytes = uploaded_file.getvalue()
                    if not file_bytes:
                        raise DocumentParseError("The uploaded file is empty.")
                    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
                        raise DocumentParseError("File is too large. Maximum size is 20 MB.")
                    
                    original_name = Path(uploaded_file.name).name
                    suffix = Path(original_name).suffix.lower()
                    upload_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
                    upload_path.parent.mkdir(parents=True, exist_ok=True)
                    upload_path.write_bytes(file_bytes)
                    
                    with st.status("🔄 Analyzing contract", expanded=True) as status:
                        st.write("✓ Document uploaded")
                        st.write("✓ Extracting text and identifying sections")
                        st.write("✓ Building semantic index")
                        st.write("⏳ Analyzing obligations and potential risks")
                        
                        st.session_state.analysis = ContractAnalyzer().analyze_contract(upload_path)
                        status.update(
                            label="✅ Analysis complete",
                            state="complete",
                            expanded=False
                        )
                    
                    st.success("✨ Contract analysis completed successfully!")
                    st.rerun()
                except (DocumentParseError, OSError, RuntimeError, ValueError) as exc:
                    log_error(f"Contract analysis failed: {exc}")
                    st.error(f"❌ Unable to analyze this contract: {exc}")
        
        # Show dashboard if contract is analyzed
        if analysis:
            render_dashboard(analysis)
    
    # Other pages
    else:
        if page == "Contract Analysis":
            render_contract_analysis(analysis)
        elif page == "Clauses":
            render_clause_view(analysis)
        elif page == "Risk Analysis":
            render_risk_view(analysis)
        elif page == "Obligations":
            render_obligation_view(analysis)
        elif page == "Ask Contract":
            render_chat_view(analysis)
        elif page == "Evidence":
            render_evidence_view(analysis)


if __name__ == "__main__":
    main()
