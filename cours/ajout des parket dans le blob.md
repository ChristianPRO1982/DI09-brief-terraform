(venv) ➜  DI09-brief-terraform git:(main) ✗ python -m src.debug_list_raw

2026-01-16 15:44:54,174 | INFO | azure.core.pipeline.policies.http_logging_policy | Request URL: 'https://stnyctaxidev9sns2p.blob.core.windows.net/raw?restype=REDACTED&comp=REDACTED'
Request method: 'GET'
Request headers:
    'x-ms-version': 'REDACTED'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.23.0 Python/3.12.3 (Linux-6.8.0-49-generic-x86_64-with-glibc2.39)'
    'x-ms-date': 'REDACTED'
    'x-ms-client-request-id': 'eb8dc6d5-f2e9-11f0-bcb4-ace2d33c94a6'
    'Authorization': 'REDACTED'
No body was attached to the request
2026-01-16 15:44:54,300 | INFO | azure.core.pipeline.policies.http_logging_policy | Response status: 200
Response headers:
    'Transfer-Encoding': 'chunked'
    'Content-Type': 'application/xml'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-request-id': '215c20de-c01e-0065-63f6-866da9000000'
    'x-ms-client-request-id': 'eb8dc6d5-f2e9-11f0-bcb4-ace2d33c94a6'
    'x-ms-version': 'REDACTED'
    'Date': 'Fri, 16 Jan 2026 14:44:53 GMT'
2026-01-16 15:44:54,301 | INFO | debug_list_raw | Listed blobs=0 (max=50)
(venv) ➜  DI09-brief-terraform git:(main) ✗ 

OK ✅ résultat ultra clair : le container raw est vide (0 blob listés). Et pourtant on a HTTP 200, donc accès OK, juste pas de data dedans.

👉 Donc la prochaine étape (unique) n’est pas “trouver le bon prefix”, mais prouver où la data a été déposée (ou pourquoi elle ne l’a pas été).

Pourquoi

Tant que raw est vide, aucun pipeline de load/transfo ne pourra être validé. Le brief attend des preuves (logs + SQL) → la preuve #1 à faire maintenant : la data existe bien quelque part (dans processed ou dans un autre container / autre storage account).

Comment (diagnostic minimal, production-friendly)

Lister le contenu de processed (on sait qu’il existe)

Si processed contient déjà les Parquet, on adapte le pipeline pour lire processed (ça reste OK : c’est juste un container).

Si processed est vide aussi, alors le pipeline d’ingestion “réussi” n’a pas écrit là où tu crois → on remonte d’un cran : vérifier l’app Container Apps env vars + logs d’écriture.

Actions concrètes (à faire maintenant)
1️⃣ Tester processed via CLI (preuve immédiate)
az storage blob list \
  --connection-string "$AZURE_STORAGE_CONNECTION_STRING" \
  --container-name processed \
  --num-results 20 \
  --output table


Puis pareil pour raw (pour archiver la preuve qu’il est vide) :

az storage blob list \
  --connection-string "$AZURE_STORAGE_CONNECTION_STRING" \
  --container-name raw \
  --num-results 20 \
  --output table


✅ Ce que j’attends :

soit tu vois des blobs dans processed

soit c’est vide aussi

2️⃣ Si processed contient des fichiers

On fait une seule modif côté .env :

AZURE_CONTAINER_NAME=processed


Et on relance :

python -m src.check_raw_blobs


(Le script utilise AZURE_CONTAINER_NAME, donc il listera processed à la place de raw.)

3️⃣ Si processed est vide aussi

Alors on passe en mode “preuve infra/app” :

Commande pour voir les env vars de ton Container App (sans Terraform) :

az containerapp show \
  --name <container_app_name> \
  --resource-group <resource_group_name> \
  --query "properties.template.containers[0].env" \
  --output table


Et logs récents :

az containerapp logs show \
  --name <container_app_name> \
  --resource-group <resource_group_name> \
  --tail 200

Petit fix pour ton bruit de logs Python (optionnel)

Là, tu as toujours les logs azure.core.pipeline... parce que ton logger “azure” ne couvre pas forcément azure.core.pipeline. Mets ça dans configure_logging() :

