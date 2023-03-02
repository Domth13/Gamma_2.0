import pandas as pd
import numpy as np
import os

##### Konstanten

### Ordner
folder_in = "./data_in"
folder_out = "./data_out"

### Datei (wird automatisch eingelesen)
filename = os.listdir(folder_in)
infile = folder_in + os.sep + filename[0]
outfile = folder_out + "/gamma.xlsx"
out_data = folder_out + "/data.xlsx"

### Spaltenbezeichnungen
var_name = 'Variables'
value_name = 'Values'

### Einstellungen: Spaltenbezeichnungen und Suchterm
id_var = ['VPN']
var_self = ['Bewertung_Attribution_g1_2_gesamt','Bewertung_SN_g1_2_gesamt',
            'Bewertung_Konsens_g1_2_gesamt', 'Bewertung_Konsistenz_g1_2_gesamt','Bewertung_Distinktheit_g1_2_gesamt', 
            'Bewertung_FA_g1_2_gesamt','Bewertung_SV_g1_2_gesamt', 'Bewertung_GWG_g1_2_gesamt']

var_expert = ['Bsp_Attr_Exp','Bsp_SN_Exp','Bsp_KE_Exp','Bsp_KI_Exp','Bsp_Dist_Exp','Bsp_FA_Exp','Bsp_SV_Exp','Bsp_GWG_Exp']
new_var_name = ['Attribution', 'SN', 'Konsens', 'Konsistenz', 'Distinktheit', 'FA', 'SV', 'GWG']
columns = [id_var[0], 'Konzept', 'Selbsteinschätzung', 'Fremdeinschätzung', 'Gamma']
split_var = ['Bsp', 'Bewertung']

### Einstellungen: Variablenauswahl (optional: True oder False)
var_boolean = False
var_selection = ['']

### Einstellungen: Sortieren (optional: True oder False)
sort_boolean = False
sort_by = id_var

##### Funktionen

### Funktion: Datensatz transponieren
def wide_to_long(): 
    if var_boolean:
        df = pd.read_excel(infile, usecols=var_selection)
    else:
        df = pd.read_excel(infile)
    value_var = list(df.columns)
    df_long = pd.melt(df, id_vars=id_var, value_vars=value_var, var_name=var_name, value_name=value_name)
    if sort_boolean:
        df_long = df_long.sort_values(by=sort_by)
    else:
        pass
    return df_long

### Funktion: Datensatz vorbereiten
def prepare_data(df):
    self = df.loc[df.iloc[:,1].str.startswith(split_var[1])]
    self = self.replace(var_self, new_var_name)
    expert = df.loc[df.iloc[:,1].str.startswith(split_var[0])]
    expert = expert.replace(var_expert, new_var_name)
    df_prepared = pd.merge(self, expert, on=[id_var[0], var_name])
    df_prepared.columns = columns[0:4]
    df_prepared = df_prepared.sort_values(by=id_var[0])
    df_prepared = df_prepared.reset_index(drop=True)
    df_prepared.to_excel(out_data, index=False)
    return df_prepared

### Funktion: Gamma Formel
def calculate_gamma(x_list, y_list):
    n = len(x_list)
    concordant = discordant = ties = 0
    
    for i in range(n):
        for j in range(i+1, n):
            if (x_list[i] > x_list[j] and y_list[i] > y_list[j]) or (x_list[i] < x_list[j] and y_list[i] < y_list[j]):
                concordant += 1
            elif (x_list[i] != x_list[j]) and (y_list[i] != y_list[j]):
                discordant += 1
            else:
                ties += 1
    if (concordant + discordant) == 0:
        gamma = np.nan
    else:
        gamma = (concordant - discordant) / (concordant + discordant)

    return gamma

### Funktion: Berechnen Gamma
def compute_gamma(df):
    gamma_dict = {}
    id_list = df.iloc[:,0]
    id_list = id_list.drop_duplicates()
    subsets = np.array_split(df, id_list.shape[0])
   
    for i in subsets:
        df_sub = pd.DataFrame(i)
        id = df_sub.iloc[:,0].tolist()[0]
        x = df_sub.iloc[:,2].tolist()
        y = df_sub.iloc[:,3].tolist()
        gamma_value = calculate_gamma(x, y)
        gamma_dict[id] = gamma_value

    df_gamma = pd.DataFrame(list(gamma_dict.items()), columns=[id_var[0], columns[-1]])

    return df_gamma
    

### Funktion: Funktionen ausführen
def main():
    df = prepare_data(wide_to_long())
    output = compute_gamma(df)
    output.to_excel(outfile, index=False)
    print(output.head())
    print(10*"_")
    print("Gamma erfolgreich berechnet. Ergebnisse im Ordner 'data_out'. :)")
    

if __name__ == '__main__':
    main()