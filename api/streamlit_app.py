"""Dashboard Streamlit — interface visual para o modelo TrafficAI de previsão de severidade."""

from __future__ import annotations

import base64
import json
import time
from datetime import datetime
from io import BytesIO

import requests
import streamlit as st
from PIL import Image

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="TrafficAI — Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://localhost:5000/api"

# ---------------------------------------------------------------------------
# Estilos customizados
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
        .severity-leve     { background:#d4edda; color:#155724; border-radius:8px; padding:12px 20px; font-size:1.4rem; font-weight:700; text-align:center; }
        .severity-moderado { background:#fff3cd; color:#856404; border-radius:8px; padding:12px 20px; font-size:1.4rem; font-weight:700; text-align:center; }
        .severity-critico  { background:#f8d7da; color:#721c24; border-radius:8px; padding:12px 20px; font-size:1.4rem; font-weight:700; text-align:center; }
        .metric-card       { background:#f8f9fa; border-radius:8px; padding:16px; text-align:center; border:1px solid #dee2e6; }
        .metric-value      { font-size:2rem; font-weight:700; color:#0d6efd; }
        .metric-label      { font-size:0.85rem; color:#6c757d; margin-top:4px; }
        .history-row       { border-bottom:1px solid #dee2e6; padding:8px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Estado da sessão
# ---------------------------------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history: list[dict] = []

if "api_ok" not in st.session_state:
    st.session_state.api_ok: bool | None = None

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SEVERITY_EMOJI = {"LEVE": "🟢", "MODERADO": "🟡", "CRÍTICO": "🔴"}
SEVERITY_CSS   = {"LEVE": "severity-leve", "MODERADO": "severity-moderado", "CRÍTICO": "severity-critico"}


def _check_api() -> bool:
    """Verifica se a API Flask está acessível."""
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


def _image_to_b64(image: Image.Image) -> str:
    """Converte uma imagem PIL para string base64."""
    buf = BytesIO()
    image.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()


def _call_predict(
    description: str,
    image_b64: str | None,
    fields: dict,
) -> dict:
    """Chama POST /api/predict e retorna o JSON de resposta."""
    payload: dict = {}
    if description:
        payload["description"] = description
    if image_b64:
        payload["image"] = image_b64
    if fields:
        payload["fields"] = fields

    response = requests.post(
        f"{API_BASE}/predict",
        json=payload,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def _severity_badge(severity: str) -> None:
    css_class = SEVERITY_CSS.get(severity, "severity-moderado")
    emoji = SEVERITY_EMOJI.get(severity, "⚪")
    st.markdown(
        f'<div class="{css_class}">{emoji} {severity}</div>',
        unsafe_allow_html=True,
    )


def _add_to_history(result: dict, description: str, had_image: bool) -> None:
    entry = {
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "severity": result.get("severity", "—"),
        "confidence": result.get("confidence", 0),
        "resource": result.get("resource", "—"),
        "source": result.get("source", "—"),
        "description_preview": (description[:60] + "…") if len(description) > 60 else description or "(sem descrição)",
        "had_image": had_image,
    }
    st.session_state.history.insert(0, entry)


# ---------------------------------------------------------------------------
# Sidebar — status da API e estatísticas rápidas
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🚦 TrafficAI")
    st.caption("Dashboard de Previsão de Severidade")

    st.divider()

    # Status da API
    if st.button("🔄 Verificar API", use_container_width=True):
        st.session_state.api_ok = _check_api()

    if st.session_state.api_ok is None:
        st.session_state.api_ok = _check_api()

    if st.session_state.api_ok:
        st.success("API Flask online ✅")
    else:
        st.error("API Flask offline ❌\nInicie com: `python app.py`")

    st.divider()

    # Estatísticas rápidas
    st.subheader("📊 Estatísticas da Sessão")
    history = st.session_state.history
    total = len(history)

    if total == 0:
        st.info("Nenhuma análise realizada ainda.")
    else:
        counts = {"LEVE": 0, "MODERADO": 0, "CRÍTICO": 0}
        confidences = []
        for h in history:
            sev = h["severity"]
            if sev in counts:
                counts[sev] += 1
            confidences.append(h["confidence"])

        st.metric("Total de análises", total)
        st.metric("Confiança média", f"{sum(confidences) / len(confidences):.1f}%")

        st.markdown("**Distribuição de severidade**")
        for label, count in counts.items():
            pct = (count / total * 100) if total else 0
            emoji = SEVERITY_EMOJI[label]
            st.progress(pct / 100, text=f"{emoji} {label}: {count} ({pct:.0f}%)")

    st.divider()
    st.caption("TrafficAI © 2024 — Modelo Orange3 + Flask")

# ---------------------------------------------------------------------------
# Conteúdo principal
# ---------------------------------------------------------------------------

st.title("🚦 TrafficAI — Análise de Severidade de Acidentes")
st.markdown(
    "Envie uma imagem e/ou descreva o acidente para obter a previsão de severidade "
    "e os recursos de emergência recomendados."
)

tab_analyze, tab_history, tab_about = st.tabs(["🔍 Analisar", "📋 Histórico", "ℹ️ Sobre"])

# ===========================================================================
# Aba: Analisar
# ===========================================================================

with tab_analyze:
    col_input, col_result = st.columns([1, 1], gap="large")

    # ---- Coluna de entrada -------------------------------------------------
    with col_input:
        st.subheader("📥 Dados do Acidente")

        uploaded_file = st.file_uploader(
            "Imagem do acidente (opcional)",
            type=["jpg", "jpeg", "png", "webp"],
            help="Envie uma foto do local do acidente para enriquecer a análise.",
        )

        image_obj: Image.Image | None = None
        image_b64: str | None = None

        if uploaded_file is not None:
            image_obj = Image.open(uploaded_file).convert("RGB")
            st.image(image_obj, caption="Imagem carregada", use_container_width=True)
            image_b64 = _image_to_b64(image_obj)

        description = st.text_area(
            "Descrição do acidente",
            placeholder="Ex.: Colisão frontal na Av. Brasil às 14h. Motorista inconsciente, veículo com fumaça.",
            height=120,
            help="Descreva o acidente com o máximo de detalhes possível.",
        )

        with st.expander("⚙️ Dados contextuais adicionais (opcional)"):
            c1, c2 = st.columns(2)
            with c1:
                especie = st.selectbox(
                    "Tipo de veículo",
                    ["", "Automóvel", "Motocicleta", "Caminhão"],
                    index=0,
                )
                sexo = st.selectbox("Sexo do condutor", ["", "M", "F"], index=0)
                cinto = st.selectbox(
                    "Cinto de segurança",
                    ["", "Sim", "Não"],
                    index=0,
                )
            with c2:
                idade = st.number_input(
                    "Idade do condutor",
                    min_value=0,
                    max_value=120,
                    value=0,
                    step=1,
                    help="0 = não informado",
                )
                pedestre = st.selectbox("Pedestre envolvido?", ["", "Sim", "Não"], index=0)
                turno = st.selectbox(
                    "Turno",
                    ["", "Manhã", "Tarde", "Noite"],
                    index=0,
                )

        # Monta dict de campos extras (apenas os preenchidos)
        extra_fields: dict = {}
        if especie:
            extra_fields["especie_veiculo"] = especie
        if sexo:
            extra_fields["sexo"] = sexo
        if cinto:
            extra_fields["cinto_seguranca"] = cinto
        if idade > 0:
            extra_fields["idade"] = idade
        if pedestre:
            extra_fields["pedestre"] = pedestre
        if turno:
            extra_fields["turno"] = turno

        analyze_btn = st.button(
            "🔍 Analisar Acidente",
            type="primary",
            use_container_width=True,
            disabled=not st.session_state.api_ok,
        )

    # ---- Coluna de resultado -----------------------------------------------
    with col_result:
        st.subheader("📊 Resultado da Análise")

        if analyze_btn:
            if not description and not image_b64 and not extra_fields:
                st.warning("⚠️ Informe ao menos uma descrição, imagem ou dado contextual.")
            else:
                with st.spinner("Analisando acidente…"):
                    try:
                        t0 = time.perf_counter()
                        result = _call_predict(description, image_b64, extra_fields)
                        elapsed = time.perf_counter() - t0

                        severity   = result.get("severity", "MODERADO")
                        confidence = result.get("confidence", 0)
                        resource   = result.get("resource", "—")
                        source     = result.get("source", "heuristic")
                        features   = result.get("features", {})

                        # Badge de severidade
                        _severity_badge(severity)
                        st.markdown("")

                        # Métricas principais
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Confiança", f"{confidence}%")
                        m2.metric("Fonte", "Modelo ML" if source == "model" else "Heurística")
                        m3.metric("Tempo", f"{elapsed:.2f}s")

                        st.info(f"🚑 **Recurso recomendado:** {resource}")

                        # Features extraídas
                        if features:
                            with st.expander("🔬 Features extraídas pelo modelo"):
                                feature_display = {
                                    "Turno": features.get("turno", "—"),
                                    "Hora": features.get("hora", "—"),
                                    "Espécie do veículo": features.get("especie_veiculo", "—"),
                                    "Sexo": features.get("sexo", "—"),
                                    "Idade": features.get("idade", "—"),
                                    "Cinto de segurança": features.get("cinto_seguranca", "—"),
                                    "Pedestre": features.get("pedestre", "—"),
                                    "Passageiro": features.get("passageiro", "—"),
                                    "Dia da semana": features.get("dia_semana", "—"),
                                }
                                for k, v in feature_display.items():
                                    st.markdown(f"- **{k}:** {v}")

                        _add_to_history(result, description, had_image=image_b64 is not None)

                    except requests.exceptions.ConnectionError:
                        st.error("❌ Não foi possível conectar à API Flask. Verifique se ela está rodando em http://localhost:5000.")
                    except requests.exceptions.Timeout:
                        st.error("⏱️ A API demorou demais para responder. Tente novamente.")
                    except requests.exceptions.HTTPError as exc:
                        try:
                            detail = exc.response.json().get("error", str(exc))
                        except Exception:
                            detail = str(exc)
                        st.error(f"❌ Erro da API: {detail}")
                    except Exception as exc:
                        st.error(f"❌ Erro inesperado: {exc}")
        else:
            st.markdown(
                """
                <div style="text-align:center; color:#6c757d; margin-top:60px;">
                    <div style="font-size:4rem;">🚗</div>
                    <p style="margin-top:12px;">Preencha os dados à esquerda e clique em <strong>Analisar Acidente</strong>.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ===========================================================================
# Aba: Histórico
# ===========================================================================

with tab_history:
    st.subheader("📋 Histórico de Análises")

    history = st.session_state.history

    if not history:
        st.info("Nenhuma análise realizada nesta sessão.")
    else:
        col_clear, col_export = st.columns([1, 5])
        with col_clear:
            if st.button("🗑️ Limpar histórico"):
                st.session_state.history = []
                st.rerun()
        with col_export:
            json_str = json.dumps(history, ensure_ascii=False, indent=2)
            st.download_button(
                label="⬇️ Exportar JSON",
                data=json_str,
                file_name=f"trafficai_historico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
            )

        st.markdown("---")

        for i, entry in enumerate(history):
            sev = entry["severity"]
            emoji = SEVERITY_EMOJI.get(sev, "⚪")
            with st.container():
                h1, h2, h3, h4 = st.columns([2, 1, 1, 2])
                h1.markdown(f"**{entry['timestamp']}**")
                h2.markdown(f"{emoji} **{sev}**")
                h3.markdown(f"🎯 {entry['confidence']}%")
                h4.markdown(f"🚑 {entry['resource']}")

                st.caption(
                    f"Descrição: {entry['description_preview']} | "
                    f"Imagem: {'Sim' if entry['had_image'] else 'Não'} | "
                    f"Fonte: {entry['source']}"
                )
                st.markdown("---")

# ===========================================================================
# Aba: Sobre
# ===========================================================================

with tab_about:
    st.subheader("ℹ️ Sobre o TrafficAI Dashboard")

    st.markdown(
        """
        ### O que é o TrafficAI?

        O **TrafficAI** é um sistema de previsão de severidade de acidentes de trânsito que combina:

        - 🤖 **Modelo de Machine Learning** treinado com Orange3 (Random Forest)
        - 🌐 **API REST** construída com Flask
        - 📊 **Dashboard interativo** construído com Streamlit (esta interface)

        ### Como funciona?

        1. O usuário fornece uma **descrição textual** do acidente e/ou uma **imagem** do local.
        2. O sistema extrai **features** relevantes (turno, tipo de veículo, uso de cinto, etc.).
        3. O modelo classifica a severidade em **LEVE**, **MODERADO** ou **CRÍTICO**.
        4. O sistema recomenda os **recursos de emergência** adequados.

        ### Níveis de severidade

        | Nível | Descrição | Recurso recomendado |
        |-------|-----------|---------------------|
        | 🟢 LEVE | Danos materiais leves, sem feridos graves | Viatura de Trânsito |
        | 🟡 MODERADO | Feridos com necessidade de atendimento médico | SAMU + Guarda Municipal |
        | 🔴 CRÍTICO | Vítimas graves, risco de vida, veículo destruído | SAMU + Bombeiros + Polícia |

        ### Arquitetura

        ```
        Streamlit Dashboard  ──►  Flask API (/api/predict)  ──►  Orange3 Model
             (porta 8501)              (porta 5000)                (.pkcls)
        ```

        ### Como executar

        ```bash
        # Terminal 1 — API Flask
        cd api && python app.py

        # Terminal 2 — Dashboard Streamlit
        cd api && streamlit run streamlit_app.py
        ```
        """
    )
