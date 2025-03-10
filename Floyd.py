from tkinter import Tk, Label, Button, OptionMenu, StringVar, Listbox, MULTIPLE, messagebox, Frame
import folium
import networkx as nx
import webbrowser
import os
import requests
import polyline

locations = {
    'Estafeta': [23.7345, -99.1450],
    'Domicilio 1': [23.7250, -99.1320],
    'Domicilio 2': [23.7480, -99.1680],
    'Domicilio 3': [23.7600, -99.1540],
    'Domicilio 4': [23.7720, -99.1770],
    'Domicilio 5': [23.7180, -99.1260],
    'Domicilio 6': [23.7550, -99.1900]
}

G = nx.Graph()
G.add_weighted_edges_from([
    ('Estafeta', 'Domicilio 1', 5),
    ('Estafeta', 'Domicilio 2', 10),
    ('Estafeta', 'Domicilio 3', 15),
    ('Estafeta', 'Domicilio 4', 20),
    ('Estafeta', 'Domicilio 5', 7),
    ('Estafeta', 'Domicilio 6', 12)
])

def get_route(start, end):
    """Consulta la API OSRM para obtener la distancia y tiempo estimado."""
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full"
    response = requests.get(url)
    data = response.json()
    if 'routes' in data:
        route = data['routes'][0]
        distance = route['legs'][0]['distance'] / 1000
        duration = route['legs'][0]['duration'] / 60
        geometry = polyline.decode(route['geometry'])
        return {'distance': distance, 'duration': duration, 'geometry': geometry}
    return None

def create_map():
    """Crea un mapa con la ruta seleccionada."""
    m = folium.Map(location=[23.7361, -99.1461], zoom_start=13)
    for name, loc in locations.items():
        folium.Marker(loc, popup=name, icon=folium.Icon(color="blue")).add_to(m)

    start = start_var.get()
    end = end_var.get()

    if start in locations and end in locations:
        route = get_route(locations[start], locations[end])
        if route:
            folium.PolyLine(locations=route['geometry'], color="red", weight=5, opacity=0.7).add_to(m)

    m.save("mapa.html")
    webbrowser.open(f'file://{os.path.realpath("mapa.html")}')

def show_distance():
    """Muestra la distancia y tiempo estimado entre dos puntos."""
    start = start_var.get()
    end = end_var.get()
    if start in locations and end in locations:
        route = get_route(locations[start], locations[end])
        if route:
            messagebox.showinfo("Información de la Ruta",
                f"🚗 Distancia: {route['distance']:.1f} km\n⏳ Tiempo estimado: {route['duration']:.1f} min")
        else:
            messagebox.showerror("Error", "No se pudo calcular la ruta.")
    else:
        messagebox.showerror("Error", "Selecciona una mensajería y un domicilio válido.")

def create_multi_route():
    """Crea un mapa con la ruta para múltiples domicilios."""
    selected_indices = listbox.curselection()
    if not selected_indices:
        messagebox.showerror("Error", "Selecciona al menos un domicilio.")
        return

    selected_domiciles = ["Estafeta"] + [list(locations.keys())[i+1] for i in selected_indices]

    m = folium.Map(location=[23.7361, -99.1461], zoom_start=13)
    for name, loc in locations.items():
        folium.Marker(loc, popup=name, icon=folium.Icon(color="blue")).add_to(m)

    total_distance, total_duration = 0, 0

    for i in range(len(selected_domiciles) - 1):
        start, end = selected_domiciles[i], selected_domiciles[i + 1]
        route = get_route(locations[start], locations[end])
        if route:
            total_distance += route['distance']
            total_duration += route['duration']
            folium.PolyLine(locations=route['geometry'], color="red", weight=5, opacity=0.7).add_to(m)

    messagebox.showinfo("Resumen del Viaje Múltiple",
        f"📍 Distancia total: {total_distance:.1f} km\n⏳ Tiempo estimado: {total_duration:.1f} min")

    m.save("mapa_multi.html")
    webbrowser.open(f'file://{os.path.realpath("mapa_multi.html")}')

root = Tk()
root.title("Algoritmo Floyd-Warshall-Proyecto Final")
root.geometry("550x600")
root.configure(bg="#2C3E50")

Label(root, text="🛵 Selección de Mensajería", font=("Helvetica", 16, "bold"), fg="white", bg="#2C3E50").pack(pady=10)
start_var = StringVar(root)
start_var.set('Estafeta')
start_menu = OptionMenu(root, start_var, *['Estafeta'])
start_menu.config(font=("Arial", 12), bg="#ECF0F1", fg="#2C3E50")
start_menu.pack(pady=5)

Label(root, text="📌 Destino:", font=("Helvetica", 14, "bold"), fg="white", bg="#2C3E50").pack(pady=5)
end_var = StringVar(root)
end_var.set('Domicilio 1')
end_menu = OptionMenu(root, end_var, *list(locations.keys())[1:])
end_menu.config(font=("Arial", 12), bg="#ECF0F1", fg="#2C3E50")
end_menu.pack(pady=5)

Button(root, text="🔍 Calcular Distancia", command=show_distance, font=("Verdana", 12, "bold"),
       bg="#27AE60", fg="white", relief="flat", padx=20, pady=5).pack(pady=10)
Button(root, text="🗺️ Ver Mapa", command=create_map, font=("Verdana", 12, "bold"),
       bg="#2980B9", fg="white", relief="flat", padx=20, pady=5).pack(pady=10)

frame_multi = Frame(root, bg="#34495E", bd=3, relief="ridge")
frame_multi.pack(pady=20, padx=10, fill="x")

Label(frame_multi, text="🚀 Viaje Múltiple", font=("Helvetica", 16, "bold"), fg="white", bg="#34495E").pack(pady=5)
listbox = Listbox(frame_multi, selectmode=MULTIPLE, font=("Courier", 12), bg="#ECF0F1", fg="#2C3E50", height=6)
for domicilio in list(locations.keys())[1:]:
    listbox.insert("end", domicilio)
listbox.pack(pady=5, padx=10)

Button(frame_multi, text="📍 Planear Ruta", command=create_multi_route, font=("Verdana", 12, "bold"),
       bg="#8E44AD", fg="white", relief="flat", padx=20, pady=5).pack(pady=10)

root.mainloop()
