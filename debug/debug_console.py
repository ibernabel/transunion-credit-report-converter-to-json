import asyncio
import sys
import json
from pathlib import Path
from src.parser.engine import ParserEngine

# Configura logs para ver si el parser se queja (warnings)
import logging
logging.basicConfig(level=logging.WARNING)

async def test_parsing(file_path: str):
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ Error: El archivo '{file_path}' no existe.")
        return

    print(f"🔍 Analizando: {path.name}...")
    
    try:
        # 1. Leer bytes (Simulando lo que hace FastAPI)
        with open(path, "rb") as f:
            content = f.read()

        # 2. Invocar al Motor (Tu nueva lógica v2)
        # Nota: Si es .txt, usa ParserEngine(text). Si es .pdf, usa from_pdf_bytes
        if path.suffix.lower() == ".pdf":
            parser = await ParserEngine.from_pdf_bytes(content)
        else:
            # Fallback para archivos de texto crudo (legacy)
            parser = ParserEngine(content.decode("utf-8"))

        # 3. Obtener el reporte estructurado
        report = await parser.get_report()

        # 4. Imprimir JSON bonito
        # model_dump_json es el método nativo de Pydantic V2
        print("\n✅ EXTRACCIÓN EXITOSA:\n")
        print(report.model_dump_json(indent=2, by_alias=True))

        # 5. Resumen rápido para validación visual
        print("\n--- RESUMEN RÁPIDO ---")
        print(f"👤 Suscriptor: {report.inquirer.subscriber}")
        print(f"📊 Score: {report.score.score if report.score else 'N/A'}")
        print(f"💳 Cuentas Abiertas Detectadas: {len(report.details_open_accounts)}")
        print(f"🛑 Cuentas en Resumen: {len(report.summary_open_accounts)}")

    except Exception as e:
        print(f"\n💥 FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python debug_console.py <ruta_al_pdf>")
        sys.exit(1)
    
    asyncio.run(test_parsing(sys.argv[1]))