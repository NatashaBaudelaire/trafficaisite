"""Inferência de severidade — modelo Orange (.pkcls) ou heurística por texto."""

from __future__ import annotations

import pickle
import re
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import Orange

    ORANGE_AVAILABLE = True
except ImportError:
    ORANGE_AVAILABLE = False

ROOT = Path(__file__).resolve().parent.parent
MODEL_CANDIDATES = (
    ROOT / "api" / "models" / "trained_accident_model.pkcls",
    ROOT / "models" / "modelo_acidente_treinado.pkcls",
    ROOT / "models" / "RandomForestModelTrained.pkcls",
    ROOT / "modelo_acidente_treinado.pkcls",
    ROOT / "RandomForestModelTrained.pkcls",
)

SEVERITY_LABELS = {
    "leve": "LEVE",
    "moderado": "MODERADO",
    "critico": "CRÍTICO",
    "crítico": "CRÍTICO",
}

RESOURCES = {
    "LEVE": "Viatura de Trânsito",
    "MODERADO": "SAMU + Guarda Municipal",
    "CRÍTICO": "SAMU + Bombeiros + Polícia",
}

WEEKDAY_NAMES = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)

ESPECIE_MAP = {
    "Automóvel": "AUTOMOVEL",
    "Motocicleta": "MOTOCICLETA",
    "Caminhão": "CAMINHAO",
}

_model = None
_model_path: Path | None = None


def get_model_info() -> dict[str, Any]:
    model = _load_model()
    return {
        "orange_available": ORANGE_AVAILABLE,
        "model_loaded": model is not None,
        "model_path": str(_model_path) if _model_path else None,
    }


def _load_model():
    global _model, _model_path
    if _model is not None:
        return _model
    if not ORANGE_AVAILABLE:
        return None

    load_obj = getattr(getattr(Orange, "serialization", None), "load_obj", None)

    for path in MODEL_CANDIDATES:
        if path.is_file():
            try:
                if load_obj is not None:
                    _model = load_obj(str(path))
                else:
                    with path.open("rb") as handle:
                        _model = pickle.load(handle)
                _model_path = path
                return _model
            except Exception:
                continue
    return None


def _normalize_severity(value: str) -> str:
    key = value.strip().lower().replace("í", "i")
    return SEVERITY_LABELS.get(key, value.upper())


def _extract_features(description: str) -> dict[str, Any]:
    text = description.lower()
    now = datetime.now()

    hour_match = re.search(r"\b(\d{1,2})\s*h\b", text)
    hour = int(hour_match.group(1)) if hour_match else now.hour

    if 6 <= hour < 12:
        turno = "Manhã"
    elif 12 <= hour < 18:
        turno = "Tarde"
    else:
        turno = "Noite"

    cinto = "Não" if re.search(r"sem cinto|não usava cinto|nao usava cinto", text) else "Sim"
    pedestre = "Sim" if re.search(r"pedestre|atropel", text) else "Não"
    passageiro = "Sim" if re.search(r"passageiro|ocupante", text) else "Não"
    condutor = "Sim" if re.search(r"motorista|condutor|piloto", text) else "Sim"

    if re.search(r"moto|motocicleta", text):
        especie = "Motocicleta"
    elif re.search(r"caminhão|caminhao|ônibus|onibus", text):
        especie = "Caminhão"
    else:
        especie = "Automóvel"

    idade_match = re.search(r"(\d{1,2})\s*anos", text)
    idade = int(idade_match.group(1)) if idade_match else 35

    sexo = "F" if re.search(r"\bmulher\b|\bfeminino\b|\bela\b", text) else "M"

    return {
        "condutor": condutor,
        "sexo": sexo,
        "cinto_seguranca": cinto,
        "idade": idade,
        "especie_veiculo": especie,
        "pedestre": pedestre,
        "passageiro": passageiro,
        "dia_semana": now.weekday(),
        "turno": turno,
        "hora": hour,
    }


