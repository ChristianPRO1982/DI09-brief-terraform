# Rendu du brief

**Sommaire :**

A - Terraform déployé correctement ?

B - Lancement des pipelines et résultats

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

### pipeline 1 - ingestion + staging + transformation dans DB Cosmos
**1 - Mettre les dates du run (START_DATE / END_DATE)**

```bash terraform
az containerapp update \
  --name ca-nyctaxi-pipeline-dev \
  --resource-group cmartinyRG \
  --set-env-vars START_DATE=2024-01 END_DATE=2024-01
```

ça peut être utile :
```bash terraform
az containerapp update \
  --name ca-nyctaxi-pipeline-dev \
  --resource-group cmartinyRG \
  --set-env-vars POSTGRES_PASSWORD="<NOUVEAU_PASSWORD>"
```

**2 - Relancer le pipeline (restart de la revision active)**

```bash terraform
az containerapp revision list \
  --name ca-nyctaxi-pipeline-dev \
  --resource-group cmartinyRG \
  -o table
```

Repère le nom de revision (ex: ca-nyctaxi-pipeline-dev--xxxxx), puis redémarre-la :
```bash terraform
az containerapp revision restart \
  --name ca-nyctaxi-pipeline-dev \
  --resource-group cmartinyRG \
  --revision <REVISION_NAME>
```
> `"Restart succeeded"`

**3 - Valider “ça run” dans les logs**

```bash terraform
az containerapp logs show \
  --name ca-nyctaxi-pipeline-dev \
  --resource-group cmartinyRG \
  --follow
```

