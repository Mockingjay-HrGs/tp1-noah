"""D3 : remise de trente pour cent à partir de deux cents postes inclus."""

from facturation.registre import tarification

tarification.paliers[200] = 0.30
