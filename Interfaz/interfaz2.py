import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import scipy.signal as signal
class RFSignalAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Señales RF")
        
        # Área de carga de archivos
        self.load_frame = tk.Frame(self.root)
        self.load_frame.pack(pady=10)
        
        self.load_button = tk.Button(self.load_frame, text="Cargar Archivos CSV", command=self.load_files)
        self.load_button.pack()

        self.file_listbox = tk.Listbox(self.load_frame, width=50)
        self.file_listbox.pack(pady=10)

        # Gráficos
        self.fig, self.ax = plt.subplots(2, 1, figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()

        # Panel de opciones
        self.options_frame = tk.Frame(self.root)
        self.options_frame.pack(pady=10)

        self.filter_label = tk.Label(self.options_frame, text="Rango de Frecuencias (MHz):")
        self.filter_label.pack()

        self.freq_range = tk.Scale(self.options_frame, from_=400, to=480, orient=tk.HORIZONTAL, label="Frecuencia", length=300)
        self.freq_range.pack()

        self.analyze_button = tk.Button(self.options_frame, text="Analizar Señal", command=self.analyze_signal)
        self.analyze_button.pack(pady=10)

    def load_files(self):
        file_paths = filedialog.askopenfilenames(title="Seleccionar Archivos CSV", filetypes=(("CSV Files", "*.csv"),))
        for file_path in file_paths:
            self.file_listbox.insert(tk.END, file_path)

    def analyze_signal(self):
        selected_files = self.file_listbox.get(0, tk.END)
        if not selected_files:
            messagebox.showwarning("Advertencia", "Por favor, cargue al menos un archivo CSV.")
            return
        
        for file in selected_files:
            data = pd.read_csv(file)
            print(data.head())  
            self.plot_signal(data)

    def plot_signal(self, data):
        # Aquí deberías ajustar esto según la estructura de tus archivos CSV
        freq = data['Frequency']  # Cambia 'Frequency' al nombre correcto de la columna
        amplitude = data['Amplitude']  # Cambia 'Amplitude' al nombre correcto de la columna
        
        self.ax[0].clear()
        self.ax[1].clear()
        
        # Gráfico de señal
        self.ax[0].plot(freq, amplitude, label='Señal RF')
        self.ax[0].set_title('Gráfico de Señal RF')
        self.ax[0].set_xlabel('Frecuencia (MHz)')
        self.ax[0].set_ylabel('Amplitud')
        self.ax[0].legend()

        # Espectrograma (puedes ajustarlo según los datos)
        self.ax[1].hist2d(freq, amplitude, bins=30, cmap='hot')
        self.ax[1].set_title('Espectrograma')
        self.ax[1].set_xlabel('Frecuencia (MHz)')
        self.ax[1].set_ylabel('Amplitud')

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = RFSignalAnalyzerApp(root)
    root.mainloop()
