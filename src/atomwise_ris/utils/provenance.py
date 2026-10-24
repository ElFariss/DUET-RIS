from pathlib import Path
import hashlib,json


def write_json(path, value):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def source_versions():
    root=Path(__file__).resolve().parents[3]
    files=list((root/'src').rglob('*.py'))+list((root/'scripts').glob('*.py'))+list((root/'configs').rglob('*.json'))
    return {str(p.relative_to(root)):sha256(p) for p in sorted(files)}
