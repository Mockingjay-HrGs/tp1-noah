"""Présentation textuelle des factures."""


def corps_de_facture(facture, abonnement) -> str:
    return "\n".join(
        [
            f"Facture {facture.numero}",
            f"Client        : {facture.client}",
            f"Emise le      : {facture.emise_le.isoformat()}",
            f"Formule       : {abonnement.formule}, {abonnement.nombre_de_postes} postes",
            f"Montant HT    : {facture.montant_ht:.2f}",
            f"Montant TTC   : {facture.montant_ttc:.2f}",
        ]
    )
