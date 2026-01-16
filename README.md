# Rendu du brief

## Terraform déployé correctement ?

> Terminal du docker faisant tourné *Terraform*.

### Exécution de `Terraform apply`

```bash terraform
> terraform apply -auto-approve
module.cosmos_postgres.random_string.name_suffix: Refreshing state... [id=x72pea]
[...]

No changes. Your infrastructure matches the configuration.

Terraform has compared your real infrastructure against your configuration and found no differences, so no changes are needed.
╷
│ Warning: Argument is deprecated
│ 
│   with module.storage.azurerm_storage_container.raw,
│   on modules/storage/main.tf line 23, in resource "azurerm_storage_container" "raw":
│   23:   storage_account_name  = azurerm_storage_account.main.name
│ 
│ the `storage_account_name` property has been deprecated in favour of `storage_account_id` and will be removed in version ]

No changes. Your infrastructure matches the configuration.

Terraform has compared your real infrastructure against your configuration and found no differences, so no changes are needed.
╷
│ Warning: Argument is deprecated
│ 
│   with module.storage.azurerm_storage_container.raw,
│   on modules/storage/main.tf line 23, in resource "azurerm_storage_container" "raw":
│   23:   storage_account_name  = azurerm_storage_account.main.name
│ 
│ the `storage_account_name` property has been deprecated in favour of `storage_account_id` and will be removed in version 5.0 of the Provider.
│ 
│ (and one more similar warning elsewhere)
╵

Apply complete! Resources: 0 added, 0 changed, 0 destroyed.

Outputs:

acr_login_server = "acrnyctaxidev.azurecr.io"
acr_name = "acrnyctaxidev"
container_app_name = "ca-nyctaxi-pipeline-dev"
log_analytics_name = "law-nyctaxi-dev"
resource_group_name = "cmartinyRG"
storage_account_name = "stnyctaxidev9sns2p"
storage_containers = {
  "processed" = "processed"
  "raw" = "raw"
}
```

### 1. Vérification de l’état Terraform

```bash terraform
> terraform state list

data.azurerm_resource_group.main
module.acr.azurerm_container_registry.main
module.container_apps.azurerm_container_app.main
module.container_apps.azurerm_container_app_environment.main
module.container_apps.azurerm_log_analytics_workspace.main
module.cosmos_postgres.azurerm_cosmosdb_postgresql_cluster.main
module.cosmos_postgres.azurerm_cosmosdb_postgresql_firewall_rule.allow_azure
module.cosmos_postgres.random_password.admin
module.cosmos_postgres.random_string.name_suffix
module.storage.azurerm_storage_account.main
module.storage.azurerm_storage_container.processed
module.storage.azurerm_storage_container.raw
module.storage.random_string.suffix
```

### 2. Vérification des outputs Terraform

```bash terraform
> terraform output

acr_login_server = "acrnyctaxidev.azurecr.io"
acr_name = "acrnyctaxidev"
container_app_name = "ca-nyctaxi-pipeline-dev"
log_analytics_name = "law-nyctaxi-dev"
resource_group_name = "cmartinyRG"
storage_account_name = "stnyctaxidev9sns2p"
storage_containers = {
  "processed" = "processed"
  "raw" = "raw"
}
```

### 3. Vérification du Resource Group

```bash terraform
> az group show --name cmartinyRG -o table

Location       Name
-------------  ----------
francecentral  cmartinyRG
```

### 4. Vérification du Container Registry (ACR)

```bash terraform
> az acr show --name acrnyctaxidev -o table

NAME           RESOURCE GROUP    LOCATION       SKU    LOGIN SERVER              CREATION DATE         ADMIN ENABLED
-------------  ----------------  -------------  -----  ------------------------  --------------------  ---------------
acrnyctaxidev  cmartinyRG        francecentral  Basic  acrnyctaxidev.azurecr.io  2026-01-16T10:36:58Z  True
```

### 5. Vérification de l’environnement Container Apps

```bash terraform
> az containerapp env show \
>   --name cae-nyctaxi-dev \
>   --resource-group cmartinyRG \
>   -o table

Location        Name             ResourceGroup
--------------  ---------------  ---------------
France Central  cae-nyctaxi-dev  cmartinyRG
```