logging.getLogger("azure").setLevel(getattr(logging, azure_level, logging.WARNING))
logging.getLogger("azure.core").setLevel(getattr(logging, azure_level, logging.WARNING))

Question rapide (pour enchaîner)

Quand tu fais la commande CLI sur processed, tu vois des blobs ?

👉 Réponds juste par :

“processed: X blobs” (même approximatif)
ou

“processed: 0”

/workspace/terraform # az containerapp show \
>   --name <container_app_name> \
>   --resource-group <resource_group_name> \
>   --query "properties.template.containers[0].env" \
>   --output table
sh: can't open container_app_name: no such file
/workspace/terraform # az containerapp logs show \
>   --name <container_app_name> \
>   --resource-group <resource_group_name> \
>   --tail 200
sh: can't open container_app_name: no such file

Tu as juste lancé les commandes avec les chevrons (<...>). En shell, ça se lit comme une redirection de fichier, donc sh: can't open ... → normal.

Étape unique (maintenant) : récupérer les vrais noms (resource group + container app)
1) Lister tes Container Apps dans l’abonnement
az containerapp list --output table


Tu vas voir une table avec au moins : Name et ResourceGroup.

2) (Optionnel) Lister les resource groups si besoin
az group list --output table

3) Relancer les commandes avec les vrais noms

Exemple (tu remplaces RG et APP) :

RG="ton-resource-group"
APP="ton-container-app-name"

az containerapp show \
  --name "$APP" \
  --resource-group "$RG" \
  --query "properties.template.containers[0].env" \
  --output table


Et les logs :

az containerapp logs show \
  --name "$APP" \
  --resource-group "$RG" \
  --tail 200

Ce que tu me colles ensuite (preuves)

La sortie de az containerapp list --output table (ou juste la ligne avec ton app)

Puis la table des env vars (celle du show ... env)

Et 20–30 lignes pertinentes de logs si on voit une écriture blob

Question rapide

Quand tu fais az containerapp list --output table, tu vois combien de Container Apps, et c’est quoi le Name + ResourceGroup de celle du pipeline ?

/workspace/terraform # az containerapp show \
>   --name "$APP" \
>   --resource-group "$RG" \
>   --query "properties.template.containers[0].env" \
>   --output table
Name               Value
-----------------  --------------------------------------------------------------------
POSTGRES_HOST      c-cosmos-nyctaxi-dev-x72pea.xsy2tm3latntrz.postgres.cosmos.azure.com
POSTGRES_PORT      5432
POSTGRES_DB        citus
POSTGRES_USER      citus
POSTGRES_SSL_MODE  require
POSTGRES_PASSWORD  dhnjnX68mkiHnHLmMNdkbala
START_DATE         2025-11
END_DATE           2025-11
RUN_ID             1768571412
/workspace/terraform # 

Top, là on a une preuve essentielle : ton Container App n’a aucune variable Azure Storage (ni connection string, ni account/container). Donc même si le pipeline “tourne”, il ne peut pas écrire dans Blob Storage → ça explique pourquoi raw est vide.

Prochaine étape (unique) : injecter les env vars Storage dans la Container App (sans Terraform)
Pourquoi

C’est le chaînon manquant pour que l’ingestion dépose des Parquet dans raw/.

C’est 100% “prod pragmatique” : config via env vars, pas de secrets en dur.

Pas besoin de refaire l’infra Terraform.

Comment

On va :

récupérer la connection string du Storage Account

la mettre en secret dans Container Apps

exposer AZURE_STORAGE_CONNECTION_STRING + AZURE_CONTAINER_NAME=raw

relancer un run et prouver avec az storage blob list + logs

Actions concrètes
1) Dans ton shell, prépare RG/APP (si pas déjà)
echo "$RG"
echo "$APP"

2) Injecter les variables dans la Container App

Option A (recommandée) : stocker la connection string en secret et la référencer.

az containerapp secret set \
  --name "$APP" \
  --resource-group "$RG" \
  --secrets storage-conn="$AZURE_STORAGE_CONNECTION_STRING"


