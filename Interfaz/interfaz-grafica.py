import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy import signal
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns

class AnalizadorRFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de Señales RF - Interactivo")
        
        # Variables
        self.datos = None
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Botón para cargar CSV
        self.btn_cargar = ttk.Button(main_frame, text="Cargar CSV", command=self.cargar_csv)
        self.btn_cargar.grid(row=0, column=0, pady=5)

        # Frame para sliders
        slider_frame = ttk.LabelFrame(main_frame, text="Rango de Frecuencias")
        slider_frame.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Sliders para rango de frecuencias
        self.freq_min = tk.DoubleVar(value=430000000)
        self.freq_max = tk.DoubleVar(value=438000000)
        ttk.Scale(slider_frame, from_=430000000, to=438000000, orient="horizontal", 
                  variable=self.freq_min, command=self.actualizar_grafico).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Scale(slider_frame, from_=430000000, to=438000000, orient="horizontal", 
                  variable=self.freq_max, command=self.actualizar_grafico).grid(row=1, column=0, sticky=(tk.W, tk.E))
        ttk.Label(slider_frame, textvariable=self.freq_min).grid(row=0, column=1)
        ttk.Label(slider_frame, textvariable=self.freq_max).grid(row=1, column=1)

        # Área para mostrar resultados
        self.resultados_var = tk.StringVar()
        self.label_resultados = ttk.Label(main_frame, textvariable=self.resultados_var, wraplength=400)
        self.label_resultados.grid(row=2, column=0, pady=5)

        # Botones para exportar
        export_frame = ttk.Frame(main_frame)
        export_frame.grid(row=3, column=0, pady=5)
        ttk.Button(export_frame, text="Exportar Gráficos a PDF", command=self.exportar_graficos_pdf).grid(row=0, column=0, padx=5)
        ttk.Button(export_frame, text="Exportar Datos a CSV", command=self.exportar_datos_csv).grid(row=0, column=1, padx=5)

        # Lienzo de Matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(4, weight=1)
        main_frame.columnconfigure(0, weight=1)

    def cargar_csv(self):
        archivo = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if archivo:
            try:
                self.datos = pd.read_csv(archivo, delimiter=";", skiprows=681)
                columnas = self.datos.columns.to_list()
                for columna in columnas:
                    if self.datos[columna].dtype == 'object':
                        self.datos[columna] = pd.to_numeric(self.datos[columna].str.replace(',', '.'))
                self.procesar_datos()
            except pd.errors.ParserError:
                messagebox.showerror("Error", "El archivo CSV tiene un formato incorrecto.")

    def procesar_datos(self):
        self.actualizar_grafico()
        self.calcular_metricas()

    def calcular_metricas(self):
        # Frecuencias de interés
        frecuencias_interes = [431e6, 432e6, 437e6]
        resultados = []

        for freq in frecuencias_interes:
            datos_filtrados = self.datos[(self.datos['Frequency [Hz]'] >= freq - 1e6) & (self.datos['Frequency [Hz]'] <= freq + 1e6)]
            
            if not datos_filtrados.empty:
                # Frecuencia central
                indice_max = datos_filtrados['Magnitude [dBm]'].idxmax()
                freq_central = datos_filtrados.loc[indice_max, 'Frequency [Hz]']

                # Ancho de banda
                bw = self.calcular_ancho_banda(datos_filtrados)

                # Potencia máxima
                potencia_max = datos_filtrados['Magnitude [dBm]'].max()

                # Nivel de ruido (estimado como el percentil 10 de las magnitudes)
                nivel_ruido = np.percentile(datos_filtrados['Magnitude [dBm]'], 10)

                # SNR
                snr = potencia_max - nivel_ruido

                resultados.append(f"Frecuencia {freq/1e6:.1f} MHz:\n"
                                  f"  Frecuencia central: {freq_central/1e6:.3f} MHz\n"
                                  f"  Ancho de banda: {bw/1e3:.2f} kHz\n"
                                  f"  Potencia máxima: {potencia_max:.2f} dBm\n"
                                  f"  Nivel de ruido: {nivel_ruido:.2f} dBm\n"
                                  f"  SNR: {snr:.2f} dB\n")

        self.resultados_var.set("\n".join(resultados))

    def calcular_ancho_banda(self, datos):
        # Calcula el ancho de banda a -3 dB del pico máximo
        max_power = datos['Magnitude [dBm]'].max()
        threshold = max_power - 3
        above_threshold = datos[datos['Magnitude [dBm]'] > threshold]
        return above_threshold['Frequency [Hz]'].max() - above_threshold['Frequency [Hz]'].min()

    def actualizar_grafico(self, *args):
        if self.datos is not None:
            min_freq = self.freq_min.get()
            max_freq = self.freq_max.get()
            datos_filtrados = self.datos[(self.datos['Frequency [Hz]'] >= min_freq) & (self.datos['Frequency [Hz]'] <= max_freq)]

            self.ax.clear()
            self.ax.plot(datos_filtrados['Frequency [Hz]'] / 1e6, datos_filtrados['Magnitude [dBm]'], label='Magnitude [dBm]')

            # Marcar frecuencias de interés
            for freq in [431, 432, 437]:
                self.ax.axvline(x=freq, color='r', linestyle='--', alpha=0.5)
                self.ax.text(freq, self.ax.get_ylim()[1], f'{freq} MHz', rotation=90, va='bottom')

            self.ax.set_title('Espectrograma (Filtrado)')
            self.ax.set_xlabel('Frecuencia (MHz)')
            self.ax.set_ylabel('Potencia (dBm)')
            self.ax.legend()
            self.ax.grid(True)

            self.canvas.draw()

    def exportar_graficos_pdf(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF file", "*.pdf")])
        if archivo:
            try:
                with PdfPages(archivo) as pdf:
                    # Espectrograma
                    self.fig.savefig(pdf, format='pdf')
                    
                    # Waterfall plot
                    fig_waterfall, ax_waterfall = plt.subplots(figsize=(10, 6))
                    datos_filtrados = self.datos[(self.datos['Frequency [Hz]'] >= self.freq_min.get()) & 
                                                 (self.datos['Frequency [Hz]'] <= self.freq_max.get())]
                    sns.heatmap(datos_filtrados.pivot(columns='Frequency [Hz]', values='Magnitude [dBm]'), 
                                cmap='viridis', ax=ax_waterfall)
                    ax_waterfall.set_title('Waterfall Plot')
                    ax_waterfall.set_xlabel('Frecuencia (Hz)')
                    ax_waterfall.set_ylabel('Tiempo')
                    fig_waterfall.savefig(pdf, format='pdf')
                    plt.close(fig_waterfall)

                messagebox.showinfo("Exportar", "Gráficos exportados exitosamente en PDF.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar los gráficos: {str(e)}")

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