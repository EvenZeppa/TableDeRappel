import csv
import random
import os
import time

# -------------------------------
# Couleurs
# -------------------------------
def rouge(texte):
    return f"\033[91m{texte}\033[0m"

def vert(texte):
    return f"\033[92m{texte}\033[0m"

def bleu(texte):
    return f"\033[94m{texte}\033[0m"

# -------------------------------
# Charger table de rappel
# -------------------------------
table_rappel = []

with open('table_rappel.csv', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # sauter l'en-tête si présent
    for row in reader:
        if len(row) >= 2:
            table_rappel.append((row[0].strip(), row[1].strip()))

if not table_rappel:
    print("Erreur : table de rappel vide ou fichier non trouvé.")
    exit()

# -------------------------------
# Charger ou créer stats CSV (ajout du temps moyen)
# -------------------------------
stats_file = 'stats_rappel.csv'
stats = {}

if os.path.exists(stats_file):
    with open(stats_file, encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            # Supporter anciennes versions à 4 colonnes
            if len(row) == 4:
                nombre, mot, score_nm, score_mn = row
                stats[(nombre, mot)] = [int(score_nm), int(score_mn), 0.0]
            elif len(row) >= 5:
                nombre, mot, score_nm, score_mn, temps_moy = row
                stats[(nombre, mot)] = [int(score_nm), int(score_mn), float(temps_moy)]
else:
    for nombre, mot in table_rappel:
        stats[(nombre, mot)] = [0, 0, 0.0]

# Vérifier que toutes les paires de la table sont bien dans les stats
for nombre, mot in table_rappel:
    if (nombre, mot) not in stats:
        stats[(nombre, mot)] = [0, 0, 0.0]



# -------------------------------
# Afficher les 10 correspondances les moins connues
# -------------------------------
def afficher_moins_connus(stats, n=10):
    # score global = somme des deux sens
    tri = sorted(stats.items(), key=lambda x: x[1][0] + x[1][1])
    print("\n--- 10 correspondances les moins connues ---")
    for i, ((nombre, mot), valeurs) in enumerate(tri[:n], 1):
        # valeurs = [score_nm, score_mn, temps_moy]
        score_nm = valeurs[0]
        score_mn = valeurs[1]
        temps_moy = valeurs[2] if len(valeurs) > 2 else 0.0

        score_nm_col = rouge(score_nm) if score_nm < 0 else vert(score_nm)
        score_mn_col = rouge(score_mn) if score_mn < 0 else vert(score_mn)

        print(
            f"{i}. {rouge(nombre)} ↔ {vert(mot)} | "
            f"Score nombre->mot: {score_nm_col}, mot->nombre: {score_mn_col}, "
            f"temps moyen: {bleu(f'{temps_moy:.2f}s/lettre')}"
        )
    print("--------------------------------------------\n")

# -------------------------------
# Afficher les 10 correspondances les plus connues
# -------------------------------
def afficher_plus_connus(stats, n=10):
    # score global = somme des deux sens
    tri = sorted(stats.items(), key=lambda x: x[1][0] + x[1][1], reverse=True)
    print("\n--- 10 correspondances les plus connues ---")
    for i, ((nombre, mot), valeurs) in enumerate(tri[:n], 1):
        # valeurs = [score_nm, score_mn, temps_moy]
        score_nm = valeurs[0]
        score_mn = valeurs[1]
        temps_moy = valeurs[2] if len(valeurs) > 2 else 0.0

        score_nm_col = rouge(score_nm) if score_nm < 0 else vert(score_nm)
        score_mn_col = rouge(score_mn) if score_mn < 0 else vert(score_mn)

        print(
            f"{i}. {rouge(nombre)} ↔ {vert(mot)} | "
            f"Score nombre->mot: {score_nm_col}, mot->nombre: {score_mn_col}, "
            f"temps moyen: {bleu(f'{temps_moy:.2f}s/lettre')}"
        )
    print("--------------------------------------------\n")

afficher_plus_connus(stats)
afficher_moins_connus(stats)

# -------------------------------
# Choix du sens (commun à tous les modes)
# -------------------------------
def ajouter_questions_selon_sens(liste_pairs):
    print("\nChoisis le sens du quiz :")
    print("1 = nombre → mot")
    print("2 = mot → nombre")
    print("3 = les deux")
    sens = input("Ton choix : ").strip()

    for nombre, mot in liste_pairs:
        if sens == "1":
            questions.append(("nombre->mot", nombre, mot))
        elif sens == "2":
            questions.append(("mot->nombre", nombre, mot))
        elif sens == "3":
            questions.append(("nombre->mot", nombre, mot))
            questions.append(("mot->nombre", nombre, mot))
        else:
            print("Choix de sens invalide.")
            exit()

# -------------------------------
# Choix du mode
# -------------------------------
print("Choisissez un mode de quiz :")
print("1 = Par bloc")
print("2 = Focus sur les faibles")
print("3 = Random global")
print("4 = Toute la table")
mode_choisi = input("Votre choix : ").strip()

questions = []

# -------------------------------
# Mode 1 : Par bloc (amélioré)
# -------------------------------
if mode_choisi == "1":
    print("Blocs disponibles : 0=0-9, 1=10-19, 2=20-29, etc.")
    print("Tu peux choisir une plage, par exemple : 0-3 (soit 0 à 39).")
    plage = input("Entrez la plage de blocs (ex: 0-2 ou 5-9) : ").strip()

    # Vérifier format de la plage
    if "-" in plage:
        debut_str, fin_str = plage.split("-")
        if debut_str.isdigit() and fin_str.isdigit():
            bloc_debut = int(debut_str)
            bloc_fin = int(fin_str)
        else:
            print("Plage invalide. Utilisez par exemple : 2-4")
            exit()
    elif plage.isdigit():
        bloc_debut = bloc_fin = int(plage)
    else:
        print("Entrée invalide.")
        exit()

    # Calculer bornes
    start = bloc_debut * 10
    end = (bloc_fin + 1) * 10 - 1

    if end == 99:
        end = 100

    # Filtrer les éléments
    bloc_elements = [pair for pair in table_rappel if start <= int(pair[0]) <= end]

    if not bloc_elements:
        print("Aucune correspondance trouvée pour cette plage.")
        exit()

    ajouter_questions_selon_sens(bloc_elements)
    random.shuffle(questions)

# -------------------------------
# Mode 2 : Focus sur les faibles
# -------------------------------
elif mode_choisi == "2":
    tri = sorted(stats.items(), key=lambda x: x[1][0] + x[1][1])  # score global croissant
    faibles = tri[:20]  # 20 correspondances les plus faibles
    ajouter_questions_selon_sens(faibles)
    random.shuffle(questions)

# -------------------------------
# Mode 3 : Random global
# -------------------------------
elif mode_choisi == "3":
    random_pairs = [random.choice(table_rappel) for _ in range(20)]
    ajouter_questions_selon_sens(random_pairs)
    random.shuffle(questions)

# -------------------------------
# Mode 4 : Toute la table
# -------------------------------
elif mode_choisi == "4":
    ajouter_questions_selon_sens(table_rappel)
    random.shuffle(questions)

else:
    print("Mode invalide")
    exit()

# -------------------------------
# Quiz
# -------------------------------
score_total = 0

mode_chrono = 1
temps_debut = time.time() if mode_chrono else None
temps_debut_total = time.time()

for i, (mode, nombre, mot) in enumerate(questions):
    if mode == "nombre->mot":
        answer = input(f"Question {i+1}: Quel mot correspond au nombre {rouge(nombre)} ? ").strip().lower()
        temps_question = time.time() - temps_debut  # mesurer temps avant correction
        if answer == mot.lower():
            print("✅ Correct !\n")
            score_total += 1
            stats[(nombre, mot)][0] += 1

            # --- Nouveau : calcul temps moyen par lettre ---
            nb_lettres = len(mot)
            if nb_lettres > 0:
                temps_par_lettre = temps_question / nb_lettres
                ancien_temps = stats[(nombre, mot)][2]
                if ancien_temps == 0:
                    nouveau_temps = temps_par_lettre
                else:
                    # moyenne simple entre l'ancien et le nouveau
                    nouveau_temps = (ancien_temps + temps_par_lettre) / 2
                stats[(nombre, mot)][2] = nouveau_temps
            # -----------------------------------------------

        else:
            print(f"❌ Faux ! La bonne réponse est : {vert(mot)}\n")
            stats[(nombre, mot)][0] -= 1
    else:  # mot->nombre
        answer = input(f"Question {i+1}: Quel nombre correspond au mot '{vert(mot)}' ? ").strip()
        if answer == nombre:
            print("✅ Correct !\n")
            score_total += 1
            stats[(nombre, mot)][1] += 1
        else:
            print(f"❌ Faux ! La bonne réponse est : {rouge(nombre)}\n")
            stats[(nombre, mot)][1] -= 1
    if mode_chrono:
        temps_question = time.time() - temps_debut
        print(f"(Temps écoulé pour cette question : {bleu(f'{temps_question:.1f}s')})\n")
        temps_debut = time.time()  # réinitialiser pour la question suivante

if mode_chrono:
    temps_total = time.time() - temps_debut_total  # si tu stockes le début du quiz
    print(f"Temps total pour le quiz : {bleu(f'{temps_total:.1f}s')}")

# -------------------------------
# Sauvegarder stats
# -------------------------------
with open(stats_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Nombre','Mot','Score_nombre->mot','Score_mot->nombre','Temps_moyen_par_lettre'])
    for (nombre, mot), (score_nm, score_mn, temps_moy) in stats.items():
        writer.writerow([nombre, mot, score_nm, score_mn, f"{temps_moy:.3f}"])


# -------------------------------
# Résultat final
# -------------------------------
print(f"Quiz terminé ! Tu as obtenu {score_total}/{len(questions)} bonnes réponses.")
print(f"Taux de réussite : {score_total/len(questions)*100:.1f}%")