Puis ajouter les env vars (dont une depuis secret) :

az containerapp update \
  --name "$APP" \
  --resource-group "$RG" \
  --set-env-vars \
    AZURE_CONTAINER_NAME=raw \
    AZURE_STORAGE_CONNECTION_STRING=secretref:storage-conn

3) Vérifier que les env vars sont bien présentes
az containerapp show \
  --name "$APP" \
  --resource-group "$RG" \
  --query "properties.template.containers[0].env" \
  --output table


Tu dois voir :

AZURE_CONTAINER_NAME

AZURE_STORAGE_CONNECTION_STRING (valeur = secretref:storage-conn)

4) Relancer le pipeline + preuve

Logs :

az containerapp logs show \
  --name "$APP" \
  --resource-group "$RG" \
  --tail 200


Et côté storage, vérifier que ça écrit enfin dans raw :

az storage blob list \
  --connection-string "$AZURE_STORAGE_CONNECTION_STRING" \
  --container-name raw \
  --num-results 20 \
  --output table

Mini-question (pour éviter un piège)

Tu préfères que le pipeline écrive dans :

raw (normal pour ingestion)

processed (si ton pipeline actuel fait déjà staging/transfo)

Réponds juste : raw ou processed.

/workspace/terraform # az containerapp update \
>   --name "$APP" \
>   --resource-group "$RG" \
>   --set-env-vars \
>     AZURE_CONTAINER_NAME=raw \
>     AZURE_STORAGE_CONNECTION_STRING=secretref:storage-conn
{
  "id": "/subscriptions/5e2150ec-ee17-4fa2-8714-825c2fb7d22a/resourceGroups/cmartinyRG/providers/Microsoft.App/containerapps/ca-nyctaxi-pipeline-dev",
  "identity": {
    "type": "None"
  },
  "location": "France Central",
  "name": "ca-nyctaxi-pipeline-dev",
  "properties": {
    "configuration": {
      "activeRevisionsMode": "Single",
      "dapr": null,
      "ingress": null,
      "maxInactiveRevisions": 0,
      "registries": [
        {
          "identity": "",
          "passwordSecretRef": "acr-password",
          "server": "acrnyctaxidev.azurecr.io",
          "username": "acrnyctaxidev"
        }
      ],
      "secrets": [
        {
          "name": "acr-password"
        },
        {
          "name": "postgres-password"
        },
        {
          "name": "storage-conn"
        }
      ],
      "service": null
    },
    "customDomainVerificationId": "84DD1EFB2BE2EF11035312420E70F0AE4D132304AB193E212884EB36B70CF8A3",
    "delegatedIdentities": [],
    "environmentId": "/subscriptions/5e2150ec-ee17-4fa2-8714-825c2fb7d22a/resourceGroups/cmartinyRG/providers/Microsoft.App/managedEnvironments/cae-nyctaxi-dev",
    "eventStreamEndpoint": "https://francecentral.azurecontainerapps.dev/subscriptions/5e2150ec-ee17-4fa2-8714-825c2fb7d22a/resourceGroups/cmartinyRG/containerApps/ca-nyctaxi-pipeline-dev/eventstream",
    "latestReadyRevisionName": "ca-nyctaxi-pipeline-dev--0000005",
    "latestRevisionFqdn": "",
    "latestRevisionName": "ca-nyctaxi-pipeline-dev--0000006",
    "managedEnvironmentId": "/subscriptions/5e2150ec-ee17-4fa2-8714-825c2fb7d22a/resourceGroups/cmartinyRG/providers/Microsoft.App/managedEnvironments/cae-nyctaxi-dev",
    "outboundIpAddresses": [
      "4.251.178.18"
    ],
    "provisioningState": "Succeeded",
    "runningStatus": "Running",
    "template": {
      "containers": [
        {
          "env": [
            {
              "name": "POSTGRES_HOST"
            },
            {
              "name": "POSTGRES_PORT"
            },
            {
              "name": "POSTGRES_DB"
            },
            {
              "name": "POSTGRES_USER"
            },
            {
              "name": "POSTGRES_SSL_MODE"
            },
            {
              "name": "POSTGRES_PASSWORD"
            },
            {
              "name": "START_DATE"
            },
            {
              "name": "END_DATE"
            },
            {
              "name": "RUN_ID"
            },
            {
              "name": "AZURE_CONTAINER_NAME"
            },
            {
              "name": "AZURE_STORAGE_CONNECTION_STRING",
              "secretRef": "storage-conn"
            }
          ],
          "image": "acrnyctaxidev.azurecr.io/nyc-taxi-pipeline:latest",
          "name": "pipeline",
          "probes": [],
          "resources": {
            "cpu": 0.5,
            "ephemeralStorage": "2Gi",
            "memory": "1Gi"
          }
        }
      ],
      "initContainers": null,
      "revisionSuffix": "",
      "scale": {
        "maxReplicas": 1,
        "minReplicas": null,
        "rules": null
      },
      "serviceBinds": null,
      "terminationGracePeriodSeconds": null,
      "volumes": []
    },
    "workloadProfileName": null
  },
  "resourceGroup": "cmartinyRG",
  "systemData": {
    "createdAt": "2026-01-16T10:57:14.6132809",
    "createdBy": "cmartiny.ext@simplonformations.onmicrosoft.com",
    "createdByType": "User",
    "lastModifiedAt": "2026-01-16T14:51:51.8282469",
    "lastModifiedBy": "cmartiny.ext@simplonformations.onmicrosoft.com",
    "lastModifiedByType": "User"
  },
  "tags": {
    "Environment": "dev",
    "ManagedBy": "Terraform",
    "Owner": "PJ",
    "Project": "NYC Taxi Pipeline"
  },
  "type": "Microsoft.App/containerApps"
}
/workspace/terraform # az containerapp logs show \
>   --name "$APP" \
>   --resource-group "$RG" \
>   --tail 200
{"TimeStamp":"2026-01-16T14:52:41.75889","Log":"Connecting to the container 'pipeline'..."}
{"TimeStamp":"2026-01-16T14:52:41.9","Log":"Successfully Connected to container: 'pipeline' [Revision: 'ca-nyctaxi-pipeline-dev--0000006', Replica: 'ca-nyctaxi-pipeline-dev--0000006-f58d8974-cv4hr']"}
{"TimeStamp":"2026-01-16T14:52:05.6316182+00:00","Log":"14:52:05.629 | INFO     | __main__:main:7 - \uD83D\uDE80 D\u00E9marrage du pipeline NYC Taxi"}
{"TimeStamp":"2026-01-16T14:52:05.938955+00:00","Log":"14:52:05.938 | INFO     | __main__:\u003Cmodule\u003E:96 - D\u00E9marrage de la Pipeline 1 : T\u00E9l\u00E9chargement des donn\u00E9es"}
{"TimeStamp":"2026-01-16T14:52:05.9390016+00:00","Log":""}
{"TimeStamp":"2026-01-16T14:52:05.942457+00:00","Log":"14:52:05.942 | INFO     | __main__:telecharger_donnees_taxi:75 - 1 fichiers \u00E0 t\u00E9l\u00E9charger"}
{"TimeStamp":"2026-01-16T14:52:05.9424801+00:00","Log":""}
{"TimeStamp":"2026-01-16T14:52:05.9424953+00:00","Log":"14:52:05.942 | INFO     | __main__:telecharger_donnees_taxi:80 - Mode Azure activ\u00E9"}
{"TimeStamp":"2026-01-16T14:52:05.9426018+00:00","Log":"14:52:05.942 | INFO     | utils.download_helper:download_file_from_url:10 - T\u00E9l\u00E9chargement de https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet..."}
{"TimeStamp":"2026-01-16T14:52:06.6324345+00:00","Log":"14:52:06.632 | SUCCESS  | utils.download_helper:download_file_from_url:17 - Fichier t\u00E9l\u00E9charg\u00E9 avec succ\u00E8s (67.84 MB)"}
{"TimeStamp":"2026-01-16T14:52:08.934176+00:00","Log":"14:52:08.933 | SUCCESS  | utils.download_helper:upload_file_to_azure:85 - Fichier upload\u00E9 vers Azure : raw/yellow_tripdata_2025-11.parquet"}
{"TimeStamp":"2026-01-16T14:52:08.9342723+00:00","Log":"14:52:08.934 | SUCCESS  | __main__:telecharger_donnees_taxi:92 -"}
{"TimeStamp":"2026-01-16T14:52:08.9342964+00:00","Log":"termin\u00E9"}
{"TimeStamp":"2026-01-16T14:52:08.9343199+00:00","Log":"14:52:08.934 | INFO     | __main__:main:10 - \uD83D\uDCE5 \u00C9tape 1: Chargement dans DuckDB..."}
{"TimeStamp":"2026-01-16T14:52:09.029352+00:00","Log":"14:52:09.029 | INFO     | __main__:\u003Cmodule\u003E:37 - D\u00E9marrage de la Pipeline DUCKDB"}
{"TimeStamp":"2026-01-16T14:52:09.0294062+00:00","Log":"14:52:09.029 | INFO     | utils.database:get_database_postgresql:15 - Connexion \u00E0 la base de donn\u00E9es PostgreSQL..."}
{"TimeStamp":"2026-01-16T14:52:09.2682584+00:00","Log":"14:52:09.268 | SUCCESS  | utils.database:get_database_postgresql:28 - Connexion \u00E0 la base de donn\u00E9es OK"}
{"TimeStamp":"2026-01-16T14:52:09.302669+00:00","Log":"14:52:09.302 | SUCCESS  | utils.database:execute_sql_file_postgresql:78 - Fichier sql/create_staging_table.sql ex\u00E9cut\u00E9 avec succ\u00E8s"}
{"TimeStamp":"2026-01-16T14:52:09.3030272+00:00","Log":"14:52:09.302 | INFO     | utils.database:get_database_postgresql:37 - Connexion ferm\u00E9e"}
{"TimeStamp":"2026-01-16T14:52:09.303075+00:00","Log":"14:52:09.302 | INFO     | __main__:\u003Cmodule\u003E:39 - TRUNCATE"}
{"TimeStamp":"2026-01-16T14:52:09.3031987+00:00","Log":"14:52:09.303 | INFO     | utils.database:get_database_postgresql:15 - Connexion \u00E0 la base de donn\u00E9es PostgreSQL..."}
{"TimeStamp":"2026-01-16T14:52:09.3685842+00:00","Log":"14:52:09.368 | SUCCESS  | utils.database:get_database_postgresql:28 - Connexion \u00E0 la base de donn\u00E9es OK"}
/workspace/terraform # 

