import funzioni as fu

#directory di lavoro corrente
cwd = fu.os.getcwd()

#ARGOMENTI utente
parser = fu.argparse.ArgumentParser(add_help=False, description="\
    Questo programma permette di creare una mappa html, colorata in base alle magnitudo \
    dei terremoti occorsi in passato in un determinato rettangolo (definito da voi) e diviso \
    in una girglia nxn (n definito da voi)\
    ")
#necessari
parser.add_argument("path", type=str, help="Nome del file estensione compresa, preceduto dal path dove risiede il file .csv")
parser.add_argument("latitude", type=str, help="Nome della colonna contenente le latitudini nel file .csv")
parser.add_argument("longitude", type=str, help="Nome della colonna contenente le longitudini nel file .csv")
parser.add_argument("magnitude", type=str, help="Nome della colonna contenente le magnitudo nel file .csv")

#print("\nOra devi definire due punti lat/lon, rispettivamente in basso a sx e in alto a dx")
#print("Dove verrà definito un rettangolo")
#print("Inserendo una lat/lon > 180 in almeno uno dei campi, si lascia il rettangolo di default sull'Italia\n")

#facoltativi
parser.add_argument("dim", type=int, nargs='?', default=2, help="Intero n, che definirà la griglia nxn all'interno del rettangolo definito precendentemente")
parser.add_argument("latLL", type=float, nargs='?', default=34.29, help="Latitudine punto in basso a sinistra")
parser.add_argument("lonLL", type=float, nargs='?', default=5.75, help="Longitudine punto in basso a sinistra")
parser.add_argument("latUR", type=float, nargs='?', default=47.29, help="Latitudine punto in alto a destra")
parser.add_argument("lonUR", type=float, nargs='?', default=18.75, help="Longitudine punto in alto a destra")

parser.add_argument('-h', '--help', action='help', default=fu.argparse.SUPPRESS, help='')

args = parser.parse_args()

print("\nIl programma è in esecuzione, attendi il messaggio di confema creazione mappa....\n")


if args.latLL > 90 or args.latLL < -90 or \
args.latUR > 90 or args.latUR < -90 or \
args.lonLL > 180 or args.lonLL < -180 or \
args.lonUR > 180 or args.lonUR < -180:
    print("Il programma funziona soltanto con valori di Latitudine e Longitudine validi ovvero:\n\n90 >= Latitudine >= -90\n180 >= Longitudine >= -180")
    exit()

#Leggo il file csv
eq = fu.pd.read_csv(args.path)

#Elimino le righe che hanno un valore vuoto o per la colonna Latitudine o Longitudine o Magnitudo
eq.dropna(subset=[args.latitude,args.longitude,args.magnitude],inplace=True)

#Elimino tutti i record fuori dal range che prendo in considerazione
indexNames = eq[ eq[args.longitude] < args.lonLL ].index
eq.drop(indexNames,inplace=True)
indexNames2 = eq[ eq[args.longitude] > args.lonUR ].index
eq.drop(indexNames2,inplace=True)
indexNames3 = eq[ eq[args.latitude] < args.latLL ].index
eq.drop(indexNames3,inplace=True)
indexNames4 = eq[ eq[args.latitude] > args.latUR ].index
eq.drop(indexNames4,inplace=True)

#START PROGETTO ALEX

lower_left = [args.latLL, args.lonLL] #Lat e Lon punto in basso a sinistra Italia
upper_right = [args.latUR, args.lonUR] #Lat e Lon punto in alto a destra Italia
m = fu.folium.Map(zoom_start = 5, location=[42.50, 12.50])
grid = fu.get_geojson_grid(upper_right, lower_left , n=args.dim) #Formo la griglia n x n

array_somme = []
num_terr = []
eqC = eq

#Mi vado a calcolare i valori di magnitudo all'interno di ogni rettangolo
for i, geo_json in enumerate(grid):
    
    count=0
    somma_parziale = 0
    
    for index, row in eqC.iterrows():
        x1=grid[i]["properties"]["lower_left"][1]
        y1=grid[i]["properties"]["lower_left"][0]
        x2=grid[i]["properties"]["upper_right"][1]
        y2=grid[i]["properties"]["upper_right"][0]
        x=row[args.latitude]
        y=row[args.longitude]
        
        if (fu.FindPoint(x1, y1, x2, y2, x, y)):
            count += 1
            somma_parziale += row[args.magnitude]
            eqC.drop(index,inplace=True)
                
    array_somme.append(somma_parziale)
    
    num_terr.append(count)

somma = sum(array_somme)
norm = []

#Normalizzo in modo che l'array norm sommi a 1
for i, geo_json in enumerate(grid):
    norm.append(array_somme[i]/somma)

massimo_norm = max(norm)

#Decido il criterio di colorazione di ogni cella della griglia
for i, geo_json in enumerate(grid):
    
    colore_rischio = norm[i]*100/massimo_norm
 
    color = "green"
    opacity = 0.3
    
    if colore_rischio > 10:
        color = "yellow"
    if colore_rischio > 20:
        color = "yellow"
        opacity = 0.4
    if colore_rischio > 30:
        color = "yellow"
        opacity = 0.5
    if colore_rischio > 40:
        color = "red"
    if colore_rischio > 50:
        color = "red"
        opacity = 0.4
    if colore_rischio > 70:
        color = "red"
        opacity = 0.6
    
    gj = fu.folium.GeoJson(geo_json,
                        style_function=lambda feature, color=color, opacity=opacity: {
                                                                        'fillColor': color,
                                                                        'color':"black",
                                                                        'weight': 2,
                                                                        'dashArray': '5, 5',
                                                                        'fillOpacity': opacity,
                                                                    })
     
    popup = fu.folium.Popup("numero di terremoti: {}, Fattore di rischio 0-100: {}".format(num_terr[i], round(colore_rischio,1)))

    gj.add_child(popup)
    
    m.add_child(gj)
    
print("\n***Trovi la tua mappa in "+cwd+" si chiama Mappa.html***\n")

m.save("Mappa.html")