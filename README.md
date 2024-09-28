# Mision-2
Este proyecto es una aplicación interactiva construida con *Tkinter* que permite cargar, visualizar y analizar señales de RF. La aplicación incluye opciones para cargar archivos CSV con datos de frecuencia y magnitud, graficar estos datos y exportar tanto los gráficos como los datos procesados a archivos PDF y CSV.

## Funcionalidades principales
1. *Cargar archivos CSV*: El usuario puede cargar un archivo CSV que contiene datos de frecuencia y magnitud.
2. *Filtrar datos*: Selecciona un rango de frecuencias a visualizar mediante sliders interactivos.
3. *Graficar datos*: Visualiza las gráficas de frecuencia vs magnitud para todas las columnas que contienen datos de magnitud.
4. *Exportar gráficos*: Guarda las gráficas generadas en un archivo PDF.
5. *Exportar datos*: Filtra los datos según el rango de frecuencias seleccionado y guárdalos en un archivo CSV.

## Requisitos

### Dependencias

Este proyecto requiere de las siguientes bibliotecas de Python:

- tkinter: Biblioteca estándar de Python para interfaces gráficas.
- pandas: Para la manipulación y procesamiento de archivos CSV.
- matplotlib: Para la generación de gráficos y exportación a PDF.
- seaborn: Biblioteca de visualización de datos que complementa a matplotlib.
- numpy: Para operaciones matemáticas (instalada automáticamente con pandas).
  
### Instalación de dependencias

Para instalar las dependencias necesarias, ejecuta el siguiente comando:

```bash
pip install pandas matplotlib seaborn