Parfait ✅ là tu as la preuve qu’on cherchait : le pipeline upload bien vers Blob Storage :

SUCCESS ... Fichier uploadé vers Azure : raw/yellow_tripdata_2025-11.parquet

Donc maintenant, la prochaine étape de pipeline (une seule) c’est :

Étape suivante : preuve de présence + convention de chemin dans raw
Pourquoi

Tu viens de prouver côté logs que ça écrit.

Il faut maintenant une preuve “storage” indépendante (CLI) + valider la convention exacte : le blob s’appelle raw/yellow_tripdata_2025-11.parquet (donc dans le container raw, le nom du blob est yellow_tripdata_2025-11.parquet).

Comment

On liste les blobs du container raw et on vérifie le nom exact.

Actions concrètes
1) Lister les blobs raw
az storage blob list \
  --connection-string "$AZURE_STORAGE_CONNECTION_STRING" \
  --container-name raw \
  --prefix yellow_tripdata_2025-11 \
  --output table


Tu dois voir un blob du genre :

yellow_tripdata_2025-11.parquet

2) Vérifier la taille (preuve)
az storage blob show \
  --connection-string "$AZURE_STORAGE_CONNECTION_STRING" \
  --container-name raw \
  --name yellow_tripdata_2025-11.parquet \
  --query "properties.contentLength" \
  --output tsv


