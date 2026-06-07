"""
Script d'importation des médicaments, catégories et fournisseurs
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['FLASK_APP'] = 'run.py'

from datetime import datetime, timedelta, date
from app import db, create_app
from app.models import User, Medicine, Supplier, Category, Sale, SaleItem, Activity, DailyReport
import random

random.seed(42)

RAW = """Numero;Nom du Medicament (DCI / Specialite);Categorie Therapeutique;Fournisseurs Principaux a Kinshasa
1;Paracétamol 500mg (Générique);Analgésique / Antipyrétique;Zenufa / Shalina Healthcare
2;Paracétamol 1g (Doliprane);Analgésique / Antipyrétique;Pharmavie / Saint Sauveur (Import Europe)
3;Ibuprofène 400mg;Anti-inflammatoire non stéroïdien;Shalina Healthcare / New Cesamex
4;Ibuprofène 200mg Sirop;Anti-inflammatoire non stéroïdien;Zenufa / Medico Plus
5;Diclofénac Sodique 50mg;Anti-inflammatoire non stéroïdien;AMT Pharma / Prince Pharma
6;Diclofénac 100mg Gel;Anti-inflammatoire topique;Shalina Healthcare (Shaligel)
7;Tramadol 50mg Gélule;Analgésique Opioïde;New Cesamex / AMT Pharma
8;Tramadol 100mg Injectable;Analgésique Opioïde;Unique Pharma / Prince Pharma
9;Aspirine 100mg (Cardio);Antiagrégant / Analgésique;Pharmavie / Saint Sauveur
10;Aspirine 500mg;Analgésique / Antipyrétique;New Cesamex
11;Acide Méfénamique 500mg;Analgésique / Anti-inflammatoire;Shalina Healthcare / AMT Pharma
12;Piroxicam 20mg;Anti-inflammatoire non stéroïdien;New Cesamex / Unique Pharma
13;Méloxicam 15mg;Anti-inflammatoire non stéroïdien;Prince Pharma / Medico Plus
14;Célécoxib 200mg;Anti-inflammatoire (Inhibiteur COX-2);Pharmavie / AMT Pharma
15;Kétoprofène 100mg;Anti-inflammatoire non stéroïdien;Saint Sauveur / New Cesamex
16;Colchicine 1mg;Traitement de la Goutte;Pharmavie / Saint Sauveur
17;Niflumique Acide (Niffluril);Anti-inflammatoire;Pharmavie (Import Europe)
18;Paracétamol Injectable 1g/100ml;Analgésique hospitalier;Unique Pharma / Prince Pharma
19;Morphine Sulfate 10mg;Analgésique Opioïde Majeur;Dépôts Spécialisés / FEDECAME
20;Codéine Phosphate 30mg;Analgésique / Antitussif;New Cesamex
21;Naloxone 0,4mg/ml Injectable;Antidote des opioïdes;FEDECAME
22;Fentanyl 0,05mg/ml Inj;Anesthésique / Analgésique;Dépôts hospitaliers agréés
23;Nifédipine 20mg (Retard);Antihypertenseur;Zenufa / Shalina Healthcare
24;Néofénac (Diclofénac) Inj;Anti-inflammatoire;Shalina Healthcare
25;Prednisone 5mg;Corticoïde / Anti-inflammatoire;New Cesamex / AMT Pharma
26;Prednisolone 20mg Effervescent;Corticoïde;Pharmavie / Saint Sauveur
27;Dexaméthasone 4mg Injectable;Corticoïde puissant;Unique Pharma / Prince Pharma
28;Betaméthasone Crème;Dermocorticoïde;Shalina Healthcare / New Cesamex
29;Hydrocortisone 100mg Injectable;Corticoïde d'urgence;Prince Pharma / AMT Pharma
30;Indométacine 25mg;Anti-inflammatoire non stéroïdien;Medico Plus
31;Artéméther 20mg + Luméfantrine 120mg (Coartem);Antipaludique (CTA);Pharmavie / Saint Sauveur (Novartis)
32;Artéméther 80mg + Luméfantrine 480mg (Générique);Antipaludique (CTA);Shalina (Artefan) / New Cesamex
33;Artéméther + Luméfantrine Sirop suspension;Antipaludique Pédiatrique;Zenufa (Zenart) / Shalina
34;Artésunate Injectable 60mg;Antipaludique Forme Grave;Prince Pharma / AMT Pharma / GHC
35;Artésunate Injectable 120mg;Antipaludique Forme Grave;Prince Pharma / New Cesamex
36;Quinine Sulfate 300mg comprimé;Antipaludique;Zenufa / New Cesamex
37;Quinimax 500mg Injectable;Antipaludique;Pharmavie / Saint Sauveur
38;Quinine Chlorhydrate Injectable 600mg;Antipaludique;Zenufa / Medico Plus
39;Sulfadoxine 500mg + Pyriméthamine 25mg (Maloxine);Antipaludique (TPI femme enceinte);Pharmavie / New Cesamex
40;Dihydroartémisinine + Pipéraquine (P-Alaxin);Antipaludique (CTA);Prince Pharma / GHC
41;Artesunate + Amodiaquine (Camoquin);Antipaludique (CTA);Pharmavie / Grossistes agréés
42;Artéméther Injectable 80mg/ml;Antipaludique;Shalina Healthcare / Medico Plus
43;Atovaquone + Proguanil (Malarone);Antipaludique prophylaxie;Pharmavie (Import Europe)
44;Méfloquine 250mg;Antipaludique;Pharmavie
45;Doxycycline 100mg (Paludisme/Infection);Antibiotique / Antipaludique;Shalina Healthcare / New Cesamex
46;Halofantrine (Halfan);Antipaludique;Pharmavie
47;Amodiaquine 200mg;Antipaludique;New Cesamex
48;Primaquine 15mg;Antipaludique (Radical);FEDECAME
49;Luméfantrine solo (Rare);Antipaludique;Grossistes spécialisés
50;Artésunate Suppositoire 200mg;Antipaludique pré-transfert;FEDECAME
51;Quinine Sirop;Antipaludique Pédiatrique;Zenufa
52;Pyriméthamine 25mg;Antiprotozoaire / Antipaludique;Medico Plus
53;Artemidine Inj;Antipaludique;Unique Pharma
54;Malastop;Antipaludique;New Cesamex
55;Artequick;Antipaludique (CTA);Prince Pharma
56;Amoxicilline 500mg Gélule;Antibiotique (Pénicilline);Zenufa / Shalina Healthcare
57;Amoxicilline 250mg Sirop;Antibiotique Pédiatrique;Zenufa / New Cesamex
58;Amoxicilline + Acide Clavulanique 1g (Augmentin);Antibiotique (Bêta-lactamine);Pharmavie / Saint Sauveur (GSK)
59;Amoxicilline + Acide Clavulanique 1g (Générique);Antibiotique;Shalina (Shalamox) / New Cesamex
60;Amoxicilline + Acide Clavulanique Sirop;Antibiotique Pédiatrique;New Cesamex / Medico Plus
61;Ampicilline 500mg;Antibiotique (Pénicilline);Zenufa / Unique Pharma
62;Ampicilline 1g Injectable;Antibiotique hospitalier;Prince Pharma / AMT Pharma
63;Cloxacilline 500mg Gélule;Antibiotique anti-staphylococcique;Zenufa / Shalina Healthcare
64;Cloxacilline 1g Injectable;Antibiotique;Unique Pharma / Medico Plus
65;Céfuroxime 500mg (Zinnat);Antibiotique (Céphalosporine 2G);Pharmavie / Saint Sauveur
66;Céfuroxime 250mg Générique;Antibiotique;New Cesamex / AMT Pharma
67;Ceftriaxone 1g Injectable;Antibiotique (Céphalosporine 3G);Shalina / New Cesamex / Prince Pharma
68;Ceftriaxone 500mg Injectable;Antibiotique;Unique Pharma / Medico Plus
69;Céfotaxime 1g Injectable;Antibiotique (Céphalosporine 3G);Prince Pharma / AMT Pharma
70;Ceftazidime 1g Injectable;Antibiotique (Anti-pyocyanique);New Cesamex / Unique Pharma
71;Céfixime 200mg Comprimé;Antibiotique (Céphalosporine 3G orale);Shalina / New Cesamex
72;Céfixime Sirop;Antibiotique Pédiatrique;Medico Plus / AMT Pharma
73;Céfadroxil 500mg;Antibiotique (Céphalosporine 1G);New Cesamex
74;Ciprofloxacine 500mg;Antibiotique (Fluoroquinolone);Shalina (Ciproshal) / Zenufa
75;Ciprofloxacine Poche Inj 200mg/100ml;Antibiotique Injectable;Unique Pharma / Prince Pharma
76;Ofloxacine 200mg;Antibiotique (Fluoroquinolone);New Cesamex / AMT Pharma
77;Norfloxacine 400mg;Antibiotique urinaire;Shalina Healthcare
78;Levofloxacine 500mg;Antibiotique (Fluoroquinolone);New Cesamex / Prince Pharma
79;Azithromycine 500mg (Zithromax);Antibiotique (Macrolide);Pharmavie / Saint Sauveur (Pfizer)
80;Azithromycine 500mg (Générique);Antibiotique (Macrolide);Shalina / New Cesamex / Zenufa
81;Érythromycine 500mg;Antibiotique (Macrolide);Zenufa / Medico Plus
82;Érythromycine Sirop;Antibiotique Pédiatrique;Zenufa
83;Clarithromycine 500mg;Antibiotique (Macrolide);New Cesamex / Prince Pharma
84;Gentamicine 80mg Injectable;Antibiotique (Aminoside);Shalina / Unique Pharma
85;Amikacine 500mg Injectable;Antibiotique (Aminoside);Prince Pharma / AMT Pharma
86;Métronidazole 500mg Comprimé;Antibiotique / Antiprotozoaire;Zenufa / Shalina (Rozal)
87;Métronidazole Poche Inj 500mg/100ml;Antibiotique Injectable;Unique Pharma / Prince Pharma
88;Métronidazole Sirop (Flagyl style);Antiparasitaire/Antibiotique;Zenufa / Medico Plus
89;Cotrimoxazole 480mg (Bactrim);Antibiotique (Sulfamide);Zenufa / Shalina Healthcare
90;Cotrimoxazole 960mg (Forte);Antibiotique;New Cesamex / Medico Plus
91;Cotrimoxazole Sirop;Antibiotique Pédiatrique;Zenufa
92;Nitrofurantoïne 100mg (Furadantine);Antibiotique urinaire;Pharmavie / New Cesamex
93;Doxycycline 100mg;Antibiotique tétracycline;Zenufa / Shalina Healthcare
94;Tétracycline 250mg;Antibiotique;Medico Plus
95;Chloramphénicol 250mg Gélule;Antibiotique;Unique Pharma
96;Chloramphénicol 1g Injectable;Antibiotique hospitalier;Prince Pharma
97;Lincomycine 500mg;Antibiotique (Lincosamide);New Cesamex / Unique Pharma
98;Clindamycine 300mg;Antibiotique;New Cesamex / AMT Pharma
99;Vancomycine 500mg Injectable;Antibiotique Glico-peptide;Prince Pharma / Grossistes hospitaliers
100;Imipénème + Cilastatine Inj;Antibiotique de réserve carbapénème;Prince Pharma / Pharmavie
101;Méropénème 1g Injectable;Antibiotique de réserve carbapénème;New Cesamex / Unique Pharma
102;Benzathine Benzylpénicilline 2.4 M UI;Pénicilline Retard (Extencilline);Pharmavie / Prince Pharma
103;Benzylpénicilline (Pénicilline G) 5M UI;Antibiotique Injectable;FEDECAME
104;Phénoxyméthylpénicilline (Pénicilline V);Antibiotique Oral;New Cesamex
105;Rifampicine + Isoniazide (RH);Antituberculeux;Programme National Tuberculose / FEDECAME
106;Éthambutol 400mg;Antituberculeux;FEDECAME
107;Pyrazinamide 500mg;Antituberculeux;FEDECAME
108;Fluconazole 150mg Gélule;Antifongique;Shalina (Flucolich) / New Cesamex
109;Fluconazole Poche Inj 200mg/100ml;Antifongique Injectable;Unique Pharma / Prince Pharma
110;Kétoconazole 200mg Comprimé;Antifongique;Shalina Healthcare
111;Kétoconazole Crème (Kétoderm);Antifongique Topique;Zenufa / Shalina Healthcare
112;Nystatine 100 000 UI Comprimé Vaginal;Antifongique Gynécologique;Zenufa / New Cesamex
113;Nystatine Suspension Orale;Antifongique Buccal;Zenufa / Medico Plus
114;Griséofulvine 500mg;Antifongique cutané/cheveux;New Cesamex / AMT Pharma
115;Amphotéricine B Injectable;Antifongique systémique;Grossistes spécialisés / Hospitalier
116;Albendazole 400mg Comprimé;Anthelminthique (Vermifuge);Zenufa (Zenazole) / Shalina (Benazole)
117;Albendazole Sirop;Vermifuge Pédiatrique;Zenufa / Medico Plus
118;Mébendazole 100mg Comprimé;Anthelminthique;Zenufa / New Cesamex
119;Mébendazole Sirop;Vermifuge Pédiatrique;Zenufa
120;Praziquantel 600mg;Anthelminthique (Bilharziose);FEDECAME / Unique Pharma
121;Ivermectine 3mg;Antiparasitaire (Gale/Onchocercose);FEDECAME / Pharmavie
122;Tinidazole 500mg;Antiprotozoaire / Anti-amibien;Shalina Healthcare / New Cesamex
123;Secnidazole 500mg;Anti-amibien;New Cesamex / Prince Pharma
124;Secnidazole 2g (Dose unique);Anti-amibien / Trichomonase;Pharmavie / Saint Sauveur
125;Nitazoxanide 500mg;Antiparasitaire large spectre;Prince Pharma
126;Oméprazole 20mg Gélule;Inhibiteur de la pompe à protons;Zenufa / Shalina (Omeshal)
127;Oméprazole 40mg Injectable;Inhibiteur de la pompe à protons;Unique Pharma / Prince Pharma
128;Lansoprazole 30mg;Inhibiteur de la pompe à protons;New Cesamex / AMT Pharma
129;Esoméprazole 40mg (Inexium);Inhibiteur de la pompe à protons;Pharmavie / Saint Sauveur (AstraZeneca)
130;Esoméprazole 40mg Générique;Inhibiteur de la pompe à protons;New Cesamex / Prince Pharma
131;Ranitidine 150mg;Anti-H2 / Anti-acide;Shalina Healthcare
132;Hydroxyde d'Aluminium + Magnésium (Maalox);Anti-acide / Pansement gastrique;Pharmavie / Saint Sauveur
133;Trisilicate de Magnésium (Générique);Anti-acide;Zenufa / Shalina Healthcare
134;Métoclopramide 10mg (Primpéran);Antiémétique;Pharmavie / Saint Sauveur
135;Métoclopramide 10mg Générique;Antiémétique;Zenufa / New Cesamex
136;Dompéridone 10mg (Motilium);Antiémétique / Procinétique;Pharmavie / Saint Sauveur
137;Dompéridone Sirop / gouttes;Antiémétique pédiatrique;New Cesamex / Medico Plus
138;Ondansetron 8mg (Zophren);Antiémétique puissant (chimio/post-op);Pharmavie / Prince Pharma
139;Lopéramide 2mg (Imodium);Antidiarrhéique;Pharmavie / Shalina (Lopeshal)
140;Sels de Réhydratation Orale (SRO) Sachet;Correction de la déshydratation;Zenufa / Shalina / New Cesamex
141;Zinc Sulfate 20mg Comprimé dispersible;Adjuvant traitement diarrhée enfant;Zenufa / Medico Plus
142;Phloroglucinol 80mg (Spasfon);Antispasmodique;Pharmavie / Saint Sauveur
143;Spasmo-Canulase ou équivalent;Antispasmodique / Digestif;Pharmavie
144;Butylbromure de Hyoscine 10mg (Buscopan);Antispasmodique;Pharmavie / New Cesamex
145;Butylbromure de Hyoscine Injectable;Antispasmodique Injectable;Unique Pharma / Prince Pharma
146;Lactulose Sirop (Duphalac);Laxatif Osmotique;Pharmavie / Saint Sauveur
147;Bisacodyl 5mg (Dulcolax);Laxatif Stimulant;Pharmavie / New Cesamex
148;Glycérine Suppositoire (Adulte/Enfant);Laxatif Local;Pharmavie / Grossistes locaux
149;Charbon Activé 250mg;Adsorbant intestinal / Ballonnements;Zenufa / New Cesamex
150;Siméthicone (Débridat ou similaire);Régulateur du transit / Ballonnements;Pharmavie / Saint Sauveur
151;Amlodipine 5mg;Antihypertenseur (Inhibiteur calcique);Shalina (Amloshal) / Zenufa
152;Amlodipine 10mg;Antihypertenseur;New Cesamex / AMT Pharma
153;Captopril 25mg;Antihypertenseur (Inhibiteur de l'ECA);Zenufa / Medico Plus
154;Énalapril 20mg;Antihypertenseur (Inhibiteur de l'ECA);New Cesamex / Shalina
155;Lisinopril 10mg;Antihypertenseur;New Cesamex / AMT Pharma
156;Lisinopril + Hydrochlorothiazide;Antihypertenseur combiné;Pharmavie / New Cesamex
157;Losartan 50mg (Cozaar style);Antihypertenseur (Antagoniste ARA-II);New Cesamex / Shalina / Prince Pharma
158;Losartan + Hydrochlorothiazide 50/12.5mg;Antihypertenseur combiné;New Cesamex / Prince Pharma
159;Valsartan 80mg / 160mg;Antihypertenseur (ARA-II);Pharmavie / Saint Sauveur
160;Aténolol 50mg;Bêta-bloquant / Antihypertenseur;Shalina Healthcare
161;Propranolol 40mg;Bêta-bloquant / Hypertension / Anxiété;Zenufa / New Cesamex
162;Carvédilol 6,25mg / 12,5mg;Bêta-bloquant (Insuffisance cardiaque);New Cesamex / Prince Pharma
163;Bisoprolol 5mg;Bêta-bloquant;Pharmavie / New Cesamex
164;Furosémide 40mg Comprimé (Lasilix);Diurétique;Zenufa / Shalina / New Cesamex
165;Furosémide 20mg Injectable;Diurétique d'urgence;Unique Pharma / Prince Pharma
166;Hydrochlorothiazide 25mg;Diurétique Thiazidique;New Cesamex / AMT Pharma
167;Spironolactone 50mg / 100mg (Aldactone);Diurétique épargneur de potassium;Pharmavie / New Cesamex
168;Méthyldopa 250mg (Aldomet);Antihypertenseur central (Femme enceinte);Shalina Healthcare / New Cesamex
169;Hydralazine Injectable;Antihypertenseur d'urgence (Pré-éclampsie);Prince Pharma / FEDECAME
170;Atorvastatine 10mg / 20mg (Tahor style);Hypolipidémiant (Statine);Shalina (Atorshal) / New Cesamex / Prince Pharma
171;Rosuvastatine 10mg;Hypolipidémiant;Pharmavie / Prince Pharma
172;Simvastatine 20mg;Hypolipidémiant;New Cesamex
173;Digoxine 0,25mg;Glycoside cardiotonique;Pharmavie / Grossistes spécialisés
174;Trinitrine Spray / Dérivés nitrés;Antiangoreux (Crise d'angor);Pharmavie
175;Isosorbide Dinitrate 10mg;Antiangoreux;New Cesamex
176;Clopidogrel 75mg (Plavix);Antiagrégant plaquettaire;Pharmavie / Saint Sauveur (Sanofi)
177;Clopidogrel 75mg Générique;Antiagrégant plaquettaire;New Cesamex / Prince Pharma
178;Énoxaparine Inj 0,4ml / 0,6ml (Lovenox);Anticoagulant (HBPM);Pharmavie / Saint Sauveur
179;Héparine Sodique Injectable;Anticoagulant;Grossistes hospitaliers
180;Acénocoumarol (Sintrom) / Warfarine;Anticoagulant oral (AVK);Pharmavie / Saint Sauveur
181;Metformine 500mg (Générique);Antidiabétique oral (Biguanide);Zenufa / Shalina Healthcare
182;Metformine 1000mg (Glucophage);Antidiabétique oral;Pharmavie / Saint Sauveur (Merck)
183;Glibenclamide 5mg (Daonil style);Antidiabétique (Sulfamide);Zenufa / Shalina (Glishal)
184;Gliclazide 60mg / 80mg (Diamicron);Antidiabétique (Sulfamide);Pharmavie / New Cesamex
185;Insuline Humaine Rapide Inj (Actrapid);Insuline / Diabète Type 1 ou Urgence;Pharmavie / Saint Sauveur (Novo Nordisk)
186;Insuline NPH (Protaphane / Humulin);Insuline Action Intermédiaire;Pharmavie / Dépôts agréés
187;Insuline Glargine (Lantus / analogue);Insuline Action Longue;Pharmavie (Sanofi) / Grossistes
188;Gliclazide 30mg Générique;Antidiabétique oral;New Cesamex
189;Lévothyroxine 50µg / 100µg (Levothyrox);Hormone thyroïdienne;Pharmavie / Saint Sauveur
190;Carbimazole 5mg / 20mg;Antithyroïdien synthétique;Pharmavie
191;Cétirizine 10mg Comprimé (Zyrtec style);Antihistaminique (Allergie);Zenufa / Shalina (Cetrizin)
192;Loratadine 10mg;Antihistaminique non sédatif;Shalina Healthcare / New Cesamex
193;Prométhazine Sirop / Comprimé (Phénergan);Antihistaminique sédatif;Pharmavie / Zenufa
194;Salbutamol Spray Inhalateur (Ventoline);Bronchodilatateur (Asthme);Pharmavie / Saint Sauveur (GSK)
195;Salbutamol 4mg Comprimé / Sirop;Bronchodilatateur;Zenufa / Shalina Healthcare
196;Fluticasone Spray Nasal;Corticoïde local / Rhinite;Pharmavie / Saint Sauveur
197;Ambroxol Sirop (Muxol style);Mucolytique / Expectorant (Toux grasse);Zenufa / New Cesamex / Medico Plus
198;Pholcodine / Dextrométhorphane Sirop;Antitussif (Toux sèche);Pharmavie / Dépôts locaux
199;Gluconate de Calcium 10% Injectable;Supplémentation calcique urgence;Prince Pharma / Unique Pharma
200;Vitamine B1 B6 B12 Comprimé (Neurobion style);Vitamines B / Neuropathies;Shalina (Vitaméla) / New Cesamex / Prince Pharma"""

def normalize_supplier_name(name):
    name = name.strip()
    name = re.sub(r'\s*\([^)]*\)\s*', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

# Prix réalistes Kinshasa (FC) - prix_vente
# Catégories de prix par type de médicament
def estimate_price(nom, categorie):
    nom_lower = nom.lower()
    
    # Antibiotiques injectables puissants
    if any(x in nom_lower for x in ['méropénème', 'imipénème', 'vancomycine']):
        return (25000, 35000)
    if 'ceftriaxone' in nom_lower and '1g' in nom_lower:
        return (8000, 12000)
    if 'ceftriaxone' in nom_lower and '500mg' in nom_lower:
        return (5000, 7000)
    if 'ciprofloxacine' in nom_lower and 'poche' in nom_lower:
        return (15000, 20000)
    if 'métronidazole' in nom_lower and 'poche' in nom_lower:
        return (8000, 12000)
    if 'fluconazole' in nom_lower and 'poche' in nom_lower:
        return (18000, 25000)
    if 'insuline' in nom_lower:
        return (25000, 40000)
    if 'lantus' in nom_lower or 'glargine' in nom_lower:
        return (45000, 60000)
    if 'ventoline' in nom_lower or 'salbutamol spray' in nom_lower:
        return (8000, 12000)
    if 'neurobion' in nom_lower or any(x in nom_lower for x in ['vitamine b1', 'vitamines b']):
        return (5000, 10000)
    if 'spasfon' in nom_lower or 'phloroglucinol' in nom_lower:
        return (7000, 10000)
    if 'coartem' in nom_lower or 'artéméther 20' in nom_lower:
        return (12000, 18000)
    if any(x in nom_lower for x in ['artésunate injectable', 'artesunate injectable']) and '60mg' in nom_lower:
        return (15000, 20000)
    if any(x in nom_lower for x in ['artésunate injectable', 'artesunate injectable']) and '120mg' in nom_lower:
        return (25000, 35000)
    if 'quinimax' in nom_lower or ('quinine' in nom_lower and 'inj' in nom_lower):
        return (8000, 12000)
    if 'co-trimoxazole' in nom_lower or 'cotrimoxazole' in nom_lower:
        return (2000, 4000)
    if 'amoxicilline 500' in nom_lower:
        return (3000, 5000)
    if 'amoxicilline' in nom_lower and 'acide clavulanique' in nom_lower and '1g' in nom_lower:
        return (8000, 12000)
    if 'amoxicilline' in nom_lower and 'sirop' in nom_lower:
        return (4000, 6000)
    if any(x in nom_lower for x in ['paracétamol 500', 'paracetamol 500']):
        return (500, 1000)
    if any(x in nom_lower for x in ['paracétamol 1g', 'paracetamol 1g']):
        return (1000, 2000)
    if 'paracétamol injectable' in nom_lower or 'paracetamol injectable' in nom_lower:
        return (8000, 12000)
    if 'ibuprofène 400' in nom_lower:
        return (2000, 4000)
    if 'ibuprofène' in nom_lower and 'sirop' in nom_lower:
        return (4000, 6000)
    if 'diclofénac' in nom_lower and '50' in nom_lower:
        return (1500, 3000)
    if 'diclofénac' in nom_lower and 'gel' in nom_lower:
        return (3000, 5000)
    if 'tramadol 50' in nom_lower:
        return (3000, 5000)
    if 'tramadol 100' in nom_lower and 'inj' in nom_lower:
        return (5000, 8000)
    if 'omeprazole 20' in nom_lower:
        return (2000, 4000)
    if 'omeprazole 40' in nom_lower and 'inj' in nom_lower:
        return (6000, 9000)
    if any(x in nom_lower for x in ['metformine 500', 'metformin 500']):
        return (3000, 5000)
    if 'metformine 1000' in nom_lower:
        return (5000, 8000)
    if 'amlodipine 5' in nom_lower:
        return (2000, 4000)
    if 'amlodipine 10' in nom_lower:
        return (3000, 5000)
    if 'losartan 50' in nom_lower:
        return (4000, 7000)
    if any(x in nom_lower for x in ['aspirine 100', 'aspirine 100mg']):
        return (1500, 2500)
    if 'aspirine 500' in nom_lower:
        return (1000, 2000)
    if 'azithromycine 500' in nom_lower:
        return (7000, 12000)
    if 'fluconazole 150' in nom_lower:
        return (5000, 8000)
    if 'albendazole 400' in nom_lower:
        return (2000, 4000)
    if 'sro' in nom_lower or 'sels de réhydratation' in nom_lower:
        return (500, 1000)
    if 'morphine' in nom_lower:
        return (8000, 15000)
    if 'fentanyl' in nom_lower:
        return (15000, 25000)
    if 'prednisone 5' in nom_lower:
        return (2000, 3500)
    if 'dexaméthasone 4' in nom_lower:
        return (3000, 5000)
    if 'cétirizine' in nom_lower or 'cetirizine' in nom_lower:
        return (2000, 3500)
    if 'loratadine' in nom_lower:
        return (2000, 3500)
    if 'métoclopramide' in nom_lower or 'metoclopramide' in nom_lower:
        return (2000, 4000)
    if 'dompéridone' in nom_lower or 'domperidone' in nom_lower:
        return (3000, 5000)
    if 'lopéramide' in nom_lower or 'loperamide' in nom_lower:
        return (2000, 3000)
    if 'charbon activé' in nom_lower or 'charbon activ' in nom_lower:
        return (3000, 5000)
    if 'furosémide 40' in nom_lower:
        return (2000, 3500)
    if 'furosémide 20' in nom_lower and 'inj' in nom_lower:
        return (4000, 6000)
    if 'captopril 25' in nom_lower:
        return (2000, 3500)
    if 'propranolol 40' in nom_lower:
        return (2000, 4000)
    if 'nifédipine' in nom_lower:
        return (3000, 5000)
    if 'colchicine 1' in nom_lower:
        return (4000, 7000)
    if any(x in nom_lower for x in ['indométacine', 'indometacine']):
        return (2000, 3500)
    if 'ketoconazole 200' in nom_lower:
        return (4000, 7000)
    if 'nystatine' in nom_lower and 'vaginal' in nom_lower:
        return (3000, 5000)
    if any(x in nom_lower for x in ['mébendazole', 'mebendazole']):
        return (1500, 3000)
    if 'ivermectine' in nom_lower:
        return (4000, 7000)
    if 'doxycycline 100' in nom_lower:
        return (3000, 5000)
    if 'praziquantel' in nom_lower:
        return (5000, 8000)
    if 'clopidogrel 75' in nom_lower:
        return (6000, 10000)
    if 'atorvastatine' in nom_lower:
        return (8000, 15000)
    if 'rosuvastatine' in nom_lower:
        return (10000, 18000)
    if 'bisoprolol' in nom_lower:
        return (3000, 6000)
    if 'spironolactone' in nom_lower:
        return (3000, 6000)
    if 'digoxine' in nom_lower:
        return (3000, 5000)
    if 'lactulose' in nom_lower:
        return (6000, 10000)
    if 'bisacodyl' in nom_lower:
        return (2000, 3500)
    if 'ambroxol' in nom_lower:
        return (4000, 6000)
    if any(x in nom_lower for x in ['dextrométhorphane', 'pholcodine']):
        return (5000, 8000)
    if 'glibenclamide' in nom_lower:
        return (2000, 3500)
    if 'gliclazide' in nom_lower:
        return (5000, 8000)
    if 'héparine' in nom_lower:
        return (12000, 20000)
    if any(x in nom_lower for x in ['énoxaparine', 'enoxaparine']):
        return (15000, 25000)
    if 'primaquine' in nom_lower:
        return (3000, 5000)
    if 'sulfadoxine' in nom_lower:
        return (2000, 4000)
    if 'artéméther' in nom_lower and 'inj' in nom_lower:
        return (10000, 15000)
    if 'amphotéricine' in nom_lower:
        return (30000, 50000)
    if 'céfixime' in nom_lower and 'sirop' in nom_lower:
        return (8000, 12000)
    if 'céfixime' in nom_lower and 'comprimé' in nom_lower:
        return (6000, 10000)
    if any(x in nom_lower for x in ['clindamycine', 'lincomycine']):
        return (5000, 8000)
    if 'gentamicine' in nom_lower:
        return (3000, 5000)
    if 'amikacine' in nom_lower:
        return (7000, 12000)
    if 'prednisolone' in nom_lower:
        return (4000, 7000)
    if 'bétaméthasone' in nom_lower or 'betamethasone' in nom_lower:
        return (5000, 8000)
    if 'hydrocortisone 100' in nom_lower:
        return (4000, 6000)
    if 'fluticasone' in nom_lower:
        return (10000, 15000)
    if 'ondansetron' in nom_lower:
        return (6000, 10000)
    if 'naloxone' in nom_lower:
        return (15000, 25000)
    if 'codéine' in nom_lower:
        return (4000, 7000)
    if 'nitazoxanide' in nom_lower:
        return (6000, 10000)
    if 'niflumique' in nom_lower:
        return (5000, 8000)
    if 'méloxicam' in nom_lower:
        return (3000, 6000)
    if 'piroxicam' in nom_lower:
        return (2000, 4000)
    if 'célécoxib' in nom_lower:
        return (7000, 12000)
    if 'kétoprofène' in nom_lower:
        return (3000, 5000)
    if 'acide méfénamique' in nom_lower:
        return (2500, 4000)
    if 'hydroxyde aluminium' in nom_lower or 'maalox' in nom_lower:
        return (5000, 8000)
    if 'trisilicate' in nom_lower:
        return (3000, 5000)
    if 'glycérine suppositoire' in nom_lower:
        return (1500, 3000)
    if 'siméthicone' in nom_lower:
        return (5000, 8000)
    if any(x in nom_lower for x in ['zinc sulfate', 'zinc 20']):
        return (1500, 3000)
    if 'ranitidine' in nom_lower:
        return (2000, 4000)
    if 'lansoprazole' in nom_lower:
        return (4000, 7000)
    if 'ésoméprazole' in nom_lower or 'esomeprazole' in nom_lower:
        return (6000, 10000)
    if 'secnidazole' in nom_lower and '2g' in nom_lower:
        return (4000, 6000)
    if 'secnidazole' in nom_lower:
        return (3000, 5000)
    if 'tinidazole' in nom_lower:
        return (3000, 5000)
    if 'valsartan' in nom_lower:
        return (6000, 10000)
    if 'carvédilol' in nom_lower:
        return (5000, 8000)
    if 'aténolol' in nom_lower:
        return (2000, 4000)
    if 'enalapril' in nom_lower:
        return (3000, 5000)
    if 'lisinopril' in nom_lower:
        return (4000, 7000)
    if 'méthyldopa' in nom_lower:
        return (4000, 7000)
    if 'hydralazine' in nom_lower:
        return (6000, 10000)
    if 'isosorbide' in nom_lower:
        return (3000, 5000)
    if 'trinitrine' in nom_lower:
        return (8000, 12000)
    if 'acénocoumarol' in nom_lower or 'sintrom' in nom_lower:
        return (4000, 6000)
    if 'warfarin' in nom_lower:
        return (4000, 6000)
    if 'simvastatine' in nom_lower:
        return (5000, 8000)
    if 'carbimazole' in nom_lower:
        return (5000, 8000)
    if 'lévothyroxine' in nom_lower or 'levothyroxine' in nom_lower:
        return (5000, 8000)
    if 'gluconate calcium' in nom_lower:
        return (5000, 8000)
    if 'prométhazine' in nom_lower:
        return (3000, 6000)
    if any(x in nom_lower for x in ['érythromycine', 'erythromycine']):
        return (4000, 7000)
    if 'clarithromycine' in nom_lower:
        return (6000, 10000)
    if 'norfloxacine' in nom_lower:
        return (3000, 5000)
    if 'ofloxacine' in nom_lower:
        return (4000, 6000)
    if 'lévofloxacine' in nom_lower:
        return (6000, 10000)
    if 'céfuroxime' in nom_lower:
        return (6000, 10000)
    if 'céfotaxime' in nom_lower:
        return (8000, 12000)
    if 'ceftazidime' in nom_lower:
        return (12000, 18000)
    if 'céfadroxil' in nom_lower:
        return (5000, 8000)
    if 'ampicilline' in nom_lower and 'inj' in nom_lower:
        return (4000, 7000)
    if 'ampicilline' in nom_lower:
        return (3000, 5000)
    if 'cloxacilline' in nom_lower and 'inj' in nom_lower:
        return (5000, 8000)
    if 'cloxacilline' in nom_lower:
        return (3000, 5000)
    if 'benzathine' in nom_lower:
        return (6000, 10000)
    if 'benzylpénicilline' in nom_lower:
        return (5000, 8000)
    if 'phénoxyméthylpénicilline' in nom_lower:
        return (3000, 5000)
    if 'rifampicine' in nom_lower:
        return (5000, 8000)
    if 'éthambutol' in nom_lower:
        return (4000, 6000)
    if 'pyrazinamide' in nom_lower:
        return (3000, 5000)
    if 'griséofulvine' in nom_lower:
        return (6000, 10000)
    if 'luméfantrine' in nom_lower:
        return (10000, 15000)
    if 'amodiaquine' in nom_lower:
        return (3000, 5000)
    if 'méfloquine' in nom_lower:
        return (12000, 18000)
    if 'atovaquone' in nom_lower or 'malarone' in nom_lower:
        return (25000, 40000)
    if 'halofantrine' in nom_lower:
        return (10000, 15000)
    if 'dihydroartémisinine' in nom_lower:
        return (10000, 15000)
    if 'pyriméthamine' in nom_lower:
        return (2000, 3500)
    if 'artemidine' in nom_lower:
        return (8000, 12000)
    if 'malastop' in nom_lower:
        return (5000, 8000)
    if 'artequick' in nom_lower:
        return (8000, 12000)
    if 'tetracycline' in nom_lower:
        return (2000, 4000)
    if 'chloramphénicol' in nom_lower and 'gélule' in nom_lower:
        return (3000, 5000)
    if 'chloramphénicol' in nom_lower and 'inj' in nom_lower:
        return (5000, 8000)
    if 'spasmo-canulase' in nom_lower:
        return (5000, 8000)
    if 'butylbromure hyoscine' in nom_lower or 'buscopan' in nom_lower:
        return (4000, 6000)
    if 'butylbromure' in nom_lower and 'inj' in nom_lower:
        return (6000, 9000)
    # Default
    return (3000, 7000)


def get_description(nom, categorie):
    nom_lower = nom.lower()
    cat_lower = categorie.lower()
    
    if 'antibiotique' in cat_lower or 'antibiotique' in nom_lower:
        return f"{nom} - Antibiotique indiqué dans le traitement des infections bactériennes. Usage selon prescription médicale."
    if 'antipaludique' in cat_lower or 'antipaludique' in nom_lower:
        return f"{nom} - Antipaludique pour le traitement et la prévention du paludisme. Suivre la posologie recommandée."
    if 'anti-inflammatoire' in cat_lower or 'anti-inflammatoire' in nom_lower:
        return f"{nom} - Anti-inflammatoire utilisé pour traiter l'inflammation et la douleur. Contre-indiqué en cas d'ulcère gastrique."
    if 'analgésique' in cat_lower or 'analgésique' in nom_lower:
        return f"{nom} - Analgésique pour le soulagement de la douleur. Respecter la dose maximale journalière."
    if 'antihypertenseur' in cat_lower:
        return f"{nom} - Antihypertenseur pour le traitement de l'hypertension artérielle. Prise quotidienne selon prescription."
    if 'antidiabétique' in cat_lower:
        return f"{nom} - Antidiabétique oral pour le contrôle de la glycémie chez les patients diabétiques de type 2."
    if 'insuline' in cat_lower or 'insuline' in nom_lower:
        return f"{nom} - Insuline pour le traitement du diabète. Conservation entre 2°C et 8°C. Usage injectable."
    if 'corticoïde' in cat_lower or 'corticoide' in cat_lower:
        return f"{nom} - Corticoïde à usage systémique ou local. Utilisation de courte durée sauf avis médical."
    if 'antifongique' in cat_lower:
        return f"{nom} - Antifongique pour le traitement des infections fongiques (mycoses)."
    if 'anthelminthique' in cat_lower or 'vermifuge' in cat_lower:
        return f"{nom} - Anthelminthique (vermifuge) pour le traitement des parasitoses intestinales."
    if 'antihistaminique' in cat_lower:
        return f"{nom} - Antihistaminique pour le traitement des réactions allergiques."
    if 'antispasmodique' in cat_lower:
        return f"{nom} - Antispasmodique pour soulager les spasmes et douleurs abdominales."
    if 'antiémétique' in cat_lower or 'antiemetique' in cat_lower:
        return f"{nom} - Antiémétique pour prévenir et traiter les nausées et vomissements."
    if 'antidiarrhéique' in cat_lower or 'diarrhée' in cat_lower:
        return f"{nom} - Antidiarrhéique pour le traitement des diarrhées aiguës."
    if 'laxatif' in cat_lower:
        return f"{nom} - Laxatif pour le traitement de la constipation."
    if 'diurétique' in cat_lower or 'diuretique' in cat_lower:
        return f"{nom} - Diurétique pour le traitement de l'hypertension et des œdèmes."
    if 'bêta-bloquant' in cat_lower:
        return f"{nom} - Bêta-bloquant indiqué dans l'hypertension, l'insuffisance cardiaque et certaines arythmies."
    if 'hypolipidémiant' in cat_lower or 'statine' in cat_lower:
        return f"{nom} - Hypolipidémiant (statine) pour réduire le taux de cholestérol sanguin."
    if 'antiagrégant' in cat_lower:
        return f"{nom} - Antiagrégant plaquettaire pour prévenir la formation de caillots sanguins."
    if 'anticoagulant' in cat_lower:
        return f"{nom} - Anticoagulant pour prévenir et traiter les thromboses."
    if 'antiacide' in cat_lower or 'pansement gastrique' in cat_lower:
        return f"{nom} - Anti-acide pour soulager les brûlures d'estomac et les reflux gastriques."
    if 'inhibiteur de la pompe' in cat_lower or 'ipp' in cat_lower:
        return f"{nom} - Inhibiteur de la pompe à protons (IPP) pour le traitement des ulcères et reflux gastro-œsophagiens."
    if 'bronchodilatateur' in cat_lower:
        return f"{nom} - Bronchodilatateur pour le traitement de l'asthme et des maladies respiratoires obstructives."
    if 'mucolytique' in cat_lower or 'expectorant' in cat_lower:
        return f"{nom} - Mucolytique pour fluidifier les sécrétions bronchiques en cas de toux grasse."
    if 'antitussif' in cat_lower:
        return f"{nom} - Antitussif pour calmer la toux sèche."
    if 'dermocorticoïde' in cat_lower:
        return f"{nom} - Dermocorticoïde pour le traitement des affections cutanées inflammatoires."
    if 'anti-oedémateux' in cat_lower:
        return f"{nom} - Anti-œdémateux pour le traitement des œdèmes."
    if 'antihypertenseur' in cat_lower:
        return f"{nom} - Antihypertenseur central indiqué dans l'hypertension artérielle."
    if 'antidote' in cat_lower:
        return f"{nom} - Antidote utilisé en urgence pour neutraliser les effets des opioïdes."
    if 'anesthésique' in cat_lower:
        return f"{nom} - Anesthésique et analgésique utilisé en milieu hospitalier."
    if 'hormone' in cat_lower:
        return f"{nom} - Hormone thyroïdienne pour le traitement de l'hypothyroïdie."
    if 'antithyroïdien' in cat_lower:
        return f"{nom} - Antithyroïdien de synthèse pour le traitement de l'hyperthyroïdie."
    if 'vitamines' in cat_lower:
        return f"{nom} - Supplément vitaminique pour les carences en vitamines B."
    if 'supplémentation' in cat_lower:
        return f"{nom} - Supplément calcique utilisé en urgence."
    return f"{nom} - {categorie}. Usage selon prescription médicale. Tenir hors de portée des enfants."


app = create_app()
with app.app_context():
    gerant = User.query.filter_by(role='gerant', parent_id=None).first()
    if not gerant:
        print("Aucun gérant trouvé!")
        sys.exit(1)
    
    print(f"Gérant: {gerant.prenom} {gerant.nom} (ID: {gerant.id})")
    
    # 1. Supprimer toutes les données existantes
    print("Suppression des données existantes...")
    SaleItem.query.delete()
    Sale.query.delete()
    Activity.query.delete()
    DailyReport.query.delete()
    Medicine.query.delete()
    Supplier.query.delete()
    Category.query.delete()
    db.session.commit()
    print("  OK - Toutes les données supprimées")
    
    # 2. Parser les données
    lines = RAW.strip().split('\n')
    header = lines[0]
    data_lines = lines[1:]
    
    # Catégories uniques - normalisation
    cat_set = set()
    for line in data_lines:
        parts = line.split(';')
        if len(parts) >= 3:
            cat_set.add(parts[2].strip())
    
    # Normaliser les catégories
    cat_mapping = {
        'Analgésique / Antipyrétique': 'Antalgiques',
        'Analgésique Opioïde': 'Antalgiques',
        'Analgésique Opioïde Majeur': 'Antalgiques',
        'Analgésique hospitalier': 'Antalgiques',
        'Analgésique / Anti-inflammatoire': 'Anti-inflammatoires',
        'Analgésique / Antitussif': 'Antitussifs',
        'Anesthésique / Analgésique': 'Antalgiques',
        'Anti-inflammatoire non stéroïdien': 'Anti-inflammatoires',
        'Anti-inflammatoire topique': 'Anti-inflammatoires',
        'Anti-inflammatoire (Inhibiteur COX-2)': 'Anti-inflammatoires',
        'Anti-inflammatoire': 'Anti-inflammatoires',
        'Corticoïde / Anti-inflammatoire': 'Anti-inflammatoires',
        'Corticoïde': 'Anti-inflammatoires',
        'Corticoïde puissant': 'Anti-inflammatoires',
        'Dermocorticoïde': 'Anti-inflammatoires',
        'Corticoïde d\'urgence': 'Anti-inflammatoires',
        'Corticoïde local / Rhinite': 'Anti-inflammatoires',
        'Antipaludique (CTA)': 'Antipaludiques',
        'Antipaludique Pédiatrique': 'Antipaludiques',
        'Antipaludique Forme Grave': 'Antipaludiques',
        'Antipaludique (TPI femme enceinte)': 'Antipaludiques',
        'Antipaludique prophylaxie': 'Antipaludiques',
        'Antipaludique (Radical)': 'Antipaludiques',
        'Antipaludique pré-transfert': 'Antipaludiques',
        'Antipaludique': 'Antipaludiques',
        'Antibiotique (Pénicilline)': 'Antibiotiques',
        'Antibiotique Pédiatrique': 'Antibiotiques',
        'Antibiotique (Bêta-lactamine)': 'Antibiotiques',
        'Antibiotique hospitalier': 'Antibiotiques',
        'Antibiotique anti-staphylococcique': 'Antibiotiques',
        'Antibiotique (Céphalosporine 2G)': 'Antibiotiques',
        'Antibiotique (Céphalosporine 3G)': 'Antibiotiques',
        'Antibiotique (Céphalosporine 3G orale)': 'Antibiotiques',
        'Antibiotique (Céphalosporine 1G)': 'Antibiotiques',
        'Antibiotique (Fluoroquinolone)': 'Antibiotiques',
        'Antibiotique Injectable': 'Antibiotiques',
        'Antibiotique urinaire': 'Antibiotiques',
        'Antibiotique (Macrolide)': 'Antibiotiques',
        'Antibiotique (Aminoside)': 'Antibiotiques',
        'Antibiotique / Antiprotozoaire': 'Antibiotiques',
        'Antiparasitaire/Antibiotique': 'Antibiotiques',
        'Antibiotique (Sulfamide)': 'Antibiotiques',
        'Antibiotique tétracycline': 'Antibiotiques',
        'Antibiotique': 'Antibiotiques',
        'Antibiotique (Lincosamide)': 'Antibiotiques',
        'Antibiotique Glico-peptide': 'Antibiotiques',
        'Antibiotique de réserve carbapénème': 'Antibiotiques',
        'Antibiotique Oral': 'Antibiotiques',
        'Antibiotique / Antipaludique': 'Antibiotiques',
        'Antituberculeux': 'Antituberculeux',
        'Antifongique': 'Antifongiques',
        'Antifongique Injectable': 'Antifongiques',
        'Antifongique Topique': 'Antifongiques',
        'Antifongique Gynécologique': 'Antifongiques',
        'Antifongique Buccal': 'Antifongiques',
        'Antifongique cutané/cheveux': 'Antifongiques',
        'Antifongique systémique': 'Antifongiques',
        'Anthelminthique (Vermifuge)': 'Antiparasitaires',
        'Vermifuge Pédiatrique': 'Antiparasitaires',
        'Anthelminthique': 'Antiparasitaires',
        'Anthelminthique (Bilharziose)': 'Antiparasitaires',
        'Antiparasitaire (Gale/Onchocercose)': 'Antiparasitaires',
        'Antiprotozoaire / Anti-amibien': 'Antiparasitaires',
        'Anti-amibien': 'Antiparasitaires',
        'Anti-amibien / Trichomonase': 'Antiparasitaires',
        'Antiparasitaire large spectre': 'Antiparasitaires',
        'Antiprotozoaire / Antipaludique': 'Antiparasitaires',
        'Antiémétique': 'Digestifs',
        'Antiémétique / Procinétique': 'Digestifs',
        'Antiémétique pédiatrique': 'Digestifs',
        'Antiémétique puissant (chimio/post-op)': 'Digestifs',
        'Antidiarrhéique': 'Digestifs',
        'Correction de la déshydratation': 'Digestifs',
        'Adjuvant traitement diarrhée enfant': 'Digestifs',
        'Antispasmodique': 'Digestifs',
        'Antispasmodique / Digestif': 'Digestifs',
        'Antispasmodique Injectable': 'Digestifs',
        'Laxatif Osmotique': 'Digestifs',
        'Laxatif Stimulant': 'Digestifs',
        'Laxatif Local': 'Digestifs',
        'Adsorbant intestinal / Ballonnements': 'Digestifs',
        'Régulateur du transit / Ballonnements': 'Digestifs',
        'Inhibiteur de la pompe à protons': 'Digestifs',
        'Anti-H2 / Anti-acide': 'Digestifs',
        'Anti-acide / Pansement gastrique': 'Digestifs',
        'Anti-acide': 'Digestifs',
        'Antihypertenseur (Inhibiteur calcique)': 'Cardiovasculaires',
        'Antihypertenseur': 'Cardiovasculaires',
        'Antihypertenseur (Inhibiteur de l\'ECA)': 'Cardiovasculaires',
        'Antihypertenseur (Antagoniste ARA-II)': 'Cardiovasculaires',
        'Antihypertenseur combiné': 'Cardiovasculaires',
        'Antihypertenseur (ARA-II)': 'Cardiovasculaires',
        'Bêta-bloquant / Antihypertenseur': 'Cardiovasculaires',
        'Bêta-bloquant / Hypertension / Anxiété': 'Cardiovasculaires',
        'Bêta-bloquant (Insuffisance cardiaque)': 'Cardiovasculaires',
        'Bêta-bloquant': 'Cardiovasculaires',
        'Diurétique': 'Cardiovasculaires',
        'Diurétique d\'urgence': 'Cardiovasculaires',
        'Diurétique Thiazidique': 'Cardiovasculaires',
        'Diurétique épargneur de potassium': 'Cardiovasculaires',
        'Antihypertenseur central (Femme enceinte)': 'Cardiovasculaires',
        'Antihypertenseur d\'urgence (Pré-éclampsie)': 'Cardiovasculaires',
        'Hypolipidémiant (Statine)': 'Cardiovasculaires',
        'Hypolipidémian': 'Cardiovasculaires',
        'Glycoside cardiotonique': 'Cardiovasculaires',
        'Antiangoreux (Crise d\'angor)': 'Cardiovasculaires',
        'Antiangoreux': 'Cardiovasculaires',
        'Antiagrégant / Analgésique': 'Cardiovasculaires',
        'Antiagrégant plaquettaire': 'Cardiovasculaires',
        'Anticoagulant (HBPM)': 'Cardiovasculaires',
        'Anticoagulant': 'Cardiovasculaires',
        'Anticoagulant oral (AVK)': 'Cardiovasculaires',
        'Antidiabétique oral (Biguanide)': 'Diabétologie',
        'Antidiabétique oral': 'Diabétologie',
        'Antidiabétique (Sulfamide)': 'Diabétologie',
        'Insuline / Diabète Type 1 ou Urgence': 'Diabétologie',
        'Insuline Action Intermédiaire': 'Diabétologie',
        'Insuline Action Longue': 'Diabétologie',
        'Antihistaminique (Allergie)': 'Antihistaminiques',
        'Antihistaminique non sédatif': 'Antihistaminiques',
        'Antihistaminique sédatif': 'Antihistaminiques',
        'Bronchodilatateur (Asthme)': 'Respiratoires',
        'Bronchodilatateur': 'Respiratoires',
        'Mucolytique / Expectorant (Toux grasse)': 'Respiratoires',
        'Antitussif (Toux sèche)': 'Respiratoires',
        'Traitement de la Goutte': 'Rhumatologie',
        'Anti-inflammatoire (AINS)': 'Rhumatologie',
        'Hormone thyroïdienne': 'Endocrinologie',
        'Antithyroïdien synthétique': 'Endocrinologie',
        'Antidote des opioïdes': 'Urgences',
        'Suppléméntation calcique urgence': 'Urgences',
        'Supplémémentation calcique urgence': 'Urgences',
        'Vitamines B / Neuropathies': 'Vitamines',
    }
    
    # Appliquer le mapping
    cat_set_normalized = set()
    for c in cat_set:
        normalized = cat_mapping.get(c, c)
        cat_set_normalized.add(normalized)
    
    cat_set = cat_set_normalized
    
    # 3. Créer les catégories
    print("Création des catégories...")
    cat_map = {}
    for cat_nom in sorted(cat_set):
        cat = Category(nom=cat_nom, gerant_id=gerant.id)
        db.session.add(cat)
        db.session.flush()
        cat_map[cat_nom] = cat.id
    print(f"  OK - {len(cat_map)} catégories créées")
    
    # 4. Fournisseurs uniques
    print("Traitement des fournisseurs...")
    supplier_names = set()
    supp_to_meds = {}  # fournisseur -> liste de médicaments
    
    for line in data_lines:
        parts = line.split(';')
        if len(parts) < 4:
            continue
        supp_text = parts[3].strip()
        suppliers = [normalize_supplier_name(s) for s in supp_text.split('/') if s.strip()]
        for s in suppliers:
            if s:
                supplier_names.add(s)
                if s not in supp_to_meds:
                    supp_to_meds[s] = []
                supp_to_meds[s].append(parts[1].strip())
    
    print(f"  {len(supplier_names)} fournisseurs uniques identifiés")
    
    # Créer les fournisseurs avec des informations réalistes
    supplier_info = {
        'Zenufa': ('0971000001', 'zenufa@cd', 'Kinshasa/Gombe', 'Directeur Commercial'),
        'Shalina Healthcare': ('0971000002', 'shalina@cd', 'Kinshasa/Limete', 'Country Manager'),
        'Pharmavie': ('0971000003', 'pharmavie@cd', 'Kinshasa/Gombe', 'Gérant'),
        'Saint Sauveur': ('0971000004', 'saintsauveur@cd', 'Kinshasa/Ngaliema', 'Directeur'),
        'New Cesamex': ('0971000005', 'cesamex@cd', 'Kinshasa/Barumbu', 'Responsable Commercial'),
        'AMT Pharma': ('0971000006', 'amtpharma@cd', 'Kinshasa/Lemba', 'Directeur Commercial'),
        'Prince Pharma': ('0971000007', 'princepharma@cd', 'Kinshasa/Kalamu', 'Gérant'),
        'Unique Pharma': ('0971000008', 'uniquepharma@cd', 'Kinshasa/Masina', 'Directeur Général'),
        'Medico Plus': ('0971000009', 'medicoplus@cd', 'Kinshasa/Kinshasa', 'Responsable'),
        'FEDECAME': ('0971000010', 'fedecame@cd', 'Kinshasa/Gombe', 'Secrétaire Exécutif'),
        'Dépôts Spécialisés': ('0971000011', 'depots@cd', 'Kinshasa/Limete', 'Responsable'),
        'Dépôts hospitaliers agréés': ('0971000012', 'depotshosp@cd', 'Kinshasa/Gombe', 'Coordonnateur'),
        'Grossistes agréés': ('0971000013', 'grossistes@cd', 'Kinshasa/Ngaliema', 'Contact Commercial'),
        'Grossistes spécialisés': ('0971000014', 'grossistesspec@cd', 'Kinshasa/Ndjili', 'Directeur'),
        'Grossistes hospitaliers': ('0971000015', 'grossisteshosp@cd', 'Kinshasa/Lemba', 'Responsable'),
        'Programme National Tuberculose': ('0971000016', 'pnt@cd', 'Kinshasa/Gombe', 'Coordonnateur PNT'),
        'Grossistes locaux': ('0971000017', 'locaux@cd', 'Kinshasa/Mont-Ngafula', 'Gérant'),
        'Shalina': ('0971000018', 'shalina2@cd', 'Kinshasa/Limete', 'Agent Commercial'),
        'Dépôts agréés': ('0971000019', 'depotsagrees@cd', 'Kinshasa/Gombe', 'Responsable logistique'),
        'GHC': ('0971000020', 'ghc@cd', 'Kinshasa/Barumbu', 'Directeur Technique'),
        'Sanofi': ('0971000021', 'sanofi@cd', 'Kinshasa/Gombe', 'Délégué Médical'),
        'Novartis': ('0971000022', 'novartis@cd', 'Kinshasa/Gombe', 'Délégué Médical'),
        'Pfizer': ('0971000023', 'pfizer@cd', 'Kinshasa/Gombe', 'Délégué Médical'),
        'Novo Nordisk': ('0971000024', 'novonordisk@cd', 'Kinshasa/Gombe', 'Délégué Médical'),
        'Merck': ('0971000025', 'merck@cd', 'Kinshasa/Gombe', 'Délégué Médical'),
        'Sanofi': ('0971000026', 'sanofi2@cd', 'Kinshasa/Gombe', 'Délégué Médical'),
        'GSK': ('0971000027', 'gsk@cd', 'Kinshasa/Gombe', 'Délégué Médical'),
        'AstraZeneca': ('0971000028', 'astrazeneca@cd', 'Kinshasa/Gombe', 'Délégué Médical'),
    }
    
    supplier_map = {}
    for s_name in sorted(supplier_names):
        info = supplier_info.get(s_name, ('0971000000', '', 'Kinshasa', 'Contact'))
        supp = Supplier(
            nom=s_name,
            telephone=info[0],
            email=info[1] if info[1] else '',
            adresse=info[2],
            responsable=info[3],
            gerant_id=gerant.id
        )
        db.session.add(supp)
        db.session.flush()
        supplier_map[s_name] = supp.id
    db.session.commit()
    
    # 5. Créer les médicaments
    print("Création des médicaments...")
    today = date.today()
    medicines_created = 0
    
    for line in data_lines:
        parts = line.split(';')
        if len(parts) < 4:
            continue
        
        numero = parts[0].strip()
        nom = parts[1].strip()
        cat_nom = cat_mapping.get(parts[2].strip(), parts[2].strip())
        supp_text = parts[3].strip()
        
        # Choisir un fournisseur principal (le premier)
        suppliers_list = [normalize_supplier_name(s) for s in supp_text.split('/') if s.strip()]
        primary_supplier = suppliers_list[0] if suppliers_list else None
        fournisseur_id = supplier_map.get(primary_supplier) if primary_supplier else None
        
        # Prix réalistes Kinshasa
        prix_min, prix_max = estimate_price(nom, cat_nom)
        prix_vente = random.randint(prix_min, prix_max)
        # Prix d'achat = ~60-75% du prix de vente
        marge = random.uniform(0.60, 0.75)
        prix_achat = round(prix_vente * marge, 0)
        
        # Quantité en stock
        if 'sirop' in nom.lower() or 'crème' in nom.lower() or 'gel' in nom.lower() or 'spray' in nom.lower() or 'poche' in nom.lower() or 'suppositoire' in nom.lower() or 'sachet' in nom.lower():
            quantite = random.randint(10, 60)
        elif 'injectable' in nom.lower() or 'inj' in nom.lower() or 'poche' in nom.lower():
            quantite = random.randint(5, 30)
        else:
            quantite = random.randint(20, 200)
        
        stock_minimum = max(5, quantite // 4)
        
        # Date d'expiration (entre 3 mois et 2 ans)
        exp_days = random.randint(90, 730)
        date_exp = today + timedelta(days=exp_days)
        
        # Description
        description = get_description(nom, cat_nom)
        
        medicine = Medicine(
            nom=nom,
            categorie=cat_nom,
            description=description,
            prix_achat=prix_achat,
            prix_vente=prix_vente,
            quantite=quantite,
            stock_minimum=stock_minimum,
            date_expiration=date_exp,
            gerant_id=gerant.id,
            fournisseur_id=fournisseur_id
        )
        db.session.add(medicine)
        medicines_created += 1
    
    db.session.commit()
    print(f"  OK - {medicines_created} médicaments créés")
    print()
    print("=== RÉSUMÉ ===")
    print(f"Médicaments: {Medicine.query.count()}")
    print(f"Fournisseurs: {Supplier.query.count()}")
    print(f"Catégories: {Category.query.count()}")
    print("Importation terminée avec succès!")