def _heuristic_severity(description: str) -> tuple[str, int]:
    text = description.lower()
    critical = (
        "crítico",
        "critico",
        "inconsciente",
        "preso",
        "fumaça",
        "fumaca",
        "fogo",
        "incêndio",
        "incendio",
        "grave",
        "morto",
        "destroços",
        "destrocos",
        "explos",
    )
    moderate = (
        "airbag",
        "deformação",
        "deformacao",
        "ferido",
        "dor",
        "moderado",
        "bloqueio",
        "socorros",
        "ambulância",
        "ambulancia",
    )

    if any(word in text for word in critical):
        return "CRÍTICO", 94
    if any(word in text for word in moderate):
        return "MODERADO", 87
    return "LEVE", 91


def _fill_one_hot_instance(model, features: dict[str, Any]):
    domain = model.domain
    instance = Orange.data.Instance(domain)

    for attr in domain.attributes:
        instance[attr.name] = 0.0

    yes_no = {"Sim": "S", "Não": "N", "Sim ": "S"}
    cinto = "SIM" if features.get("cinto_seguranca") == "Sim" else "NÃO"

    one_hot = {
        f"condutor={yes_no.get(features.get('condutor', 'Sim'), 'S')}": 1.0,
        f"sexo={features.get('sexo', 'M')}": 1.0,
        f"cinto_seguranca={cinto}": 1.0,
        "embreagues=NÃO": 1.0,
        f"pedestre={yes_no.get(features.get('pedestre', 'Não'), 'N')}": 1.0,
        f"passageiro={yes_no.get(features.get('passageiro', 'Não'), 'N')}": 1.0,
        f"turno={features.get('turno', 'Manhã')}": 1.0,
    }

    weekday = int(features.get("dia_semana", datetime.now().weekday()))
    one_hot[f"dia_semana={WEEKDAY_NAMES[weekday % 7]}"] = 1.0

    especie_key = ESPECIE_MAP.get(features.get("especie_veiculo", "Automóvel"), "AUTOMOVEL")
    for attr in domain.attributes:
        if attr.name.startswith("especie_veiculo=") and especie_key in attr.name.upper():
            one_hot[attr.name] = 1.0
            break

    for attr in domain.attributes:
        if attr.name == "idade":
            instance[attr.name] = float(features.get("idade", 35))
        elif attr.name in one_hot:
            instance[attr.name] = one_hot[attr.name]

    return instance


def _predict_with_orange(model, features: dict[str, Any]) -> tuple[str, int]:
    instance = _fill_one_hot_instance(model, features)
    prediction = model(instance)

    class_var = model.domain.class_var
    if class_var is not None:
        if isinstance(prediction, (int, float)):
            label = str(class_var.values[int(prediction)])
        else:
            label = str(prediction)
    else:
        label = str(prediction)

    label = _normalize_severity(label)

    confidence = 85
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(instance)
        if probs is not None and len(probs) > 0:
            confidence = int(round(max(probs) * 100))

    return label, confidence


def predict_accident(
    description: str = "",
    image_provided: bool = False,
    fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    features = _extract_features(description) if description else _extract_features("")
    if fields:
        for key, value in fields.items():
            if value is not None and value != "":
                features[key] = value
    model = _load_model()
    source = "heuristic"

    has_input = bool(description) or bool(fields)
    if model is not None and has_input:
        try:
            severity, confidence = _predict_with_orange(model, features)
            source = "model"
        except Exception:
            severity, confidence = _heuristic_severity(description or "")
    elif description:
        severity, confidence = _heuristic_severity(description)
    else:
        severity, confidence = "MODERADO", 82

    if image_provided and not description:
        severity, confidence = "MODERADO", 78
        source = "heuristic"

    return {
        "severity": severity,
        "confidence": confidence,
        "resource": RESOURCES.get(severity, RESOURCES["MODERADO"]),
        "source": source,
        "features": features,
    }
