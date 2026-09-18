"""Les passerelles vers les services externes."""

class ClientSMTP:
    """Le fournisseur reellement utilise en production."""

    def __init__(self, serveur: str = "smtp.interne", port: int = 25) -> None:
        self.serveur = serveur
        self.port = port

    def envoyer_courriel(self, destinataire: str, sujet: str, corps: str) -> None:
        print(f"[SMTP {self.serveur}:{self.port}] a {destinataire} : {sujet}")
        print(corps)

    def verifier_adresse(self, adresse: str) -> bool:
        return "@" in adresse

    def statistiques_d_envoi(self) -> dict:
        return {"envoyes": 0}

    def purger_la_file(self) -> int:
        return 0
