"""Les passerelles vers les services externes."""

from abc import ABC, abstractmethod


class PasserelleDeCommunication(ABC):
    """Tout ce qu'un fournisseur de communication sait faire."""

    @abstractmethod
    def envoyer_courriel(self, destinataire: str, sujet: str, corps: str) -> None: ...

    @abstractmethod
    def envoyer_sms(self, numero: str, texte: str) -> None: ...

    @abstractmethod
    def envoyer_notification_push(self, appareil: str, texte: str) -> None: ...

    @abstractmethod
    def verifier_adresse(self, adresse: str) -> bool: ...

    @abstractmethod
    def statistiques_d_envoi(self) -> dict: ...

    @abstractmethod
    def purger_la_file(self) -> int: ...


class ClientSMTP(PasserelleDeCommunication):
    """Le fournisseur reellement utilise en production."""

    def __init__(self, serveur: str = "smtp.interne", port: int = 25) -> None:
        self.serveur = serveur
        self.port = port

    def envoyer_courriel(self, destinataire: str, sujet: str, corps: str) -> None:
        print(f"[SMTP {self.serveur}:{self.port}] a {destinataire} : {sujet}")
        print(corps)

    def envoyer_sms(self, numero: str, texte: str) -> None:
        raise NotImplementedError("ce fournisseur ne fait pas de SMS")

    def envoyer_notification_push(self, appareil: str, texte: str) -> None:
        raise NotImplementedError("ce fournisseur ne fait pas de push")

    def verifier_adresse(self, adresse: str) -> bool:
        return "@" in adresse

    def statistiques_d_envoi(self) -> dict:
        return {"envoyes": 0}

    def purger_la_file(self) -> int:
        return 0
