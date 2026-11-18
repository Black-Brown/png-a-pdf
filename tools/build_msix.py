"""Build an unsigned Store MSIX using the exact identity from Partner Center."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FOUNDATION = "http://schemas.microsoft.com/appx/manifest/foundation/windows10"
UAP = "http://schemas.microsoft.com/appx/manifest/uap/windows10"
UAP10 = "http://schemas.microsoft.com/appx/manifest/uap/windows10/10"
RESCAP = "http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"


def read_identity(path):
    identity = json.loads(path.read_text(encoding="utf-8-sig"))
    for key in ("PackageName", "Publisher", "PublisherDisplayName", "DisplayName", "Version"):
        value = identity.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Falta {key}. Copia su valor exacto desde Partner Center.")
        if value != value.strip():
            raise ValueError(f"{key} contiene espacios al principio o al final.")
    if not re.fullmatch(r"[A-Za-z0-9.-]{3,50}", identity["PackageName"]):
        raise ValueError("PackageName debe ser Identity/Name, no el nombre visible de la aplicación.")
    if not identity["Publisher"].startswith("CN="):
        raise ValueError("Publisher debe ser el valor completo de Identity/Publisher (CN=...).")
    if not re.fullmatch(r"\d+\.\d+\.\d+\.0", identity["Version"]):
        raise ValueError("Usa una versión de cuatro componentes con revisión final 0, por ejemplo 1.2.0.0.")
    if any(int(part) > 65535 for part in identity["Version"].split(".")):
        raise ValueError("Los componentes de versión no pueden superar 65535.")
    return identity


def find_makeappx():
    direct = shutil.which("makeappx.exe")
    if direct:
        return Path(direct)
    kits = Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Windows Kits/10/bin"
    candidates = list(kits.glob("10.*/x64/makeappx.exe"))
    if not candidates:
        raise FileNotFoundError("Instala Windows SDK para disponer de MakeAppx.exe.")
    return max(candidates, key=lambda p: tuple(int(x) for x in p.parent.parent.name.split(".")))


def generate_assets(destination):
    destination.mkdir(parents=True, exist_ok=True)
    with Image.open(ROOT / "assets/app.png") as icon:
        for name, side in (("StoreLogo.png", 50), ("Square44x44Logo.png", 44), ("Square150x150Logo.png", 150)):
            icon.resize((side, side), Image.Resampling.LANCZOS).save(destination / name)


def write_manifest(destination, identity):
    ET.register_namespace("", FOUNDATION)
    ET.register_namespace("uap", UAP)
    ET.register_namespace("uap10", UAP10)
    ET.register_namespace("rescap", RESCAP)
    def tag(name):
        return f"{{{FOUNDATION}}}{name}"
    package = ET.Element(tag("Package"), IgnorableNamespaces="uap uap10 rescap")
    ET.SubElement(package, tag("Identity"), Name=identity["PackageName"], Publisher=identity["Publisher"], Version=identity["Version"], ProcessorArchitecture="x64")
    properties = ET.SubElement(package, tag("Properties"))
    for key, value in (("DisplayName", identity["DisplayName"]), ("PublisherDisplayName", identity["PublisherDisplayName"]), ("Description", "Conversión local de imágenes PNG a PDF con vista previa."), ("Logo", "Assets\\StoreLogo.png")):
        ET.SubElement(properties, tag(key)).text = value
    resources = ET.SubElement(package, tag("Resources"))
    ET.SubElement(resources, tag("Resource"), Language="es-ES")
    dependencies = ET.SubElement(package, tag("Dependencies"))
    ET.SubElement(dependencies, tag("TargetDeviceFamily"), Name="Windows.Desktop", MinVersion="10.0.19041.0", MaxVersionTested="10.0.26100.0")
    applications = ET.SubElement(package, tag("Applications"))
    application = ET.SubElement(applications, tag("Application"), {
        "Id": "PngToPdf", "Executable": "Runtime\\PNG a PDF.exe",
        f"{{{UAP10}}}RuntimeBehavior": "packagedClassicApp",
        f"{{{UAP10}}}TrustLevel": "mediumIL",
    })
    ET.SubElement(application, f"{{{UAP}}}VisualElements", DisplayName=identity["DisplayName"], Description="Convierte imágenes PNG a PDF.", Square150x150Logo="Assets\\Square150x150Logo.png", Square44x44Logo="Assets\\Square44x44Logo.png", BackgroundColor="transparent")
    capabilities = ET.SubElement(package, tag("Capabilities"))
    ET.SubElement(capabilities, f"{{{RESCAP}}}Capability", Name="runFullTrust")
    ET.indent(package)
    ET.ElementTree(package).write(destination, encoding="utf-8", xml_declaration=True)


def build(identity, payload=None):
    makeappx = find_makeappx()
    builds = ROOT / "store/build"
    builds.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="msix-", dir=builds))
    package = work / "package"
    package.mkdir()
    if payload is None:
        subprocess.run([
            sys.executable, "-m", "PyInstaller", "--noconfirm", "--onedir", "--windowed",
            "--exclude-module", "numpy", "--name", "PNG a PDF",
            "--icon", str(ROOT / "assets/app.ico"),
            "--add-data", str(ROOT / "assets") + os.pathsep + "assets",
            "--version-file", str(ROOT / "version_info.txt"),
            "--distpath", str(work / "runtime"), "--workpath", str(work / "pyinstaller"),
            "--specpath", str(work), str(ROOT / "png_a_pdf.py"),
        ], check=True)
        payload = work / "runtime/PNG a PDF"
    if not (payload / "PNG a PDF.exe").is_file():
        raise FileNotFoundError("La carpeta de runtime no contiene PNG a PDF.exe.")
    shutil.copytree(payload, package / "Runtime")
    for name in ("LICENSE", "THIRD_PARTY_NOTICES.md", "PRIVACIDAD.md"):
        shutil.copy2(ROOT / name, package / name)
    generate_assets(package / "Assets")
    write_manifest(package / "AppxManifest.xml", identity)
    output = ROOT / "store/dist"
    output.mkdir(parents=True, exist_ok=True)
    msix = output / f"{identity['PackageName']}_{identity['Version']}_x64.msix"
    if msix.exists():
        raise FileExistsError(f"Ya existe {msix}. Conserva ese archivo o aumenta la versión antes de repetir.")
    subprocess.run([str(makeappx), "pack", "/h", "SHA256", "/d", str(package), "/p", str(msix)], check=True)
    print(f"MSIX generado: {msix}\nSin firma propia: destinado a envío a Microsoft Store, no a instalación directa.")
    return msix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identity", type=Path, default=ROOT / "store/identity.json")
    parser.add_argument("--payload", type=Path, help="Runtime ya compilado, completo y con sus dependencias.")
    args = parser.parse_args()
    try:
        identity = read_identity(args.identity)
        build(identity, args.payload)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"No se pudo generar MSIX: {exc}\n")


if __name__ == "__main__":
    main()
