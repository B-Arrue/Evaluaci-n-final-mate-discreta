# =========================================================================
# Asignatura: Matemática Discreta
# Profesor: Elliott Mardones
# Integrantes:
#             • Benjamín Arrué
#             • Benjamín Baeza
#             • Emily Jara
#             • Berenice Llanquinao
# =========================================================================

import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import heapq

# Formato de conexiones: (Ciudad1, Ciudad2, Costo_CLP, Distancia_KM)
conexiones = [
    ("Madrid", "Barcelona", 169500, 620), ("Madrid", "Valencia", 96900, 350),
    ("Madrid", "Zaragoza", 87400, 310), ("Madrid", "Valladolid", 58400, 190),
    ("Madrid", "Albacete", 70100, 250), ("Madrid", "Bilbao", 108900, 400),
    ("Madrid", "Sevilla", 144700, 530), ("Barcelona", "Girona", 28100, 100),
    ("Barcelona", "Zaragoza", 80800, 310), ("Barcelona", "Valencia", 95300, 350),
    ("Valencia", "Murcia", 65800, 230), ("Valencia", "Albacete", 52100, 190),
    ("Murcia", "Almería", 59500, 220), ("Almería", "Granada", 45600, 160),
    ("Granada", "Málaga", 34100, 130), ("Málaga", "Cádiz", 64200, 240),
    ("Cádiz", "Sevilla", 34100, 120), ("Sevilla", "Málaga", 56200, 210),
    ("Sevilla", "Valladolid", 177100, 650), ("Valladolid", "Vigo", 124200, 440),
    ("Bilbao", "Valladolid", 76400, 280), ("Bilbao", "Zaragoza", 88500, 300),
    ("Zaragoza", "Valencia", 84400, 310), ("Zaragoza", "Girona", 94700, 390)
]

ciudades = sorted(list(set([u for u, v, cost, km in conexiones] + [v for u, v, cost, km in conexiones])))

grafo_ady = {c: {} for c in ciudades}
for u, v, cost, km in conexiones:
    grafo_ady[u][v] = {"costo": cost, "km": km}
    grafo_ady[v][u] = {"costo": cost, "km": km}

def dijkstra(grafo, origen, destino):
    distancias = {nodo: float('inf') for nodo in grafo}
    predecesores = {nodo: None for nodo in grafo}
    distancias[origen] = 0
    
    cola_prioridad = [(0, origen)]
    
    while cola_prioridad:
        distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)
        
        if nodo_actual == destino:
            break
            
        if distancia_actual > distancias[nodo_actual]:
            continue
            
        for vecino, datos in grafo[nodo_actual].items():
            peso = datos["costo"]
            camino_alternativo = distancia_actual + peso
            
            if camino_alternativo < distancias[vecino]:
                distancias[vecino] = camino_alternativo
                predecesores[vecino] = nodo_actual
                heapq.heappush(cola_prioridad, (camino_alternativo, vecino))
                
    camino = []
    actual = destino
    while actual is not None:
        camino.insert(0, actual)
        actual = predecesores[actual]
        
    km_totales = 0
    for i in range(len(camino) - 1):
        km_totales += grafo[camino[i]][camino[i+1]]["km"]
        
    return camino, distancias[destino], km_totales

