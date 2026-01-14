# 📝 Mémo — Terraform + Azure RBAC (Brief NYC Taxi)
## 🎯 Contexte
* Compte Azure de formation
* Terraform exécuté dans Docker
* Authentification Azure via az login dans le container
* Architecture Terraform modulaire (root + modules)

## 🔐 Problème rencontré

Lors du terraform apply, erreur :
```
AuthorizationFailed
Microsoft.Resources/subscriptions/resourcegroups/write
```

### Cause

Le compte Azure :
* est **Reader** au niveau de la subscription
* n’a **pas le droit de créer des Resource Groups**

👉 Terraform n’a donc pas le droit d’exécuter :

```
azurerm_resource_group
```

## 🔍 Diagnostic RBAC (commandes utiles)
Vérifier la subscription active
```bash
az account show --query "{name:name,id:id,tenantId:tenantId,user:user.name}" -o table
```

Vérifier les rôles au niveau subscription
```bash
SUB_ID=$(az account show --query id -o tsv)

az role assignment list \
  --assignee "cmartiny.ext@simplonformations.onmicrosoft.com" \
  --scope "/subscriptions/$SUB_ID" \
  -o table
```


Résultat :

* **Reader** → lecture seule ❌

## ✅ Découverte clé

Il existe un **Resource Group personnel** :

```
cmartinyRG
```


Sur lequel le rôle est :

```
Contributor
```


Vérification :

```bash
RG_NAME="cmartinyRG"

az role assignment list \
  --assignee "cmartiny.ext@simplonformations.onmicrosoft.com" \
  --scope "/subscriptions/$SUB_ID/resourceGroups/$RG_NAME" \
  -o table
```


> 👉 Contributor sur ce RG = droits d’écriture complets dans ce périmètre

## 🧠 Conséquence Terraform (bonne pratique)

On **ne crée plus le Resource Group** avec Terraform.
On **réutilise un RG existant** via un `data` source.

### Pourquoi c’est propre ?

* Conforme aux contraintes RBAC réelles
* Fréquent en entreprise (RG imposé par la plateforme)
* Terraform reste idempotent et modulaire

## 🏗️ Pattern Terraform adopté
### ❌ À éviter
```hcl
resource "azurerm_resource_group" "main" { ... }
```

### ✅ À faire
```hcl
data "azurerm_resource_group" "main" {
  name = "cmartinyRG"
}
```


Puis injecter :

```hcl
resource_group_name = data.azurerm_resource_group.main.name
location            = data.azurerm_resource_group.main.location
```

## 🎓 Leçon clé

> **Terraform n’a jamais plus de droits que ton identité Azure.**
> Une erreur Terraform *403* = presque toujours un problème **RBAC**, pas de code.

## 🧪 Mini-quiz (mémo mental)

**Pourquoi créer un Resource Group nécessite des droits au niveau subscription ?**

> 👉 Parce qu’un RG est une ressource subscription-scoped, créée sous :
```bash
/subscriptions/<id>/resourceGroups/<name>
```