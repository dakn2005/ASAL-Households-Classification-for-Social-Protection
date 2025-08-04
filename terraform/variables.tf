
variable "location" {
    description = "Project location"  
    default = "US"
}

variable "bq_dataset_name" {
    description = "BQ dataset name"  
    default = "[dataset name]"
}

variable "gcs_storage_class" {
    description = "Bucket storage class"
    default = "STANDARD"

}

variable "gcs_bucket_name" {
    description = "My bucket name"
    default = "[globally unique bucket name]"

}