class SistemaEnrutadorG2:
    def __init__(self, root):
        self.root = root
        self.root.title("Navegación Óptima Interurbana")
        self.root.geometry("1350x820")
        self.root.configure(bg="#1e222b")
        
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)
        
        self.estilar_interfaz()
        
        panel_izq = ttk.LabelFrame(root, text=" Configuración de Ruta ", padding=20, style="Card.TLabelframe")
        panel_izq.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        lbl_origen = tk.Label(panel_izq, text="Ciudad de Origen:", font=("Segoe UI", 10, "bold"), fg="#b2bec3", bg="#282c34")
        lbl_origen.pack(anchor="w", pady=(5, 5))
        self.combo_origen = ttk.Combobox(panel_izq, values=ciudades, state="readonly", font=("Segoe UI", 10))
        self.combo_origen.pack(fill="x", pady=(0, 15))
        self.combo_origen.set("Madrid")
        
        lbl_destino = tk.Label(panel_izq, text="Ciudad de Destino:", font=("Segoe UI", 10, "bold"), fg="#b2bec3", bg="#282c34")
        lbl_destino.pack(anchor="w", pady=(5, 5))
        self.combo_destino = ttk.Combobox(panel_izq, values=ciudades, state="readonly", font=("Segoe UI", 10))
        self.combo_destino.pack(fill="x", pady=(0, 20))
        self.combo_destino.set("Vigo")
        
        btn_calcular = ttk.Button(panel_izq, text="Buscar Ruta Óptima", style="Accent.TButton", command=self.procesar_busqueda)
        btn_calcular.pack(fill="x", pady=(0, 20))
        
        lbl_res = tk.Label(panel_izq, text="Detalle del Itinerario:", font=("Segoe UI", 10, "bold"), fg="#b2bec3", bg="#282c34")
        lbl_res.pack(anchor="w", pady=(5, 5))
        
        self.txt_consola = tk.Text(panel_izq, height=18, wrap="word", font=("Consolas", 10), bg="#1e222b", fg="#f8f9fa", relief="flat", highlightthickness=1, highlightbackground="#3e4451")
        self.txt_consola.pack(fill="both", expand=True, pady=5)
        
        self.panel_der = ttk.LabelFrame(root, text=" Mapa Dinámico de Conexiones ", padding=15, style="Card.TLabelframe")
        self.panel_der.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.G = nx.Graph()
        for u, v, cost, km in conexiones:
            self.G.add_edge(u, v, costo=cost, km=km)
            
        self.posiciones_estables = {
            "Vigo": (-3.0, 3.0), "Bilbao": (0.5, 3.2), "Girona": (4.5, 3.0),
            "Barcelona": (4.0, 2.0), "Zaragoza": (1.8, 1.8), "Valladolid": (-1.0, 1.8),
            "Madrid": (0.0, 0.3), "Valencia": (1.8, -0.3), "Albacete": (0.7, -0.8),
            "Sevilla": (-1.8, -2.0), "Cádiz": (-1.8, -3.2), "Málaga": (-0.6, -3.0),
            "Granada": (0.2, -2.3), "Murcia": (1.5, -1.6), "Almería": (1.0, -2.8)
        }
        
        self.fig, self.ax = plt.subplots(figsize=(8, 7), facecolor="#282c34")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.panel_der)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.actualizar_render_mapa()

    def estilar_interfaz(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Card.TLabelframe", background="#282c34", bordercolor="#3e4451", borderwidth=1, relief="solid")
        style.configure("Card.TLabelframe.Label", font=("Segoe UI", 11, "bold"), foreground="#00b894", background="#282c34")
        
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#00b894", borderwidth=0, focuscolor="none", padding=8)
        style.map("Accent.TButton", background=[("active", "#55efc4")])
        
        style.configure("TCombobox", fieldbackground="#21252b", background="#282c34", foreground="#ffffff", arrowcolor="#00b894")

    def actualizar_render_mapa(self, ruta_activa=None):
        self.ax.clear()
        self.ax.set_facecolor("#282c34")
        
        color_nodos_base = "#4b5263"   
        color_aristas_base = "#3e4451" 
        color_resaltado = "#00b894"   
        
        nx.draw_networkx_edges(self.G, self.posiciones_estables, ax=self.ax, edge_color=color_aristas_base, width=1.5)
        nx.draw_networkx_nodes(self.G, self.posiciones_estables, ax=self.ax, node_color=color_nodos_base, node_size=320)
        
        if ruta_activa:
            aristas_camino = list(zip(ruta_activa[:-1], ruta_activa[1:]))
            nx.draw_networkx_edges(self.G, self.posiciones_estables, edgelist=aristas_camino, ax=self.ax, edge_color=color_resaltado, width=4.5)
            nx.draw_networkx_nodes(self.G, self.posiciones_estables, ax=self.ax, nodelist=ruta_activa, node_color=color_resaltado, node_size=460)
            
        pos_etiquetas = {k: (v[0], v[1] + 0.24) for k, v in self.posiciones_estables.items()}
        nx.draw_networkx_labels(self.G, pos_etiquetas, ax=self.ax, font_size=9, font_weight="bold", font_color="#ffffff", font_family="sans-serif")
        
        etiquetas_aristas = { (u, v): f"${d['costo']:,}\n{d['km']} km" for u, v, d in self.G.edges(data=True) }
        nx.draw_networkx_edge_labels(self.G, self.posiciones_estables, edge_labels=etiquetas_aristas, font_size=7, font_color="#abb2bf", font_family="sans-serif", bbox=dict(facecolor="#282c34", edgecolor="none", alpha=0.85), ax=self.ax)
        
        self.ax.set_xlim(-4.0, 5.5)
        self.ax.set_ylim(-4.0, 4.0)
        self.ax.axis('off')  
        self.fig.tight_layout()
        self.canvas.draw()    

    def procesar_busqueda(self):
        origen = self.combo_origen.get()
        destino = self.combo_destino.get()
        
        if origen == destino:
            messagebox.showwarning("Aviso", "La ciudad de origen y la de destino deben ser distintas.")
            return
            
        camino_final, costo_final, km_final = dijkstra(grafo_ady, origen, destino)
        
        self.txt_consola.delete("1.0", tk.END)
        self.txt_consola.insert(tk.END, " ═════════════════════════════════════\n", "borde")
        self.txt_consola.insert(tk.END, "       REPORTES DE RUTA ÓPTIMA        \n", "titulo")
        self.txt_consola.insert(tk.END, " ═════════════════════════════════════\n\n", "borde")
        self.txt_consola.insert(tk.END, " ❖ Trayecto Inicial:\n", "seccion")
        self.txt_consola.insert(tk.END, f"   • Origen:  {origen}\n", "texto")
        self.txt_consola.insert(tk.END, f"   • Destino: {destino}\n\n", "texto")
        self.txt_consola.insert(tk.END, " ❖ Secuencia de Itinerario:\n", "seccion")
        self.txt_consola.insert(tk.END, f"   {' ➔ '.join(camino_final)}\n\n", "ruta")
        self.txt_consola.insert(tk.END, " ❖ Métricas del Viaje:\n", "seccion")
        self.txt_consola.insert(tk.END, f"   • Distancia: {km_final:,} Kilómetros\n", "texto")
        self.txt_consola.insert(tk.END, f"   • Costo:    ${costo_final:,} CLP\n\n", "precio")
        self.txt_consola.insert(tk.END, " ═════════════════════════════════════", "borde")
        
        self.txt_consola.tag_config("borde", foreground="#3e4451")
        self.txt_consola.tag_config("titulo", foreground="#00b894", font=("Consolas", 10, "bold"))
        self.txt_consola.tag_config("seccion", foreground="#b2bec3", font=("Consolas", 10, "bold"))
        self.txt_consola.tag_config("texto", foreground="#f8f9fa", font=("Consolas", 10))
        self.txt_consola.tag_config("ruta", foreground="#55efc4", font=("Consolas", 10, "bold"))
        self.txt_consola.tag_config("precio", foreground="#00b894", font=("Consolas", 11, "bold"))
        
        self.actualizar_render_mapa(ruta_activa=camino_final)

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaEnrutadorG2(root)
    root.mainloop()