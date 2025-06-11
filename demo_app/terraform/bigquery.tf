resource "google_bigquery_dataset" "dataset" {
  #checkov:skip=CKV_GCP_81:Google-managed keys are acceptable
  dataset_id = "corporate_events"
  location   = local.gcp_region
}

resource "google_bigquery_table" "dataset_info" {
  #checkov:skip=CKV_GCP_80:Google-managed keys are acceptable
  #checkov:skip=CKV_GCP_121:No delete protection
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  deletion_protection = false
  table_id            = "inventory"
  schema              = <<EOF
  [
    {
        "name": "product_id", "type": "STRING", "mode": "REQUIRED"
    },
    {
        "name": "product_name", "type": "STRING", "mode": "REQUIRED"
    },
    {
        "name": "product_count", "type": "INT64", "mode": "REQUIRED"
    },
    {
        "name": "product_description", "type": "STRING", "mode": "NULLABLE"
    },
    {
        "name": "product_image_url", "type": "STRING", "mode": "NULLABLE"
    }
  ]
  EOF
}