résultats
```bash terraform
{"TimeStamp":"2026-01-16T13:50:41.68749","Log":"Connecting to the container 'pipeline'..."}
{"TimeStamp":"2026-01-16T13:50:41.78468","Log":"Successfully Connected to container: 'pipeline' [Revision: 'ca-nyctaxi-pipeline-dev--0000005', Replica: 'ca-nyctaxi-pipeline-dev--0000005-586d5c78d9-9bbtn']"}
{"TimeStamp":"2026-01-16T13:50:29.8949095+00:00","Log":"13:50:29.894 | INFO     | utils.database:get_database_postgresql:15 - Connexion \u00E0 la base de donn\u00E9es PostgreSQL..."}
{"TimeStamp":"2026-01-16T13:50:29.9342694+00:00","Log":"13:50:29.934 | SUCCESS  | utils.database:get_database_postgresql:28 - Connexion \u00E0 la base de donn\u00E9es OK"}
{"TimeStamp":"2026-01-16T13:50:29.9425858+00:00","Log":"13:50:29.942 | SUCCESS  | utils.database:execute_sql_file_postgresql:78 - Fichier sql/create_staging_table.sql ex\u00E9cut\u00E9 avec succ\u00E8s"}
{"TimeStamp":"2026-01-16T13:50:29.9428519+00:00","Log":"13:50:29.942 | INFO     | utils.database:get_database_postgresql:37 - Connexion ferm\u00E9e"}
{"TimeStamp":"2026-01-16T13:50:29.9430131+00:00","Log":"13:50:29.942 | INFO     | __main__:\u003Cmodule\u003E:39 - TRUNCATE"}
{"TimeStamp":"2026-01-16T13:50:29.9430313+00:00","Log":"13:50:29.942 | INFO     | utils.database:get_database_postgresql:15 - Connexion \u00E0 la base de donn\u00E9es PostgreSQL..."}
{"TimeStamp":"2026-01-16T13:50:29.9812842+00:00","Log":"13:50:29.981 | SUCCESS  | utils.database:get_database_postgresql:28 - Connexion \u00E0 la base de donn\u00E9es OK"}
{"TimeStamp":"2026-01-16T13:50:30.000284+00:00","Log":"13:50:29.999 | SUCCESS  | utils.database:execute_sql_file_postgresql:78 - Fichier sql/truncate.sql ex\u00E9cut\u00E9 avec succ\u00E8s"}
{"TimeStamp":"2026-01-16T13:50:30.0004856+00:00","Log":"13:50:30.000 | INFO     | utils.database:get_database_postgresql:37 - Connexion ferm\u00E9e"}
{"TimeStamp":"2026-01-16T13:50:30.0005232+00:00","Log":"13:50:30.000 | INFO     | utils.database:get_database_duckdb:42 - Connexion \u00E0 la base de donn\u00E9es DuckDB..."}
{"TimeStamp":"2026-01-16T13:50:30.0006764+00:00","Log":"13:50:30.000 | INFO     | utils.database:get_database_duckdb:46 - Configuration DuckDB : 4 threads"}
{"TimeStamp":"2026-01-16T13:50:32.2935108+00:00","Log":"13:50:32.293 | SUCCESS  | utils.database:get_database_duckdb:60 - Connexion \u00E0 la base de donn\u00E9es OK"}
{"TimeStamp":"2026-01-16T13:50:32.2965706+00:00","Log":"13:50:32.296 | INFO     | utils.database:get_database_duckdb:69 - Connexion ferm\u00E9e"}
{"TimeStamp":"2026-01-16T13:50:32.2966009+00:00","Log":"13:50:32.296 | INFO     | __main__:charger_avec_duckdb:24 - 1 fichiers d\u00E9tect\u00E9s"}
{"TimeStamp":"2026-01-16T13:50:32.2967334+00:00","Log":"13:50:32.296 | INFO     | __main__:charger_avec_duckdb:28 - Chargement optimis\u00E9 de TOUS les fichiers : data/raw/*.parquet"}
{"TimeStamp":"2026-01-16T13:50:32.2969108+00:00","Log":"13:50:32.296 | DEBUG    | utils.database:execute_sql_file_duckdb:98 - Param\u00E8tre remplac\u00E9 : {glob_pattern} -\u003E data/raw/*.parquet"}
{"TimeStamp":"2026-01-16T13:50:32.2980558+00:00","Log":"13:50:32.296 | INFO     | utils.database:get_database_duckdb:42 - Connexion \u00E0 la base de donn\u00E9es DuckDB..."}
{"TimeStamp":"2026-01-16T13:50:32.2980719+00:00","Log":"13:50:32.296 | INFO     | utils.database:get_database_duckdb:46 - Configuration DuckDB : 4 threads"}
{"TimeStamp":"2026-01-16T13:50:33.0964556+00:00","Log":"13:50:33.096 | SUCCESS  | utils.database:get_database_duckdb:60 - Connexion \u00E0 la base de donn\u00E9es OK"}
{"TimeStamp":"2026-01-16T13:50:33.0965061+00:00","Log":"13:50:33.096 | INFO     | utils.database:execute_sql_file_duckdb:101 - Ex\u00E9cution de sql/insert_to.sql..."}
{"TimeStamp":"2026-01-16T13:51:07.9018384+00:00","Log":"13:51:07.901 | SUCCESS  | utils.database:execute_sql_file_duckdb:103 - \u2713 sql/insert_to.sql ex\u00E9cut\u00E9 avec succ\u00E8s"}
{"TimeStamp":"2026-01-16T13:51:07.9084797+00:00","Log":"13:51:07.908 | INFO     | utils.database:get_database_duckdb:69 - Connexion ferm\u00E9e"}
{"TimeStamp":"2026-01-16T13:51:07.909395+00:00","Log":"13:51:07.908 | SUCCESS  | __main__:charger_avec_duckdb:30 - insert_to.sql ex\u00E9cut\u00E9 avec succ\u00E8s"}
{"TimeStamp":"2026-01-16T13:51:07.9094129+00:00","Log":"13:51:07.908 | INFO     | __main__:main:13 - \uD83D\uDD04 \u00C9tape 2: Transformation des donn\u00E9es..."}
{"TimeStamp":"2026-01-16T13:51:07.909449+00:00","Log":"13:51:07.909 | INFO     | __main__:\u003Cmodule\u003E:21 - D\u00E9marrage de la Pipeline : Transformation des donn\u00E9es"}
{"TimeStamp":"2026-01-16T13:51:07.9096544+00:00","Log":"13:51:07.909 | INFO     | utils.database:get_database_postgresql:15 - Connexion \u00E0 la base de donn\u00E9es PostgreSQL..."}
{"TimeStamp":"2026-01-16T13:51:07.992883+00:00","Log":"13:51:07.992 | SUCCESS  | utils.database:get_database_postgresql:28 - Connexion \u00E0 la base de donn\u00E9es OK"}
{"TimeStamp":"2026-01-16T13:51:08.3008+00:00","Log":"13:51:08.300 | SUCCESS  | utils.database:execute_sql_file_postgresql:78 - Fichier sql/transformations.sql ex\u00E9cut\u00E9 avec succ\u00E8s"}
{"TimeStamp":"2026-01-16T13:51:08.3012373+00:00","Log":"13:51:08.301 | INFO     | utils.database:get_database_postgresql:37 - Connexion ferm\u00E9e"}
{"TimeStamp":"2026-01-16T13:51:08.3012782+00:00","Log":"13:51:08.301 | INFO     | __main__:transformer_donnees:17 - Connexion ferm\u00E9e"}
{"TimeStamp":"2026-01-16T13:51:08.3015503+00:00","Log":"13:51:08.301 | SUCCESS  | __main__:\u003Cmodule\u003E:23 - Pipeline termin\u00E9e : success"}
{"TimeStamp":"2026-01-16T13:51:08.301565+00:00","Log":"13:51:08.301 | SUCCESS  | __main__:main:16 - \u2705 Pipeline termin\u00E9 avec succ\u00E8s"}
```

