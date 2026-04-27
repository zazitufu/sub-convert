from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PUBLIC_MARKERS = [
    "gotest" + ".win",
    "245a" + "da7b",
    "beff" + "b25a",
    "eb58" + "19a8",
    "10c3" + "ec70",
    "4952" + "8ef8",
    "9906" + "828d",
    "9d7d" + "bda7",
    "182e" + "1611",
    "2992" + "0772",
    "8001" + "6a88",
    "0727" + "08a0",
]


def test_bootstrap_script_checks_prerequisites_and_installs_service():
    script = (ROOT / "deploy" / "bootstrap.sh").read_text(encoding="utf-8")

    assert "os-release" in script
    assert "apt-get" in script
    assert "python3-venv" in script
    assert "python3-pip" in script
    assert "systemctl" in script
    assert "subscription-converter.service" in script
    assert "APP_DIR" in script
    assert "PROJECT_DIR" in script
    assert "VENV_DIR" in script
    assert "SUBSCRIPTIONS_DIR" in script
    assert "SCAN_INTERVAL_SECONDS" in script
    assert "RULES_REFRESH_HOURS" in script
    assert "render_service_file" in script
    assert "Deployment summary" in script
    assert "journalctl -u" in script
    assert "systemctl is-active --quiet" in script
    assert "sed " not in script
    assert "\n    systemctl status" not in script


def test_install_script_delegates_to_bootstrap():
    script = (ROOT / "deploy" / "install.sh").read_text(encoding="utf-8")

    assert "bootstrap.sh" in script


def test_runtime_dependencies_are_declared_without_dev_or_unrelated_packages():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert requirements == ["-e ."]
    assert sorted(pyproject["project"]["dependencies"]) == [
        "PyYAML>=6.0,<7",
        "requests>=2.32,<3",
    ]
    assert pyproject["project"]["optional-dependencies"]["dev"] == ["pytest>=8.3,<9"]

    dependency_text = "\n".join(requirements + pyproject["project"]["dependencies"])
    assert "feedparser" not in dependency_text
    assert "beautifulsoup" not in dependency_text
    assert "pytest" not in dependency_text


def test_public_repository_does_not_contain_known_private_fixture_markers():
    scanned_files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
        and ".pytest_cache" not in path.parts
    ]

    for path in scanned_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        lower_text = text.lower()
        for marker in FORBIDDEN_PUBLIC_MARKERS:
            assert marker.lower() not in lower_text, f"{marker} found in {path}"
