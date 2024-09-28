import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import csv
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages  # Para guardar en PDF

class AnalizadorRFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de Señales RF - Interactivo")
        
        # Variables
        self.datos = None
        self.fig, self.ax = plt.subplots()
        
        # Botón para cargar CSV
        self.btn_cargar = tk.Button(root, text="Cargar CSV", command=self.cargar_csv)
        self.btn_cargar.pack()

        # Crear slider para rango de frecuencias
        self.freq_min = tk.DoubleVar(value=400000000)
        self.freq_max = tk.DoubleVar(value=450000000)
        self.slider_min = tk.Scale(root, from_=400000000, to=480000000, orient="horizontal", label="Frecuencia mínima", variable=self.freq_min, command=self.actualizar_grafico)
        self.slider_min.pack()
        self.slider_max = tk.Scale(root, from_=400000000, to=480000000, orient="horizontal", label="Frecuencia máxima", variable=self.freq_max, command=self.actualizar_grafico)
        self.slider_max.pack()

        # Área para mostrar resultados
        self.resultados_var = tk.StringVar()
        self.label_resultados = tk.Label(root, textvariable=self.resultados_var)
        self.label_resultados.pack()

        # Botón para exportar resultados
        self.btn_exportar_pdf = tk.Button(root, text="Exportar Gráficos a PDF", command=self.exportar_graficos_pdf)
        self.btn_exportar_pdf.pack()

        self.btn_exportar_csv = tk.Button(root, text="Exportar Datos a CSV", command=self.exportar_datos_csv)
        self.btn_exportar_csv.pack()

        # Lienzo de Matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

    # Función para cargar archivo CSV
    def cargar_csv(self):
        archivo = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if archivo:
            try:
                self.datos = pd.read_csv(archivo, delimiter=";", skiprows=681)  # Ignorar líneas problemáticas
                print(self.datos)
                
                columnas = self.datos.columns.to_list()
                for columna in columnas:
                    if self.datos[columna].dtype == 'object':
                        self.datos[columna] = pd.to_numeric(self.datos[columna].str.replace(',', '.'))
                        
                print(self.datos.describe())
                print(self.datos.dtypes)

                self.procesar_datos()
                df = self.datos

                # 2. Limpiar las columnas numéricas para el heatmap (excluyendo las columnas innecesarias)
                df_clean = df.drop(columns=['Unnamed: 1024'], errors='ignore')  # Excluir columna innecesaria
                df_clean = df_clean.drop(columns=['Frequency [Hz]'])  # No incluir la columna de frecuencias en los datos numéricos

                # 3. Configuración del heatmap, usando las frecuencias como etiquetas en el eje Y
                plt.figure(figsize=(10, 8))
                sns.heatmap(df_clean, cmap="YlGnBu", annot=False, cbar=True, yticklabels=df['Frequency [Hz]'])

                # 4. Configuración del gráfico
                plt.title("Heatmap de Magnitudes en dBm con Frecuencias")
                plt.xlabel("Muestras")
                plt.ylabel("Frecuencia [Hz]")
                plt.show()
            except pd.errors.ParserError:
                messagebox.showerror("Error", "El archivo CSV tiene un formato incorrecto.")
            
        
        


    # Función para procesar y graficar los datos
    def procesar_datos(self):
        # Cálculos automáticos (ejemplo básico)
        frecuencia_central = self.datos['Frequency [Hz]'].mean()  # Frecuencia central aproximada
        # snr = self.calcular_snr(self.datos['potencia'], self.datos['ruido'])  # SNR (Relación señal-ruido)

        # Mostrar los resultados en la GUI
        self.resultados_var.set(f"Frecuencia central: {frecuencia_central:.2f} Hz\nSNR:  dB")
        print(frecuencia_central)

        # # Graficar el espectrograma inicial
        self.actualizar_grafico()

    # Función para calcular la relación señal-ruido (SNR)
    def calcular_snr(self, potencia, ruido):
        pass
        # return 10 * np.log10(np.mean(potencia) / np.mean(ruido))

    # Función para actualizar los gráficos según los filtros seleccionados
    def actualizar_grafico(self, *args):
        if self.datos is not None:
            # Filtrar los datos según el rango de frecuencias seleccionado
            min_freq = self.freq_min.get()
            max_freq = self.freq_max.get()
            datos_filtrados = self.datos[(self.datos['Frequency [Hz]'] >= min_freq) & (self.datos['Frequency [Hz]'] <= max_freq)]

            # Limpiar el gráfico anterior
            self.ax.clear()

            # Graficar todas las columnas que empiezan con 'Magnitude [dBm]'
            columnas_magnitud = [col for col in self.datos.columns if col.startswith('Magnitude [dBm]')]
            print(datos_filtrados['Magnitude [dBm]'])

            
            self.ax.plot( datos_filtrados['Frequency [Hz]'], datos_filtrados['Magnitude [dBm]'], label='Magnitude [dBm]')

            # Configurar etiquetas y leyenda
            self.ax.set_title('Espectrograma (Filtrado)')
            self.ax.set_xlabel('Frecuencia (MHz)')
            self.ax.set_ylabel('Potencia (dBm)')
            self.ax.legend()

            # Actualizar el gráfico
            self.canvas.draw()
            
    # Función para exportar gráficos a PDF
    def exportar_graficos_pdf(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF file", "*.pdf")])
        if archivo:
            try:
                with PdfPages(archivo) as pdf:
                    # Limpiar el gráfico por si hay artefactos de un gráfico anterior
                    self.ax.clear()

                    # Volver a graficar los datos filtrados
                    min_freq = self.freq_min.get()
                    max_freq = self.freq_max.get()
                    datos_filtrados = self.datos[(self.datos['Frequency [Hz]'] >= min_freq) & (self.datos['Frequency [Hz]'] <= max_freq)]
                    columnas_magnitud = [col for col in self.datos.columns if col.startswith('Magnitude [dBm]')]

                    for columna in columnas_magnitud:
                        self.ax.plot(datos_filtrados['Frequency [Hz]'], datos_filtrados[columna], label=columna)

                    # Etiquetas y leyenda
                    self.ax.set_title('Espectrograma (Filtrado)')
                    self.ax.set_xlabel('Frecuencia (MHz)')
                    self.ax.set_ylabel('Potencia (dBm)')
                    self.ax.legend()

                    # Guardar la figura en el PDF
                    pdf.savefig(self.fig)  # Guardar el gráfico actual en el PDF
                    plt.close(self.fig)  # Cerrar la figura para evitar artefactos

                messagebox.showinfo("Exportar", "Gráficos exportados exitosamente en PDF.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar los gráficos: {str(e)}")


    # Función para exportar los resultados
    def exportar_datos_csv(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV file", "*.csv")])
        if archivo:
            min_freq = self.freq_min.get()
            max_freq = self.freq_max.get()
            datos_filtrados = self.datos[(self.datos['Frequency [Hz]'] >= min_freq) & (self.datos['Frequency [Hz]'] <= max_freq)]
            datos_filtrados.to_csv(archivo, index=False)
            messagebox.showinfo("Exportar", "Datos exportados exitosamente en CSV.")

# Inicializar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = AnalizadorRFApp(root)
    root.mainloop()