Tu devrais être autour de ~70MB (67.84 MB d’après tes logs).

3) Corriger ton script Python de listing (ton bug de prefix)

Dans src/check_raw_blobs.py, remplace :

prefix = f"yellow_tripdata_{month}"


par :

prefix = f"yellow_tripdata_{month}"


⚠️ Attends : ton upload est avec un tiret (2025-11), donc ça reste bon, MAIS ton premier script cherchait yellow_tripdata_2025-11 et il a trouvé 0 parce que… à ce moment-là, le container était vide.
Donc pas de changement de code nécessaire pour le prefix : on reteste maintenant que ça a écrit.

Relance :

python -m src.check_raw_blobs

Question rapide

Quand tu fais la commande az storage blob list ... --container-name raw --prefix yellow_tripdata_2025-11, tu vois bien le blob yellow_tripdata_2025-11.parquet ?
👉 Oui / Non

coté hôte :
(venv) ➜  DI09-brief-terraform git:(main) ✗ python -m src.debug_list_raw

2026-01-16 15:54:04,790 | INFO | azure.core.pipeline.policies.http_logging_policy | Request URL: 'https://stnyctaxidev9sns2p.blob.core.windows.net/raw?restype=REDACTED&comp=REDACTED'
Request method: 'GET'
Request headers:
    'x-ms-version': 'REDACTED'
    'Accept': 'application/xml'
    'User-Agent': 'azsdk-python-storage-blob/12.23.0 Python/3.12.3 (Linux-6.8.0-49-generic-x86_64-with-glibc2.39)'
    'x-ms-date': 'REDACTED'
    'x-ms-client-request-id': '33befb50-f2eb-11f0-a655-ace2d33c94a6'
    'Authorization': 'REDACTED'
