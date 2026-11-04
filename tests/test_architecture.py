"""Hlídá směr závislostí web → services → repositories → models (zadání: povinné minimum bod 1).

Kontrola čte importy ze zdrojových souborů (AST), takže selže hned, jak někdo
napíše SQL do routeru nebo HTTP do služby.
"""
import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1] / "app"

# vrstva -> zakázané prefixy importů
FORBIDDEN = {
    "web": ["app.repositories", "app.models", "sqlalchemy.sql", "sqlalchemy.select", "sqlalchemy.text"],
    "services": ["app.web", "fastapi", "starlette", "sqlalchemy.sql", "sqlalchemy.select", "sqlalchemy.text",
                 "sqlalchemy.delete", "sqlalchemy.func", "sqlalchemy.update", "sqlalchemy.insert"],
    "repositories": ["app.services", "app.web", "fastapi", "starlette"],
    "models": ["app.repositories", "app.services", "app.web", "fastapi", "starlette"],
}


def _imports(path: Path) -> list[str]:
    names = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            # `from sqlalchemy import select` → "sqlalchemy.select"
            names += [node.module] + [f"{node.module}.{a.name}" for a in node.names]
    return names


@pytest.mark.parametrize("layer", FORBIDDEN)
def test_layer_does_not_import_upwards_or_skip(layer):
    violations = [
        f"{path.relative_to(APP)}: {name}"
        for path in (APP / layer).rglob("*.py")
        for name in _imports(path)
        if any(name == bad or name.startswith(bad + ".") for bad in FORBIDDEN[layer])
    ]
    assert not violations, "Porušený směr závislostí:\n" + "\n".join(violations)