**4 - Coté DBeaver**
```sql
select *
  from public.staging_taxi_trips
 limit 10
```
résultats
| trip_id | vendor_id | tpep_pickup_datetime     | tpep_dropoff_datetime    | passenger_count | trip_distance | ratecode_id | pu_location_id | do_location_id | payment_type | fare_amount | extra | mta_tax | tip_amount | tolls_amount | improvement_surcharge | total_amount | trip_duration_minutes |
|--------:|----------:|--------------------------|--------------------------|----------------:|--------------:|------------:|---------------:|---------------:|-------------:|------------:|------:|--------:|-----------:|--------------:|-----------------------:|-------------:|----------------------:|
| 478742  | 2         | 2025-11-05 17:33:06.000  | 2025-11-05 17:43:28.000  | 1               | 0.95          | 1           | 68             | 234            | 4            | 9.3         | 2.5   | 0.5     | 0.0        | 0.0           | 1.0                    | 16.55        | 10.37                 |
| 478743  | 2         | 2025-11-05 17:57:33.000  | 2025-11-05 18:03:55.000  | 5               | 0.72          | 1           | 170            | 186            | 1            | 7.2         | 2.5   | 0.5     | 2.89       | 0.0           | 1.0                    | 17.34        | 6.37                  |
| 478744  | 2         | 2025-11-05 17:55:12.000  | 2025-11-05 19:01:45.000  | 3               | 17.74         | 1           | 132            | 48             | 1            | 80.0        | 2.5   | 0.5     | 18.84      | 6.94          | 1.0                    | 114.78       | 66.55                 |
| 478745  | 2         | 2025-11-05 17:29:49.000  | 2025-11-05 17:50:14.000  | 3               | 1.02          | 1           | 230            | 164            | 1            | 17.0        | 2.5   | 0.5     | 4.85       | 0.0           | 1.0                    | 29.10        | 20.42                 |
| 478746  | 2         | 2025-11-05 17:52:37.000  | 2025-11-05 18:06:49.000  | 1               | 0.67          | 1           | 164            | 230            | 1            | 12.8        | 2.5   | 0.5     | 4.01       | 0.0           | 1.0                    | 24.06        | 14.20                 |
| 478747  | 1         | 2025-11-05 17:25:18.000  | 2025-11-05 17:33:22.000  | 1               | 0.70          | 1           | 107            | 107            | 2            | 8.6         | 5.75  | 0.5     | 0.0        | 0.0           | 1.0                    | 15.85        | 8.07                  |
| 478748  | 2         | 2025-11-05 17:46:53.000  | 2025-11-05 17:59:02.000  | 1               | 0.88          | 1           | 163            | 237            | 1            | 11.4        | 2.5   | 0.5     | 5.59       | 0.0           | 1.0                    | 24.24        | 12.15                 |
| 478749  | 2         | 2025-11-05 17:09:21.000  | 2025-11-05 17:32:21.000  | 1               | 1.94          | 1           | 162            | 140            | 1            | 20.5        | 2.5   | 0.5     | 3.0        | 0.0           | 1.0                    | 30.75        | 23.00                 |
| 478750  | 2         | 2025-11-05 17:47:40.000  | 2025-11-05 17:53:31.000  | 1               | 0.87          | 1           | 229            | 237            | 1            | 7.2         | 2.5   | 0.5     | 2.89       | 0.0           | 1.0                    | 17.34        | 5.85                  |
| 478751  | 2         | 2025-11-05 17:16:35.000  | 2025-11-05 17:33:17.000  | 1               | 1.46          | 1           | 239            | 230            | 1            | 15.6        | 2.5   | 0.5     | 4.57       | 0.0           | 1.0                    | 27.42        | 16.70                 |

### Pipeline 2 — Load (Blob Storage ➜ PostgreSQL “staging”)

Voir le code python dans `./src/`