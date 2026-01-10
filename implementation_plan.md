# Plan de Implementación - Refactorización de Robusticidad del Parser (v2.1)

El objetivo es corregir los fallos de validación detectados al ejecutar la prueba con `idequel.pdf` y mejorar la extracción de datos personales y detalles de cuentas, adaptándonos al formato real del PDF.

## 1. Ajustes en Modelos Pydantic (`src/models/report.py`)

- Cambiar campos de `InquirerInfo` a `Optional` o permitir valores por defecto para evitar que un fallo en un campo no crítico rompa toda la ejecución.
- Asegurar que los campos numéricos tengan valores por defecto coherentes.

## 2. Mejoras en el Motor de Extracción (`src/parser/engine.py`)

### A. Flexibilidad en `extract_field`

- Ajustar las expresiones regulares para manejar valores que pueden estar en la misma línea o en la siguiente.
- Usar un patrón más genérico para `consultation_time` (hora) que acepte AM/PM y opcionalmente segundos.

### B. Mejora en Datos Personales

- Los campos como "NOMBRES", "APELLIDOS", "FECHA NACIMIENTO" vienen seguidos de un salto de línea antes del valor.
- Ajustar los regex para capturar el texto que sigue a la etiqueta, saltando posibles saltos de línea.

### C. Refactorización de `parse_account_summaries`

- Abandonar la lógica de "cada 11 líneas" si es posible, o hacerla más tolerante a variaciones de layout (visto en el dump que el subtotal aparece intercalado).

### D. Refactorización de `parse_account_details_v2`

- Validar el anclaje con `>>`.
- Mejorar la extracción de montos y fechas dentro de los bloques.
- Manejar correctamente el "Vector de Comportamiento" que en el PDF aparece con espacios (ej. `000  000  000  000`).

## 3. Pruebas y Verificación

- Ejecutar `debug_console.py` nuevamente.
- Verificar que el JSON resultante sea completo y correcto.
- Ejecutar tests unitarios existentes.

---
**Autor:** Antigravity (Architect Mode)
**Revisado por:** Idequel Bernabel
