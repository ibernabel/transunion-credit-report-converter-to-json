# Walkthrough - Validación de Robusticidad del Parser

Se ha corregido y mejorado el motor de extracción para manejar las variaciones de formato detectadas en los reportes de Transunion (PDF).

## Cambios Realizados

### 1. Modelos de Datos (`src/models/report.py`)

- Se marcaron los campos de `InquirerInfo` como `Optional` para mayor robusticidad.

### 2. Motor de Extracción (`src/parser/engine.py`)

- **Limpieza de Texto:** Uso de `unidecode` para normalizar caracteres especiales (como `»` que se convierte en `>>`).
- **Inquirer & Personal Data:** Regex mejorados para manejar valores multilínea y evitar el desbordamiento entre etiquetas.
- **Resumen de Cuentas:** Lógica robusta que detecta el inicio de los datos tras las cabeceras de moneda (`rd$`/`us$`) y omite filas de subtotales.
- **Detalle de Cuentas:**
  - Soporte para múltiples registros bajo un mismo suscriptor (ej. versiones en DOP y USD de una misma tarjeta).
  - Uso del "Vector de Comportamiento" como ancla para separar registros dentro de un bloque.
  - Detección precisa de moneda (`RD$` / `US$`).
  - Herencia de tipo de cuenta si el encabezado siguiente no lo especifica.
  - Exclusión de la sección "TOTALES GENERALES" para evitar registros fantasmas.

## Verificación

Se ejecutó la prueba con el archivo `idequel.pdf`:

```bash
PYTHONPATH=. ./myenv/bin/python3 ./debug/debug_console.py ./legacy_backup/credit_reports/idequel.pdf
```

### Resultados Obtenidos

- ✅ **Inquirer:** Datos de suscriptor, usuario, fecha y hora (AM/PM) extraídos correctamente.
- ✅ **Personal Data:** Todos los campos extraídos sin solapamiento de etiquetas.
- ✅ **Score:** Puntuación (766) y factores de impacto capturados.
- ✅ **Summary:** 2 cuentas detectadas (BHD León y Soluciones Fix).
- ✅ **Details:** 3 registros detectados (BHD León DOP, BHD León USD, Soluciones Fix DOP).

## Mensaje de Commit

`feat: robust parsing of multi-currency account details and improved personal info extraction`