### 6. Vérification de l’application Container App

```bash terraform
> az containerapp show \
>   --name ca-nyctaxi-pipeline-dev \
>   --resource-group cmartinyRG \
>   -o table

Name                     Location        ResourceGroup
-----------------------  --------------  ---------------
ca-nyctaxi-pipeline-dev  France Central  cmartinyRG
```

### 7. Vérification des logs de la Container App

```bash terraform
> az containerapp logs show \
>   --name ca-nyctaxi-pipeline-dev \
>   --resource-group cmartinyRG

{"TimeStamp":"2026-01-16T12:30:51.72357","Log":"Connecting to the container 'pipeline'..."}
{"TimeStamp":"2026-01-16T12:30:51.76625","Log":"Successfully Connected to container: 'pipeline' [Revision: 'ca-nyctaxi-pipeline-dev--vjstqsr', Replica: 'ca-nyctaxi-pipeline-dev--vjstqsr-5459c8d7bb-9647c']"}
{"TimeStamp":"2026-01-16T12:28:52.83374+00:00","Log":"12:28:52.833 | INFO     | utils.database:get_database_duckdb:69 - Connexion ferm\u00E9e"}
{"TimeStamp":"2026-01-16T12:28:52.8338089+00:00","Log":"12:28:52.833 | ERROR    | __main__:main:20 - \u274C Erreur dans le pipeline : IO Error: Unable to connect to Postgres at "postgresql://citus:50[Sj\u003EDO79!1GnldH*n\u003Ez%Kk@c-cosmos-nyctaxi-dev-x72pea.xsy2tm3latntrz.postgres.cosmos.azure.com:5432/citus": invalid percent-encoded token: "50[Sj\u003EDO79!1GnldH*n\u003Ez%Kk""}
{"TimeStamp":"2026-01-16T12:28:52.8338271+00:00","Log":""}
{"TimeStamp":"2026-01-16T12:28:52.8345647+00:00","Log":"(most recent call last):"}
{"TimeStamp":"2026-01-16T12:28:52.8347991+00:00","Log":"File "/app/main.py", line 11, in main"}
{"TimeStamp":"2026-01-16T12:28:52.8348144+00:00","Log":"runpy.run_path("pipelines/staging/load_duckdb.py", run_name="__main__")"}
{"TimeStamp":"2026-01-16T12:28:52.8348218+00:00","Log":"File "\u003Cfrozen runpy\u003E", line 291, in run_path"}
{"TimeStamp":"2026-01-16T12:28:52.8348284+00:00","Log":"File "\u003Cfrozen runpy\u003E", line 98, in _run_module_code"}
{"TimeStamp":"2026-01-16T12:28:52.8348344+00:00","Log":"File "\u003Cfrozen runpy\u003E", line 88, in _run_code"}
{"TimeStamp":"2026-01-16T12:28:52.834841+00:00","Log":"File "pipelines/staging/load_duckdb.py", line 41, in \u003Cmodule\u003E"}
{"TimeStamp":"2026-01-16T12:28:52.8348475+00:00","Log":"charger_avec_duckdb()"}
{"TimeStamp":"2026-01-16T12:28:52.8348536+00:00","Log":"File "pipelines/staging/load_duckdb.py", line 16, in charger_avec_duckdb"}
{"TimeStamp":"2026-01-16T12:28:52.8348596+00:00","Log":"with get_database_duckdb():"}
{"TimeStamp":"2026-01-16T12:28:52.8349284+00:00","Log":"File "/usr/local/lib/python3.11/contextlib.py", line 137, in __enter__"}
{"TimeStamp":"2026-01-16T12:28:52.8349389+00:00","Log":"return next(self.gen)"}
{"TimeStamp":"2026-01-16T12:28:52.8349458+00:00","Log":"^^^^^^^^^^^^^^"}
{"TimeStamp":"2026-01-16T12:28:52.8349525+00:00","Log":"File "/app/utils/database.py", line 51, in get_database_duckdb"}
{"TimeStamp":"2026-01-16T12:28:52.8349587+00:00","Log":"connection.execute(f""""}
{"TimeStamp":"2026-01-16T12:28:52.8349667+00:00","Log":"IO Error: Unable to connect to Postgres at "postgresql://citus:50[Sj\u003EDO79!1GnldH*n\u003Ez%Kk@c-cosmos-nyctaxi-dev-x72pea.xsy2tm3latntrz.postgres.cosmos.azure.com:5432/citus": invalid percent-encoded token: "50[Sj\u003EDO79!1GnldH*n\u003Ez%Kk""}
{"TimeStamp":"2026-01-16T12:28:52.8349728+00:00","Log":""}
```