No body was attached to the request
2026-01-16 15:54:04,884 | INFO | azure.core.pipeline.policies.http_logging_policy | Response status: 200
Response headers:
    'Transfer-Encoding': 'chunked'
    'Content-Type': 'application/xml'
    'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0'
    'x-ms-request-id': '6105edf3-501e-00e1-3ff7-861fa8000000'
    'x-ms-client-request-id': '33befb50-f2eb-11f0-a655-ace2d33c94a6'
    'x-ms-version': 'REDACTED'
    'Date': 'Fri, 16 Jan 2026 14:54:04 GMT'
2026-01-16 15:54:04,886 | INFO | debug_list_raw | Blob name=yellow_tripdata_2025-11.parquet size=71134255
2026-01-16 15:54:04,886 | INFO | debug_list_raw | Listed blobs=1 (max=50)
(venv) ➜  DI09-brief-terraform git:(main) ✗ 

Parfait ✅ tu as maintenant la preuve côté hôte :

blob présent : yellow_tripdata_2025-11.parquet

taille : 71134255 (~67.9 MB)

Donc on peut passer à la prochaine étape de pipeline (une seule) :

Étape suivante : Load “raw Parquet ➜ PostgreSQL staging” (preuve SQL)
Pourquoi

Tu as l’ingestion (raw) validée.

Le brief veut des preuves en base (requêtes SQL) → on charge dans une table staging.

Ça prépare direct la transformation “processed/star schema”.

Comment

Télécharger le Parquet depuis Blob (temp local)

Lire avec DuckDB (rapide + compatible Parquet)

Créer la table staging si absente

Insérer en batch

Log : lignes chargées + durée

Actions concrètes
1) Ajouter un script de load (minimal, robuste)

Crée src/load_to_postgres.py :

"""Load NYC Taxi parquet files from Azure Blob Storage into PostgreSQL staging."""

from __future__ import annotations

import logging
import os
import tempfile
import time

import duckdb
from dotenv import load_dotenv

from src.azure_blob import AzureBlobClient
from src.config import load_config
from src.logging_utils import configure_logging
from src.pipeline_load import build_pg_client


