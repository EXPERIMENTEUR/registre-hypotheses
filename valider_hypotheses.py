# -*- coding: ascii -*-
"""Validation du registre d'hypotheses. Code de sortie 0 si tout est valide, 1 sinon.
Usage : python valider_hypotheses.py [hypotheses.json]"""
import json, re, sys

STATUTS = {"non_testee", "en_cours", "corroboree", "refutee", "non_concluante"}
OBLIGATOIRES = ["id", "titre", "enonce", "corpus", "prediction", "refutation", "methode", "limites", "statut"]
CONCLUS = {"corroboree", "refutee"}

def erreurs_fiche(h, deja):
    e = []
    if not isinstance(h, dict):
        return ["la fiche n'est pas un objet JSON"]
    for k in OBLIGATOIRES:
        v = h.get(k)
        if v in (None, "", []):
            e.append("champ obligatoire vide ou absent : " + k)
    hid = h.get("id", "")
    if not re.fullmatch(r"H\d{3,}", str(hid)):
        e.append("id invalide (attendu H001, H002...) : %r" % (hid,))
    if hid in deja:
        e.append("id en double : %s" % hid)
    if h.get("statut") not in STATUTS:
        e.append("statut invalide : %r (autorises : %s)" % (h.get("statut"), ", ".join(sorted(STATUTS))))
    if len(str(h.get("refutation", "")).strip()) < 20:
        e.append("critere de refutation trop court (20 caracteres minimum) : une hypothese doit pouvoir etre fausse")
    if not isinstance(h.get("corpus", []), list):
        e.append("corpus doit etre une liste")
    hist = h.get("historique", [])
    if not isinstance(hist, list):
        e.append("historique doit etre une liste")
        hist = []
    for ligne in hist:
        if not isinstance(ligne, dict) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ligne.get("date", ""))):
            e.append("historique : date absente ou invalide (format AAAA-MM-JJ)")
        elif ligne.get("statut") not in STATUTS:
            e.append("historique : statut invalide a la date %s" % ligne.get("date"))
    if h.get("statut") in CONCLUS:
        if not str(h.get("resultat", "")).strip():
            e.append("un statut conclusif (corroboree/refutee) exige un resultat chiffre")
        if not str(h.get("donnees", "")).strip():
            e.append("un statut conclusif exige de preciser les donnees (traduction, version des motifs, date)")
        if not hist:
            e.append("un statut conclusif exige au moins une ligne d'historique datee")
    return e

def valider(chemin):
    with open(chemin, encoding="utf-8-sig") as f:
        d = json.load(f)
    if not isinstance(d, dict) or not isinstance(d.get("hypotheses"), list):
        return ["structure attendue : {\"hypotheses\": [ ... ]}"]
    tout, ids = [], set()
    for i, h in enumerate(d["hypotheses"]):
        for m in erreurs_fiche(h, ids):
            tout.append("fiche %d (%s) : %s" % (i + 1, h.get("id", "?") if isinstance(h, dict) else "?", m))
        if isinstance(h, dict):
            ids.add(h.get("id"))
    return tout

if __name__ == "__main__":
    chemin = sys.argv[1] if len(sys.argv) > 1 else "hypotheses.json"
    problemes = valider(chemin)
    if problemes:
        print("REFUSE : %d probleme(s)" % len(problemes))
        for p in problemes:
            print(" -", p)
        sys.exit(1)
    print("Registre valide.")
