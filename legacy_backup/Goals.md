## Objetivo: Conseguir un analizador de reportes de historial de credito de Transunion.

### Problemas: Se debe analizar el reporte que viene en formato pdf, pasarlo a un formato que pueda ser leido por un programa.

### Luego hay que convertir el texto en un formato de objeto: diccionario de python.

### Con los datos en formato de diccionario, se puede usar de diferentes formas: Se puede usar para crear un API, para actualizar datos en la base de datos. O se puede usar en una funcionalidad que analize e interprete el reporte de credito. Posiblemente usando una herramienta como GPT-4

Pasos:

1. [x] Crear funcionalidad para leer el archivo pdf y convertirlo a texto plano.
   * Listo -> pdf-to-text.py
2. [x] A partir del texto plano, convertirlo en un diccionario despues de analizar la estructura de dicho text. Listo -> building_variables.py
3. [x] Este diccionario, exportarlo en formato JSON para usarlo en otras herramientas. Listo -> building_variables.py
4. [ ] Optimizar, documentar codigo, hacer pruebas de funcionamiento y pruebas de testing.
5. [ ] Unir todo el codigo a travez de todos los archivos y crear un servicio tipo API con FastAPI, donde subes un Reporte de Credito en formato pdf y te devuelve la informacion principal en formato json.
6. [ ] Implementar la encriptacion del servicio, y el manejo de credenciales y usuarios, permisos, pagos, etc. (tipo Saas)
[ ] Desplegar el servicio de API o Saas en servidor en la nube.
[ ] Crear herramienta que analize e interprete el Reporte de Credito usando un LLM como GPT-4. (No se va a realizar en este proyecto, sino como otro proyecto aparte)

[x] A partir del texto plano, convertirlo en un diccionario despues de analizar la estructura de dicho text.

[x] Este diccionario, exportarlo en formato JSON para usarlo en otras herramientas.

[ ] Optimizar, documentar codigo, hacer pruebas de funcionamiento y pruebas de testing.

[ ] Unir todo el codigo a travez de todos los archivos y crear un servicio tipo API, donde subes un Reposte de Credito en formato pdf y te devuelve la informacion principal en formato json.

[ ] Implementar la encriptacion del servicio, y el manejo de credenciales y usuarios, permisos, pagos, etc. (tipo Saas)

[ ] Desplegar el servicio de API y de Saas en servidor en la nube.

[ ] Crear herramienta que analize e interprete el Reporte de Credito usando un LLM como GPT-4.
