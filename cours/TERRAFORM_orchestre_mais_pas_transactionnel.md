# Terraform orchestré, mais pas transactionnel

## Réponse consolidée (version infra / ESN)

> Les ressources cloud n’ont pas de transaction globale ni de mécanisme de rollback commun.
> Chaque service est provisionné indépendamment, via des API différentes, avec des effets parfois irréversibles ou coûteux.

Donc :

* Terraform **orchestré**, mais **pas transactionnel**
* Succès partiels = état normal du monde cloud
* La responsabilité du contrôle revient à l’ingénieur (plan, ciblage, rollback manuel)

> 👉 C’est exactement pour ça que Terraform existe : **déclarer l’état voulu**, puis converger progressivement.

## ✅ On clôt ce chapitre conceptuel

Tu as maintenant compris :
* state local vs réel
* ordre d’exécution
* absence de rollback
* pourquoi `plan` est sacré

C’est un **gros milestone** pour quelqu’un de novice en Terraform.