> L’erreur est liée à l’encodage du mot de passe PostgreSQL dans l’URL de connexion.
> L’infrastructure est fonctionnelle, mais la configuration applicative nécessite un `URL encoding` du mot de passe pour les caractères spéciaux.

### 8. Vérification du compte de stockage

```bash terraform
> az storage account show \
>   --name stnyctaxidev9sns2p \
>   --resource-group cmartinyRG \
>   -o table

AccessTier    AllowBlobPublicAccess    AllowCrossTenantReplication    AllowSharedKeyAccess    CreationTime                      DefaultToOAuthAuthentication    DnsEndpointType    EnableHttpsTrafficOnly    EnableNfsV3    IsHnsEnabled    IsLocalUserEnabled    IsSftpEnabled    Kind       Location       MinimumTlsVersion    Name                PrimaryLocation    ProvisioningState    PublicNetworkAccess    ResourceGroup    StatusOfPrimary
------------  -----------------------  -----------------------------  ----------------------  --------------------------------  ------------------------------  -----------------  ------------------------  -------------  --------------  --------------------  ---------------  ---------  -------------  -------------------  ------------------  -----------------  -------------------  ---------------------  ---------------  -----------------
Hot           False                    False                          True                    2026-01-16T10:36:57.361083+00:00  False                           Standard           True                      False          False           True                  False            StorageV2  francecentral  TLS1_2               stnyctaxidev9sns2p  francecentral      Succeeded            Enabled                cmartinyRG       available
```

### 9. Vérification des containers du Storage Account

```bash terraform
> az storage container list \
>   --account-name stnyctaxidev9sns2p \
>   --auth-mode login \
>   -o table

Name       Lease Status    Last Modified
---------  --------------  -------------------------
processed                  2026-01-16T10:37:59+00:00
raw                        2026-01-16T10:37:59+00:00
```

### 10. Vérification du cluster Cosmos DB for PostgreSQL

```bash terraform
> az resource show \
>   --name cosmos-nyctaxi-dev-x72pea \
>   --resource-group cmartinyRG \
>   --resource-type "Microsoft.DBforPostgreSQL/serverGroupsv2" \
>   -o table

Location       Name                       ResourceGroup
-------------  -------------------------  ---------------
francecentral  cosmos-nyctaxi-dev-x72pea  cmartinyRG
```

### 11. Vérification de la règle firewall PostgreSQL

```bash terraform
> az resource list \
>   --resource-group cmartinyRG \
>   --resource-type "Microsoft.DBforPostgreSQL/serverGroupsv2/firewallRules" \
>   -o table

[vide]
```

> Aucune règle listée via Azure CLI, cependant la règle `allow-azure-services` est bien créée via Terraform et visible dans le state.

### 12. Vérification de la connectivité PostgreSQL

Connexion avec DBeaver avec les informations suivantes :

Le host (`fullyQualifiedDomainName`) :
```bash terraform
az resource show \
   -g cmartinyRG \
   -n cosmos-nyctaxi-dev-x72pea \
   --resource-type "Microsoft.DBforPostgreSQL/serverGroupsv2" \
   --query "properties" \
   -o jsonc
```

DB : citus
user : citus
pwd en clair : `terraform output -raw cosmos_postgres_admin_password` à condition d'avoir le pwd dans les outputs même <sensive>.

Une fois connecté, faire un `select 1` dans Postgres pour vérifier.

## Lancement des pipelines