def main() -> int:
    load_dotenv()
    configure_logging()
    logger = logging.getLogger("load_to_postgres")

    cfg = load_config()

    blob_name = f"yellow_tripdata_{cfg.start_date}.parquet"
    logger.info("Loading blob=%s from container=%s", blob_name, cfg.azure_container_name)

    blob_client = AzureBlobClient(
        connection_string=cfg.azure_storage_connection_string,
        container_name=cfg.azure_container_name,
    )

    pg_client = build_pg_client(
        host=cfg.postgres_host,
        port=cfg.postgres_port,
        dbname=cfg.postgres_db,
        user=cfg.postgres_user,
        password=cfg.postgres_password,
        sslmode=cfg.postgres_ssl_mode,
    )

    pg_client.ensure_staging_table(cfg.staging_table)

    start_ts = time.time()
    with tempfile.TemporaryDirectory() as tmpdir:
        local_path = os.path.join(tmpdir, blob_name)
        blob_client.download_to_path(blob_name, local_path)
        logger.info("Downloaded to %s", local_path)

        con = duckdb.connect(database=":memory:")
        con.execute("INSTALL postgres;")
        con.execute("LOAD postgres;")

        con.execute(
            """
            CREATE TEMP TABLE cleaned AS
            SELECT
                row_number() OVER ()::BIGINT AS trip_id,
                VendorID::INTEGER AS vendor_id,
                tpep_pickup_datetime::TIMESTAMP AS tpep_pickup_datetime,
                tpep_dropoff_datetime::TIMESTAMP AS tpep_dropoff_datetime,
                passenger_count::INTEGER AS passenger_count,
                trip_distance::DOUBLE AS trip_distance,
                RatecodeID::INTEGER AS ratecode_id,
                PULocationID::INTEGER AS pu_location_id,
                DOLocationID::INTEGER AS do_location_id,
                payment_type::INTEGER AS payment_type,
                fare_amount::DOUBLE AS fare_amount,
                extra::DOUBLE AS extra,
                mta_tax::DOUBLE AS mta_tax,
                tip_amount::DOUBLE AS tip_amount,
                tolls_amount::DOUBLE AS tolls_amount,
                improvement_surcharge::DOUBLE AS improvement_surcharge,
                total_amount::DOUBLE AS total_amount,
                (
                    EXTRACT(EPOCH FROM (tpep_dropoff_datetime::TIMESTAMP - tpep_pickup_datetime::TIMESTAMP))
                    / 60.0
                )::DOUBLE AS trip_duration_minutes
            FROM read_parquet(?)
            WHERE
                trip_distance IS NOT NULL
                AND trip_distance > 0
                AND tpep_pickup_datetime IS NOT NULL
                AND tpep_dropoff_datetime IS NOT NULL
                AND tpep_dropoff_datetime >= tpep_pickup_datetime;
            """,
            [local_path],
        )

        row_count = con.execute("SELECT COUNT(*) FROM cleaned;").fetchone()[0]
        logger.info("Prepared cleaned rows=%d", row_count)

        pg_dsn = pg_client._dsn.to_dsn_string()
        con.execute("ATTACH ? AS pg (TYPE postgres);", [pg_dsn])

        con.execute(f"TRUNCATE TABLE pg.public.{cfg.staging_table};")
        con.execute(f"INSERT INTO pg.public.{cfg.staging_table} SELECT * FROM cleaned;")

        logger.info("Loaded rows=%d into %s", row_count, cfg.staging_table)

    elapsed = time.time() - start_ts
    logger.info("Done elapsed=%.2fs", elapsed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


Note : je fais un TRUNCATE pour que ce run soit rejouable sans doublons (pratique pour le brief).

2) Lancer côté hôte

Assure-toi que ton .env contient bien :

AZURE_CONTAINER_NAME=raw
STAGING_TABLE=staging_taxi_trips
START_DATE=2025-11
END_DATE=2025-11


Puis :

python -m src.load_to_postgres

Preuves à produire (SQL)

Une fois chargé, prouve avec :

SELECT COUNT(*) AS rows FROM staging_taxi_trips;

SELECT
  MIN(tpep_pickup_datetime) AS min_pickup,
  MAX(tpep_pickup_datetime) AS max_pickup
FROM staging_taxi_trips;

SELECT
  AVG(trip_duration_minutes) AS avg_duration_min,
  AVG(trip_distance) AS avg_distance
FROM staging_taxi_trips;

Question rapide (avant que tu lances)

Tu exécutes ce load :

A) sur ta machine hôte (python local)

B) dans la Container App (pipeline end-to-end)

Réponds A ou B.