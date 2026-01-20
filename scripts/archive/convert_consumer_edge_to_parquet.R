library(data.table)
library(arrow)

input_dir <- "/global/scratch/users/maxkagan/01_foot_traffic_location/consumer_edge_data_2026-01-12/brand-and-geography-cohort-breakout-usa-1"
output_dir <- "/global/scratch/users/maxkagan/01_foot_traffic_location/consumer_edge_data_2026-01-12/parquet"

dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

files <- list.files(input_dir, pattern = "\\.csv\\.gz$", full.names = TRUE)
cat("Found", length(files), "CSV files to convert\n")

cat("Reading all CSV files...\n")
start_time <- Sys.time()
dt <- rbindlist(lapply(files, fread), fill = TRUE)
read_time <- Sys.time()
cat("Read", nrow(dt), "rows in", round(difftime(read_time, start_time, units = "mins"), 2), "minutes\n")

if (!inherits(dt$PERIOD_START_DT, "Date")) {
  dt[, PERIOD_START_DT := as.Date(PERIOD_START_DT)]
}
if (!inherits(dt$PERIOD_END_DT, "Date")) {
  dt[, PERIOD_END_DT := as.Date(PERIOD_END_DT)]
}

output_file <- file.path(output_dir, "consumer_edge_brand_geo.parquet")
cat("Writing Parquet file to:", output_file, "\n")
write_parquet(dt, output_file, compression = "snappy")
write_time <- Sys.time()

file_size_gb <- file.info(output_file)$size / 1e9
cat("Parquet file size:", round(file_size_gb, 2), "GB\n")
cat("Write completed in", round(difftime(write_time, read_time, units = "mins"), 2), "minutes\n")
cat("Total time:", round(difftime(write_time, start_time, units = "mins"), 2), "minutes\n")
